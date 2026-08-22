/**
 * 身份证号脱敏展示，规则与后端 `apps.core.utils.mask_id_card` 保持一致。
 * 若字符串已含 *（服务端已脱敏），原样返回，避免二次处理。
 */
export function maskIdCard(plain: string | null | undefined): string {
  if (plain == null || plain === '') return ''
  const s = String(plain).trim()
  if (!s) return ''
  if (s.includes('*')) return s

  const n = s.length
  if (n === 18 && /^\d{17}[\dXx]$/.test(s)) {
    return `${s.slice(0, 6)}********${s.slice(-4)}`
  }
  if (n === 15 && /^\d{15}$/.test(s)) {
    return `${s.slice(0, 6)}*****${s.slice(-4)}`
  }
  if (n <= 3) return '*'.repeat(n)
  if (n <= 6) return `${s[0]}***${s[n - 1]}`
  return `${s.slice(0, 2)}${'*'.repeat(n - 4)}${s.slice(-2)}`
}
