<template>
  <div class="data-flow-animation">
    <!-- 数据流动画点 -->
    <div
      v-for="flow in activeFlows"
      :key="flow.id"
      class="flow-dot"
      :style="getFlowStyle(flow)"
    >
      <div class="flow-pulse" />
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'

const props = defineProps({
  flows: {
    type: Array,
    default: () => []
  },
  edges: {
    type: Array,
    default: () => []
  }
})

const activeFlows = ref([])
let animationFrame = null

// 获取流动点的样式
const getFlowStyle = (flow) => {
  const edge = props.edges.find(e => 
    e.source === flow.fromNodeId && e.target === flow.toNodeId
  )
  
  if (!edge) return {}
  
  // 计算流动点的位置
  const progress = flow.progress / 100
  
  return {
    left: `${edge.sourceX + (edge.targetX - edge.sourceX) * progress}px`,
    top: `${edge.sourceY + (edge.targetY - edge.sourceY) * progress}px`,
    transform: 'translate(-50%, -50%)'
  }
}

// 更新动画
const updateAnimation = () => {
  activeFlows.value = activeFlows.value.map(flow => ({
    ...flow,
    progress: Math.min(flow.progress + 2, 100)
  })).filter(flow => flow.progress < 100)
  
  if (activeFlows.value.length > 0) {
    animationFrame = requestAnimationFrame(updateAnimation)
  }
}

// 开始数据流动画
const startFlow = (fromNodeId, toNodeId, data) => {
  const flowId = `${fromNodeId}-${toNodeId}-${Date.now()}`
  
  activeFlows.value.push({
    id: flowId,
    fromNodeId,
    toNodeId,
    progress: 0,
    data
  })
  
  if (!animationFrame) {
    updateAnimation()
  }
}

// 停止所有动画
const stopAllFlows = () => {
  activeFlows.value = []
  if (animationFrame) {
    cancelAnimationFrame(animationFrame)
    animationFrame = null
  }
}

onUnmounted(() => {
  stopAllFlows()
})

// 暴露方法给父组件
defineExpose({
  startFlow,
  stopAllFlows
})
</script>

<style scoped>
.data-flow-animation {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
}

.flow-dot {
  position: absolute;
  width: 8px;
  height: 8px;
  background: #409eff;
  border-radius: 50%;
  box-shadow: 0 0 8px rgba(64, 158, 255, 0.6);
  animation: pulse 1s infinite;
}

.flow-pulse {
  position: absolute;
  top: -4px;
  left: -4px;
  width: 16px;
  height: 16px;
  border: 2px solid #409eff;
  border-radius: 50%;
  opacity: 0.6;
  animation: pulse-ring 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.2);
  }
}

@keyframes pulse-ring {
  0% {
    transform: scale(0.8);
    opacity: 0.8;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}
</style>