import { useState, useEffect } from 'react'
import { useCrud } from './useCrud'

const API = ''

const today = new Date().toISOString().split('T')[0]
const EMPTY = { title: '', description: '', discount_percent: '', start_date: today, end_date: '', is_active: true, membership_ids: [] }

export default function AdminPromotions() {
  const { items, loading, create, update, remove } = useCrud('/api/admin/promotions/')
  const [allMemberships, setAllMemberships] = useState([])
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [imageFile, setImageFile] = useState(null)
  const [imagePreview, setImagePreview] = useState('')
  const [err, setErr] = useState('')
  const [saving, setSaving] = useState(false)
  const [confirm, setConfirm] = useState(null)

  useEffect(() => {
    fetch(`${API}/api/memberships/?limit=50`, { credentials: 'include' })
      .then(r => r.json()).then(d => setAllMemberships(d.results || []))
  }, [])

  function set(field) {
    return e => setForm(p => ({ ...p, [field]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))
  }
  function toggleMembership(id) {
    setForm(p => ({
      ...p,
      membership_ids: p.membership_ids.includes(id)
        ? p.membership_ids.filter(x => x !== id)
        : [...p.membership_ids, id]
    }))
  }
  function handleImageChange(e) {
    const f = e.target.files[0]
    if (!f) return
    setImageFile(f)
    setImagePreview(URL.createObjectURL(f))
  }

  async function handleSave(e) {
    e.preventDefault(); setErr(''); setSaving(true)
    try {
      const files = {}
      if (imageFile) files.image = imageFile
      if (modal === 'create') await create(form, files)
      else await update(modal.id, form, files)
      setModal(null)
    } catch (e) { setErr(e.message) } finally { setSaving(false) }
  }

  const STATUS_COLOR = { Активна: 'tag-green', 'Скоро начнется': 'tag-blue', Завершена: 'tag-orange' }

  return (
    <div>
      <div className="admin-page-header">
        <h2 className="admin-page-title">🎁 Акции</h2>
        <button className="btn btn-primary" onClick={() => { setForm(EMPTY); setImageFile(null); setImagePreview(''); setErr(''); setModal('create') }}>+ Добавить</button>
      </div>
      {loading && <div className="loading"><div className="loading-spinner" /></div>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead><tr><th>#</th><th>Изображение</th><th>Название</th><th>Скидка</th><th>Начало</th><th>Конец</th><th>Статус</th><th>Абонементы</th><th>Действия</th></tr></thead>
          <tbody>
            {items.map(p => (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>
                  {p.image_url
                    ? <img src={p.image_url}
                           style={{ width: 48, height: 36, objectFit: 'cover', borderRadius: 6 }} alt="" />
                    : <div style={{ width: 48, height: 36, background: '#f0f0f0', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🎁</div>
                  }
                </td>
                <td><strong>{p.title}</strong></td>
                <td style={{ fontWeight: 800, color: '#e85d04' }}>−{p.discount_percent}%</td>
                <td>{p.start_date}</td>
                <td>{p.end_date}</td>
                <td><span className={`tag ${STATUS_COLOR[p.status_display] || 'tag-blue'}`}>{p.status_display}</span></td>
                <td style={{ fontSize: '0.8rem', color: '#6b7280' }}>{p.membership_ids?.length || 0} шт.</td>
                <td className="admin-table-actions">
                  <button className="admin-btn-edit" onClick={() => {
                    setForm({ ...p, discount_percent: String(p.discount_percent), membership_ids: p.membership_ids || [] })
                    setImageFile(null)
                    setImagePreview(p.image_url || '')
                    setErr(''); setModal(p)
                  }}>✏️</button>
                  <button className="admin-btn-del" onClick={() => setConfirm(p.id)}>🗑</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3 className="modal-title">{modal === 'create' ? '+ Новая акция' : '✏️ Редактировать акцию'}</h3>
            {err && <div className="auth-error">{err}</div>}
            <form onSubmit={handleSave}>
              <div className="form-row-2">
                <div className="form-group"><label className="form-label">Название *</label><input className="form-input" value={form.title} onChange={set('title')} required /></div>
                <div className="form-group"><label className="form-label">Скидка (%) *</label><input className="form-input" type="number" min="0" max="100" value={form.discount_percent} onChange={set('discount_percent')} required /></div>
              </div>
              <div className="form-group"><label className="form-label">Описание</label><textarea className="form-input" rows={2} value={form.description} onChange={set('description')} /></div>
              <div className="form-row-2">
                <div className="form-group"><label className="form-label">Дата начала *</label><input className="form-input" type="date" value={form.start_date} onChange={set('start_date')} required /></div>
                <div className="form-group"><label className="form-label">Дата окончания *</label><input className="form-input" type="date" value={form.end_date} onChange={set('end_date')} required /></div>
              </div>

              {/* Изображение */}
              <div className="form-group">
                <label className="form-label">Изображение акции</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  {imagePreview && <img src={imagePreview} style={{ width: 80, height: 56, objectFit: 'cover', borderRadius: 8, border: '2px solid #e85d04' }} alt="" />}
                  <label className="file-upload-btn">
                    🖼 {imageFile ? imageFile.name : 'Выбрать изображение'}
                    <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleImageChange} />
                  </label>
                </div>
              </div>

              {/* Привязка абонементов */}
              <div className="form-group">
                <label className="form-label">Абонементы по акции</label>
                <div className="membership-checklist">
                  {allMemberships.map(m => (
                    <label key={m.id} className="membership-check-item">
                      <input
                        type="checkbox"
                        checked={form.membership_ids.includes(m.id)}
                        onChange={() => toggleMembership(m.id)}
                      />
                      <span>{m.title} — {Number(m.price).toLocaleString('ru-RU')} ₽</span>
                    </label>
                  ))}
                </div>
              </div>

              <label className="form-checkbox"><input type="checkbox" checked={form.is_active} onChange={set('is_active')} /> Активна</label>
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
            <h3>Удалить акцию?</h3>
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
