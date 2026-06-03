import { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'

const API = ''

const ROLES = [
  { value: 'client', label: 'Клиент' },
  { value: 'gym_admin', label: 'Администратор' },
  { value: 'superadmin', label: 'Суперадмин' },
]

export default function AdminUsers() {
  const { user: me } = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [changing, setChanging] = useState(null)

  useEffect(() => {
    fetch(`${API}/api/admin/users/`, { credentials: 'include' })
      .then(r => r.json()).then(d => { setUsers(d.results || []); setLoading(false) })
  }, [])

  async function changeRole(id, role) {
    setChanging(id)
    try {
      const r = await fetch(`${API}/api/admin/users/${id}/role/`, {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error)
      setUsers(prev => prev.map(u => u.id === id ? { ...u, role: data.role, role_display: ROLES.find(r => r.value === data.role)?.label } : u))
    } catch (e) { alert(e.message) } finally { setChanging(null) }
  }

  const ROLE_CLS = { client: 'tag-green', gym_admin: 'tag-orange', superadmin: 'tag-blue' }

  return (
    <div>
      <h2 className="admin-page-title">👥 Пользователи</h2>
      <p style={{ color: '#6b7280', marginBottom: 24 }}>Только суперадмин может менять роли</p>
      {loading && <div className="loading"><div className="loading-spinner" /></div>}
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead><tr><th>#</th><th>ФИО</th><th>Email</th><th>Телефон</th><th>Роль</th><th>Дата</th><th>Изменить роль</th></tr></thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} style={{ opacity: u.id === me?.id ? 0.7 : 1 }}>
                <td>{u.id}</td>
                <td><strong>{u.full_name}</strong> {u.id === me?.id && <span className="tag tag-blue" style={{ fontSize: '0.7rem' }}>Вы</span>}</td>
                <td>{u.email}</td>
                <td>{u.phone || '—'}</td>
                <td><span className={`tag ${ROLE_CLS[u.role] || 'tag-blue'}`}>{u.role_display}</span></td>
                <td>{u.created_at}</td>
                <td>
                  {u.id !== me?.id ? (
                    <select
                      className="form-input"
                      style={{ padding: '5px 8px', fontSize: '0.85rem', width: 'auto' }}
                      value={u.role}
                      onChange={e => changeRole(u.id, e.target.value)}
                      disabled={changing === u.id}
                    >
                      {ROLES.map(r => <option key={r.value} value={r.value}>{r.label}</option>)}
                    </select>
                  ) : <span style={{ color: '#9ca3af' }}>—</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
