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
  // Backend v2 devuelve strings separados por ; o ,
  // Backend v1 devolvía arrays. Normalizamos a array para visualización consistente.
  let autores = []
  if (Array.isArray(item.autores)) autores = item.autores
  else if (typeof item.autores === 'string') autores = item.autores.split(';').map(s => s.trim()).filter(Boolean)

  let etiquetas = []
  if (Array.isArray(item.etiquetas)) etiquetas = item.etiquetas
  else if (typeof item.etiquetas === 'string') etiquetas = item.etiquetas.split(',').map(s => s.trim()).filter(Boolean)

  const resumen = (item.descripcion_resumen || item.resumen || '').slice(0, 160)

  return `
    <a class="card hover:shadow-sm transition flex flex-col h-full p-4 border rounded-lg bg-white" href="./detalle.html?id=${encodeURIComponent(item.id)}">
      <h3 class="card-title text-lg font-semibold mb-2 text-gray-900">${item.titulo || ''}</h3>
      <div class="text-xs font-medium text-indigo-600 mb-1 uppercase tracking-wide">${item.institucion_fuente || item.coleccion || ''}</div>
      <p class="card-meta text-sm text-gray-600 mb-2">${autores.join('; ')}</p>
      <p class="text-sm text-gray-700 mb-3 flex-grow">${resumen}${(item.descripcion_resumen || item.resumen || '').length > 160 ? '…' : ''}</p>
      
      <div class="mb-3 flex flex-wrap gap-1">
        ${etiquetas.slice(0, 3).map(t => `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">${t}</span>`).join('')}
      </div>

      <div class="mt-auto flex items-center justify-between text-sm text-gray-500 pt-2 border-t">
        <span>${item.anio_publicacion || ''}</span>
        <span class="px-2 py-1 rounded bg-indigo-50 text-indigo-700 text-xs font-medium">${item.tipo_recurso || item.tipo_documento || ''}</span>
      </div>
    </a>
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
    $('#results-count').textContent = 'Error al buscar'
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

$('#filters-form').addEventListener('submit', (e) => {
  e.preventDefault()
  state.page = 1
  state.orden = $('#orden').value
  stateToParams()
  search()
})

$('#clear-filters').addEventListener('click', () => {
  $$('#filters-form input, #filters-form select').forEach(el => el.value = '')
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

paramsToState()
stateToParams()
search()
