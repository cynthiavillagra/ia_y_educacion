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
    location.href = '/public/admin/ingestion.html'
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
  const form = document.getElementById('ingestion-form')
  if (!form) return
  const token = getToken()
  if (!token) { location.href = '/public/admin/login.html'; return }
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
    location.href = '/public/admin/login.html'
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

function initAdmin() {
  handleLoginInit()
  // Only check auth on pages that are NOT login
  if (!location.pathname.includes('login.html')) {
    requireAuthOrRedirect()
    handleIngestionInit()
    handleEditionInit()
  }
}

// Expose to global scope
window.initAdmin = initAdmin

