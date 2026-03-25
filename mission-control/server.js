import express from 'express'
import { execFile } from 'node:child_process'
import { promises as fs } from 'node:fs'
import os from 'node:os'
import { promisify } from 'node:util'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const execFileAsync = promisify(execFile)
const app = express()
const HOST = process.env.HOST || '0.0.0.0'
const PORT = Number(process.env.PORT || 4180)
const SESSION_ID = 'mission-control-local'
const WORKSPACE = '/home/haolun/.openclaw/workspace'
const SCHEDULE_TIME_ZONE = 'America/New_York'
const TASKS_PATH = path.join(WORKSPACE, 'mission-control/data/tasks.json')
const RECURRING_PATH = path.join(WORKSPACE, 'mission-control/data/recurring.json')
const MEMORY_DIR = path.join(WORKSPACE, 'memory')
const DIST_DIR = path.join(__dirname, 'dist')

app.use(express.json({ limit: '1mb' }))

function getListenUrls(port, host) {
  if (host !== '0.0.0.0' && host !== '::') {
    return [`http://${host}:${port}`]
  }

  const urls = new Set([`http://127.0.0.1:${port}`])
  const interfaces = os.networkInterfaces()
  for (const entries of Object.values(interfaces)) {
    for (const entry of entries || []) {
      if (entry.family === 'IPv4' && !entry.internal) {
        urls.add(`http://${entry.address}:${port}`)
      }
    }
  }

  return [...urls]
}

function normalizeTask(task) {
  const normalized = {
    id: String(task?.id || ''),
    title: String(task?.title || '').trim(),
    notes: String(task?.notes || '').trim(),
    description: String(task?.description || '').trim(),
    lane: String(task?.lane || 'capture'),
    scheduledStart: typeof task?.scheduledStart === 'string' ? task.scheduledStart : '',
    scheduledEnd: typeof task?.scheduledEnd === 'string' ? task.scheduledEnd : '',
    createdAt: String(task?.createdAt || new Date().toISOString()),
    updatedAt: String(task?.updatedAt || task?.createdAt || new Date().toISOString()),
  }

  if (!['capture', 'workbench', 'parking', 'archive'].includes(normalized.lane)) normalized.lane = 'capture'

  const startMs = normalized.scheduledStart ? Date.parse(normalized.scheduledStart) : Number.NaN
  const endMs = normalized.scheduledEnd ? Date.parse(normalized.scheduledEnd) : Number.NaN
  if (normalized.scheduledStart && Number.isNaN(startMs)) normalized.scheduledStart = ''
  if (normalized.scheduledEnd && Number.isNaN(endMs)) normalized.scheduledEnd = ''
  if (normalized.scheduledStart && normalized.scheduledEnd && !Number.isNaN(startMs) && !Number.isNaN(endMs) && endMs < startMs) {
    normalized.scheduledEnd = normalized.scheduledStart
  }

  return normalized
}

function sortTasks(tasks) {
  return [...tasks].sort((a, b) => {
    const aScheduled = a.scheduledStart ? Date.parse(a.scheduledStart) : Number.NaN
    const bScheduled = b.scheduledStart ? Date.parse(b.scheduledStart) : Number.NaN
    if (!Number.isNaN(aScheduled) && !Number.isNaN(bScheduled) && aScheduled !== bScheduled) return aScheduled - bScheduled
    if (!Number.isNaN(aScheduled)) return -1
    if (!Number.isNaN(bScheduled)) return 1
    return Date.parse(b.updatedAt) - Date.parse(a.updatedAt)
  })
}

async function runJsonCommand(command, args) {
  const { stdout } = await execFileAsync(command, args, {
    cwd: WORKSPACE,
    timeout: 600000,
    maxBuffer: 1024 * 1024 * 8,
  })
  return JSON.parse(stdout)
}

async function readJsonFile(filePath, fallback = []) {
  try {
    const raw = await fs.readFile(filePath, 'utf8')
    return JSON.parse(raw)
  } catch {
    return fallback
  }
}

async function readTasks() {
  const raw = await fs.readFile(TASKS_PATH, 'utf8')
  return sortTasks(JSON.parse(raw).map(normalizeTask))
}

async function writeTasks(tasks) {
  await fs.writeFile(TASKS_PATH, `${JSON.stringify(tasks.map(normalizeTask), null, 2)}\n`, 'utf8')
}

async function readTextIfExists(filePath) {
  try {
    return await fs.readFile(filePath, 'utf8')
  } catch {
    return ''
  }
}

function excerpt(text, length = 180) {
  const clean = text.replace(/\s+/g, ' ').trim()
  if (clean.length <= length) return clean
  return `${clean.slice(0, length).trim()}…`
}

function toMemoryEntry(id, title, kind, filePath, content) {
  const lines = content.split('\n').filter((line) => line.trim())
  return { id, title, kind, filePath, excerpt: excerpt(content), content, lineCount: lines.length }
}

async function readMemoryEntries() {
  const activeStatePath = path.join(MEMORY_DIR, 'active-state.md')
  const today = new Date().toISOString().slice(0, 10)
  const dailyFiles = (await fs.readdir(MEMORY_DIR).catch(() => []))
    .filter((name) => /^\d{4}-\d{2}-\d{2}\.md$/.test(name))
    .sort()
    .reverse()
    .slice(0, 8)

  const entries = []
  const active = await readTextIfExists(activeStatePath)
  if (active) entries.push(toMemoryEntry('active-state', 'Active State', 'active-state', activeStatePath, active))

  const userContent = await readTextIfExists(path.join(WORKSPACE, 'USER.md'))
  if (userContent) entries.push(toMemoryEntry('user-profile', 'User Context', 'curated', path.join(WORKSPACE, 'USER.md'), userContent))

  const longTerm = await readTextIfExists(path.join(WORKSPACE, 'MEMORY.md'))
  if (longTerm) entries.push(toMemoryEntry('long-term-memory', 'Long-Term Memory', 'curated', path.join(WORKSPACE, 'MEMORY.md'), longTerm))

  for (const name of dailyFiles) {
    const filePath = path.join(MEMORY_DIR, name)
    const content = await readTextIfExists(filePath)
    if (!content) continue
    entries.push(toMemoryEntry(`daily-${name}`, name.replace('.md', '') === today ? `Today · ${today}` : name.replace('.md', ''), 'daily-note', filePath, content))
  }

  return entries
}

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, sessionId: SESSION_ID, mode: 'single-server', host: HOST, port: PORT })
})

app.get('/api/schedule', async (_req, res) => {
  try {
    const [tasks, recurring] = await Promise.all([readTasks(), readJsonFile(RECURRING_PATH, [])])
    const scheduled = tasks.filter((task) => task.scheduledStart && task.lane !== 'archive')
    res.json({ ok: true, timeZone: SCHEDULE_TIME_ZONE, scheduled, needsScheduling: tasks.filter((task) => !task.scheduledStart && task.lane !== 'archive'), recurring, fetchedAt: new Date().toISOString() })
  } catch (error) {
    const detail = error?.stderr || error?.stdout || error?.message || 'Unknown error'
    res.status(500).json({ ok: false, error: detail })
  }
})

app.get('/api/memory', async (_req, res) => {
  try {
    const entries = await readMemoryEntries()
    res.json({ ok: true, entries, fetchedAt: new Date().toISOString() })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to load memory.' })
  }
})

app.get('/api/tasks', async (_req, res) => {
  try {
    const tasks = await readTasks()
    res.json({ ok: true, tasks })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to load tasks.' })
  }
})

app.post('/api/tasks', async (req, res) => {
  const title = typeof req.body?.title === 'string' ? req.body.title.trim() : ''
  const notes = typeof req.body?.notes === 'string' ? req.body.notes.trim() : ''
  const description = typeof req.body?.description === 'string' ? req.body.description.trim() : ''
  const lane = typeof req.body?.lane === 'string' ? req.body.lane : 'capture'
  const scheduledStart = typeof req.body?.scheduledStart === 'string' ? req.body.scheduledStart : ''
  const scheduledEnd = typeof req.body?.scheduledEnd === 'string' ? req.body.scheduledEnd : ''
  if (!title) return res.status(400).json({ ok: false, error: 'Task title is required.' })

  try {
    const tasks = await readTasks()
    const now = new Date().toISOString()
    const task = normalizeTask({ id: `task-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`, title, notes, description, lane, scheduledStart, scheduledEnd, createdAt: now, updatedAt: now })
    tasks.unshift(task)
    await writeTasks(tasks)
    res.json({ ok: true, task })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to create task.' })
  }
})

app.patch('/api/tasks/:id', async (req, res) => {
  try {
    const tasks = await readTasks()
    const task = tasks.find((item) => item.id === req.params.id)
    if (!task) return res.status(404).json({ ok: false, error: 'Task not found.' })

    if (typeof req.body?.title === 'string') task.title = req.body.title.trim() || task.title
    if (typeof req.body?.notes === 'string') task.notes = req.body.notes.trim()
    if (typeof req.body?.description === 'string') task.description = req.body.description.trim()
    if (typeof req.body?.lane === 'string') task.lane = req.body.lane
    if (typeof req.body?.scheduledStart === 'string') task.scheduledStart = req.body.scheduledStart
    if (typeof req.body?.scheduledEnd === 'string') task.scheduledEnd = req.body.scheduledEnd
    task.updatedAt = new Date().toISOString()

    const normalized = normalizeTask(task)
    const nextTasks = tasks.map((item) => (item.id === normalized.id ? normalized : item))
    await writeTasks(nextTasks)
    res.json({ ok: true, task: normalized })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to update task.' })
  }
})

app.post('/api/chat', async (req, res) => {
  const message = typeof req.body?.message === 'string' ? req.body.message.trim() : ''
  if (!message) return res.status(400).json({ ok: false, error: 'Message is required.' })
  try {
    const parsed = await runJsonCommand('openclaw', ['agent', '--json', '--session-id', SESSION_ID, '--message', message])
    const text = parsed?.result?.payloads?.map((item) => item?.text).filter(Boolean).join('\n\n') || 'No text reply returned.'
    res.json({ ok: true, reply: text, meta: parsed?.result?.meta?.agentMeta ?? null })
  } catch (error) {
    const detail = error?.stderr || error?.stdout || error?.message || 'Unknown error'
    res.status(500).json({ ok: false, error: detail })
  }
})

app.use(express.static(DIST_DIR, {
  etag: false,
  lastModified: false,
  maxAge: 0,
  setHeaders(res) {
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate')
  },
}))
app.get('*', async (_req, res, next) => {
  try {
    await fs.access(path.join(DIST_DIR, 'index.html'))
    res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate')
    res.sendFile(path.join(DIST_DIR, 'index.html'))
  } catch {
    next()
  }
})

app.listen(PORT, HOST, () => {
  const urls = getListenUrls(PORT, HOST)
  console.log(`Mission Control listening on:\n${urls.map((url) => `- ${url}`).join('\n')}`)
})
