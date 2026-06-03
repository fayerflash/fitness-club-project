import { useState, useEffect } from 'react'

const API = ''


const DAYS_RU = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
const MONTHS_RU = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']

function formatDateRu(dateStr) {
  const d = new Date(dateStr)
  return `${d.getDate()} ${MONTHS_RU[d.getMonth()]}`
}

function getDayLabel(dateStr) {
  const d = new Date(dateStr)
  const today = new Date()
  today.setHours(0,0,0,0)
  const diff = Math.round((d - today) / 86400000)
  if (diff === 0) return 'Сегодня'
  if (diff === 1) return 'Завтра'
  return DAYS_RU[d.getDay()]
}

export default function SchedulePage() {
  const [schedule, setSchedule] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    setLoading(true)
    fetch(`${API}/api/schedule/`)
      .then(r => r.json())
      .then(d => { setSchedule(d.results); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const filtered = search
    ? schedule.filter(s =>
        s.service.title.toLowerCase().includes(search.toLowerCase()) ||
        s.trainer.full_name.toLowerCase().includes(search.toLowerCase())
      )
    : schedule

  // Группируем по дате
  const byDate = filtered.reduce((acc, item) => {
    if (!acc[item.class_date]) acc[item.class_date] = []
    acc[item.class_date].push(item)
    return acc
  }, {})

  function handleSearch(e) {
    e.preventDefault()
    setSearch(searchInput)
  }

  return (
    <div className="page">
      <h1 className="page-title">📅 Расписание занятий</h1>
      <p className="page-subtitle">Данные из таблиц: расписание, услуги, тренеры</p>

      {/* Поиск */}
      <form className="search-bar" onSubmit={handleSearch}>
        <input
          className="search-input"
          type="text"
          placeholder="Поиск по занятию или тренеру..."
          value={searchInput}
          onChange={e => setSearchInput(e.target.value)}
        />
        <button className="search-btn" type="submit">Найти</button>
        {search && (
          <button className="btn btn-outline" type="button" onClick={() => { setSearch(''); setSearchInput('') }}>✕</button>
        )}
      </form>

      {loading && <div className="loading"><div className="loading-spinner" />Загрузка расписания...</div>}

      {!loading && Object.keys(byDate).length === 0 && (
        <div className="empty-msg">Занятий не найдено</div>
      )}

      {Object.entries(byDate).map(([date, items]) => (
        <div key={date} className="schedule-day">
          <div className="schedule-day-title">
            <span>{getDayLabel(date)}</span>
            <span>{formatDateRu(date)}</span>
          </div>
          <div className="schedule-list">
            {items.map(item => (
              <div key={item.id} className="schedule-item">
                <div>
                  <div className="schedule-time">{item.start_time} – {item.end_time}</div>
                </div>
                <div className="schedule-hall">{item.hall}</div>
                <div>
                  <div className="schedule-service">{item.service.title}</div>
                  <div className="schedule-service-en">{item.service.title_en}</div>
                  <div className="schedule-trainer">👤 {item.trainer.full_name} · {item.trainer.specialization}</div>
                </div>
                <div>
                  {(item.trainer.photo_file_url || item.trainer.photo_url)
                    ? <img src={item.trainer.photo_file_url || item.trainer.photo_url} alt={item.trainer.full_name} className="schedule-trainer-img" />
                    : <div style={{ width: 36, height: 36, borderRadius: '50%', background: '#e8f4ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>👤</div>
                  }
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
