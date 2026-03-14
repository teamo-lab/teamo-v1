/**
 * Patch for src/api/engine.js
 *
 * Add new API function for instance status query.
 * Append to the end of the file.
 */

// Add to src/api/engine.js:

/**
 * Get Claude Code instance status for current user
 * @returns {Promise<{code: number, result: {status: string, credits_remaining: number, daily_cost: number, estimated_days: number}}>}
 */
export function apiGetInstanceStatus() {
  return request({
    url: '/api/engine/instanceStatus',
    method: 'get',
  })
}

/**
 * Get credits info for current user
 * @returns {Promise<{code: number, result: {total: number, daily: number, days: number, warning: string|null}}>}
 */
export function apiGetCreditsInfo() {
  return request({
    url: '/api/engine/creditsInfo',
    method: 'get',
  })
}
