import { useState } from 'react'
import { useCrud } from './useCrud'

const EMPTY = { title: '', title_en: '', description: '', price: '', duration_days: '', visits_limit: '', is_active: true }

export default function AdminMemberships() {
  const { items, loading, create, update, remove } = useCrud('/api/admin/memberships/')
  const [modal, setModal] = useState(null) // null | 'create' | item
  const [form, setForm] = useState(EMPTY)
  const [err, setErr] = useState('')
  const [saving, setSaving] = useState(false)
  const [confirm, setConfirm] = useState(null)

  function openCreate() { setForm(EMPTY); setErr(''); setModal('create') }
  function openEdit(item) { setForm({ ...item, price: String(item.price), visits_limit: item.visits_limit || '' }); setErr(''); setModal(item) }

  function set(field) { return e => setForm(p => ({ ...p, [field]: e.target.type === 'checkbox' ? e.target.checked : e.target.value })) }

  async function handleSave(e) {
    e.preventDefault(); setErr(''); setSaving(true)
    try {
      if (modal === 'create') await create(form)
      else await update(modal.id, form)
      setModal(null)
    } catch (e) { setErr(e.message) } finally { setSaving(false) }
  }

  async function handleDelete(id) {
    try { await remove(id); setConfirm(null) } catch (e) { alert(e.message) }
  }

  return (
    <div>
      <div className="admin-page-header">
        <h2 className="admin-page-title">🎫 Абонементы</h2>
        <button className="btn btn-primary" onClick={openCreate}>+ Добавить</button>
      </div>

      {loading && <div className="loading"><div className="loading-spinner" /></div>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr><th>#</th><th>Название</th><th>Англ.</th><th>Цена</th><th>Дней</th><th>Визиты</th><th>Статус</th><th>Действия</th></tr>
          </thead>
          <tbody>
            {items.map(m => (
              <tr key={m.id}>
                <td>{m.id}</td>
                <td><strong>{m.title}</strong></td>
                <td style={{ color: '#6b7280', fontStyle: 'italic' }}>{m.title_en}</td>
                <td>{Number(m.price).toLocaleString('ru-RU')} ₽</td>
                <td>{m.duration_days}</td>
                <td>{m.visits_limit || '∞'}</td>
                <td><span className={`tag ${m.is_active ? 'tag-green' : 'tag-orange'}`}>{m.is_active ? 'Активен' : 'Откл.'}</span></td>
                <td className="admin-table-actions">
                  <button className="admin-btn-edit" onClick={() => openEdit(m)}>✏️</button>
                  <button className="admin-btn-del" onClick={() => setConfirm(m.id)}>🗑</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3 className="modal-title">{modal === 'create' ? '+ Новый абонемент' : '✏️ Редактировать'}</h3>
            {err && <div className="auth-error">{err}</div>}
            <form onSubmit={handleSave}>
              <div className="form-row-2">
                <div className="form-group"><label className="form-label">Название *</label><input className="form-input" value={form.title} onChange={set('title')} required /></div>
                <div className="form-group"><label className="form-label">Англ. название</label><input className="form-input" value={form.title_en} onChange={set('title_en')} /></div>
              </div>
              <div className="form-group"><label className="form-label">Описание</label><textarea className="form-input" rows={2} value={form.description} onChange={set('description')} /></div>
              <div className="form-row-3">
                <div className="form-group"><label className="form-label">Цена (₽) *</label><input className="form-input" type="number" value={form.price} onChange={set('price')} required /></div>
                <div className="form-group"><label className="form-label">Срок (дней) *</label><input className="form-input" type="number" value={form.duration_days} onChange={set('duration_days')} required /></div>
                <div className="form-group"><label className="form-label">Лимит визитов</label><input className="form-input" type="number" value={form.visits_limit} onChange={set('visits_limit')} placeholder="∞" /></div>
              </div>
              <label className="form-checkbox"><input type="checkbox" checked={form.is_active} onChange={set('is_active')} /> Активен</label>
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
            <h3>Удалить абонемент?</h3>
            <p style={{ color: '#6b7280', margin: '12px 0' }}>Это действие нельзя отменить.</p>
            <div className="modal-actions">
              <button className="btn btn-primary" style={{ background: '#dc2626' }} onClick={() => handleDelete(confirm)}>🗑 Удалить</button>
              <button className="btn btn-outline" onClick={() => setConfirm(null)}>Отмена</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
