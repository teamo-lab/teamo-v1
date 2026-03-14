<template>
  <div class="mode-selector">
    <div
      class="mode-card"
      :class="{ active: currentMode === 'claude_code' }"
      @click="switchMode('claude_code')"
    >
      <span
        v-if="currentMode === 'claude_code'"
        class="status-dot"
        :class="instanceStatus"
      />
      <span class="icon">&#9889;</span>
      <span class="label">Claude Code</span>
    </div>
    <div
      class="mode-card"
      :class="{ active: currentMode === 'research' }"
      @click="switchMode('research')"
    >
      <span class="icon">&#128269;</span>
      <span class="label">Research</span>
    </div>
    <div v-if="currentMode === 'claude_code' && creditsInfo" class="credits-info">
      {{ creditsInfo.total }} credits &middot; ~{{ creditsInfo.days }}d
    </div>
  </div>
</template>

<script>
const STORAGE_KEY = 'chatMode'
const DEFAULT_MODE = 'claude_code'

export default {
  name: 'ModeSelector',
  props: {
    instanceStatus: {
      type: String,
      default: 'running', // running | creating | stopped
    },
    creditsInfo: {
      type: Object,
      default: null, // { total, daily, days }
    },
  },
  data() {
    return {
      currentMode: DEFAULT_MODE,
    }
  },
  created() {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && ['claude_code', 'research'].includes(saved)) {
      this.currentMode = saved
    }
    this.$emit('mode-change', this.currentMode)
  },
  methods: {
    switchMode(mode) {
      if (this.currentMode === mode) return
      this.currentMode = mode
      localStorage.setItem(STORAGE_KEY, mode)
      this.$emit('mode-change', mode)
    },
    getValue() {
      return this.currentMode
    },
  },
}
</script>

<style scoped>
.mode-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-secondary, #f5f5f5);
  border-radius: 8px;
}

.mode-card {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-secondary, #666);
  transition: all 0.2s;
  user-select: none;
}

.mode-card:hover {
  background: var(--bg-hover, #e8e8e8);
}

.mode-card.active {
  background: var(--primary-light, #e3f2fd);
  color: var(--primary, #1976d2);
  font-weight: 600;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot.running {
  background: #4caf50;
}

.status-dot.creating {
  background: #ff9800;
  animation: pulse 1.5s infinite;
}

.status-dot.stopped {
  background: #f44336;
}

.credits-info {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

.icon {
  font-size: 14px;
}

.label {
  font-size: 13px;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
