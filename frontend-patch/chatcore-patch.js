/**
 * Patch for src/mixin/chatcore.js
 *
 * Modification 1: getModeValue() — add claude_code mapping
 * Location: ~line 371-373
 *
 * BEFORE:
 *   getModeValue(m) {
 *     const map = { ... }
 *     return map[m] || m
 *   }
 *
 * AFTER:
 *   getModeValue(m) {
 *     // If ModeSelector is active, use its value directly
 *     if (this.$refs.modeSelector) {
 *       return this.$refs.modeSelector.getValue()
 *     }
 *     const map = { ... }
 *     return map[m] || m
 *   }
 *
 * Modification 2: getMultiEngineQuery() — pass mode to requestParams
 * Location: ~line 998-1155
 *
 * BEFORE (in requestParams construction):
 *   mode: this.getModeValue(this.$refs.agentSelecter?.getValue?.()),
 *
 * AFTER:
 *   mode: this.getModeValue(this.$refs.modeSelector?.getValue?.() || this.$refs.agentSelecter?.getValue?.()),
 *
 * Modification 3: mcpNext() — handle claude_code SSE events
 * Location: ~line 676-997 (inside SSE event parsing)
 *
 * The existing mcpNext already handles step/answer_chunk/task_done events.
 * No changes needed — the proxy converts Claude Code events to this format.
 */

// Mode value mapping for reference
export function getModeValuePatched(modeSelector, agentSelecter, originalGetModeValue) {
  // Priority: ModeSelector > AgentSelecter > original
  if (modeSelector) {
    const val = modeSelector.getValue()
    if (val === 'claude_code') return 'claude_code'
    if (val === 'research') return 'a2a'  // Research mode uses old a2a engine
  }
  if (agentSelecter) {
    return originalGetModeValue(agentSelecter.getValue())
  }
  return 'claude_code' // Default
}
