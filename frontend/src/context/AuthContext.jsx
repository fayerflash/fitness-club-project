import { createContext, useContext, useState, useEffect } from 'react'

const API = ''


const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // Проверяем сессию при загрузке
  useEffect(() => {
    fetch(`${API}/api/auth/me/`, { credentials: 'include' })
      .then(r => r.json())
      .then(d => { setUser(d.user); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  async function login(email, password) {
    const r = await fetch(`${API}/api/auth/login/`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.error || 'Ошибка входа')
    setUser(data.user)
    return data.user
  }

  async function register(formData) {
    const r = await fetch(`${API}/api/auth/register/`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.error || 'Ошибка регистрации')
    setUser(data.user)
    return data.user
  }

  async function logout() {
    await fetch(`${API}/api/auth/logout/`, { method: 'POST', credentials: 'include' })
    setUser(null)
  }

  async function updateProfile(formData) {
    const r = await fetch(`${API}/api/auth/profile/update/`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })
    const data = await r.json()
    if (!r.ok) throw new Error(data.error || 'Ошибка обновления')
    setUser(data.user)
    return data.user
  }

  const isClient = user?.role === 'client'
  const isGymAdmin = user?.role === 'gym_admin'
  const isSuperAdmin = user?.role === 'superadmin'
  const isAdmin = isGymAdmin || isSuperAdmin

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, updateProfile, isClient, isGymAdmin, isSuperAdmin, isAdmin }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
