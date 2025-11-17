const $ = (s, d=document) => d.querySelector(s)
const $$ = (s, d=document) => Array.from(d.querySelectorAll(s))

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
  $('#coleccion').value = p.get('coleccion') || ''
  $('#tipo').value = p.get('tipo') || ''
  state.page = parseInt(p.get('page') || '1', 10)
  state.orden = p.get('orden') || 'relevancia'
  $('#orden').value = state.orden
}

function stateToParams() {
  const url = new URL(location.href)
  const p = url.searchParams
  p.set('page', String(state.page))
  p.set('orden', state.orden)
  const map = { q:'#q', autor:'#autor', anio:'#anio', coleccion:'#coleccion', tipo:'#tipo' }
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
  const btn = (label, target, disabled=false) => {
    const a = document.createElement('button')
    a.type = 'button'
    a.textContent = label
    a.className = `px-3 py-1.5 rounded-md text-sm ${disabled? 'bg-gray-100 text-gray-400' : 'bg-white border hover:bg-gray-50'}`
    if (!disabled) a.addEventListener('click', () => { state.page = target; stateToParams(); search() })
    return a
  }
  c.append(btn('Anterior', Math.max(1, page-1), page<=1))
  const windowSize = 5
  const start = Math.max(1, page - Math.floor(windowSize/2))
  const end = Math.min(totalPages, start + windowSize - 1)
  for (let i=start; i<=end; i++) {
    const b = btn(String(i), i, false)
    if (i === page) b.className = 'px-3 py-1.5 rounded-md text-sm bg-indigo-600 text-white'
    c.append(b)
  }
  c.append(btn('Siguiente', Math.min(totalPages, page+1), page>=totalPages))
}

function cardTemplate(item) {
  const autores = (item.autores||[]).join('; ')
  const resumen = (item.resumen||'').slice(0, 160)
  return `
    <a class="card hover:shadow-sm transition" href="./detalle.html?id=${encodeURIComponent(item.id)}">
      <h3 class="card-title mb-2">${item.titulo||''}</h3>
      <p class="card-meta mb-2">${autores}</p>
      <p class="text-sm text-gray-700 mb-3">${resumen}${item.resumen && item.resumen.length>160 ? '…' : ''}</p>
      <div class="mt-auto flex items-center justify-between text-sm text-gray-600">
        <span>${item.año_publicacion||''}</span>
        <span class="badge badge-gray">${item.tipo_documento||''}</span>
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
  const coleccion = $('#coleccion').value.trim(); if (coleccion) params.set('coleccion', coleccion)
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
  const items = data.items || data.resultados || []
  state.total = data.total || 0
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
