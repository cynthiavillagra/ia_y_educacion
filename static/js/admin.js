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
  const sel = document.getElementById('archivo_local')
  const localGroup = document.getElementById('group-local')
  const urlGroup = document.getElementById('group-url')

  // value viene como string "true"/"false" del select
  const isLocal = sel.value === 'true'

  if (isLocal) {
    localGroup.classList.remove('hidden')
    // urlGroup.classList.add('hidden') // Opcional: ¿queremos ocultar la URL externa si sube archivo? V2 permite ambas.
    // Dejemos visible la URL siempre, ya que es "url_fuente_original" (obligatoria en DB, o recomendada).
    // Si la DB dice url_fuente_original NOT NULL, hay que pedirla siempre.
    // Pero si archivo_local=true, quizás la URL sea la del archivo.
    // El backend se encarga de rellenar url_fuente si falta.
    // Mostrémosla siempre por claridad.
  } else {
    localGroup.classList.add('hidden')
    // urlGroup.classList.remove('hidden')
  }
}

async function handleIngestionInit() {
  const form = document.getElementById('ingestion-form')
  if (!form) return

  const selOrigen = document.getElementById('archivo_local')
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

    // Preparar FormData
    const fd = new FormData(form)

    // Autores y Etiquetas: obtener string directo del input.
    // El backend v2 espera texto (ej: "Autor1; Autor2").
    // Los inputs ya tienen ese texto si el usuario usó el autocomplete o escribió.
    // Aseguramos que se envía lo que hay en el input.
    const autores = document.getElementById('autores').value
    const palabras_clave = document.getElementById('etiquetas').value // el input se llama 'etiquetas' en HTML pero name='palabras_clave'

    // Si el name del input es 'palabras_clave', FormData ya lo tiene.
    // Pero chequeamos si el input name="etiquetas" o "palabras_clave" en HTML nuevo.
    // En HTML nuevo puse name="palabras_clave" para etiquetas.
    // name="autores" para autores.
    // Así que FormData ya captura los valores correctos.
    // No hace falta setearlos manual si el name coincide.

    const res = await fetch('/api/admin/ingestion', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${getToken()}` },
      body: fd
    })

    if (!res.ok) {
      const err = await res.json()
      status.textContent = 'Error al guardar: ' + (err.error || err.detail || 'Desconocido')
      return
    }

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

    // Map fields v2
    // Hidden ID field
    if (document.getElementById('recurso_id')) document.getElementById('recurso_id').value = r.id

    const setVal = (id, val) => { if ($(id)) $(id).value = val || '' }

    setVal('#titulo', r.titulo)
    setVal('#titulo_original', r.titulo_original)
    setVal('#doi', r.doi)
    setVal('#isbn_issn', r.isbn_issn)
    setVal('#anio', r.anio_publicacion)

    setVal('#institucion_fuente', r.institucion_fuente)
    setVal('#institucion_autora', r.institucion_autora)

    setVal('#resumen', r.descripcion_resumen)
    setVal('#autores', r.autores) // string
    setVal('#etiquetas', r.palabras_clave) // string

    setVal('#tipo_recurso', r.tipo_recurso || 'paper_academico')
    setVal('#archivo_local', r.archivo_local ? 'true' : 'false')
    setVal('#licencia', r.licencia)
    setVal('#url_fuente_original', r.url_fuente_original)

    toggleOrigenFields()
  } catch (e) {
    console.error('Error al cargar datos del recurso:', e)
  }

  const selOrigen = document.getElementById('archivo_local')
  if (selOrigen) selOrigen.addEventListener('change', toggleOrigenFields)

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
    // Agregar ID explícitamente si no está en form
    fd.append('id', id)

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
      location.href = `/detalle.html?id=${id}` // Ajuste de path relativo
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

