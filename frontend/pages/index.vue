<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">게시판</h1>
    
    <div v-if="pending" class="text-center py-8">
      로딩중...
    </div>
    
    <div v-else-if="error" class="text-center py-8 text-red-600">
      오류가 발생했습니다.
    </div>
    
    <div v-else class="space-y-3">
      <NuxtLink 
        v-for="board in boards" 
        :key="board.id"
        :to="`/board/${board.board_type}`"
        class="block bg-white border border-gray-300 rounded p-4 hover:bg-gray-50 transition-colors no-underline"
      >
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-lg font-bold text-gray-900 mb-1">{{ board.name }}</h2>
            <p class="text-sm text-gray-600">{{ board.description }}</p>
          </div>
          <div class="text-sm text-gray-500">
            {{ board.post_count }}개의 글
          </div>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()

const { data: boards, pending, error } = await useAsyncData(
  'boards',
  () => api.getBoards()
)
</script>
