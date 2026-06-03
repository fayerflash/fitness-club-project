import { useState, useRef } from 'react'
import { useCrud } from './useCrud'

const EMPTY = { full_name: '', full_name_en: '', specialization: '', experience_years: 0, bio: '', is_active: true }

export default function AdminTrainers() {
  const { items, loading, create, update, remove } = useCrud('/api/admin/trainers/')
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(EMPTY)
  const [photoFile, setPhotoFile] = useState(null)
  const [cvFile, setCvFile] = useState(null)
  const [photoPreview, setPhotoPreview] = useState('')
  const [err, setErr] = useState('')
  const [saving, setSaving] = useState(false)
  const [confirm, setConfirm] = useState(null)
  const photoRef = useRef()
  const cvRef = useRef()

  function openCreate() {
    setForm(EMPTY); setPhotoFile(null); setCvFile(null); setPhotoPreview(''); setErr(''); setModal('create')
  }
  function openEdit(item) {
    setForm({
      full_name: item.full_name,
      full_name_en: item.full_name_en || '',
      specialization: item.specialization || '',
      experience_years: item.experience_years,
      bio: item.bio || '',
      is_active: item.is_active,
    })
    setPhotoFile(null); setCvFile(null)
    setPhotoPreview(item.photo_file_url || item.photo_url || '')
    setErr(''); setModal(item)
  }
  function set(field) {
    return e => setForm(p => ({ ...p, [field]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))
  }
  function handlePhotoChange(e) {
    const f = e.target.files[0]
    if (!f) return
    setPhotoFile(f)
    setPhotoPreview(URL.createObjectURL(f))
  }
  function handleCvChange(e) {
    const f = e.target.files[0]
    if (!f) return
    if (!f.name.endsWith('.pdf')) { setErr('Резюме должно быть PDF файлом'); return }
    setCvFile(f); setErr('')
  }

  async function handleSave(e) {
    e.preventDefault(); setErr(''); setSaving(true)
    try {
      const files = {}
      if (photoFile) files.photo = photoFile
      if (cvFile) files.cv_file = cvFile
      if (modal === 'create') await create(form, files)
      else await update(modal.id, form, files)
      setModal(null)
    } catch (e) { setErr(e.message) } finally { setSaving(false) }
  }

  return (
    <div>
      <div className="admin-page-header">
        <h2 className="admin-page-title">👨‍🏫 Тренеры</h2>
        <button className="btn btn-primary" onClick={openCreate}>+ Добавить</button>
      </div>

      {loading && <div className="loading"><div className="loading-spinner" /></div>}

      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead>
            <tr><th>#</th><th>Фото</th><th>ФИО</th><th>Англ. имя</th><th>Специализация</th><th>Опыт</th><th>Резюме</th><th>Статус</th><th>Действия</th></tr>
          </thead>
          <tbody>
            {items.map(t => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td>
                  {(t.photo_file_url || t.photo_url)
                    ? <img src={t.photo_file_url || t.photo_url} style={{ width: 40, height: 40, borderRadius: '50%', objectFit: 'cover' }} alt="" />
                    : <div style={{ width: 40, height: 40, borderRadius: '50%', background: '#e8f4ff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem' }}>👤</div>
                  }
                </td>
                <td><strong>{t.full_name}</strong></td>
                <td style={{ color: '#6b7280', fontStyle: 'italic' }}>{t.full_name_en}</td>
                <td>{t.specialization}</td>
                <td>{t.experience_years} лет</td>
                <td>
                  {t.cv_url
                    ? <a href={t.cv_url} target="_blank" rel="noreferrer"
                        style={{ color: '#e85d04', fontWeight: 600, fontSize: '0.85rem' }}>📄 PDF</a>
                    : <span style={{ color: '#9ca3af', fontSize: '0.8rem' }}>—</span>
                  }
                </td>
                <td><span className={`tag ${t.is_active ? 'tag-green' : 'tag-orange'}`}>{t.is_active ? 'Активен' : 'Откл.'}</span></td>
                <td className="admin-table-actions">
                  <button className="admin-btn-edit" onClick={() => openEdit(t)}>✏️</button>
                  <button className="admin-btn-del" onClick={() => setConfirm(t.id)}>🗑</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {modal && (
        <div className="modal-overlay" onClick={() => setModal(null)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <h3 className="modal-title">{modal === 'create' ? '+ Новый тренер' : '✏️ Редактировать тренера'}</h3>
            {err && <div className="auth-error">{err}</div>}
            <form onSubmit={handleSave}>
              <div className="form-row-2">
                <div className="form-group"><label className="form-label">ФИО *</label><input className="form-input" value={form.full_name} onChange={set('full_name')} required /></div>
                <div className="form-group"><label className="form-label">ФИО (англ.)</label><input className="form-input" value={form.full_name_en} onChange={set('full_name_en')} /></div>
              </div>
              <div className="form-row-2">
                <div className="form-group"><label className="form-label">Специализация</label><input className="form-input" value={form.specialization} onChange={set('specialization')} /></div>
                <div className="form-group"><label className="form-label">Опыт (лет)</label><input className="form-input" type="number" min="0" max="50" value={form.experience_years} onChange={set('experience_years')} /></div>
              </div>
              <div className="form-group"><label className="form-label">Биография</label><textarea className="form-input" rows={3} value={form.bio} onChange={set('bio')} /></div>

              {/* Фото — только с устройства */}
              <div className="form-group">
                <label className="form-label">Фото тренера</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  {photoPreview && (
                    <img src={photoPreview} style={{ width: 60, height: 60, borderRadius: '50%', objectFit: 'cover', border: '2px solid #e85d04' }} alt="" />
                  )}
                  <label className="file-upload-btn">
                    📷 {photoFile ? photoFile.name : (modal !== 'create' && (modal.photo_file_url || modal.photo_url) ? 'Изменить фото' : 'Загрузить фото')}
                    <input ref={photoRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={handlePhotoChange} />
                  </label>
                  {photoFile && <span style={{ fontSize: '0.8rem', color: '#6b7280' }}>{(photoFile.size / 1024).toFixed(0)} KB</span>}
                </div>
              </div>

              {/* Резюме PDF — только с устройства */}
              <div className="form-group">
                <label className="form-label">Резюме (PDF)</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  {modal !== 'create' && modal.cv_url && !cvFile && (
                    <a href={modal.cv_url} target="_blank" rel="noreferrer"
                       style={{ color: '#e85d04', fontSize: '0.85rem', fontWeight: 600 }}>
                      📄 Текущий PDF
                    </a>
                  )}
                  <label className="file-upload-btn">
                    📎 {cvFile ? cvFile.name : 'Загрузить PDF'}
                    <input ref={cvRef} type="file" accept=".pdf" style={{ display: 'none' }} onChange={handleCvChange} />
                  </label>
                  {cvFile && <span style={{ fontSize: '0.8rem', color: '#6b7280' }}>{(cvFile.size / 1024).toFixed(0)} KB</span>}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: 4 }}>Только .pdf</div>
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
            <h3>Удалить тренера?</h3>
            <p style={{ color: '#6b7280', margin: '12px 0' }}>Также будут удалены все занятия этого тренера.</p>
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