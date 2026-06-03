import { useState, useEffect, useCallback } from 'react'

const API = ''


async function apiFetch(url, method = 'GET', body = null, isForm = false) {
  const opts = { method, credentials: 'include' }
  if (body) {
    if (isForm) {
      opts.body = body // FormData — без Content-Type, браузер сам ставит boundary
    } else {
      opts.headers = { 'Content-Type': 'application/json' }
      opts.body = JSON.stringify(body)
    }
  }
  const r = await fetch(`${API}${url}`, opts)
  const data = await r.json()
  if (!r.ok) throw new Error(data.error || 'Ошибка запроса')
  return data
}

export function useCrud(endpoint) {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    setLoading(true)
    apiFetch(endpoint)
      .then(d => { setItems(d.results || []); setLoading(false) })
      .catch(e => { setError(e.message); setLoading(false) })
  }, [endpoint])

  useEffect(() => { load() }, [load])

  async function create(data, files = {}) {
    const fd = toFormData(data, files)
    const result = await apiFetch(`${endpoint}create/`, 'POST', fd, true)
    load()
    return result
  }

  async function update(pk, data, files = {}) {
    const fd = toFormData(data, files)
    const result = await apiFetch(`${endpoint}${pk}/update/`, 'POST', fd, true)
    load()
    return result
  }

  async function remove(pk) {
    await apiFetch(`${endpoint}${pk}/delete/`, 'POST')
    load()
  }

  return { items, loading, error, create, update, remove, reload: load }
}

function toFormData(data, files = {}) {
  const fd = new FormData()
  for (const [k, v] of Object.entries(data)) {
    if (Array.isArray(v)) {
      v.forEach(item => fd.append(k, item))
    } else if (v !== null && v !== undefined) {
      fd.append(k, v)
    }
  }
  for (const [k, v] of Object.entries(files)) {
    if (v) fd.append(k, v)
  }
  return fd
}
