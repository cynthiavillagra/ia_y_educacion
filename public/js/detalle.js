const $ = (s, d=document) => d.querySelector(s)

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

  $('#breadcrumb-title').textContent = r.titulo || 'Detalle'
  $('#titulo').textContent = r.titulo || ''
  $('#anio').textContent = r.año_publicacion || ''
  $('#tipo').textContent = r.tipo_documento || ''
  $('#coleccion').textContent = r.coleccion || ''

  const autores = r.autores || []
  $('#autores').innerHTML = autores.map(a => `<li>${a}</li>`).join('')

  $('#resumen').textContent = r.resumen || ''

  const tags = r.etiquetas || []
  $('#etiquetas').innerHTML = tags.map(t => `<span class="badge badge-gray">${t}</span>`).join('')

  $('#licencia_badge').src = ccBadgeFrom(r.licencia_cc)
  $('#licencia_texto').textContent = r.licencia_cc || ''

  const btn = $('#btn_acceso')
  if (r.estado_alojamiento === 'ALOJADO') {
    btn.textContent = 'Descargar'
    btn.href = r.url_descarga
  } else {
    btn.textContent = 'Ir al sitio original'
    btn.href = r.url_descarga
  }

  if (r.codigo_documento) $('#codigo_documento').textContent = r.codigo_documento
  if (r.fecha_ingreso) $('#fecha_ingreso').textContent = new Date(r.fecha_ingreso).toLocaleString()
}

loadDetalle()
