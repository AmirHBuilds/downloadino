<template>
  <section class="relative overflow-hidden">
    <div class="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.18),_transparent_38%),radial-gradient(circle_at_bottom_right,_rgba(139,92,246,0.16),_transparent_34%)]"></div>
    <div class="relative max-w-6xl mx-auto px-4 py-12 sm:py-16">
      <div class="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] items-start">
        <div class="space-y-6">
          <div class="inline-flex items-center gap-2 rounded-full border border-accent-2/30 bg-accent-2/10 px-3 py-1 text-xs font-mono uppercase tracking-[0.24em] text-accent-2">
            <span class="h-2 w-2 rounded-full bg-accent-2 shadow-[0_0_12px_rgba(34,211,238,0.9)]"></span>
            Donation
          </div>

          <div>
            <h1 class="max-w-3xl text-4xl font-semibold tracking-tight text-fg sm:text-5xl">
              Help keep the mirror fast, independent, and always available.
            </h1>
            <p class="mt-4 max-w-2xl text-base leading-7 text-muted sm:text-lg">
              {{ donationMessage }}
            </p>
          </div>

          <div class="grid gap-4 sm:grid-cols-3">
            <div
              v-for="stat in supportStats"
              :key="stat.label"
              class="rounded-2xl border border-white/8 bg-white/5 p-4 shadow-[0_18px_60px_rgba(15,23,42,0.18)] backdrop-blur"
            >
              <p class="text-2xl font-semibold text-fg">{{ stat.value }}</p>
              <p class="mt-1 text-sm text-muted">{{ stat.label }}</p>
            </div>
          </div>

          <div class="rounded-3xl border border-accent/20 bg-gradient-to-br from-accent/12 via-surface-1 to-surface-1 p-6 shadow-[0_24px_80px_rgba(15,23,42,0.28)]">
            <div class="flex flex-wrap items-center gap-3 text-sm text-muted">
              <span class="rounded-full border border-success/25 bg-success/10 px-3 py-1 text-success">Community funded</span>
              <span class="rounded-full border border-border bg-surface/70 px-3 py-1">Independent infrastructure</span>
              <span class="rounded-full border border-border bg-surface/70 px-3 py-1">No third-party payment widgets</span>
            </div>
            <p class="mt-4 text-sm leading-7 text-muted sm:text-base">
              Every contribution helps us cover uptime, storage, bandwidth, and development work. Pick the method that is easiest for you and use the details below exactly as shown.
            </p>
          </div>
        </div>

        <div class="card relative overflow-hidden border-white/10 bg-surface-1/85 p-6 shadow-[0_30px_90px_rgba(2,6,23,0.5)] backdrop-blur-xl sm:p-7">
          <div class="absolute inset-x-6 top-0 h-px bg-gradient-to-r from-transparent via-accent-2/70 to-transparent"></div>

          <div class="flex items-center justify-between gap-4 border-b border-border/80 pb-5">
            <div>
              <p class="text-sm font-medium text-fg">Donation details</p>
              <p class="mt-1 text-sm text-muted">Choose your preferred method and copy the information safely.</p>
            </div>
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl border border-accent-2/20 bg-accent-2/10 text-accent-2">
              <Icon name="mdilocal:shield-check-outline" class="h-6 w-6" />
            </div>
          </div>

          <div class="mt-6 space-y-4">
            <article
              v-for="method in donationMethods"
              :key="method.title"
              class="group rounded-3xl border border-white/7 bg-gradient-to-br from-white/[0.06] to-white/[0.02] p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-accent-2/35 hover:shadow-[0_16px_50px_rgba(34,211,238,0.08)] sm:p-5"
            >
              <div class="flex items-start gap-4">
                <div class="flex h-14 w-14 items-center justify-center rounded-2xl border border-white/10 bg-surface-2 p-3 shadow-inner">
                  <Icon :name="method.icon" class="h-full w-full" />
                </div>

                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-3">
                    <h2 class="text-lg font-semibold text-fg">{{ method.title }}</h2>
                    <span class="rounded-full border border-border bg-surface/80 px-2.5 py-1 text-[11px] font-mono uppercase tracking-[0.22em] text-muted">
                      {{ method.tag }}
                    </span>
                  </div>
                  <p class="mt-2 text-sm leading-6 text-muted">{{ method.description }}</p>
                </div>
              </div>

              <div class="mt-4 rounded-2xl border border-accent-2/15 bg-slate-950/40 p-4">
                <p class="text-[11px] font-mono uppercase tracking-[0.28em] text-accent-2/80">{{ method.label }}</p>
                <p class="mt-2 break-all font-mono text-sm leading-6 text-fg sm:text-[15px]">
                  {{ method.value }}
                </p>
              </div>
            </article>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
const config = useRuntimeConfig()

const donationMessage = computed(
  () => config.public.donationMessage || 'If Mirrorino helps your workflow, your donation helps keep the platform stable, modern, and accessible for everyone.',
)

const donationMethods = computed(() => [
  {
    title: 'Bitcoin',
    tag: 'BTC',
    label: 'Wallet address',
    value: config.public.donationBitcoin || 'Not configured yet',
    description: 'Ideal for direct international support with native Bitcoin transfers.',
    icon: 'donation:bitcoin',
  },
  {
    title: 'USDT (BEP20)',
    tag: 'BSC',
    label: 'Wallet address',
    value: config.public.donationUsdtBep20 || 'Not configured yet',
    description: 'Use the Binance Smart Chain network when sending USDT to this address.',
    icon: 'donation:usdt-bep20',
  },
  {
    title: 'Card number',
    tag: 'CARD',
    label: 'Card number',
    value: config.public.donationCardNumber || 'Not configured yet',
    description: 'For supporters who prefer a direct card transfer instead of crypto.',
    icon: 'donation:card',
  },
])

const supportStats = [
  { value: '24/7', label: 'availability worth protecting' },
  { value: '3', label: 'simple ways to contribute' },
  { value: '100%', label: 'community-backed energy' },
]

useSeoMeta({
  title: 'Donation',
  description: 'Donate to Mirrorino with Bitcoin, USDT (BEP20), or card transfer details.',
})
</script>
