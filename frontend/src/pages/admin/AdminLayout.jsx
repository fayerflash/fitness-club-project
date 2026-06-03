import { NavLink, Outlet, Navigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const NAV = [
  { to: '/admin', label: 'Дашборд', icon: '📊', end: true },
  { to: '/admin/memberships', label: 'Абонементы', icon: '🎫' },
  { to: '/admin/trainers', label: 'Тренеры', icon: '👨‍🏫' },
  { to: '/admin/services', label: 'Услуги', icon: '🏋️' },
  { to: '/admin/schedule', label: 'Расписание', icon: '📅' },
  { to: '/admin/promotions', label: 'Акции', icon: '🎁' },
  { to: '/admin/analytics', label: 'Аналитика', icon: '📈' },
]

export default function AdminLayout() {
  const { user, loading, isSuperAdmin } = useAuth()

  if (loading) return <div className="loading"><div className="loading-spinner" /></div>
  if (!user) return <Navigate to="/login" replace />
  if (!['gym_admin', 'superadmin'].includes(user.role)) return <Navigate to="/" replace />

  return (
    <div className="admin-wrap">
      <aside className="admin-sidebar">
        <div className="admin-sidebar-title">
          <span>⚙️</span>
          <span>Управление</span>
        </div>
        <div className="admin-sidebar-role">
          {user.role === 'superadmin' ? '👑 Суперадмин' : '🔧 Администратор'}
        </div>
        <nav className="admin-nav">
          {NAV.map(item => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => 'admin-nav-link' + (isActive ? ' active' : '')}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
          {isSuperAdmin && (
            <NavLink
              to="/admin/users"
              className={({ isActive }) => 'admin-nav-link' + (isActive ? ' active' : '')}
            >
              <span>👥</span><span>Пользователи</span>
            </NavLink>
          )}
        </nav>
        {isSuperAdmin && (
          <a
            href="http://127.0.0.1:8000/admin/"
            target="_blank"
            rel="noreferrer"
            className="admin-django-link"
          >
            🛠 Django Admin
          </a>
        )}
      </aside>
      <div className="admin-content">
        <Outlet />
      </div>
    </div>
  )
}
