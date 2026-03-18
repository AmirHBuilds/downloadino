<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex flex-col gap-6 mb-8 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-xs font-mono uppercase tracking-[0.3em] text-accent-2/80 mb-2">Discover</p>
        <h1 class="text-3xl font-bold tracking-tight">Explore repositories</h1>
        <p class="mt-2 max-w-2xl text-sm text-muted">
          Browse public mirrors with fast paging, clearer sorting, and quick jumps to the exact page you want.
        </p>
      </div>

      <div class="grid w-full gap-3 rounded-2xl border border-border bg-surface/70 p-4 shadow-sm backdrop-blur sm:grid-cols-[minmax(0,1fr)_auto] lg:w-auto lg:min-w-[26rem]">
        <label class="flex flex-col gap-1 text-xs font-medium uppercase tracking-wide text-muted">
          Sort by
          <select v-model="sort" class="input py-2 text-sm">
            <option value="downloads">Most downloaded</option>
            <option value="clones">Most cloned</option>
            <option value="recent">Recently updated</option>
          </select>
        </label>
        <div class="rounded-xl border border-accent-2/20 bg-accent-2/5 px-4 py-3 text-sm">
          <p class="text-xs font-medium uppercase tracking-wide text-muted">Showing</p>
          <p class="mt-1 font-mono text-foreground">
            {{ pageRangeLabel }}
          </p>
        </div>
      </div>
    </div>

    <div v-if="pending" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div v-for="i in pageSize" :key="i" class="card h-40 animate-pulse"></div>
    </div>

    <template v-else>
      <div v-if="repos.length === 0" class="rounded-2xl border border-dashed border-border bg-surface/40 px-6 py-20 text-center text-muted">
        <Icon name="mdilocal:source-repository-multiple" class="mx-auto mb-3 h-12 w-12 opacity-30" />
        <p class="text-base font-medium text-foreground">No repositories found</p>
        <p class="mt-1 text-sm text-muted">Try another sort option or come back after new mirrors are published.</p>
      </div>

      <template v-else>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <RepoCard v-for="repo in repos" :key="repo.id" :repo="repo" />
        </div>

        <div class="mt-8 rounded-2xl border border-border bg-surface/70 p-4 shadow-sm backdrop-blur">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p class="text-sm font-semibold">Pagination</p>
              <p class="mt-1 text-sm text-muted">
                Page {{ currentPage }} of {{ totalPages }} · {{ totalCount.toLocaleString() }} repositories total
              </p>
            </div>

            <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
              <div class="inline-flex items-center gap-2 rounded-xl border border-border bg-surface-2/80 p-1">
                <button
                  class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition hover:bg-surface disabled:cursor-not-allowed disabled:opacity-50"
                  :disabled="currentPage <= 1 || pending"
                  @click="goToPage(currentPage - 1)"
                >
                  <Icon name="mdilocal:arrow-left" class="h-4 w-4" />
                  Previous
                </button>
                <div class="hidden h-8 w-px bg-border sm:block"></div>
                <button
                  class="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition hover:bg-surface disabled:cursor-not-allowed disabled:opacity-50"
                  :disabled="currentPage >= totalPages || pending"
                  @click="goToPage(currentPage + 1)"
                >
                  Next
                  <Icon name="mdilocal:arrow-left" class="h-4 w-4 rotate-180" />
                </button>
              </div>

              <form class="flex items-center gap-2 rounded-xl border border-border bg-surface-2/50 px-3 py-2" @submit.prevent="submitPageJump">
                <label for="explore-page" class="text-xs font-medium uppercase tracking-wide text-muted">Go to page</label>
                <input
                  id="explore-page"
                  v-model="pageInput"
                  inputmode="numeric"
                  pattern="[0-9]*"
                  class="w-20 rounded-lg border border-border bg-surface px-3 py-1.5 text-sm font-mono focus:border-accent focus:outline-none"
                  :placeholder="String(currentPage)"
                />
                <button class="btn-primary py-1.5 text-sm" :disabled="pending">Go</button>
              </form>
            </div>
          </div>
        </div>
      </template>
    </template>

    <AdSlot position="explore_inline" :limit="3" compact wrapper-class="mt-8" />
  </div>
</template>

<script setup lang="ts">
import type { Repo } from '~/types'

useSeoMeta({ title: 'Explore' })

const route = useRoute()
const router = useRouter()
const apiBase = useRuntimeConfig().public.apiBase
const pageSize = 12
const allowedSorts = new Set(['downloads', 'clones', 'recent'])

function normalizePage(value: unknown) {
  const parsed = Number.parseInt(Array.isArray(value) ? value[0] || '' : String(value || ''), 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1
}

const sort = ref(allowedSorts.has(String(route.query.sort || 'downloads')) ? String(route.query.sort || 'downloads') : 'downloads')
const currentPage = ref(normalizePage(route.query.page))
const pageInput = ref(String(currentPage.value))

const { data, pending, refresh } = await useAsyncData(
  () => `explore:${sort.value}:${currentPage.value}` ,
  async () => {
    const url = new URL(`${apiBase}/api/repos/`)
    url.searchParams.set('sort', sort.value)
    url.searchParams.set('page', String(currentPage.value))
    url.searchParams.set('limit', String(pageSize))

    const response = await fetch(url.toString())
    if (!response.ok) throw new Error('Failed to load repositories')

    const items = await response.json() as Repo[]
    const totalCount = Number.parseInt(response.headers.get('x-total-count') || '0', 10) || 0
    return { items, totalCount }
  },
  { server: false, default: () => ({ items: [], totalCount: 0 }) },
)

const repos = computed(() => data.value.items)
const totalCount = computed(() => data.value.totalCount)
const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize)))
const pageRangeLabel = computed(() => {
  if (!totalCount.value || repos.value.length === 0) return '0 repositories'
  const start = (currentPage.value - 1) * pageSize + 1
  const end = start + repos.value.length - 1
  return `${start}-${end} of ${totalCount.value.toLocaleString()} repos`
})

async function updateRoute() {
  const query: Record<string, string> = {}
  if (sort.value !== 'downloads') query.sort = sort.value
  if (currentPage.value > 1) query.page = String(currentPage.value)
  await router.replace({ query })
}

async function goToPage(page: number) {
  const nextPage = Math.min(Math.max(1, page), totalPages.value)
  if (nextPage === currentPage.value) return
  currentPage.value = nextPage
  pageInput.value = String(nextPage)
  await updateRoute()
  await refresh()
  if (process.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function submitPageJump() {
  const parsed = Number.parseInt(pageInput.value, 10)
  await goToPage(Number.isFinite(parsed) ? parsed : currentPage.value)
}

watch(sort, async () => {
  currentPage.value = 1
  pageInput.value = '1'
  await updateRoute()
  await refresh()
})

watch(
  () => route.query,
  async (query) => {
    const nextSort = allowedSorts.has(String(query.sort || 'downloads')) ? String(query.sort || 'downloads') : 'downloads'
    const nextPage = normalizePage(query.page)
    const changed = nextSort !== sort.value || nextPage !== currentPage.value
    sort.value = nextSort
    currentPage.value = nextPage
    pageInput.value = String(nextPage)
    if (changed) await refresh()
  },
)

watch(totalPages, async (value) => {
  if (currentPage.value > value) await goToPage(value)
})
</script>
