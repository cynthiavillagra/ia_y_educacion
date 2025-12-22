/**
 * search.js
 * Lógica completa para búsqueda, filtrado y paginación en el frontend.
 * Se conecta a la API V2 (/api/search -> handle_list_materials).
 */

const $ = (selector) => document.querySelector(selector)
const $$ = (selector) => Array.from(document.querySelectorAll(selector))

// Estado global de la búsqueda
const state = {
  page: 1,
  perPage: 20,
  total: 0,
  orden: 'relevancia',
  q: '',
  autor: '',
  anio: '',
  fuente: '',
  tipo: ''
}

/**
 * Inicializa el estado leyendo la URL actual.
 */
function paramsToState() {
  const params = new URLSearchParams(location.search)
  state.q = params.get('q') || ''
  state.autor = params.get('autor') || ''
  state.anio = params.get('anio') || ''
  state.fuente = params.get('fuente') || ''
  state.tipo = params.get('tipo') || ''
  state.page = parseInt(params.get('page') || '1', 10)
  state.orden = params.get('orden') || 'relevancia'

  // Sincronizar inputs del DOM
  if ($('#q')) $('#q').value = state.q
  if ($('#autor')) $('#autor').value = state.autor
  if ($('#anio')) $('#anio').value = state.anio
  if ($('#fuente')) $('#fuente').value = state.fuente
  if ($('#tipo')) $('#tipo').value = state.tipo
  if ($('#orden')) $('#orden').value = state.orden
}

/**
 * Actualiza la URL con el estado actual (sin recargar).
 */
function stateToParams() {
  const url = new URL(location.href)
  const p = url.searchParams

  // Actualizar estado desde inputs por si acaso cambio algo sin submit
  // (aunque idealmente usamos el submit del form)

  if (state.q) p.set('q', state.q); else p.delete('q')
  if (state.autor) p.set('autor', state.autor); else p.delete('autor')
  if (state.anio) p.set('anio', state.anio); else p.delete('anio')
  if (state.fuente) p.set('fuente', state.fuente); else p.delete('fuente')
  if (state.tipo) p.set('tipo', state.tipo); else p.delete('tipo')

  p.set('page', state.page.toString())
  p.set('orden', state.orden)

  history.replaceState(null, '', url.toString())
}

/**
 * Genera el HTML de una tarjeta de recurso.
 */
function cardTemplate(item) {
  // Manejo robusto de autores (puede ser array de legacy o string de V2)
  let autoresArr = []
  if (Array.isArray(item.autores)) {
    autoresArr = item.autores
  } else if (typeof item.autores === 'string') {
    autoresArr = item.autores.split(';').map(s => s.trim()).filter(Boolean)
  }

  // Manejo de etiquetas
  let tagsArr = []
  if (Array.isArray(item.etiquetas)) {
    tagsArr = item.etiquetas
  } else if (typeof item.etiquetas === 'string') {
    tagsArr = item.etiquetas.split(',').map(s => s.trim()).filter(Boolean)
  }

  // Resumen / Descripción
  // Backend V2 usa 'descripcion_resumen', backup con 'resumen'
  const textBody = item.descripcion_resumen || item.resumen || ''
  const resumen = textBody.slice(0, 240)
  const isClipped = textBody.length > 240

  // Íconos por tipo
  const typeMap = {
    'paper_academico': '📄',
    'libro': '📘',
    'capitulo_libro': '🔖',
    'informe': '📊',
    'guia': '🧭',
    'normativa': '⚖️',
    'diseno_curricular': '🎓',
    'articulo_web': '🌐',
    'web_institucional': '🏫',
    'material_docente': '👩‍🏫',
    'video': '🎥',
    'dataset': '💾',
    'presentacion': '📽️',
    'boletin': '📰',
    'default': '📎'
  }
  const tipoKey = item.tipo_recurso || 'default'
  const icon = typeMap[tipoKey] || typeMap.default

  // Texto del tipo (reemplazar guiones bajos)
  const tipoLabel = tipoKey.replace(/_/g, ' ')

  return `
    <article class="article-card">
      <div class="article-icon" title="${tipoLabel}">${icon}</div>
      <div class="article-content">
        <div class="article-header">
          <a class="article-title" href="./detalle.html?id=${encodeURIComponent(item.id)}">
            ${item.titulo || 'Sin Título'}
          </a>
          <span class="article-type">${tipoLabel}</span>
        </div>

        <div class="article-meta">
          ${autoresArr.join('; ') || 'Autor desconocido'} 
          <span class="meta-sep">•</span> 
          <span>${item.anio_publicacion || 's.f.'}</span>
          <span class="meta-sep">•</span>
          <span class="meta-source">${item.institucion_fuente || item.coleccion || 'Fuente desconocida'}</span>
        </div>

        <p class="article-abstract">
          ${resumen}${isClipped ? '...' : ''}
        </p>

        <div class="article-tags">
          ${tagsArr.slice(0, 5).map(t => `<span class="tag">${t}</span>`).join('')}
        </div>
      </div>
    </article>
  `
}

/**
 * Renderiza los botones de paginación.
 */
function renderPagination(total, page, perPage) {
  const container = $('#pagination')
  container.innerHTML = ''

  if (total <= 0) return

  const totalPages = Math.ceil(total / perPage)
  if (totalPages <= 1) return

  const createBtn = (label, pageNum, isActive, isDisabled) => {
    const btn = document.createElement('button')
    btn.type = 'button'
    btn.textContent = label

    if (isActive) {
      btn.className = 'px-3 py-1.5 rounded-md text-sm bg-indigo-600 text-white border border-indigo-600'
    } else if (isDisabled) {
      btn.className = 'px-3 py-1.5 rounded-md text-sm bg-gray-100 text-gray-400 border border-gray-200 cursor-not-allowed'
      btn.disabled = true
    } else {
      btn.className = 'px-3 py-1.5 rounded-md text-sm bg-white border border-gray-300 hover:bg-gray-50 text-gray-700'
      btn.addEventListener('click', () => {
        state.page = pageNum
        stateToParams()
        search()
      })
    }
    return btn
  }

  // Botón Anterior
  container.appendChild(createBtn('Anterior', page - 1, false, page === 1))

  // Ventana de páginas (ej: 1 .. 4 5 6 .. 10)
  const windowSize = 5
  let start = Math.max(1, page - Math.floor(windowSize / 2))
  let end = Math.min(totalPages, start + windowSize - 1)

  if (end - start + 1 < windowSize) {
    start = Math.max(1, end - windowSize + 1)
  }

  for (let i = start; i <= end; i++) {
    container.appendChild(createBtn(i.toString(), i, i === page, false))
  }

  // Botón Siguiente
  container.appendChild(createBtn('Siguiente', page + 1, false, page === totalPages))
}

/**
 * Ejecuta la búsqueda contra la API.
 */
async function search() {
  const container = $('#results')
  const countLabel = $('#results-count')

  // Feedback visual inmediato
  container.style.opacity = '0.5'
  countLabel.textContent = 'Buscando...'

  try {
    // Construir Query Params para fetch
    const params = new URLSearchParams()
    if (state.q) params.set('q', state.q)
    if (state.autor) params.set('autor', state.autor)
    if (state.anio) params.set('anio', state.anio)
    if (state.fuente) params.set('fuente', state.fuente)
    if (state.tipo) params.set('tipo', state.tipo)

    params.set('page', state.page)
    params.set('per_page', state.perPage)
    params.set('orden', state.orden)

    // Llamada API
    // Usamos la ruta canónica V2
    const res = await fetch(`/api/material/list?${params.toString()}`)

    if (!res.ok) {
      let errorMsg = `Error ${res.status}`
      try {
        // Clonamos para poder leer dos veces si falla la primera
        const resClone = res.clone()
        try {
          const errJson = await res.json()
          if (errJson.error) errorMsg = errJson.error
          else if (errJson.detail) errorMsg = errJson.detail
        } catch (e) {
          const text = await resClone.text()
          if (text) errorMsg = text.slice(0, 500)
        }
      } catch (rootErr) {
        console.warn('Error parsing error response:', rootErr)
      }
      throw new Error(errorMsg)
    }

    const data = await res.json()

    // Normalizar respuesta (acepta {items: [], total: N} o array directo)
    let items = []
    let total = 0

    if (Array.isArray(data)) {
      items = data
      total = data.length
    } else {
      items = data.items || data.resultados || []
      total = typeof data.total === 'number' ? data.total : items.length
    }

    state.total = total

    // Renderizar
    countLabel.textContent = `${total} resultados encontrados`

    if (items.length === 0) {
      container.innerHTML = `
        <div class="text-center py-12 text-gray-500">
          <p class="text-lg">No se encontraron resultados.</p>
          <p class="text-sm">Intenta con otros términos o filtros.</p>
        </div>
      `
    } else {
      container.innerHTML = items.map(cardTemplate).join('')
    }

    renderPagination(total, state.page, state.perPage)

  } catch (error) {
    console.error('Search ERROR:', error)
    countLabel.innerHTML = `<span class="text-red-600 font-bold">Error: ${error.message}</span>`
    container.innerHTML = ''
  } finally {
    container.style.opacity = '1'
  }
}

// -------------------------------------------------------------
// EVENT LISTENERS
// -------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {

  // 1. Inicializar desde URL
  paramsToState()

  // 2. Formulario de Filtros Sidebar
  const filtersForm = $('#filters-form')
  if (filtersForm) {
    filtersForm.addEventListener('submit', (e) => {
      e.preventDefault()
      // Actualizar estado desde inputs
      state.fuente = $('#fuente').value.trim()
      state.autor = $('#autor').value.trim()
      state.anio = $('#anio').value.trim()
      state.tipo = $('#tipo').value.trim()

      // Reset a página 1 al filtrar
      state.page = 1

      stateToParams()
      search()

      // Scroll top en móvil
      if (window.innerWidth < 1024) {
        $('#results').scrollIntoView({ behavior: 'smooth' })
      }
    })
  }

  // 3. Botón Limpiar
  const clearBtn = $('#clear-filters')
  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      // Limpiar inputs visuales
      $$('#filters-form input').forEach(i => i.value = '')
      $$('#filters-form select').forEach(s => s.value = '')
      const heroSearch = $('#q')
      if (heroSearch) heroSearch.value = ''

      // Limpiar estado
      state.q = ''
      state.autor = ''
      state.anio = ''
      state.fuente = ''
      state.tipo = ''
      state.page = 1
      state.orden = 'relevancia'

      // Reset Select orden visual
      const sortSelect = $('#orden')
      if (sortSelect) sortSelect.value = 'relevancia'

      stateToParams()
      search()
    })
  }

  // 4. Ordenamiento
  const sortSelect = $('#orden')
  if (sortSelect) {
    sortSelect.addEventListener('change', () => {
      state.orden = sortSelect.value
      state.page = 1 // Reset page on sort change? Generalmente sí.
      stateToParams()
      search()
    })
  }

  // 5. Exponer búsqueda globalmente para el form del Hero (si está en otro scope)
  window.search = search
  window.state = state
  window.stateToParams = stateToParams

  // Si el usuario llega con URL limpia, hacemos búsqueda inicial
  search()
})

// Fix para el Hero Search que está fuera del sidebar
// (El script inline en index.html llama a window.search)
// Aseguramos que actualice state.q antes de llamar
window.updateSearchQuery = (val) => {
  state.q = val
  state.page = 1
}
