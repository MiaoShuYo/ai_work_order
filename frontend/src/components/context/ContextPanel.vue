<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTaskContext } from '../../composables/useTaskContext'
import OrderInfoCard from '../business/OrderInfoCard.vue'
import TicketInfoCard from '../business/TicketInfoCard.vue'
import UserInfoCard from '../business/UserInfoCard.vue'
import ToolResultDetail from '../tools/ToolResultDetail.vue'

const { state } = useTaskContext()
const selectedId = ref<number | null>(null)

const selectedRecord = computed(() => state.history.find((record) => record.id === selectedId.value) ?? null)

function selectRecord(id: number) {
  // 再点一次同一条记录时收起详情，避免用户想关掉详情时无从下手
  selectedId.value = selectedId.value === id ? null : id
}
</script>

<template>
  <aside class="context-panel">
    <section class="context-section">
      <h3>当前用户</h3>
      <UserInfoCard v-if="state.user" :data="state.user" />
      <p v-else class="context-empty">暂无用户信息</p>
    </section>
    <section class="context-section">
      <h3>当前订单</h3>
      <OrderInfoCard v-if="state.order" :data="state.order" />
      <p v-else class="context-empty">暂无订单信息</p>
    </section>
    <section class="context-section">
      <h3>当前工单</h3>
      <TicketInfoCard v-if="state.ticket" :data="state.ticket" />
      <p v-else class="context-empty">暂无工单信息</p>
    </section>
    <section class="context-section">
      <h3>工具调用记录</h3>
      <p v-if="!state.history.length" class="context-empty">本轮对话还没有调用过工具</p>
      <ul class="history-list">
        <li
          v-for="record in state.history"
          :key="record.id"
          class="history-item"
          :class="{ active: record.id === selectedId }"
          @click="selectRecord(record.id)"
        >
          {{ record.name }}
        </li>
      </ul>
      <ToolResultDetail
        v-if="selectedRecord"
        class="history-detail"
        :name="selectedRecord.name"
        :result="selectedRecord.result"
      />
    </section>
  </aside>
</template>

<style scoped>
.context-panel {
  width: 280px;
  border-left: 1px solid #e5e7eb;
  padding: 16px;
  overflow-y: auto;
}

.context-section {
  margin-bottom: 20px;
}

.context-section h3 {
  margin: 0 0 8px;
  font-size: 13px;
  color: #6b7280;
}

.context-empty {
  margin: 0;
  font-size: 13px;
  color: #9ca3af;
}

.history-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.history-item {
  padding: 6px 8px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  color: #374151;
}

.history-item:hover {
  background-color: #f3f4f6;
}

.history-item.active {
  background-color: #eff6ff;
  color: #2563eb;
}

.history-detail {
  margin-top: 8px;
}
</style>