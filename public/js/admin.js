const $ = (s, d = document) => d.querySelector(s)

function getToken() {
  const v = localStorage.getItem('sb_access_token')
  return v || ''
}

function setToken(token) {
  if (token) localStorage.setItem('sb_access_token', token)
}

function clearToken() {
  localStorage.removeItem('sb_access_token')
}

async function handleLoginInit() {
  const form = document.getElementById('login-form')
  if (!form) return
  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    const email = document.getElementById('email').value
    const password = document.getElementById('password').value
    const out = document.getElementById('login-error')
    out.classList.add('hidden'); out.textContent = ''
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) { out.textContent = 'Credenciales inválidas'; out.classList.remove('hidden'); return }
    setToken(data.session?.access_token)
    location.href = '/admin/ingestion.html'
  })
}

function toggleOrigenFields() {
  const sel = document.getElementById('estado_alojamiento')
  const alojado = document.getElementById('group-alojado')
  const original = document.getElementById('group-original')
  const v = sel.value
  alojado.classList.toggle('hidden', v !== 'ALOJADO')
  original.classList.toggle('hidden', v !== 'ORIGINAL')
}

async function requireAuthOrRedirect() {
  const form = document.getElementById('ingestion-form') || document.getElementById('edicion-form')
  if (!form) return
  const token = getToken()
  if (!token) { location.href = '/admin/login.html'; return }
}

async function loadTags() {
  try {
    const res = await fetch('/api/etiquetas')
    if (!res.ok) return
    const tags = await res.json()

    // Initialize etiquetas autocomplete
    if (window.etiquetasAutocomplete) {
      window.etiquetasAutocomplete.setSuggestions(tags)
    }
  } catch (e) {
    console.error('Error loading tags:', e)
  }
}

async function loadAuthors() {
  try {
    const res = await fetch('/api/autores')
    if (!res.ok) return
    const authors = await res.json()

    // Initialize autores autocomplete
    if (window.autoresAutocomplete) {
      window.autoresAutocomplete.setSuggestions(authors)
    }
  } catch (e) {
    console.error('Error loading authors:', e)
  }
}

function setupAutocomplete() {
  // Create autocomplete instances
  if (document.getElementById('etiquetas') && window.MultiAutocomplete) {
    window.etiquetasAutocomplete = new window.MultiAutocomplete('etiquetas', 'etiquetas-dropdown', [], ',')
  }
  if (document.getElementById('autores') && window.MultiAutocomplete) {
    window.autoresAutocomplete = new window.MultiAutocomplete('autores', 'autores-dropdown', [], ';')
  }
}

async function handleIngestionInit() {
  const form = document.getElementById('ingestion-form')
  if (!form) return
  const selOrigen = document.getElementById('estado_alojamiento')
  toggleOrigenFields()
  selOrigen.addEventListener('change', toggleOrigenFields)

  document.getElementById('logout').addEventListener('click', async () => {
    await supabase.auth.signOut()
    clearToken()
    location.href = '/admin/login.html'
  })

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    const status = document.getElementById('ingestion-status')
    status.textContent = 'Guardando…'
    const fd = new FormData(form)
    const autores = (document.getElementById('autores').value || '').split(';').map(s => s.trim()).filter(Boolean)
    const etiquetas = (document.getElementById('etiquetas').value || '').split(',').map(s => s.trim()).filter(Boolean)
    fd.set('autores', JSON.stringify(autores))
    fd.set('etiquetas', JSON.stringify(etiquetas))

    const res = await fetch('/api/admin/ingestion', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${getToken()}` },
      body: fd
    })
    if (!res.ok) { status.textContent = 'Error al guardar'; return }
    status.textContent = 'Guardado correctamente'
    form.reset()
    toggleOrigenFields()
  })
}

async function handleEditionInit() {
  const form = document.getElementById('edicion-form')
  if (!form) return

  const url = new URL(location.href)
  const id = url.searchParams.get('id')
  if (!id) {
    alert('No se especificó un ID de recurso')
    location.href = '/admin/ingestion.html'
    return
  }

  // Load data
  try {
    const res = await fetch(`/api/recurso_detalle?id=${id}`)
    if (!res.ok) throw new Error('Error al cargar recurso')
    const r = await res.json()

    document.getElementById('recurso_id').value = r.id
    document.getElementById('titulo').value = r.titulo || ''
    document.getElementById('codigo_documento').value = r.codigo_documento || ''
    document.getElementById('anio').value = r.año_publicacion || ''
    document.getElementById('coleccion').value = r.coleccion || ''
    document.getElementById('resumen').value = r.resumen || ''
    document.getElementById('autores').value = (r.autores || []).join('; ')
    document.getElementById('etiquetas').value = (r.etiquetas || []).join(', ')
    document.getElementById('tipo_documento').value = r.tipo_documento || 'ARTICULO'
    document.getElementById('estado_alojamiento').value = r.estado_alojamiento || 'ORIGINAL'
    document.getElementById('licencia_cc').value = r.licencia_cc || 'CC BY 4.0'
    document.getElementById('url_descarga').value = r.url_descarga || ''

    toggleOrigenFields()
  } catch (e) {
    console.error('Error al cargar datos del recurso:', e)
    // Don't show alert, data might still load partially
  }

  const selOrigen = document.getElementById('estado_alojamiento')
  selOrigen.addEventListener('change', toggleOrigenFields)

  document.getElementById('logout').addEventListener('click', async () => {
    await supabase.auth.signOut()
    clearToken()
    location.href = '/admin/login.html'
  })

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    const status = document.getElementById('edicion-status')
    status.textContent = 'Guardando cambios…'
    const fd = new FormData(form)
    const autores = (document.getElementById('autores').value || '').split(';').map(s => s.trim()).filter(Boolean)
    const etiquetas = (document.getElementById('etiquetas').value || '').split(',').map(s => s.trim()).filter(Boolean)
    fd.set('autores', JSON.stringify(autores))
    fd.set('etiquetas', JSON.stringify(etiquetas))

    const res = await fetch('/api/admin/update', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${getToken()}` },
      body: fd
    })
    if (!res.ok) {
      const err = await res.json()
      status.textContent = 'Error al guardar: ' + (err.error || 'Desconocido')
      return
    }
    status.textContent = 'Cambios guardados correctamente'
    setTimeout(() => {
      location.href = `/public/detalle.html?id=${id}`
    }, 1000)
  })
}

function initAdmin() {
  handleLoginInit()
  // Only check auth on pages that are NOT login
  if (!location.pathname.includes('login.html')) {
    requireAuthOrRedirect()
    setupAutocomplete()  // Setup autocomplete components
    loadTags()  // Load tags for autocomplete
    loadAuthors()  // Load authors for autocomplete
    handleIngestionInit()
    handleEditionInit()
  }
}

// Expose to global scope
window.initAdmin = initAdmin

