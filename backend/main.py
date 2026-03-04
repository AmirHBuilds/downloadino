from fastapi import FastAPI, Depends, UploadFile, File as FastAPIFile, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import magic
from database import engine, Base, get_db
from models import User, Repository, File
from s3_utils import upload_to_s3, get_presigned_url, delete_from_s3
import uuid

# Create tables automatically (for MVP. Later use Alembic for migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Downloadino API")

# --- Dummy Auth for Demonstration ---
# In a full setup, we will use OAuth2PasswordBearer and JWT tokens here.
def get_current_user(db: Session = Depends(get_db)):
    # Fake user for testing: creates a user if none exists
    user = db.query(User).first()
    if not user:
        user = User(username="admin_test", role="SUPERADMIN")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# --- Repositories ---
@app.post("/api/repos")
def create_repo(name: str, description: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    existing = db.query(Repository).filter(Repository.owner_id == user.id, Repository.name == name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Repo already exists")
    
    repo = Repository(owner_id=user.id, name=name, description=description)
    db.add(repo)
    db.commit()
    return {"message": "Repository created", "repo_id": repo.id}

# --- File Upload with Security & Quota ---
@app.post("/api/repos/{repo_id}/upload")
async def upload_file(
    repo_id: str, 
    file: UploadFile = FastAPIFile(...), 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # 1. Read file into memory to check size & type
    file_bytes = await file.read()
    file_size = len(file_bytes)
    
    # 2. Check Quota
    if user.storage_used + file_size > user.storage_limit:
        raise HTTPException(status_code=402, detail="QUOTA_EXCEEDED: Please upgrade plan or request verification.")

    # 3. Security Check: Validate actual file type with python-magic
    mime_type = magic.from_buffer(file_bytes, mime=True)
    is_raw = mime_type.startswith('text/') or file.filename.endswith(('.sh', '.py', '.md'))
    
    # 4. Generate S3 Path
    s3_key = f"{user.username}/{repo.name}/{file.filename}"
    
    # 5. Reset file cursor and upload to S3
    await file.seek(0)
    success = upload_to_s3(file.file, s3_key, mime_type)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to upload to storage server")

    # 6. Database Update
    status_val = "APPROVED" if repo.owner_id == user.id else "PENDING_REVIEW"
    
    new_file = File(
        repo_id=repo.id,
        uploader_id=user.id,
        filename=file.filename,
        s3_key=s3_key,
        file_size=file_size,
        is_raw=is_raw,
        status=status_val
    )
    db.add(new_file)
    
    # Update user storage quota if approved immediately
    if status_val == "APPROVED":
        user.storage_used += file_size
        
    db.commit()
    return {"message": "File uploaded successfully", "filename": file.filename, "status": status_val}

# --- The "RAW" & "DOWNLOAD" System ---
@app.get("/raw/{username}/{repo_name}/{filename}")
def get_raw_file(username: str, repo_name: str, filename: str, db: Session = Depends(get_db)):
    """
    This behaves like raw.githubusercontent.com
    If someone runs `curl -Ls https://raw.downloadino.com/username/repo/file.sh`,
    we redirect them to the ArvanCloud pure text link.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user: raise HTTPException(status_code=404)
    
    repo = db.query(Repository).filter(Repository.owner_id == user.id, Repository.name == repo_name).first()
    if not repo: raise HTTPException(status_code=404)
    
    file_record = db.query(File).filter(File.repo_id == repo.id, File.filename == filename, File.status == "APPROVED").first()
    if not file_record: raise HTTPException(status_code=404, detail="File not found or pending review")

    # Get short-lived ArvanCloud URL
    url = get_presigned_url(file_record.s3_key, is_raw=file_record.is_raw)
    
    # 302 Redirect. curl handles this perfectly with the -L flag!
    return RedirectResponse(url=url)