<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 mb-8">
      <div>
        <p class="text-xs font-mono uppercase tracking-[0.3em] text-accent-2/80 mb-2">Explore</p>
        <h1 class="text-2xl sm:text-3xl font-bold">Discover repositories</h1>
        <p class="text-sm text-muted mt-2 max-w-2xl">
          Browse community mirrors and projects sorted the way you want.
        </p>
      </div>

      <label class="w-full lg:w-auto">
        <span class="block text-[11px] font-mono uppercase tracking-[0.25em] text-muted mb-2">Sort by</span>
        <select v-model="sort" class="input py-2 text-sm sm:w-52">
          <option value="downloads">Most downloaded</option>
          <option value="clones">Most cloned</option>
          <option value="recent">Recently updated</option>
        </select>
      </label>
    </div>

    <div v-if="pending" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="i in 9" :key="i" class="card p-4 animate-pulse h-32"></div>
    </div>
    <div v-else-if="repos.length === 0" class="card text-center py-20 text-muted">
      <Icon name="mdilocal:source-repository-multiple" class="w-12 h-12 mx-auto mb-3 opacity-30" />
      <p class="text-sm">No repositories found for this page.</p>
      <button v-if="page > 1" class="btn-ghost mt-4" @click="goToPage(page - 1)">Go back one page</button>
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <RepoCard v-for="repo in repos" :key="repo.id" :repo="repo" />
    </div>

    <div class="mt-10 space-y-8">
      <div class="card p-4 sm:p-5">
        <div class="flex justify-center">
          <div class="inline-flex max-w-full items-center gap-1.5 overflow-x-auto rounded-2xl border border-border bg-surface px-1.5 py-1.5 shadow-sm">
            <button
              class="inline-flex h-10 items-center gap-2 rounded-xl px-3 text-sm font-medium text-muted transition-colors hover:bg-surface-2 hover:text-fg disabled:opacity-50 disabled:hover:bg-transparent disabled:hover:text-muted"
              :disabled="page === 1 || pending"
              @click="goToPage(page - 1)"
            >
              <Icon name="mdilocal:arrow-left" class="w-4 h-4" />
              Previous
            </button>
            <template v-for="item in paginationItems" :key="item.key">
              <span
                v-if="item.type === 'ellipsis'"
                class="inline-flex h-10 min-w-10 items-center justify-center px-2 text-sm text-muted"
              >
                …
              </span>
              <button
                v-else
                class="min-w-10 h-10 rounded-xl px-3 text-sm font-medium transition-all"
                :class="item.value === page ? 'bg-accent text-white shadow-sm' : 'text-muted hover:bg-surface-2 hover:text-fg'"
                :disabled="pending"
                @click="goToPage(item.value)"
              >
                {{ item.value }}
              </button>
            </template>
            <button
              class="inline-flex h-10 items-center gap-2 rounded-xl bg-accent px-3 text-sm font-medium text-white transition-colors hover:bg-accent/90 disabled:opacity-50"
              :disabled="!canGoNext || pending"
              @click="goToPage(page + 1)"
            >
              Next
              <Icon name="mdilocal:arrow-left" class="w-4 h-4 rotate-180" />
            </button>
          </div>
        </div>
      </div>

      <AdSlot position="explore_inline" :limit="3" compact />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Repo } from '~/types'

useSeoMeta({ title: 'Explore' })

const pageSize = 30
const route = useRoute()
const router = useRouter()
const { get } = useApi()
const allowedSorts = new Set(['downloads', 'clones', 'recent'])

type PaginationItem =
  | { type: 'page'; key: string; value: number }
  | { type: 'ellipsis'; key: string }

type ExploreData = {
  repos: Repo[]
  totalCount: number
}

function parsePage(value: unknown) {
  const parsed = Number.parseInt(String(value || '1'), 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1
}

const sort = ref(allowedSorts.has(String(route.query.sort || 'downloads')) ? String(route.query.sort || 'downloads') : 'downloads')
const page = ref(parsePage(route.query.page))

const { data: exploreData, pending } = await useAsyncData(
  () => `explore:${sort.value}:${page.value}`,
  async (): Promise<ExploreData> => {
    const [repos, count] = await Promise.all([
      get<Repo[]>(`/api/repos/?page=${page.value}&limit=${pageSize}&sort=${sort.value}`),
      get<{ total: number }>('/api/repos/count'),
    ])
    return { repos, totalCount: count.total }
  },
  { server: false, default: () => ({ repos: [], totalCount: 0 }), watch: [sort, page] },
)

const repos = computed(() => exploreData.value.repos)
const totalPages = computed(() => Math.max(1, Math.ceil(exploreData.value.totalCount / pageSize)))
const canGoNext = computed(() => page.value < totalPages.value)
const paginationItems = computed<PaginationItem[]>(() => {
  const items: PaginationItem[] = []
  const current = page.value
  const total = totalPages.value

  const addPage = (value: number) => {
    items.push({ type: 'page', key: `page-${value}`, value })
  }

  const addEllipsis = (key: string) => {
    items.push({ type: 'ellipsis', key })
  }

  if (total <= 7) {
    for (let value = 1; value <= total; value += 1) addPage(value)
    return items
  }

  if (current <= 3) {
    addPage(1)
    addPage(2)
    addPage(3)
    addEllipsis('right')
    addPage(total)
    return items
  }

  if (current >= total - 2) {
    addPage(1)
    addEllipsis('left')
    addPage(total - 2)
    addPage(total - 1)
    addPage(total)
    return items
  }

  addPage(1)
  addEllipsis('left')
  addPage(current - 1)
  addPage(current)
  addPage(current + 1)
  addEllipsis('right')
  addPage(total)
  return items
})

async function syncRoute() {
  const query: Record<string, string> = {}
  if (sort.value !== 'downloads') query.sort = sort.value
  if (page.value > 1) query.page = String(page.value)
  await router.replace({ query })
}

async function goToPage(nextPage: number) {
  if (nextPage < 1 || nextPage > totalPages.value || nextPage === page.value) return
  page.value = nextPage
  await syncRoute()
  if (import.meta.client) window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(sort, async (newSort, oldSort) => {
  if (newSort === oldSort) return
  page.value = 1
  await syncRoute()
})

watch(totalPages, async (nextTotalPages) => {
  if (page.value <= nextTotalPages) return
  page.value = nextTotalPages
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
