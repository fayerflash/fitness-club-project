import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage() {
  const { register, user } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({ full_name: '', email: '', phone: '', password: '', password2: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (user) { navigate('/', { replace: true }); return null }

  function set(field) {
    return e => setForm(p => ({ ...p, [field]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (form.password !== form.password2) {
      setError('Пароли не совпадают')
      return
    }
    if (form.password.length < 6) {
      setError('Пароль должен быть не менее 6 символов')
      return
    }

    setLoading(true)
    try {
      await register({ full_name: form.full_name, email: form.email, phone: form.phone, password: form.password })
      navigate('/', { replace: true })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">🏋️</div>
        <h1 className="auth-title">Регистрация</h1>
        <p className="auth-sub">Создайте аккаунт в FitClub</p>

        {error && <div className="auth-error">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label className="form-label">ФИО *</label>
            <input className="form-input" type="text" placeholder="Иван Иванов" value={form.full_name} onChange={set('full_name')} required />
          </div>
          <div className="form-group">
            <label className="form-label">Email *</label>
            <input className="form-input" type="email" placeholder="your@email.com" value={form.email} onChange={set('email')} required />
          </div>
          <div className="form-group">
            <label className="form-label">Телефон</label>
            <input className="form-input" type="tel" placeholder="+7 (999) 000-00-00" value={form.phone} onChange={set('phone')} />
          </div>
          <div className="form-group">
            <label className="form-label">Пароль *</label>
            <input className="form-input" type="password" placeholder="Минимум 6 символов" value={form.password} onChange={set('password')} required />
          </div>
          <div className="form-group">
            <label className="form-label">Повторите пароль *</label>
            <input
              className={`form-input${form.password2 && form.password !== form.password2 ? ' input-error' : ''}`}
              type="password"
              placeholder="••••••••"
              value={form.password2}
              onChange={set('password2')}
              required
            />
          </div>
          <button className="btn btn-primary auth-submit" type="submit" disabled={loading}>
            {loading ? 'Регистрируем...' : '📝 Зарегистрироваться'}
          </button>
        </form>

        <p className="auth-switch">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </div>
  )
}
