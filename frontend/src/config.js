// Все запросы идут через Vite-прокси на localhost:5173
// Браузер считает их same-origin → куки сессии работают корректно
export const API = ''

// Для медиафайлов (картинки, PDF) тоже через прокси
export function mediaUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path  // внешние URL без изменений
  return path  // /media/... → Vite проксирует на Django
}
