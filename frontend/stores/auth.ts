import { defineStore } from 'pinia'
import type { User } from '~/types'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    token: null as string | null,
    hydrated: false,
  }),
  actions: {
    clearLocalSession() {
      this.user = null
      this.token = null
      useCookie<string | null>('token').value = null
      if (process.client) localStorage.removeItem('token')
    },
    hydrateToken() {
      const tokenCookie = useCookie<string | null>('token')
      const token = tokenCookie.value || (process.client ? localStorage.getItem('token') : null)
      this.token = token || null
      if (token) {
        tokenCookie.value = token
        if (process.client) localStorage.setItem('token', token)
      }
      this.hydrated = true
    },
    async login(token: string) {
      this.token = token
      useCookie<string | null>('token').value = token
      if (process.client) localStorage.setItem('token', token)
      await this.fetchUser()
    },
    async logout() {
      try {
        const config = useRuntimeConfig()
        await fetch(`${config.public.apiBase}/api/auth/logout`, {
          method: 'POST',
          credentials: 'include',
        })
      } catch {
        // Ignore network errors during best-effort logout.
      }
      this.clearLocalSession()
      navigateTo('/login')
    },
    async refreshToken() {
      try {
        const config = useRuntimeConfig()
        const res = await fetch(`${config.public.apiBase}/api/auth/refresh`, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
        })
        if (!res.ok) {
          if (res.status === 401 || res.status === 403) this.clearLocalSession()
          return null
        }

        const data = await res.json() as { access_token: string }
        this.token = data.access_token
        useCookie<string | null>('token').value = data.access_token
        if (process.client) localStorage.setItem('token', data.access_token)
        return data.access_token
      } catch {
        return null
      }
    },
    async fetchUser() {
      try {
        const config = useRuntimeConfig()
        let token = this.token || useCookie<string | null>('token').value || (process.client ? localStorage.getItem('token') : null)

        if (!token) {
          token = await this.refreshToken()
          if (!token) return
        }

        let res = await fetch(`${config.public.apiBase}/api/users/me`, {
          headers: { Authorization: `Bearer ${token}` },
          credentials: 'include',
        })

        if (res.status === 401 || res.status === 403) {
          const refreshedToken = await this.refreshToken()
          if (!refreshedToken) return
          token = refreshedToken
          res = await fetch(`${config.public.apiBase}/api/users/me`, {
            headers: { Authorization: `Bearer ${refreshedToken}` },
            credentials: 'include',
          })
        }

        if (res.ok) {
          this.user = await res.json()
          this.token = token
          useCookie<string | null>('token').value = token
        } else if (res.status === 401 || res.status === 403) {
          this.clearLocalSession()
        }
      } catch {
        // Keep existing session on transient network issues.
      }
    },
  },
})
