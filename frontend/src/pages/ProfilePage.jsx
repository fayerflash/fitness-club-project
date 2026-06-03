import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const API = ''

const STATUS_COLOR = { active: '#d1fae5', expired: '#fee2e2', frozen: '#fef3c7' }
const ORDER_COLOR = { paid: '#16a34a', pending: '#d97706', cancelled: '#dc2626', refunded: '#6b7280' }

export default function ProfilePage() {
  const { user, logout, updateProfile, isAdmin } = useAuth()
  const navigate = useNavigate()
  const [profileData, setProfileData] = useState(null)
  const [allMemberships, setAllMemberships] = useState([])
  const [allTrainers, setAllTrainers] = useState([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({ full_name: '', phone: '' })
  const [editError, setEditError] = useState('')
  const [editLoading, setEditLoading] = useState(false)
  const [successMsg, setSuccessMsg] = useState('')
  const [showMembershipModal, setShowMembershipModal] = useState(false)
  const [showTrainerModal, setShowTrainerModal] = useState(false)
  const [switching, setSwitching] = useState(null)
  const [choosingTrainer, setChoosingTrainer] = useState(false)

  useEffect(() => {
    if (!user) { navigate('/login'); return }
    Promise.all([
      fetch(`${API}/api/auth/profile/`, { credentials: 'include' }).then(r => r.json()),
      fetch(`${API}/api/memberships/?limit=20&ordering=price`).then(r => r.json()),
      fetch(`${API}/api/trainers/`).then(r => r.json()),
    ]).then(([profile, mems, trainers]) => {
      setProfileData(profile)
      setAllMemberships(mems.results || [])
      setAllTrainers(trainers.results || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [user])

  function reload() {
    fetch(`${API}/api/auth/profile/`, { credentials: 'include' })
      .then(r => r.json()).then(setProfileData)
  }

  async function handleEditSubmit(e) {
    e.preventDefault(); setEditError(''); setEditLoading(true)
    try {
      await updateProfile(editForm)
      setEditing(false); setSuccessMsg('Профиль обновлён!'); setTimeout(() => setSuccessMsg(''), 3000)
    } catch (err) { setEditError(err.message) } finally { setEditLoading(false) }
  }

  async function handleSwitch(id) {
    setSwitching(id)
    try {
      const r = await fetch(`${API}/api/memberships/${id}/switch/`, { method: 'POST', credentials: 'include' })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error)
      setSuccessMsg(data.message); setTimeout(() => setSuccessMsg(''), 4000)
      setShowMembershipModal(false); reload()
    } catch (e) { setSuccessMsg('Ошибка: ' + e.message) } finally { setSwitching(null) }
  }

  async function handleChooseTrainer(trainerId) {
    setChoosingTrainer(trainerId)
    try {
      const r = await fetch(`${API}/api/auth/trainer/set/`, {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trainer_id: trainerId }),
      })
      const data = await r.json()
      if (!r.ok) throw new Error(data.error)
      setSuccessMsg(trainerId ? `Тренер выбран: ${data.trainer?.full_name}` : 'Тренер откреплён')
      setTimeout(() => setSuccessMsg(''), 3000)
      setShowTrainerModal(false)
      window.location.reload()
    } catch (e) { setSuccessMsg('Ошибка: ' + e.message) } finally { setChoosingTrainer(null) }
  }

  async function handleLogout() { await logout(); navigate('/') }

  if (!user) return null
  if (loading) return <div className="page"><div className="loading"><div className="loading-spinner" /></div></div>

  const ROLE_BADGE = {
    client: { label: 'Клиент', cls: 'tag-green' },
    gym_admin: { label: 'Администратор', cls: 'tag-orange' },
    superadmin: { label: 'Суперадмин', cls: 'tag-blue' },
  }
  const badge = ROLE_BADGE[user.role] || { label: user.role, cls: 'tag-blue' }
  const pt = user.preferred_trainer

  return (
    <div className="page">
      <h1 className="page-title">👤 Мой профиль</h1>
      {successMsg && <div className={successMsg.startsWith('Ошибка') ? 'auth-error' : 'auth-success'}>{successMsg}</div>}

      <div className="profile-grid">
        {/* Левая колонка */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="profile-card">
            <div className="profile-avatar">{user.full_name.charAt(0).toUpperCase()}</div>
            {!editing ? (
              <>
                <h2 className="profile-name">{user.full_name}</h2>
                <span className={`tag ${badge.cls}`} style={{ fontSize: '0.85rem', marginBottom: 12, display: 'inline-block' }}>
                  {badge.label}
                </span>
                <div className="profile-info-list">
                  <div className="profile-info-row"><span>📧</span><span>{user.email}</span></div>
                  <div className="profile-info-row"><span>📱</span><span>{user.phone || 'Не указан'}</span></div>
                  <div className="profile-info-row"><span>📅</span><span>С {user.created_at}</span></div>
                </div>
                <div style={{ display: 'flex', gap: 10, marginTop: 16, flexWrap: 'wrap' }}>
                  <button className="btn btn-primary" onClick={() => { setEditForm({ full_name: user.full_name, phone: user.phone || '' }); setEditing(true) }}>✏️ Редактировать</button>
                  <button className="btn btn-outline" onClick={handleLogout} style={{ color: '#dc2626', borderColor: '#dc2626' }}>🚪 Выйти</button>
                </div>
                {isAdmin && (
                  <Link to="/admin" className="btn btn-outline" style={{ marginTop: 10, display: 'flex', justifyContent: 'center' }}>⚙️ Панель управления</Link>
                )}
              </>
            ) : (
              <form onSubmit={handleEditSubmit} style={{ width: '100%' }}>
                <h3 style={{ marginBottom: 16 }}>Редактирование</h3>
                {editError && <div className="auth-error" style={{ marginBottom: 12 }}>{editError}</div>}
                <div className="form-group">
                  <label className="form-label">ФИО</label>
                  <input className="form-input" value={editForm.full_name} onChange={e => setEditForm(p => ({ ...p, full_name: e.target.value }))} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Телефон</label>
                  <input className="form-input" value={editForm.phone} onChange={e => setEditForm(p => ({ ...p, phone: e.target.value }))} />
                </div>
                <div style={{ display: 'flex', gap: 10 }}>
                  <button className="btn btn-primary" type="submit" disabled={editLoading}>{editLoading ? 'Сохраняем...' : '💾 Сохранить'}</button>
                  <button className="btn btn-outline" type="button" onClick={() => setEditing(false)}>Отмена</button>
                </div>
              </form>
            )}
          </div>

          {/* Мой тренер */}
          {user.role === 'client' && (
            <div className="profile-card" style={{ textAlign: 'left' }}>
              <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: 12 }}>⭐ Мой тренер</div>
              {pt ? (
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                  {(pt.photo_file_url || pt.photo_url)
                    ? <img src={pt.photo_file_url || pt.photo_url} style={{ width: 48, height: 48, borderRadius: '50%', objectFit: 'cover' }} alt="" />
                    : <div style={{ width: 48, height: 48, borderRadius: '50%', background: '#e8f4ff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.4rem' }}>👤</div>
                  }
                  <div>
                    <div style={{ fontWeight: 700 }}>{pt.full_name}</div>
                    <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{pt.specialization}</div>
                  </div>
                </div>
              ) : (
                <div style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: 12 }}>Тренер не выбран</div>
              )}
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <button className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '7px 14px' }} onClick={() => setShowTrainerModal(true)}>
                  {pt ? '🔄 Сменить' : '⭐ Выбрать тренера'}
                </button>
                {pt && (
                  <Link to={`/trainers/${pt.id}`} className="btn btn-outline" style={{ fontSize: '0.85rem', padding: '7px 14px' }}>
                    Профиль →
                  </Link>
                )}
                {pt && (
                  <button className="btn btn-outline" style={{ fontSize: '0.85rem', padding: '7px 14px', color: '#dc2626', borderColor: '#dc2626' }}
                    onClick={() => handleChooseTrainer(null)}>
                    Открепить
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Правая колонка */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Мои абонементы */}
          <div className="widget">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
              <h3 className="widget-title">🎫 Мои абонементы</h3>
              {user.role === 'client' && (
                <button className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '7px 14px' }}
                  onClick={() => setShowMembershipModal(true)}>
                  🔄 Сменить
                </button>
              )}
            </div>
            {profileData?.memberships?.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {profileData.memberships.map(um => (
                  <div key={um.id} style={{ background: STATUS_COLOR[um.status] || '#f9fafb', padding: '12px 16px', borderRadius: 10 }}>
                    <div style={{ fontWeight: 700 }}>{um.membership_title}</div>
                    <div style={{ fontSize: '0.8rem', color: '#6b7280', fontStyle: 'italic' }}>{um.membership_title_en}</div>
                    <div style={{ fontSize: '0.85rem', marginTop: 4 }}>📅 {um.start_date} — {um.end_date}</div>
                    <div style={{ fontSize: '0.85rem' }}>
                      Статус: <strong>{um.status_display}</strong>
                      {' · '}Визиты: {um.visits_used} {um.visits_limit ? `из ${um.visits_limit}` : '(безлимит)'}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: '#6b7280', marginBottom: 12 }}>Нет активных абонементов</div>
            )}
            {user.role === 'client' && (
              <div style={{ display: 'flex', gap: 10, marginTop: 12, flexWrap: 'wrap' }}>
                <Link to="/memberships" className="btn btn-primary" style={{ fontSize: '0.9rem' }}>🛒 Купить абонемент</Link>
                <Link to="/promotions" className="btn btn-outline" style={{ fontSize: '0.9rem' }}>🎁 Акции</Link>
              </div>
            )}
          </div>

          {/* История заказов */}
          {profileData?.orders?.length > 0 && (
            <div className="widget">
              <h3 className="widget-title" style={{ marginBottom: 16 }}>📦 История заказов</h3>
              {profileData.orders.map(o => (
                <div key={o.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid #e5e7eb' }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>Заказ №{o.id}</div>
                    <div style={{ fontSize: '0.82rem', color: '#6b7280' }}>{o.order_date} · {o.payment_method}</div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontWeight: 700, color: '#e85d04' }}>{Number(o.total_amount).toLocaleString('ru-RU')} ₽</div>
                    <div style={{ fontSize: '0.82rem', color: ORDER_COLOR[o.status] || '#6b7280', fontWeight: 600 }}>{o.status_display}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Модал: смена абонемента */}
      {showMembershipModal && (
        <div className="modal-overlay" onClick={() => setShowMembershipModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 600 }}>
            <h3 className="modal-title">🔄 Сменить абонемент</h3>
            <p style={{ color: '#6b7280', marginBottom: 16, fontSize: '0.9rem' }}>
              Текущий активный абонемент будет деактивирован, будет активирован выбранный.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 400, overflowY: 'auto' }}>
              {allMemberships.map(m => {
                const isCurrent = profileData?.memberships?.some(um => um.membership_title === m.title)
                return (
                  <div key={m.id} style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '12px 16px', borderRadius: 10,
                    border: isCurrent ? '2px solid #e85d04' : '2px solid #e5e7eb',
                    background: isCurrent ? '#fff7ed' : '#fff',
                  }}>
                    <div>
                      <div style={{ fontWeight: 700 }}>{m.title} <span style={{ fontStyle: 'italic', color: '#9ca3af', fontWeight: 400 }}>{m.title_en}</span></div>
                      <div style={{ fontSize: '0.82rem', color: '#6b7280' }}>{m.duration_days} дней {m.visits_limit ? `· ${m.visits_limit} визитов` : '· безлимит'}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 800, color: '#e85d04', fontSize: '1.1rem' }}>{Number(m.price).toLocaleString('ru-RU')} ₽</div>
                      {isCurrent
                        ? <span className="tag tag-green" style={{ fontSize: '0.75rem' }}>Активен</span>
                        : <button className="btn btn-primary" style={{ marginTop: 4, fontSize: '0.82rem', padding: '5px 14px' }}
                            onClick={() => handleSwitch(m.id)} disabled={switching === m.id}>
                            {switching === m.id ? '...' : 'Выбрать'}
                          </button>
                      }
                    </div>
                  </div>
                )
              })}
            </div>
            <button className="btn btn-outline" style={{ marginTop: 16 }} onClick={() => setShowMembershipModal(false)}>Закрыть</button>
          </div>
        </div>
      )}

      {/* Модал: выбор тренера */}
      {showTrainerModal && (
        <div className="modal-overlay" onClick={() => setShowTrainerModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()} style={{ maxWidth: 600 }}>
            <h3 className="modal-title">⭐ Выбрать тренера</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 420, overflowY: 'auto' }}>
              {allTrainers.map(t => {
                const isMine = user.preferred_trainer?.id === t.id
                const photo = t.photo_file_url || t.photo_url
                return (
                  <div key={t.id} style={{
                    display: 'flex', alignItems: 'center', gap: 14,
                    padding: '10px 14px', borderRadius: 10,
                    border: isMine ? '2px solid #e85d04' : '2px solid #e5e7eb',
                    background: isMine ? '#fff7ed' : '#fff',
                  }}>
                    {photo
                      ? <img src={photo} style={{ width: 48, height: 48, borderRadius: '50%', objectFit: 'cover', flexShrink: 0 }} alt="" />
                      : <div style={{ width: 48, height: 48, borderRadius: '50%', background: '#e8f4ff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.4rem', flexShrink: 0 }}>👤</div>
                    }
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 700 }}>{t.full_name}</div>
                      <div style={{ fontSize: '0.8rem', color: '#6b7280' }}>{t.specialization} · {t.experience_years} лет</div>
                    </div>
                    <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                      <Link to={`/trainers/${t.id}`} className="btn btn-outline" style={{ fontSize: '0.8rem', padding: '4px 10px' }}>
                        Профиль
                      </Link>
                      {isMine
                        ? <span className="tag tag-orange" style={{ alignSelf: 'center' }}>Мой</span>
                        : <button className="btn btn-primary" style={{ fontSize: '0.82rem', padding: '5px 14px' }}
                            onClick={() => handleChooseTrainer(t.id)}
                            disabled={choosingTrainer === t.id}>
                            {choosingTrainer === t.id ? '...' : 'Выбрать'}
                          </button>
                      }
                    </div>
                  </div>
                )
              })}
            </div>
            <button className="btn btn-outline" style={{ marginTop: 16 }} onClick={() => setShowTrainerModal(false)}>Закрыть</button>
          </div>
        </div>
      )}
    </div>
  )
}
