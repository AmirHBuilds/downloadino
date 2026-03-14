<template>
  <div>
    <div class="flex flex-col gap-4 mb-6 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-xl font-bold">Platform Statistics</h1>
        <p class="text-sm text-muted mt-1">Live platform metrics, visitor activity, and growth trends.</p>
      </div>
      <div class="flex items-center gap-2">
        <select v-model="period" class="input text-sm w-40">
          <option value="today">Today</option>
          <option value="7d">This Week</option>
          <option value="30d">Last 30 Days</option>
          <option value="90d">Last 90 Days</option>
        </select>
        <button class="btn-ghost text-xs" @click="refresh">Refresh</button>
      </div>
    </div>

    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-for="item in totalCards" :key="item.label" class="card p-4 bg-gradient-to-br from-surface to-surface-2">
        <p class="text-xs text-muted mb-1">{{ item.label }}</p>
        <p class="text-2xl font-mono font-bold">{{ item.value }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
      <div class="card p-4" v-for="growth in growthCards" :key="growth.label">
        <p class="text-xs text-muted">{{ growth.label }}</p>
        <p class="text-2xl font-mono font-bold mt-1" :class="growth.value >= 0 ? 'text-success' : 'text-danger'">{{ growth.value >= 0 ? '+' : '' }}{{ growth.value }}%</p>
        <p class="text-xs text-muted mt-1">Last 7 days: {{ growth.current }}</p>
      </div>
    </div>

    <div class="card p-4">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold">Activity Timeline ({{ periodLabel }})</h2>
        <span class="text-xs text-muted">Visitors + signups + repository activity</span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-border text-xs text-muted font-mono">
            <tr>
              <th class="text-left py-2">Day</th>
              <th class="text-left py-2">Visitors</th>
              <th class="text-left py-2">Unique Visitors</th>
              <th class="text-left py-2">New Users</th>
              <th class="text-left py-2">New Repositories</th>
              <th class="text-left py-2">New Files</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            <tr v-for="point in analytics?.timeline || []" :key="point.day">
              <td class="py-2 font-mono text-xs">{{ point.day }}</td>
              <td class="py-2">{{ point.visits }}</td>
              <td class="py-2">{{ point.unique_visitors }}</td>
              <td class="py-2">{{ point.users }}</td>
              <td class="py-2">{{ point.repos }}</td>
              <td class="py-2">{{ point.files }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AdminAnalytics } from '~/types'
import { formatBytes } from '~/utils/format'

definePageMeta({ layout: 'admin', middleware: 'admin' })
useSeoMeta({ title: 'Admin · Statistics' })

const { get } = useApi()
const period = ref<'today' | '7d' | '30d' | '90d'>('30d')

const { data: analytics, refresh } = await useAsyncData(
  'admin-analytics',
  () => get<AdminAnalytics>(`/api/admin/analytics?period=${period.value}`),
  {
    server: false,
    default: () => null,
    watch: [period],
  },
)

const periodLabel = computed(() => {
  if (period.value === 'today') return 'Today'
  if (period.value === '7d') return 'This Week'
  if (period.value === '90d') return 'Last 90 Days'
  return 'Last 30 Days'
})

const totalCards = computed(() => [
  { label: 'Total Users', value: analytics.value?.totals.users || 0 },
  { label: 'Total Repos', value: analytics.value?.totals.repos || 0 },
  { label: 'Total Files', value: analytics.value?.totals.files || 0 },
  { label: 'Storage', value: formatBytes(analytics.value?.totals.storage_bytes || 0) },
  { label: 'Downloads', value: analytics.value?.totals.downloads || 0 },
  { label: 'Total Visits', value: analytics.value?.totals.visits || 0 },
  { label: 'Unique Visitors', value: analytics.value?.totals.unique_visitors || 0 },
  { label: `${periodLabel.value} Visits`, value: analytics.value?.growth.visits_current_period || 0 },
])

const growthCards = computed(() => [
  { label: 'User Growth (7d)', value: analytics.value?.growth.users_7d || 0, current: analytics.value?.growth.users_current_7d || 0 },
  { label: 'Repo Growth (7d)', value: analytics.value?.growth.repos_7d || 0, current: analytics.value?.growth.repos_current_7d || 0 },
  { label: 'File Growth (7d)', value: analytics.value?.growth.files_7d || 0, current: analytics.value?.growth.files_current_7d || 0 },
])
</script>
