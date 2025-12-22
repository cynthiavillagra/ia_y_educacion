const $ = (s, d = document) => d.querySelector(s)

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

async function loadDetalle() {
  const url = new URL(location.href)
  const id = url.searchParams.get('id')
  if (!id) return
  const res = await fetch(`/api/recurso_detalle?id=${encodeURIComponent(id)}`)
  if (!res.ok) return
  const r = await res.json()

  const titulo = r.titulo || r.titulo_original || 'Sin título'
  $('#breadcrumb-title').textContent = titulo
  $('#titulo').textContent = titulo
  $('#anio').textContent = r.anio_publicacion || r.año_publicacion || ''
  $('#tipo').textContent = r.tipo_recurso || r.tipo_documento || ''
  $('#coleccion').textContent = r.institucion_fuente || r.coleccion || ''

  let autores = []
  if (Array.isArray(r.autores)) autores = r.autores
  else if (typeof r.autores === 'string') autores = r.autores.split(';').map(s => s.trim()).filter(Boolean)

  if (autores.length > 0) {
    $('#autores').innerHTML = autores.map(a => `<li>${a}</li>`).join('')
    $('#autores').parentElement.style.display = 'block'
  } else {
    $('#autores').parentElement.style.display = 'none'
  }

  const resumen = r.descripcion_resumen || r.resumen
  if (resumen) {
    $('#resumen').textContent = resumen
    $('#resumen').parentElement.style.display = 'block'
  } else {
    $('#resumen').parentElement.style.display = 'none'
  }

  let tags = []
  if (Array.isArray(r.etiquetas) || Array.isArray(r.palabras_clave)) tags = r.etiquetas || r.palabras_clave
  else {
    const rawTags = r.palabras_clave || r.etiquetas
    if (typeof rawTags === 'string') tags = rawTags.split(',').map(s => s.trim()).filter(Boolean)
  }

  if (tags.length > 0) {
    $('#etiquetas').innerHTML = tags.map(t => `<span class="badge badge-gray">${t}</span>`).join('')
    $('#etiquetas').parentElement.style.display = 'block'
  } else {
    $('#etiquetas').parentElement.style.display = 'none'
  }

  $('#licencia_badge').src = ccBadgeFrom(r.licencia_cc)
  $('#licencia_texto').textContent = r.licencia_cc || ''

  const btn = $('#btn_acceso')
  // v2 usa archivo_local (bool) y url_fuente_original / url_archivo_local
  // v1 usaba estado_alojamiento === 'ALOJADO'
  const isHosted = r.archivo_local === true || r.estado_alojamiento === 'ALOJADO'
  const downloadUrl = r.url_archivo_local || r.url_directa_pdf || r.url_descarga
  const viewUrl = r.url_fuente_original || r.url_descarga

  if (isHosted && downloadUrl) {
    btn.textContent = '📥 Descargar documento'
    btn.href = downloadUrl
    btn.title = 'Descargar el archivo PDF'
  } else {
    btn.textContent = '🔗 Ver documento original'
    btn.href = viewUrl || '#'
    btn.title = viewUrl || 'Ver en sitio original'

    // Add URL below the button
    const urlDisplay = document.createElement('a')
    urlDisplay.href = viewUrl || '#'
    urlDisplay.target = '_blank'
    urlDisplay.rel = 'noopener'
    urlDisplay.textContent = viewUrl || ''
    urlDisplay.className = 'text-xs text-gray-500 hover:text-indigo-600 break-all block mt-2'
    btn.parentElement.appendChild(urlDisplay)
  }

  const codigo = r.doi || r.isbn_issn || r.codigo_documento
  if (codigo) {
    $('#codigo_documento').textContent = codigo
    $('#codigo_documento').parentElement.style.display = 'block'
  } else {
    $('#codigo_documento').parentElement.style.display = 'none'
  }

  const fecha = r.fecha_incorporacion_repo || r.fecha_ingreso
  if (fecha) {
    $('#fecha_ingreso').textContent = new Date(fecha).toLocaleDateString()
  }

  // Check admin auth
  const token = localStorage.getItem('sb_access_token')
  if (token) {
    const editContainer = $('#edit-container')
    if (editContainer) {
      editContainer.classList.remove('hidden')
    }

    const btnEdit = $('#btn-editar')
    if (btnEdit) {
      btnEdit.href = `/admin/edicion.html?id=${id}`
    }

    const btnDelete = $('#btn-eliminar')
    if (btnDelete) {
      btnDelete.addEventListener('click', async () => {
        const confirmMessage = `¿Estás segura de que deseas eliminar este recurso?\n\nTítulo: ${r.titulo}\n\nEsta acción no se puede deshacer.`
        if (!confirm(confirmMessage)) return

        try {
          const res = await fetch(`/api/admin/delete?id=${encodeURIComponent(id)}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })

          if (!res.ok) {
            const err = await res.json()
            alert('Error al eliminar: ' + (err.error || 'Desconocido'))
            return
          }

          alert('Recurso eliminado correctamente')
          location.href = '/index.html'
        } catch (e) {
          alert('Error al eliminar el recurso: ' + e.message)
        }
      })
    }

    const btnLogout = $('#btn-logout')
    if (btnLogout) {
      btnLogout.classList.remove('hidden')
      btnLogout.addEventListener('click', async () => {
        // We can try to sign out from supabase if we had the client, but clearing token is enough for UI
        localStorage.removeItem('sb_access_token')
        location.reload()
      })
    }
  }
}

loadDetalle()
