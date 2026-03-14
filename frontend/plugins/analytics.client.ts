export default defineNuxtPlugin((nuxtApp) => {
  const config = useRuntimeConfig()
  const endpoint = `${config.public.apiBase}/api/analytics/visit`

  const track = (path: string) => {
    fetch(endpoint, {
      method: 'POST',
      headers: {
        'X-Page-Path': path,
      },
      keepalive: true,
    }).catch(() => undefined)
  }

  nuxtApp.hook('page:finish', () => {
    if (process.client) {
      track(window.location.pathname + window.location.search)
    }
  })
})
