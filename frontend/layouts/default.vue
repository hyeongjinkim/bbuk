<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 헤더 -->
    <header class="bg-white border-b border-gray-300 sticky top-0 z-50">
      <div class="container-custom py-3">
        <NuxtLink to="/" class="text-xl font-bold text-gray-900 no-underline">
          비백억
        </NuxtLink>
      </div>
    </header>

    <!-- 메인 컨텐츠 -->
    <main class="container-custom py-4">
      <slot />
    </main>

    <!-- 푸터 -->
    <footer class="bg-white border-t border-gray-300 mt-8">
      <div class="container-custom py-4 text-center text-sm text-gray-500">
        © 2024 비백억. All rights reserved.
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '~/stores/user'

const userStore = useUserStore()

onMounted(() => {
  userStore.loadAuthorName()
})
</script>
