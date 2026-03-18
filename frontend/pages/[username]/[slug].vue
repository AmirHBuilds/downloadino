<template>
  <RepoDetailView />
</template>

<script setup lang="ts">
const route = useRoute()

function normalizeRoutePath(value: unknown) {
  const raw = Array.isArray(value) ? value.join('/') : value
  if (typeof raw !== 'string') return ''
  return raw
    .replace(/\\/g, '/')
    .split('/')
    .map((part) => part.trim())
    .filter((part) => part && part !== '.' && part !== '..')
    .join('/')
}

const legacyPath = normalizeRoutePath(route.query.path)

if (legacyPath) {
  const cleanedQuery = Object.fromEntries(Object.entries(route.query).filter(([key]) => key !== 'path'))
  await navigateTo({
    path: `/${encodeURIComponent(String(route.params.username || ''))}/${encodeURIComponent(String(route.params.slug || ''))}/${legacyPath.split('/').map((segment) => encodeURIComponent(segment)).join('/')}`,
    query: cleanedQuery,
    replace: true,
  })
}
</script>
