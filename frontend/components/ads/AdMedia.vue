<template>
  <video
    v-if="isVideo"
    :src="resolvedSrc"
    class="w-full h-full object-cover"
    autoplay
    loop
    muted
    playsinline
  />
  <img v-else :src="resolvedSrc" :alt="alt" class="w-full h-full object-cover" loading="lazy" />
</template>

<script setup lang="ts">
const props = defineProps<{ src: string; alt: string }>()

const apiBase = useRuntimeConfig().public.apiBase.replace(/\/$/, '')

const resolvedSrc = computed(() => {
  const src = props.src.trim()
  if (!src) return src

  if (/^(?:[a-z][a-z\d+.-]*:|\/\/|blob:|data:)/i.test(src)) return src
  if (!src.startsWith('/')) return src

  return `${apiBase}${src}`
})

const isVideo = computed(() => /\.(mp4|webm|ogg)(\?.*)?$/i.test(resolvedSrc.value))
</script>
