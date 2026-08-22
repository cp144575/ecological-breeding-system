export const allowed_image_types = ['image/jpeg', 'image/png', 'image/gif'] as const

export const max_image_size_bytes = 5 * 1024 * 1024

export const is_valid_image_filename = (filename: string): boolean => {
  const base_name = filename.split(/[/\\]/).pop() || ''
  return /^[\u4e00-\u9fa5a-zA-Z0-9_.-]+$/.test(base_name)
}

export const validate_image_file = async (
  file: File
): Promise<{ ok: true } | { ok: false; error_msg: string }> => {
  if (!allowed_image_types.includes(file.type as any)) {
    return { ok: false, error_msg: '请上传JPG/PNG/GIF格式图片' }
  }
  if (file.size > max_image_size_bytes) {
    return { ok: false, error_msg: '图片大小不能超过5MB' }
  }
  if (!is_valid_image_filename(file.name)) {
    return { ok: false, error_msg: '文件名不允许包含特殊字符' }
  }

  return { ok: true }
}
