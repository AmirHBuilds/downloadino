<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex flex-col gap-6 mb-8">
      <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
        <div>
          <p class="text-xs font-mono uppercase tracking-[0.3em] text-accent-2/80 mb-2">Explore</p>
          <h1 class="text-2xl sm:text-3xl font-bold">Discover repositories</h1>
          <p class="text-sm text-muted mt-2 max-w-2xl">
            Browse community mirrors and projects with a calmer flow — 40 repositories per page, sorted the way you want.
          </p>
        </div>

        <div class="card p-3 sm:p-4 w-full lg:w-auto">
          <div class="flex flex-col sm:flex-row gap-3 sm:items-center">
            <div class="rounded-2xl border border-accent-2/20 bg-accent-2/10 px-3 py-2 min-w-[10rem]">
              <p class="text-[11px] font-mono uppercase tracking-[0.25em] text-accent-2/80">Page size</p>
              <p class="text-sm font-semibold mt-1">40 repositories</p>
            </div>
            <label class="flex-1 sm:flex-none">
              <span class="block text-[11px] font-mono uppercase tracking-[0.25em] text-muted mb-2">Sort by</span>
              <select v-model="sort" class="input py-2 text-sm sm:w-52">
                <option value="downloads">Most downloaded</option>
                <option value="clones">Most cloned</option>
                <option value="recent">Recently updated</option>
              </select>
            </label>
          </div>
        </div>
      </div>

      <div class="card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gradient-to-r from-surface-1 via-surface-1 to-accent-2/5">
        <div>
          <p class="text-sm font-medium">Page {{ page }}</p>
          <p class="text-xs text-muted mt-1">
            <template v-if="pending">Loading repositories…</template>
            <template v-else>
              Showing {{ repos.length }} repository<span v-if="repos.length !== 1">ies</span><span v-else>y</span>
              on this page.
            </template>
          </p>
        </div>

        <div class="flex items-center gap-2 self-start sm:self-auto">
          <button class="btn-secondary px-3 py-2" :disabled="page === 1 || pending" @click="goToPage(page - 1)">
            <Icon name="mdilocal:arrow-left" class="w-4 h-4" />
            Previous
          </button>
          <div class="flex items-center gap-2 rounded-full border border-border bg-surface px-2 py-1.5 shadow-sm">
            <button
              v-for="pageNumber in visiblePages"
              :key="pageNumber"
              class="min-w-9 h-9 rounded-full text-sm font-medium transition-colors"
              :class="pageNumber === page ? 'bg-accent text-white shadow-sm' : 'text-muted hover:text-fg hover:bg-surface-2'"
              :disabled="pending"
              @click="goToPage(pageNumber)"
            >
              {{ pageNumber }}
            </button>
          </div>
          <button class="btn-primary px-3 py-2" :disabled="!canGoNext || pending" @click="goToPage(page + 1)">
            Next
          </button>
        </div>
      </div>
    </div>

    <div v-if="pending" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 9" :key="i" class="card p-4 animate-pulse h-32"></div>
    </div>
    <div v-else-if="repos?.length === 0" class="card text-center py-20 text-muted">
      <Icon name="mdilocal:source-repository-multiple" class="w-12 h-12 mx-auto mb-3 opacity-30" />
      <p class="text-sm">No repositories found for this page.</p>
      <button v-if="page > 1" class="btn-ghost mt-4" @click="goToPage(page - 1)">Go back one page</button>
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <RepoCard v-for="repo in repos" :key="repo.id" :repo="repo" />
    </div>

    <div class="mt-8 space-y-8">
      <div class="card p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <p class="text-sm font-medium">Keep exploring</p>
          <p class="text-xs text-muted mt-1">
            Use the page controls to move through the catalog in tidy 40-repository batches.
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button class="btn-secondary px-3 py-2" :disabled="page === 1 || pending" @click="goToPage(page - 1)">
            <Icon name="mdilocal:arrow-left" class="w-4 h-4" />
            Previous
          </button>
          <button class="btn-primary px-3 py-2" :disabled="!canGoNext || pending" @click="goToPage(page + 1)">
            Next page
          </button>
        </div>
      </div>

      <AdSlot position="explore_inline" :limit="3" compact />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Repo } from '~/types'

useSeoMeta({ title: 'Explore' })

const pageSize = 40
const route = useRoute()
const router = useRouter()
const { get } = useApi()
const allowedSorts = new Set(['downloads', 'clones', 'recent'])

function parsePage(value: unknown) {
  const parsed = Number.parseInt(String(value || '1'), 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1
}

const sort = ref(allowedSorts.has(String(route.query.sort || 'downloads')) ? String(route.query.sort || 'downloads') : 'downloads')
const page = ref(parsePage(route.query.page))

const { data: repos, pending } = await useAsyncData(
  () => `explore:${sort.value}:${page.value}`,
  () => get<Repo[]>(`/api/repos/?page=${page.value}&limit=${pageSize}&sort=${sort.value}`),
  { server: false, default: () => [], watch: [sort, page] },
)

const canGoNext = computed(() => repos.value.length === pageSize)
const visiblePages = computed(() => {
  const pages = new Set<number>([page.value])
  if (page.value > 1) pages.add(page.value - 1)
  if (page.value > 2) pages.add(1)
  if (canGoNext.value) pages.add(page.value + 1)
  return [...pages].sort((a, b) => a - b)
})

async function syncRoute() {
  const query: Record<string, string> = {}
  if (sort.value !== 'downloads') query.sort = sort.value
  if (page.value > 1) query.page = String(page.value)
  await router.replace({ query })
}

async function goToPage(nextPage: number) {
  if (nextPage < 1 || nextPage === page.value) return
  page.value = nextPage
  await syncRoute()
  if (import.meta.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(sort, async (newSort, oldSort) => {
  if (newSort === oldSort) return
  page.value = 1
  await syncRoute()
})

watch(
  () => route.query,
  (query) => {
    const nextSort = allowedSorts.has(String(query.sort || 'downloads')) ? String(query.sort || 'downloads') : 'downloads'
    const nextPage = parsePage(query.page)
    if (nextSort !== sort.value) sort.value = nextSort
    if (nextPage !== page.value) page.value = nextPage
  },
)
</script>
