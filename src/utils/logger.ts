// 统一日志工具（支持环境与级别开关）
// 使用方式：import { logger } from '@/utils/logger'
// 环境变量：
// - import.meta.env.DEV: Vite 开发环境布尔值
// - VITE_LOG_LEVEL: debug|info|warn|error|silent（优先级更高）
// - VITE_ENABLE_DEBUG: 'true' 开启开发环境下的 debug 级别

type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'silent'

const DEV: boolean = Boolean((import.meta as any)?.env?.DEV)
const env = (import.meta as any)?.env || {}

const ORDER: LogLevel[] = ['debug', 'info', 'warn', 'error', 'silent']

function normalizeLevel(l?: unknown): LogLevel | undefined {
  if (typeof l !== 'string') return undefined
  const v = l.toLowerCase()
  if (ORDER.includes(v as LogLevel)) return v as LogLevel
  return undefined
}

function resolveInitialLevel(): LogLevel {
  const levelFromEnv = normalizeLevel(env.VITE_LOG_LEVEL)
  if (levelFromEnv) return levelFromEnv
  const enableDebug = String(env.VITE_ENABLE_DEBUG).toLowerCase() === 'true'
  // 开发环境默认 info，若开启 VITE_ENABLE_DEBUG 则为 debug；生产默认 warn
  if (DEV) return enableDebug ? 'debug' : 'info'
  return 'warn'
}

let currentLevel: LogLevel = resolveInitialLevel()

function shouldLog(level: LogLevel): boolean {
  return ORDER.indexOf(level) >= ORDER.indexOf(currentLevel)
}

export const logger = {
  setLevel(level: LogLevel): void {
    currentLevel = level
  },
  getLevel(): LogLevel {
    return currentLevel
  },
  debug(...args: unknown[]): void {
    if (shouldLog('debug')) console.debug(...args)
  },
  info(...args: unknown[]): void {
    if (shouldLog('info')) console.info(...args)
  },
  warn(...args: unknown[]): void {
    if (shouldLog('warn')) console.warn(...args)
  },
  error(...args: unknown[]): void {
    if (shouldLog('error')) console.error(...args)
  }
}

export type { LogLevel }