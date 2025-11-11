import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    // 쿠키에 저장된 작성자 정보 (편의성)
    savedAuthorName: '',
  }),
  
  actions: {
    loadAuthorName() {
      if (process.client) {
        this.savedAuthorName = localStorage.getItem('authorName') || ''
      }
    },
    
    saveAuthorName(name: string) {
      this.savedAuthorName = name
      if (process.client) {
        localStorage.setItem('authorName', name)
      }
    },
    
    clearAuthorName() {
      this.savedAuthorName = ''
      if (process.client) {
        localStorage.removeItem('authorName')
      }
    }
  }
})
