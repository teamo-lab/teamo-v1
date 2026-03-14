# Frontend Integration Guide

## Files to modify

### 1. New file: `src/components/ModeSelector.vue`
Copy `components/ModeSelector.vue` to the frontend project.

### 2. Modify: `src/views/chat/index.vue`
Import and register ModeSelector component:

```vue
<script>
import ModeSelector from '@/components/ModeSelector.vue'

export default {
  components: { ModeSelector },
  data() {
    return {
      chatMode: 'claude_code',
      instanceStatus: 'running',
      creditsInfo: null,
    }
  },
  methods: {
    onModeChange(mode) {
      this.chatMode = mode
    },
  },
}
</script>
```

Add ModeSelector below the ChatInput component:

```vue
<ModeSelector
  ref="modeSelector"
  :instance-status="instanceStatus"
  :credits-info="creditsInfo"
  @mode-change="onModeChange"
/>
```

### 3. Modify: `src/mixin/chatcore.js`
In `getModeValue()` (~line 371), add priority check for ModeSelector:

```js
getModeValue(m) {
  if (this.$refs.modeSelector) {
    const val = this.$refs.modeSelector.getValue()
    if (val === 'claude_code') return 'claude_code'
    if (val === 'research') return 'a2a'
  }
  // Original logic below...
}
```

### 4. Modify: `src/api/engine.js`
Add `apiGetInstanceStatus()` and `apiGetCreditsInfo()` (see api-engine-patch.js).

### 5. No changes needed to SSE handling
The proxy service converts Claude Code events to the existing frontend SSE format (step/answer_chunk/task_done), so `mcpNext()` in chatcore.js works as-is.
