import { useState, useEffect } from 'react'
import { useCrud } from './useCrud'

const API = ''

const today = new Date().toISOString().split('T')[0]
const EMPTY = { service_id: '', trainer_id: '', class_date: today, start_time: '09:00', end_time: '10:00', hall: '', capacity: 20 }

export default function AdminSchedule() {
  const { items, loading, create, update, remove } = useCrud('/api/admin/schedule/')
  const [services, setServices] = useState([])
  const [trainers, setTrainers] = useState([])
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [err, setErr] = useState('')
  const [saving, setSaving] = useState(false)
  const [confirm, setConfirm] = useState(null)

  useEffect(() => {
    fetch(`${API}/api/services/`, { credentials: 'include' }).then(r => r.json()).then(d => setServices(d.results || []))
    fetch(`${API}/api/trainers/`, { credentials: 'include' }).then(r => r.json()).then(d => setTrainers(d.results || []))
  }, [])

  function set(field) { return e => setForm(p => ({ ...p, [field]: e.target.value })) }

  async function handleSave(e) {
    e.preventDefault(); setErr(''); setSaving(true)
    try {
      modal === 'create' ? await create(form) : await update(modal.id, form)
      setModal(null)
    } catch (e) { setErr(e.message) } finally { setSaving(false) }
  }

  const grouped = items.reduce((acc, s) => {
    if (!acc[s.class_date]) acc[s.class_date] = []
    acc[s.class_date].push(s)
    return acc
  }, {})

  return (
    <div>
      <div className="admin-page-header">
        <h2 className="admin-page-title">📅 Расписание</h2>
        <button className="btn btn-primary" onClick={() => { setForm(EMPTY); setErr(''); setModal('create') }}>+ Добавить занятие</button>
      </div>
      {loading && <div className="loading"><div className="loading-spinner" /></div>}

      {Object.entries(grouped).map(([date, slots]) => (
        <div key={date} style={{ marginBottom: 24 }}>
          <div style={{ fontWeight: 700, color: '#e85d04', borderBottom: '2px solid #e85d04', paddingBottom: 6, marginBottom: 10, fontSize: '1rem' }}>
            📅 {new Date(date).toLocaleDateString('ru-RU', { weekday: 'long', day: 'numeric', month: 'long' })}
          </div>
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead><tr><th>Время</th><th>Услуга</th><th>Тренер</th><th>Зал</th><th>Мест</th><th>Действия</th></tr></thead>
              <tbody>
                {slots.map(s => (
                  <tr key={s.id}>
                    <td style={{ fontWeight: 700, color: '#e85d04' }}>{s.start_time}–{s.end_time}</td>
                    <td><strong>{s.service_title}</strong></td>
                    <td>{s.trainer_name}</td>
                    <td>{s.hall}</td>
                    <td>{s.capacity}</td>
                    <td className="admin-table-actions">
                      <button className="admin-btn-edit" onClick={() => { setForm({ service_id: String(s.service_id), trainer_id: String(s.trainer_id), class_date: s.class_date, start_time: s.start_time, end_time: s.end_time, hall: s.hall, capacity: s.capacity }); setErr(''); setModal(s) }}>✏️</button>
                      <button className="admin-btn-del" onClick={() => setConfirm(s.id)}>🗑</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3 className="modal-title">{modal === 'create' ? '+ Новое занятие' : '✏️ Редактировать занятие'}</h3>
            {err && <div className="auth-error">{err}</div>}
            <form onSubmit={handleSave}>
              <div className="form-row-2">
                <div className="form-group">
                  <label className="form-label">Услуга *</label>
                  <select className="form-input" value={form.service_id} onChange={set('service_id')} required>
                    <option value="">— Выберите —</option>
                    {services.map(s => <option key={s.id} value={s.id}>{s.title}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label className="form-label">Тренер *</label>
                  <select className="form-input" value={form.trainer_id} onChange={set('trainer_id')} required>
                    <option value="">— Выберите —</option>
                    {trainers.map(t => <option key={t.id} value={t.id}>{t.full_name}</option>)}
                  </select>
                </div>
              </div>
              <div className="form-row-3">
                <div className="form-group"><label className="form-label">Дата *</label><input className="form-input" type="date" value={form.class_date} onChange={set('class_date')} required /></div>
                <div className="form-group"><label className="form-label">Начало *</label><input className="form-input" type="time" value={form.start_time} onChange={set('start_time')} required /></div>
                <div className="form-group"><label className="form-label">Конец *</label><input className="form-input" type="time" value={form.end_time} onChange={set('end_time')} required /></div>
              </div>
              <div className="form-row-2">
                <div className="form-group"><label className="form-label">Зал</label><input className="form-input" value={form.hall} onChange={set('hall')} placeholder="Зал 1" /></div>
                <div className="form-group"><label className="form-label">Вместимость</label><input className="form-input" type="number" value={form.capacity} onChange={set('capacity')} /></div>
              </div>
              <div className="modal-actions">
                <button className="btn btn-primary" type="submit" disabled={saving}>{saving ? 'Сохраняем...' : '💾 Сохранить'}</button>
                <button className="btn btn-outline" type="button" onClick={() => setModal(null)}>Отмена</button>
              </div>
            </form>
          </div>
        </div>
      )}
      {confirm && (
        <div className="modal-overlay" onClick={() => setConfirm(null)}>
          <div className="modal modal-sm" onClick={e => e.stopPropagation()}>
            <h3>Удалить занятие?</h3>
            <div className="modal-actions">
              <button className="btn btn-primary" style={{ background: '#dc2626' }} onClick={async () => { await remove(confirm); setConfirm(null) }}>🗑 Удалить</button>
              <button className="btn btn-outline" onClick={() => setConfirm(null)}>Отмена</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
