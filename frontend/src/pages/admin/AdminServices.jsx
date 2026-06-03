import { useState } from 'react'
import { useCrud } from './useCrud'

const EMPTY = { title: '', title_en: '', description: '', image_url: '', is_active: true }

export default function AdminServices() {
  const { items, loading, create, update, remove } = useCrud('/api/admin/services/')
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [err, setErr] = useState('')
  const [saving, setSaving] = useState(false)
  const [confirm, setConfirm] = useState(null)

  function set(field) { return e => setForm(p => ({ ...p, [field]: e.target.type === 'checkbox' ? e.target.checked : e.target.value })) }

  async function handleSave(e) {
    e.preventDefault(); setErr(''); setSaving(true)
    try {
      modal === 'create' ? await create(form) : await update(modal.id, form)
      setModal(null)
    } catch (e) { setErr(e.message) } finally { setSaving(false) }
  }

  return (
    <div>
      <div className="admin-page-header">
        <h2 className="admin-page-title">🏋️ Услуги</h2>
        <button className="btn btn-primary" onClick={() => { setForm(EMPTY); setErr(''); setModal('create') }}>+ Добавить</button>
      </div>
      {loading && <div className="loading"><div className="loading-spinner" /></div>}
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead><tr><th>#</th><th>Название</th><th>Англ.</th><th>Занятий</th><th>Статус</th><th>Действия</th></tr></thead>
          <tbody>
            {items.map(s => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td><strong>{s.title}</strong></td>
                <td style={{ color: '#6b7280', fontStyle: 'italic' }}>{s.title_en}</td>
                <td>{s.schedules_count}</td>
                <td><span className={`tag ${s.is_active ? 'tag-green' : 'tag-orange'}`}>{s.is_active ? 'Активна' : 'Откл.'}</span></td>
                <td className="admin-table-actions">
                  <button className="admin-btn-edit" onClick={() => { setForm({ ...s }); setErr(''); setModal(s) }}>✏️</button>
                  <button className="admin-btn-del" onClick={() => setConfirm(s.id)}>🗑</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3 className="modal-title">{modal === 'create' ? '+ Новая услуга' : '✏️ Редактировать услугу'}</h3>
            {err && <div className="auth-error">{err}</div>}
            <form onSubmit={handleSave}>
              <div className="form-row-2">
                <div className="form-group"><label className="form-label">Название *</label><input className="form-input" value={form.title} onChange={set('title')} required /></div>
                <div className="form-group"><label className="form-label">Англ. название</label><input className="form-input" value={form.title_en} onChange={set('title_en')} /></div>
              </div>
              <div className="form-group"><label className="form-label">Описание</label><textarea className="form-input" rows={2} value={form.description} onChange={set('description')} /></div>
              <div className="form-group"><label className="form-label">Ссылка на изображение</label><input className="form-input" value={form.image_url} onChange={set('image_url')} placeholder="https://..." /></div>
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
            <h3>Удалить услугу?</h3>
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
