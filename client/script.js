/**
 * AskRocky — chat client.
 *
 * Independent student project. Not affiliated with USF.
 */

const API_URL = import.meta.env.VITE_SERVER

const chatLog = document.querySelector('#chat_container')
const form = document.querySelector('#composer')
const input = document.querySelector('#composer-input')
const sendButton = document.querySelector('#composer-send')
const themeToggle = document.querySelector('#theme-toggle')
const statusEl = document.querySelector('#status')
const statusLabel = document.querySelector('#status-label')

const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)')

const SUGGESTIONS = [
  'What campuses does USF have?',
  'How do I apply, and what are the deadlines?',
  'What majors and programs are offered?'
]

let isBusy = false

/* ------------------------------------------------------------------ *
 * Appearance
 * ------------------------------------------------------------------ */

function systemPrefersDark() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function currentTheme() {
  return document.documentElement.getAttribute('data-theme') || (systemPrefersDark() ? 'dark' : 'light')
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme)
  const next = theme === 'dark' ? 'light' : 'dark'
  themeToggle.setAttribute('aria-label', `Switch to ${next} appearance`)
  try {
    localStorage.setItem('askrocky-theme', theme)
  } catch (e) {
    /* Storage is unavailable in some privacy modes; the toggle still works
       for this session. */
  }
}

themeToggle.addEventListener('click', () => {
  applyTheme(currentTheme() === 'dark' ? 'light' : 'dark')
})

// Reflect the correct starting label without forcing a choice the user
// hasn't made (that would break "follow the system setting").
themeToggle.setAttribute('aria-label', `Switch to ${currentTheme() === 'dark' ? 'light' : 'dark'} appearance`)

/* ------------------------------------------------------------------ *
 * Backend readiness
 *
 * The embedding model loads in a background thread on the server, so
 * early answers come from the LLM alone with no USF sources. Surfacing
 * that is honest and explains why the first answers look different.
 * ------------------------------------------------------------------ */

function setStatus(state, label) {
  if (!label) {
    statusEl.hidden = true
    return
  }
  statusEl.hidden = false
  statusEl.dataset.state = state
  statusLabel.textContent = label
}

async function pollReadiness() {
  if (!API_URL) return

  let healthUrl
  try {
    healthUrl = new URL(API_URL)
    healthUrl.pathname = healthUrl.pathname.replace(/\/api(\/chat)?$/, '') + '/health'
  } catch (e) {
    return
  }

  for (let attempt = 0; attempt < 40; attempt++) {
    try {
      const res = await fetch(healthUrl, { method: 'GET' })
      if (res.ok) {
        const data = await res.json()
        if (data.ready) {
          setStatus('ready', 'Knowledge base ready')
          setTimeout(() => setStatus('ready', ''), 4000)
          return
        }
        setStatus('warming', 'Loading knowledge base…')
      } else {
        setStatus('offline', 'Backend unreachable')
      }
    } catch (e) {
      setStatus('offline', 'Backend unreachable')
    }
    await new Promise((resolve) => setTimeout(resolve, 3000))
  }
}

/* ------------------------------------------------------------------ *
 * Rendering
 *
 * Model output is inserted with textContent, never innerHTML, so a
 * response containing markup can't inject nodes into the page.
 * ------------------------------------------------------------------ */

function el(tag, className, text) {
  const node = document.createElement(tag)
  if (className) node.className = className
  if (text != null) node.textContent = text
  return node
}

function addRow(kind) {
  const row = el('div', `row row--${kind}`)

  if (kind !== 'user') {
    const avatar = el('div', 'avatar', 'R')
    avatar.setAttribute('aria-hidden', 'true')
    row.appendChild(avatar)
  }

  const bubble = el('div', 'bubble')
  row.appendChild(bubble)
  chatLog.appendChild(row)
  scrollToBottom()
  return { row, bubble }
}

function scrollToBottom() {
  chatLog.scrollTop = chatLog.scrollHeight
}

function hostOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch (e) {
    return ''
  }
}

/**
 * Secondary label for a source row. Every source is a usf.edu page, so the
 * hostname on each row is noise -- the path is what tells two pages apart.
 * Overflow is trimmed by CSS so it never breaks mid-word here.
 */
function locationOf(url) {
  try {
    const parsed = new URL(url)
    const host = parsed.hostname.replace(/^www\./, '')
    const path = parsed.pathname.replace(/\/$/, '')
    if (!path || path === '/') return host
    return host.endsWith('usf.edu') ? path : host + path
  } catch (e) {
    return hostOf(url)
  }
}

/**
 * Retrieval returns one entry per matching chunk, and the same page routinely
 * comes back several times under URLs that differ only by a `www.` prefix,
 * tracking parameters, or a `#fragment`. Normalising first collapses those
 * into the single source they actually are — and drops the tracking params
 * from the link we hand the reader.
 */
function normalizeUrl(raw) {
  try {
    const url = new URL(raw)
    url.hash = ''
    url.protocol = 'https:'
    url.hostname = url.hostname.toLowerCase().replace(/^www\./, '')
    // The USF CMS serves a directory and its index file as the same page, so
    // /registrar/calendars and /registrar/calendars/index.aspx are one source.
    url.pathname = url.pathname
      .replace(/\/(index|default)\.(aspx|html?|php)$/i, '')
      .replace(/\/+$/, '') || '/'

    const tracking = []
    url.searchParams.forEach((_, key) => {
      if (/^(utm_|fbclid|gclid|mc_|ref$)/i.test(key)) tracking.push(key)
    })
    tracking.forEach((key) => url.searchParams.delete(key))

    return url.toString()
  } catch (e) {
    return raw
  }
}

function uniqueSources(urls, titles) {
  const seen = new Set()
  const out = []
  for (let i = 0; i < urls.length; i++) {
    if (!urls[i]) continue
    const url = normalizeUrl(urls[i])
    if (seen.has(url)) continue
    seen.add(url)
    out.push({ url, title: titles[i] || hostOf(url) || url })
    if (out.length === 4) break
  }
  return out
}

function renderSources(bubble, urls, titles) {
  const sources = uniqueSources(urls || [], titles || [])
  if (!sources.length) return

  const wrap = el('div', 'sources')
  wrap.appendChild(el('div', 'sources__label', sources.length === 1 ? 'Source' : 'Sources'))

  const list = el('ul', 'sources__list')
  sources.forEach((source, i) => {
    const item = document.createElement('li')
    const link = el('a', 'source')
    link.href = source.url
    link.target = '_blank'
    link.rel = 'noopener noreferrer'

    link.appendChild(el('span', 'source__index', `${i + 1}.`))
    link.appendChild(el('span', 'source__title', source.title))

    const location = locationOf(source.url)
    if (location) link.appendChild(el('span', 'source__host', location))

    item.appendChild(link)
    list.appendChild(item)
  })

  wrap.appendChild(list)
  bubble.appendChild(wrap)
}

function renderCopyAction(bubble, text) {
  if (!navigator.clipboard) return

  const actions = el('div', 'actions')
  const button = el('button', 'text-button')
  button.type = 'button'
  button.appendChild(el('span', null, 'Copy'))

  button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(text)
      button.firstChild.textContent = 'Copied'
      setTimeout(() => {
        button.firstChild.textContent = 'Copy'
      }, 1600)
    } catch (e) {
      button.firstChild.textContent = 'Press ⌘C'
    }
  })

  actions.appendChild(button)
  bubble.appendChild(actions)
}

/**
 * Reveal the answer a few characters per frame.
 *
 * The old version did `innerHTML += char` on a timer, which re-parsed the
 * entire chat on every character and slowed to a crawl on long answers.
 * This writes to a single text node instead, and skips the effect entirely
 * when the user has asked for reduced motion.
 */
function typeText(target, text) {
  return new Promise((resolve) => {
    let settled = false
    const finish = () => {
      if (settled) return
      settled = true
      target.textContent = text
      scrollToBottom()
      resolve()
    }

    if (prefersReducedMotion.matches || !text) {
      finish()
      return
    }

    // Time-based rather than characters-per-frame: a long answer finishes in
    // the same brief moment as a short one, and a throttled frame rate (a
    // backgrounded tab, a busy machine) can't stretch it out.
    const duration = Math.min(900, Math.max(250, text.length * 4))
    const start = performance.now()

    function step(now) {
      const progress = Math.min(1, (now - start) / duration)
      target.textContent = text.slice(0, Math.round(progress * text.length))
      scrollToBottom()
      if (progress < 1) {
        requestAnimationFrame(step)
      } else {
        finish()
      }
    }

    requestAnimationFrame(step)
    // If the tab is hidden, rAF may never fire. Never leave the answer or its
    // sources unrendered because of an animation.
    setTimeout(finish, duration + 500)
  })
}

/* ------------------------------------------------------------------ *
 * Suggested questions
 * ------------------------------------------------------------------ */

function renderSuggestions() {
  const wrap = el('div', 'suggestions')
  wrap.id = 'suggestions'
  wrap.appendChild(el('p', 'suggestions__label', 'Try asking'))

  SUGGESTIONS.forEach((question) => {
    const chip = el('button', 'chip', question)
    chip.type = 'button'
    // Listener is bound to the element itself and the log is never rebuilt
    // with innerHTML, so these survive every later message. The old version
    // wiped them out as soon as the first reply arrived.
    chip.addEventListener('click', () => {
      if (isBusy) return
      removeSuggestions()
      ask(question)
    })
    wrap.appendChild(chip)
  })

  chatLog.appendChild(wrap)
}

function removeSuggestions() {
  const node = document.querySelector('#suggestions')
  if (node) node.remove()
}

/* ------------------------------------------------------------------ *
 * Asking
 * ------------------------------------------------------------------ */

function setBusy(busy) {
  isBusy = busy
  sendButton.disabled = busy
  sendButton.dataset.busy = String(busy)
  sendButton.setAttribute('aria-label', busy ? 'Waiting for an answer' : 'Send question')
}

function showError(bubble, message, retryQuestion) {
  bubble.textContent = ''
  bubble.parentElement.classList.add('row--error')
  bubble.appendChild(el('p', 'bubble__text', message))

  const actions = el('div', 'actions')
  const retry = el('button', 'text-button', 'Try again')
  retry.type = 'button'
  retry.addEventListener('click', () => {
    if (isBusy) return
    bubble.parentElement.remove()
    ask(retryQuestion)
  })
  actions.appendChild(retry)
  bubble.appendChild(actions)
  scrollToBottom()
}

async function ask(question) {
  const prompt = String(question || '').trim()
  if (!prompt || isBusy) return

  setBusy(true)

  const userTurn = addRow('user')
  userTurn.bubble.appendChild(el('p', 'bubble__text', prompt))

  const aiTurn = addRow('ai')
  const thinking = el('div', 'thinking')
  thinking.append(el('span'), el('span'), el('span'))
  const srStatus = el('span', 'sr-only', 'Thinking…')
  aiTurn.bubble.append(thinking, srStatus)
  scrollToBottom()

  if (!API_URL) {
    showError(
      aiTurn.bubble,
      'This build has no backend configured. Set VITE_SERVER to the API chat endpoint and rebuild.',
      prompt
    )
    setBusy(false)
    return
  }

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    })

    if (!response.ok) {
      throw new Error(`The server replied ${response.status}.`)
    }

    const data = await response.json()
    const bot = (data && data.bot) || {}
    const answer = (bot.result || '').trim()

    aiTurn.bubble.textContent = ''

    if (!answer) {
      showError(aiTurn.bubble, "The server didn't return an answer. Try rephrasing the question.", prompt)
      return
    }

    const paragraph = el('p', 'bubble__text')
    aiTurn.bubble.appendChild(paragraph)
    await typeText(paragraph, answer)

    renderSources(aiTurn.bubble, bot.source, bot.title)
    renderCopyAction(aiTurn.bubble, answer)
    scrollToBottom()
  } catch (error) {
    console.error(error)
    showError(
      aiTurn.bubble,
      'Could not reach AskRocky. Check your connection, then try again.',
      prompt
    )
  } finally {
    setBusy(false)
    input.focus()
  }
}

/* ------------------------------------------------------------------ *
 * Composer
 * ------------------------------------------------------------------ */

function autoGrow() {
  input.style.height = 'auto'
  input.style.height = `${Math.min(input.scrollHeight, 144)}px`
}

input.addEventListener('input', autoGrow)

form.addEventListener('submit', (event) => {
  event.preventDefault()
  const question = input.value
  if (!question.trim()) return
  removeSuggestions()
  input.value = ''
  autoGrow()
  ask(question)
})

// Enter sends, Shift+Enter adds a newline. `key` rather than the deprecated
// keyCode, and isComposing so IME candidate selection doesn't submit.
input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing) {
    event.preventDefault()
    form.requestSubmit()
  }
})

/* ------------------------------------------------------------------ *
 * Start
 * ------------------------------------------------------------------ */

const greeting = addRow('ai')
greeting.bubble.appendChild(
  el(
    'p',
    'bubble__text',
    "Hi, I'm AskRocky. Ask me anything about the University of South Florida and I'll answer with links to the usf.edu pages I used."
  )
)

renderSuggestions()
pollReadiness()
