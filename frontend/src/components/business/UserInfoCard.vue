<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  data: Record<string, unknown>
}>()

const LEVEL_COLOR: Record<string, string> = {
  普通: '#6b7280',
  VIP: '#2563eb',
  SVIP: '#b45309',
}

const userId = computed(() => String(props.data.user_id ?? ''))
const name = computed(() => String(props.data.name ?? ''))
const level = computed(() => String(props.data.level ?? ''))
const phone = computed(() => String(props.data.phone ?? ''))
const hasError = computed(() => typeof props.data.error === 'string')
</script>

<template>
  <div v-if="hasError" class="user-card user-card-error">{{ data.error }}</div>
  <div v-else class="user-card">
    <div class="user-row">
      <span class="user-label">用户 ID</span>
      <span>{{ userId }}</span>
    </div>
    <div class="user-row">
      <span class="user-label">姓名</span>
      <span>{{ name }}</span>
    </div>
    <div class="user-row">
      <span class="user-label">等级</span>
      <span :style="{ color: LEVEL_COLOR[level] ?? '#374151' }">{{ level }}</span>
    </div>
    <div class="user-row">
      <span class="user-label">手机号</span>
      <span>{{ phone }}</span>
    </div>
  </div>
</template>

<style scoped>
.user-card {
  margin-top: 4px;
  padding: 8px 10px;
  border-radius: 6px;
  background-color: #fff;
  border: 1px solid #e5e7eb;
}

.user-card-error {
  color: #dc2626;
}

.user-row {
  display: flex;
  justify-content: space-between;
  padding: 2px 0;
  font-size: 13px;
}

.user-label {
  color: #6b7280;
}
</style>