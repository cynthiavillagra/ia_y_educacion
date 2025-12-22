const $ = (s, d = document) => d.querySelector(s)
const $$ = (s, d = document) => Array.from(d.querySelectorAll(s))

const state = {
  page: 1,
  perPage: 20,
  total: 0,
  orden: 'relevancia',
}

function paramsToState() {
  const url = new URL(location.href)
  const p = url.searchParams
  $('#q').value = p.get('q') || ''
  $('#autor').value = p.get('autor') || ''
  $('#anio').value = p.get('anio') || ''
  $('#fuente').value = p.get('fuente') || ''
  $('#tipo').value = p.get('tipo') || ''
  state.page = parseInt(p.get('page') || '1', 10)
  state.orden = p.get('orden') || 'relevancia'
  $('#orden').value = state.orden
}

function stateToParams() {
  const url = new URL(location.href)
  const p = url.searchParams
  p.set('page', String(state.page))
  // Mapear orden frontend -> backend v2
  // 'fecha_ingreso' ahora es 'fecha_incorporacion_repo' en DB, pero el handler puede manejar alias o usamos el nombre nuevo en el select.
  // El handler ya usa el valor directamente, así que aseguramos que el HTML tenga los values correctos o el handler haga el map.
  // Por ahora mantenemos los valores del select HTML ('relevancia', 'anio_desc', 'fecha_ingreso_desc')
  // y dejamos que el backend decida si necesita adaptación.
  p.set('orden', state.orden)
  const map = { q: '#q', autor: '#autor', anio: '#anio', fuente: '#fuente', tipo: '#tipo' }
  Object.entries(map).forEach(([k, sel]) => {
    const v = $(sel).value.trim()
    if (v) p.set(k, v); else p.delete(k)
  })
  history.replaceState(null, '', url.toString())
}

function renderPagination(total, page, perPage) {
  const totalPages = Math.max(1, Math.ceil(total / perPage))
  const c = $('#pagination')
  c.innerHTML = ''
  const btn = (label, target, disabled = false) => {
    const a = document.createElement('button')
    a.type = 'button'
    a.textContent = label
    a.className = `px-3 py-1.5 rounded-md text-sm ${disabled ? 'bg-gray-100 text-gray-400' : 'bg-white border hover:bg-gray-50'}`
    if (!disabled) a.addEventListener('click', () => { state.page = target; stateToParams(); search() })
    return a
  }
  c.append(btn('Anterior', Math.max(1, page - 1), page <= 1))
  const windowSize = 5
  const start = Math.max(1, page - Math.floor(windowSize / 2))
  const end = Math.min(totalPages, start + windowSize - 1)
  for (let i = start; i <= end; i++) {
    const b = btn(String(i), i, false)
    if (i === page) b.className = 'px-3 py-1.5 rounded-md text-sm bg-indigo-600 text-white'
    c.append(b)
  }
  c.append(btn('Siguiente', Math.min(totalPages, page + 1), page >= totalPages))
}

function cardTemplate(item) {
  let autores = []
  if (Array.isArray(item.autores)) autores = item.autores
  else if (typeof item.autores === 'string') autores = item.autores.split(';').map(s => s.trim()).filter(Boolean)

  let etiquetas = []
  if (Array.isArray(item.etiquetas)) etiquetas = item.etiquetas
  else if (typeof item.etiquetas === 'string') etiquetas = item.etiquetas.split(',').map(s => s.trim()).filter(Boolean)

  const resumen = (item.descripcion_resumen || item.resumen || '').slice(0, 240)
  const isClipped = (item.descripcion_resumen || item.resumen || '').length > 240

  const typeMap = {
    'paper_academico': '📄', 'libro': '📘', 'informe': '📊', 'video': '🎥', 'default': '📎'
  }
  const icon = typeMap[item.tipo_recurso] || typeMap.default

  return `
    <article class="article-card">
      <div class="article-icon">${icon}</div>
      <div class="article-content">
        <div class="article-header">
          <a class="article-title" href="./detalle.html?id=${encodeURIComponent(item.id)}">
            ${item.titulo || 'Sin Título'}
          </a>
          <span class="article-type">
            ${item.tipo_recurso ? item.tipo_recurso.replace('_', ' ') : 'Recurso'}
          </span>
        </div>

        <div class="article-meta">
          ${autores.join('; ') || 'Autor desconocido'} 
          <span class="meta-sep">•</span> 
          <span>${item.anio_publicacion || 's.f.'}</span>
          <span class="meta-sep">•</span>
          <span class="meta-source">${item.institucion_fuente || item.coleccion || 'Fuente desconocida'}</span>
        </div>

        <p class="article-abstract">
          ${resumen}${isClipped ? '...' : ''}
        </p>

        <div class="article-tags">
          ${etiquetas.slice(0, 4).map(t => `<span class="tag">${t}</span>`).join('')}
        </div>
      </div>
    </article>
  `
}

async function search() {
  $('#results').innerHTML = ''
  $('#results-count').textContent = 'Buscando…'
  const params = new URLSearchParams()
  const q = $('#q').value.trim(); if (q) params.set('q', q)
  const autor = $('#autor').value.trim(); if (autor) params.set('autor', autor)
  const anio = $('#anio').value.trim(); if (anio) params.set('anio', anio)
  const fuente = $('#fuente').value.trim(); if (fuente) params.set('fuente', fuente)
  const tipo = $('#tipo').value.trim(); if (tipo) params.set('tipo', tipo)
  params.set('page', String(state.page))
  params.set('per_page', String(state.perPage))
  params.set('orden', state.orden)

  const res = await fetch(`/api/search?${params.toString()}`)
  if (!res.ok) {
    let msg = 'Error al buscar'
    try {
      const errData = await res.json()
      msg = errData.error || errData.detail || msg
    } catch (e) {
      try { msg = await res.text() } catch (e2) { }
    }
    console.error('API Error:', msg)
    $('#results-count').innerHTML = `<span class="text-red-600">Error: ${msg.slice(0, 100)}</span>`
    return
  }
  const data = await res.json()
  // Soporte para estructura { total, items } o lista directa (legacy)
  const items = Array.isArray(data) ? data : (data.items || data.resultados || [])
  state.total = typeof data.total === 'number' ? data.total : items.length
  $('#results-count').textContent = `${state.total} resultados`
  $('#results').innerHTML = items.map(cardTemplate).join('')
  renderPagination(state.total, state.page, state.perPage)
}

// Bind events
$('#filters-form').addEventListener('submit', (e) => {
  e.preventDefault()
  state.page = 1
  state.orden = $('#orden').value
  stateToParams()
  search()
})

$('#clear-filters').addEventListener('click', () => {
  $$('#filters-form input, #filters-form select').forEach(el => el.value = '')
  // Also clear hero search if it exists
  const heroQ = document.getElementById('q')
  if (heroQ) heroQ.value = ''

  state.page = 1
  state.orden = 'relevancia'
  stateToParams()
  search()
})

$('#orden').addEventListener('change', () => {
  state.page = 1
  state.orden = $('#orden').value
  stateToParams()
  search()
})

// Expose to window for inline scripts
window.state = state
window.search = search
window.stateToParams = stateToParams

paramsToState()
stateToParams()
search()
