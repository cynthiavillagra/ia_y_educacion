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

  // Icon based on type
  const typeMap = {
    'paper_academico': '📄', 'libro': '📘', 'informe': '📊', 'video': '🎥', 'default': '📎'
  }
  const icon = typeMap[item.tipo_recurso] || typeMap.default

  return `
    <article class="flex flex-col sm:flex-row gap-4 p-5 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow group">
      <!-- Icon/Type Indicator (Mobile hidden or small) -->
      <div class="hidden sm:flex flex-col items-center justify-start pt-1 min-w-[3rem] text-3xl opacity-50 select-none">
        ${icon}
      </div>

      <div class="flex-grow">
        <div class="flex flex-col-reverse sm:flex-row sm:justify-between sm:items-start gap-2 mb-1">
          <h3 class="text-xl font-serif font-semibold text-primary-700 group-hover:text-primary-900 leading-tight">
            <a href="./detalle.html?id=${encodeURIComponent(item.id)}" class="hover:underline">${item.titulo || 'Sin Título'}</a>
          </h3>
          <span class="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600 whitespace-nowrap uppercase tracking-wider">
            ${item.tipo_recurso ? item.tipo_recurso.replace('_', ' ') : 'Recurso'}
          </span>
        </div>

        <div class="text-sm text-green-700 font-medium mb-2">
          ${autores.join('; ') || 'Autor desconocido'} 
          <span class="text-slate-400 mx-1">•</span> 
          <span class="text-slate-600">${item.anio_publicacion || 's.f.'}</span>
          <span class="text-slate-400 mx-1">•</span>
          <span class="text-slate-600 italic">${item.institucion_fuente || item.coleccion || 'Fuente desconocida'}</span>
        </div>

        <p class="text-sm text-slate-600 mb-3 leading-relaxed">
          ${resumen}${isClipped ? '...' : ''}
        </p>

        <div class="flex flex-wrap items-center gap-2 mt-auto">
          ${etiquetas.slice(0, 4).map(t => `
            <span class="inline-flex items-center px-2 py-1 rounded text-xs text-slate-600 bg-slate-50 border border-slate-200">
              ${t}
            </span>
          `).join('')}
        </div>
      </div>
    </article>
  `
}

// ... (search function remains mostly same)

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
