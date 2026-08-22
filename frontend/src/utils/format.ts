/**
 * 文件功能：通用数据格式化工具函数
 */
import dayjs from 'dayjs'

/**
 * 格式化日期时间
 * @param date 日期字符串或对象
 * @param format 格式模板，默认为 YYYY-MM-DD HH:mm:ss
 */
export const format_date_time = (date: string | Date | null | undefined, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!date) return '-'
  return dayjs(date).format(format)
}

/**
 * 格式化日期
 * @param date 日期字符串或对象
 */
export const format_date = (date: string | Date | null | undefined) => {
  return format_date_time(date, 'YYYY-MM-DD')
}

/**
 * 格式化文件大小
 * @param bytes 字节数
 */
export const format_file_size = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
