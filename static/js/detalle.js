/**
 * detalle.js
 * Carga y renderiza la ficha completa de un recurso.
 * Compatible con esquema Metadatos V2.
 */

const $ = (selector) => document.querySelector(selector)

/**
 * Genera la URL del badge de licencia CC.
 */
function ccBadgeFrom(licencia) {
  const map = {
    'CC BY 4.0': 'by',
    'CC BY-SA 4.0': 'by-sa',
    'CC BY-ND 4.0': 'by-nd',
    'CC BY-NC 4.0': 'by-nc',
    'CC BY-NC-SA 4.0': 'by-nc-sa',
    'CC BY-NC-ND 4.0': 'by-nc-nd',
    'CC0 1.0': 'zero'
  }
  const slug = map[licencia] || 'by'
  return `https://licensebuttons.net/l/${slug}/4.0/88x31.png`
}

/**
 * Formatea el tipo de recurso para mostrar.
 */
function formatTipo(tipo) {
  if (!tipo) return '—'
  return tipo.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

/**
 * Carga y renderiza el detalle del recurso.
 */
async function loadDetalle() {
  const url = new URL(location.href)
  const id = url.searchParams.get('id')

  if (!id) {
    $('#titulo').textContent = 'Error: No se especificó un ID de recurso'
    return
  }

  try {
    const res = await fetch(`/api/recurso_detalle?id=${encodeURIComponent(id)}`)

    if (!res.ok) {
      const err = await res.json().catch(() => ({ error: 'Error desconocido' }))
      $('#titulo').textContent = `Error: ${err.error || 'Recurso no encontrado'}`
      return
    }

    const r = await res.json()

    // Título
    const titulo = r.titulo || r.titulo_original || 'Sin título'
    document.title = `${titulo} | Repositorio IA y Educación`
    $('#breadcrumb-title').textContent = titulo.length > 60 ? titulo.slice(0, 60) + '...' : titulo
    $('#titulo').textContent = titulo

    // Tipo Badge
    const tipoBadge = $('#detail-type-badge')
    if (tipoBadge && r.tipo_recurso) {
      tipoBadge.textContent = formatTipo(r.tipo_recurso)
    }

    // Subtítulo
    $('#anio').textContent = r.anio_publicacion || '—'
    $('#coleccion').textContent = r.institucion_fuente || '—'

    // Resumen
    const resumen = r.descripcion_resumen || r.resumen
    if (resumen) {
      $('#resumen').textContent = resumen
      $('#abstract-section').style.display = 'block'
    }

    // Autores
    let autores = []
    if (Array.isArray(r.autores)) {
      autores = r.autores
    } else if (typeof r.autores === 'string' && r.autores.trim()) {
      autores = r.autores.split(';').map(s => s.trim()).filter(Boolean)
    }

    const autoresEl = $('#autores')
    if (autores.length > 0) {
      autoresEl.innerHTML = autores.map(a => `<li>${a}</li>`).join('')
    } else {
      $('#row-autores').style.display = 'none'
    }

    // Metadata Table
    setMetadata('institucion_fuente', r.institucion_fuente)
    setMetadata('tipo', formatTipo(r.tipo_recurso))
    setMetadata('anio_publicacion', r.anio_publicacion)
    setMetadata('idioma', r.idioma)
    setMetadata('pais_origen', r.pais_origen)
    setMetadata('formato', r.formato)
    setMetadata('tipo_acceso', r.tipo_acceso)

    // DOI/ISBN
    const codigo = r.doi || r.isbn_issn
    if (codigo) {
      $('#codigo_documento').textContent = codigo
    } else {
      $('#row-doi').style.display = 'none'
    }

    // Fecha Ingreso
    const fecha = r.fecha_incorporacion_repo || r.fecha_ingreso
    if (fecha) {
      $('#fecha_ingreso').textContent = new Date(fecha).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    // Etiquetas
    let tags = []
    if (typeof r.palabras_clave === 'string' && r.palabras_clave.trim()) {
      tags = r.palabras_clave.split(',').map(s => s.trim()).filter(Boolean)
    } else if (Array.isArray(r.palabras_clave)) {
      tags = r.palabras_clave
    } else if (typeof r.etiquetas === 'string') {
      tags = r.etiquetas.split(',').map(s => s.trim()).filter(Boolean)
    }

    const etiquetasEl = $('#etiquetas')
    if (tags.length > 0) {
      etiquetasEl.innerHTML = tags.map(t => `<span class="tag">${t}</span>`).join('')
    } else {
      $('#row-etiquetas').style.display = 'none'
    }

    // Licencia
    const licencia = r.licencia || r.licencia_cc
    if (licencia) {
      $('#licencia_badge').src = ccBadgeFrom(licencia)
      $('#licencia_texto').textContent = licencia
    } else {
      $('#license-section').style.display = 'none'
    }

    // Botón de Acceso
    const btn = $('#btn_acceso')
    const isHosted = r.archivo_local === true
    const downloadUrl = r.url_archivo_local || r.url_pdf_directo
    const viewUrl = r.url_fuente_original

    if (isHosted && downloadUrl) {
      btn.innerHTML = '📥 Descargar Documento'
      btn.href = downloadUrl
    } else if (viewUrl) {
      btn.innerHTML = '🔗 Acceder al Recurso Original'
      btn.href = viewUrl
    } else {
      btn.innerHTML = '❌ Sin enlace disponible'
      btn.classList.remove('btn-primary')
      btn.classList.add('btn-secondary')
      btn.removeAttribute('href')
      btn.style.cursor = 'not-allowed'
    }

    // Admin Section
    const token = localStorage.getItem('sb_access_token')
    if (token) {
      $('#edit-container').classList.remove('hidden')

      const btnEdit = $('#btn-editar')
      if (btnEdit) {
        btnEdit.href = `/admin/edicion.html?id=${id}`
      }

      const btnDelete = $('#btn-eliminar')
      if (btnDelete) {
        btnDelete.addEventListener('click', async () => {
          const confirmMsg = `¿Eliminar este recurso?\n\n"${titulo}"\n\nEsta acción no se puede deshacer.`
          if (!confirm(confirmMsg)) return

          try {
            const delRes = await fetch(`/api/admin/delete?id=${encodeURIComponent(id)}`, {
              method: 'DELETE',
              headers: { 'Authorization': `Bearer ${token}` }
            })

            if (!delRes.ok) {
              const err = await delRes.json()
              alert('Error: ' + (err.error || 'No se pudo eliminar'))
              return
            }

            alert('Recurso eliminado')
            location.href = '/index.html'
          } catch (e) {
            alert('Error: ' + e.message)
          }
        })
      }

      const btnLogout = $('#btn-logout')
      if (btnLogout) {
        btnLogout.classList.remove('hidden')
        btnLogout.addEventListener('click', () => {
          localStorage.removeItem('sb_access_token')
          location.reload()
        })
      }
    }

  } catch (err) {
    console.error('Error loading detail:', err)
    $('#titulo').textContent = 'Error al cargar el recurso'
  }
}

/**
 * Helper para establecer metadatos en la tabla.
 */
function setMetadata(id, value) {
  const el = $('#' + id)
  if (!el) return

  if (value && value !== '—') {
    el.textContent = value
  } else {
    // Ocultar la fila si no hay dato
    const row = el.closest('tr')
    if (row) row.style.display = 'none'
  }
}

// Iniciar
document.addEventListener('DOMContentLoaded', loadDetalle)
