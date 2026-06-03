import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const API = ''

const DAYS_RU = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
const MONTHS_RU = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']

function fmtDate(ds) {
  const d = new Date(ds)
  const diff = Math.round((d - new Date().setHours(0,0,0,0)) / 86400000)
  const label = diff === 0 ? 'Сегодня' : diff === 1 ? 'Завтра' : DAYS_RU[d.getDay()]
  return `${label}, ${d.getDate()} ${MONTHS_RU[d.getMonth()]}`
}

export default function TrainerDetailPage() {
  const { id } = useParams()
  const { user, isClient } = useAuth()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [choosing, setChoosing] = useState(false)
  const [chooseMsg, setChooseMsg] = useState('')

  const isMyTrainer = user?.preferred_trainer?.id === Number(id)

  useEffect(() => {
    fetch(`${API}/api/trainers/${id}/`)
      .then(r => { if (!r.ok) throw new Error(); return r.json() })
      .then(d => { setData(d); setLoading(false) })
      .catch(() => { setLoading(false) })
  }, [id])

  async function handleChooseTrainer() {
    if (!user) { navigate('/login'); return }
    setChoosing(true)
    try {
      const r = await fetch(`${API}/api/auth/trainer/set/`, {
        method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ trainer_id: isMyTrainer ? null : Number(id) }),
      })
      const result = await r.json()
      if (!r.ok) throw new Error(result.error)
      setChooseMsg(isMyTrainer ? 'Тренер откреплён' : `Вы выбрали тренера ${data.trainer.full_name}!`)
      // Обновляем данные пользователя — перезагружаем страницу
      window.location.reload()
    } catch (e) {
      setChooseMsg('Ошибка: ' + e.message)
    } finally {
      setChoosing(false)
    }
  }

  if (loading) return <div className="page"><div className="loading"><div className="loading-spinner" /></div></div>
  if (!data) return <div className="page"><div className="error-msg">Тренер не найден</div><Link to="/trainers" className="btn btn-primary" style={{ marginTop: 16, display: 'inline-block' }}>← Все тренеры</Link></div>

  const { trainer, schedule } = data
  const photo = trainer.photo_file_url || trainer.photo_url

  const byDate = schedule.reduce((acc, s) => {
    if (!acc[s.class_date]) acc[s.class_date] = []
    acc[s.class_date].push(s)
    return acc
  }, {})

  return (
    <div className="page">
      <Link to="/trainers" style={{ color: '#6b7280', fontSize: '0.9rem', marginBottom: 20, display: 'inline-block' }}>
        ← Все тренеры
      </Link>

      <div className="trainer-detail-grid">
        {/* Левая колонка — фото + инфо */}
        <div>
          <div className="trainer-detail-card">
            {photo
              ? <img src={photo} alt={trainer.full_name} className="trainer-detail-photo" />
              : <div className="trainer-detail-photo-placeholder">👤</div>
            }
            <h1 className="trainer-detail-name">{trainer.full_name}</h1>
            {trainer.full_name_en && <div className="trainer-detail-name-en">{trainer.full_name_en}</div>}

            <div className="trainer-detail-tags">
              {trainer.specialization.split(', ').map(s => (
                <span key={s} className="tag tag-orange">{s}</span>
              ))}
            </div>

            <div className="trainer-detail-stats">
              <div className="trainer-detail-stat">
                <div className="trainer-detail-stat-value">{trainer.experience_years}</div>
                <div className="trainer-detail-stat-label">лет опыта</div>
              </div>
              <div className="trainer-detail-stat">
                <div className="trainer-detail-stat-value">{schedule.length}</div>
                <div className="trainer-detail-stat-label">занятий</div>
              </div>
              <div className="trainer-detail-stat">
                <div className="trainer-detail-stat-value">
                  {new Date(trainer.hired_at).getFullYear()}
                </div>
                <div className="trainer-detail-stat-label">в клубе с</div>
              </div>
            </div>

            {chooseMsg && (
              <div className="auth-success" style={{ margin: '12px 0', textAlign: 'center' }}>{chooseMsg}</div>
            )}

            {isClient && (
              <button
                className={`btn ${isMyTrainer ? 'btn-outline' : 'btn-primary'}`}
                style={{ width: '100%', justifyContent: 'center', marginTop: 12 }}
                onClick={handleChooseTrainer}
                disabled={choosing}
              >
                {choosing ? '...' : isMyTrainer ? '✓ Мой тренер (открепить)' : '⭐ Выбрать тренером'}
              </button>
            )}

            {trainer.cv_url && (
              <a
                href={trainer.cv_url}
                target="_blank"
                rel="noreferrer"
                className="btn btn-outline"
                style={{ width: '100%', textAlign: 'center', justifyContent: 'center', marginTop: 10, display: 'flex' }}
              >
                📄 Скачать резюме (PDF)
              </a>
            )}

            {!user && (
              <Link to="/login" className="btn btn-outline" style={{ width: '100%', textAlign: 'center', justifyContent: 'center', marginTop: 12, display: 'flex' }}>
                Войдите чтобы выбрать тренера
              </Link>
            )}
          </div>
        </div>

        {/* Правая колонка — биография + расписание */}
        <div>
          {trainer.bio && (
            <div className="widget" style={{ marginBottom: 24 }}>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: 16 }}>📖 Биография</h2>
              <p style={{ color: '#374151', lineHeight: 1.8 }}>{trainer.bio}</p>
            </div>
          )}

          <div className="widget">
            <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: 16 }}>📅 Ближайшие занятия</h2>
            {Object.keys(byDate).length === 0 ? (
              <div className="empty-msg" style={{ padding: '20px 0' }}>Нет запланированных занятий</div>
            ) : (
              Object.entries(byDate).map(([date, slots]) => (
                <div key={date} className="schedule-day">
                  <div className="schedule-day-title">{fmtDate(date)}</div>
                  <div className="schedule-list">
                    {slots.map(s => (
                      <div key={s.id} className="schedule-item" style={{ gridTemplateColumns: '110px 60px 1fr' }}>
                        <div className="schedule-time">{s.start_time}–{s.end_time}</div>
                        <div className="schedule-hall">{s.hall}</div>
                        <div>
                          <div className="schedule-service">{s.service_title}</div>
                          <div className="schedule-service-en">{s.service_title_en}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
            <Link to="/schedule" className="btn btn-outline" style={{ marginTop: 16, display: 'inline-block' }}>
              Всё расписание →
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
