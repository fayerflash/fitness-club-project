import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="navbar-brand">
          <span>🏋️</span> FitClub
        </NavLink>

        <div className="navbar-links">
          <NavLink to="/" end className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Главная</NavLink>
          <NavLink to="/memberships" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Абонементы</NavLink>
          <NavLink to="/trainers" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Тренеры</NavLink>
          <NavLink to="/schedule" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Расписание</NavLink>
          <NavLink to="/promotions" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Акции</NavLink>
          <NavLink to="/statistics" className={({ isActive }) => 'nav-link' + (isActive ? ' active' : '')}>Статистика</NavLink>
        </div>

        <div className="navbar-auth">
          {user ? (
            <div className="navbar-user">
              <NavLink to="/profile" className="navbar-user-btn">
                <div className="navbar-avatar">{user.full_name.charAt(0).toUpperCase()}</div>
                <div className="navbar-user-info">
                  <div className="navbar-user-name">{user.full_name.split(' ')[0]}</div>
                  <div className="navbar-user-role">{user.role_display}</div>
                </div>
              </NavLink>
              {isAdmin && (
                <NavLink to="/admin" className="nav-link" style={{ fontWeight: 700, color: '#e85d04' }}>⚙️ Управление</NavLink>
              )}
              <button className="nav-link nav-logout" onClick={handleLogout} title="Выйти">🚪</button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: 8 }}>
              <NavLink to="/login" className="nav-link">Войти</NavLink>
              <NavLink to="/register" className="btn btn-primary" style={{ padding: '7px 16px', fontSize: '0.9rem' }}>
                Регистрация
              </NavLink>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
