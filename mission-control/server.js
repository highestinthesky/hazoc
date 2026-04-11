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
const EVENTS_PATH = path.join(WORKSPACE, 'mission-control/data/events.json')
const RECURRING_PATH = path.join(WORKSPACE, 'mission-control/data/recurring.json')
const PROTOCOL_PATH = path.join(WORKSPACE, 'mission-control/data/protocol.json')
const DIGEST_USERS_PATH = path.join(WORKSPACE, 'skills/market-watch/config/digest_users.json')
const DIGESTS_DIR = path.join(WORKSPACE, 'skills/market-watch/state/digest/digests')
const MEMORY_DIR = path.join(WORKSPACE, 'memory')
const LOCAL_SKILLS_DIR = path.join(WORKSPACE, 'skills')
const GLOBAL_SKILLS_DIR = path.join(os.homedir(), '.npm-global/lib/node_modules/openclaw/skills')
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
  const incomingLane = String(task?.lane || 'workbench')
  const normalized = {
    id: String(task?.id || ''),
    title: String(task?.title || '').trim(),
    notes: String(task?.notes || '').trim(),
    description: String(task?.description || '').trim(),
    lane: incomingLane === 'capture' ? 'workbench' : incomingLane,
    scheduledStart: typeof task?.scheduledStart === 'string' ? task.scheduledStart : '',
    scheduledEnd: typeof task?.scheduledEnd === 'string' ? task.scheduledEnd : '',
    createdAt: String(task?.createdAt || new Date().toISOString()),
    updatedAt: String(task?.updatedAt || task?.createdAt || new Date().toISOString()),
  }

  if (!['workbench', 'parking', 'archive'].includes(normalized.lane)) normalized.lane = 'workbench'

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

function normalizeEvent(event) {
  const normalized = {
    id: String(event?.id || ''),
    title: String(event?.title || '').trim(),
    notes: String(event?.notes || '').trim(),
    description: String(event?.description || '').trim(),
    owner: String(event?.owner || 'haolun').trim() || 'haolun',
    status: String(event?.status || 'active'),
    scheduledStart: typeof event?.scheduledStart === 'string' ? event.scheduledStart : '',
    scheduledEnd: typeof event?.scheduledEnd === 'string' ? event.scheduledEnd : '',
    createdAt: String(event?.createdAt || new Date().toISOString()),
    updatedAt: String(event?.updatedAt || event?.createdAt || new Date().toISOString()),
  }

  if (!['active', 'archived'].includes(normalized.status)) normalized.status = 'active'

  const startMs = normalized.scheduledStart ? Date.parse(normalized.scheduledStart) : Number.NaN
  const endMs = normalized.scheduledEnd ? Date.parse(normalized.scheduledEnd) : Number.NaN
  if (normalized.scheduledStart && Number.isNaN(startMs)) normalized.scheduledStart = ''
  if (normalized.scheduledEnd && Number.isNaN(endMs)) normalized.scheduledEnd = ''
  if (normalized.scheduledStart && normalized.scheduledEnd && !Number.isNaN(startMs) && !Number.isNaN(endMs) && endMs < startMs) {
    normalized.scheduledEnd = normalized.scheduledStart
  }

  return normalized
}

function sortEvents(events) {
  return [...events].sort((a, b) => {
    const aScheduled = a.scheduledStart ? Date.parse(a.scheduledStart) : Number.NaN
    const bScheduled = b.scheduledStart ? Date.parse(b.scheduledStart) : Number.NaN
    if (!Number.isNaN(aScheduled) && !Number.isNaN(bScheduled) && aScheduled !== bScheduled) return aScheduled - bScheduled
    if (!Number.isNaN(aScheduled)) return -1
    if (!Number.isNaN(bScheduled)) return 1
    return Date.parse(b.updatedAt) - Date.parse(a.updatedAt)
  })
}

function normalizeProtocolItem(item) {
  return {
    id: String(item?.id || ''),
    title: String(item?.title || '').trim(),
    summary: String(item?.summary || '').trim(),
    category: String(item?.category || 'workflow').trim() || 'workflow',
    cadence: String(item?.cadence || 'continuous').trim() || 'continuous',
    createdAt: String(item?.createdAt || new Date().toISOString()),
    updatedAt: String(item?.updatedAt || item?.createdAt || new Date().toISOString()),
  }
}

function sortProtocolItems(items) {
  return [...items].sort((a, b) => Date.parse(b.updatedAt) - Date.parse(a.updatedAt))
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

async function readEvents() {
  const raw = await fs.readFile(EVENTS_PATH, 'utf8')
  return sortEvents(JSON.parse(raw).map(normalizeEvent))
}

async function writeEvents(events) {
  await fs.writeFile(EVENTS_PATH, `${JSON.stringify(events.map(normalizeEvent), null, 2)}\n`, 'utf8')
}

async function readProtocolItems() {
  const raw = await fs.readFile(PROTOCOL_PATH, 'utf8')
  return sortProtocolItems(JSON.parse(raw).map(normalizeProtocolItem))
}

async function writeProtocolItems(items) {
  await fs.writeFile(PROTOCOL_PATH, `${JSON.stringify(items.map(normalizeProtocolItem), null, 2)}\n`, 'utf8')
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

function parseFrontmatter(raw) {
  const match = raw.match(/^---\n([\s\S]*?)\n---\n?/)
  if (!match) return { meta: {}, body: raw }

  const meta = {}
  for (const line of match[1].split('\n')) {
    const item = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/)
    if (!item) continue
    meta[item[1]] = item[2].trim().replace(/^['"]|['"]$/g, '')
  }

  return { meta, body: raw.slice(match[0].length) }
}

function normalizeFlowLabel(text) {
  return String(text || '')
    .replace(/^\d+[.)-]?\s*/, '')
    .replace(/^phase\s+\d+\s+[—-]\s*/i, '')
    .replace(/^step\s+\d+\s*[:.-]?\s*/i, '')
    .trim()
}

function extractFlowSteps(body) {
  const skip = new Set(['overview', 'references', 'reference', 'commands', 'command', 'guardrails'])
  const headingMatches = [...body.matchAll(/^#{2,3}\s+(.+)$/gm)]
  const headingSteps = headingMatches
    .map((match) => normalizeFlowLabel(match[1]))
    .filter((label) => label && !skip.has(label.toLowerCase()))

  if (headingSteps.length >= 2) return [...new Set(headingSteps)].slice(0, 8)

  const orderedMatches = [...body.matchAll(/^\d+\.\s+(.+)$/gm)]
  const orderedSteps = orderedMatches
    .map((match) => normalizeFlowLabel(match[1]))
    .filter(Boolean)
  if (orderedSteps.length >= 2) return [...new Set(orderedSteps)].slice(0, 8)

  const bulletMatches = [...body.matchAll(/^-\s+(.+)$/gm)]
  const bulletSteps = bulletMatches
    .map((match) => normalizeFlowLabel(match[1]))
    .filter((label) => label && label.length <= 120)
  if (bulletSteps.length >= 2) return [...new Set(bulletSteps)].slice(0, 8)

  return ['Detect trigger', 'Read SKILL.md', 'Load extra references or scripts if needed', 'Execute the workflow', 'Validate and record the result']
}

function summarizeSkillType(source) {
  return source === 'workspace' ? 'Workspace skill' : 'System skill'
}

function shortPath(filePath) {
  return String(filePath)
    .replace(`${os.homedir()}/`, '~/')
    .replace(`${WORKSPACE}/`, '')
}

async function readSkills() {
  const sources = [
    { dir: LOCAL_SKILLS_DIR, source: 'workspace' },
    { dir: GLOBAL_SKILLS_DIR, source: 'system' },
  ]

  const skills = []
  const seen = new Set()

  for (const bucket of sources) {
    const names = await fs.readdir(bucket.dir).catch(() => [])
    for (const name of names.sort()) {
      const skillDir = path.join(bucket.dir, name)
      const stat = await fs.stat(skillDir).catch(() => null)
      if (!stat?.isDirectory()) continue

      const skillPath = path.join(skillDir, 'SKILL.md')
      const raw = await readTextIfExists(skillPath)
      if (!raw) continue

      const { meta, body } = parseFrontmatter(raw)
      const skillName = meta.name || name
      if (seen.has(skillName)) continue
      seen.add(skillName)

      const referencesDir = path.join(skillDir, 'references')
      const scriptsDir = path.join(skillDir, 'scripts')
      const assetsDir = path.join(skillDir, 'assets')
      const [references, scripts, assets] = await Promise.all([
        fs.readdir(referencesDir).catch(() => []),
        fs.readdir(scriptsDir).catch(() => []),
        fs.readdir(assetsDir).catch(() => []),
      ])

      skills.push({
        id: `${bucket.source}:${skillName}`,
        name: skillName,
        source: bucket.source,
        sourceLabel: summarizeSkillType(bucket.source),
        skillPath: shortPath(skillPath),
        description: meta.description || excerpt(body, 220),
        flow: extractFlowSteps(body),
        referencesCount: references.length,
        scriptsCount: scripts.length,
        assetsCount: assets.length,
      })
    }
  }

  return skills.sort((a, b) => {
    if (a.source !== b.source) return a.source === 'workspace' ? -1 : 1
    return a.name.localeCompare(b.name)
  })
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

function normalizeJournalItem(item, index = 0) {
  return {
    id: String(item?.url || item?.headline || `item-${index}`),
    headline: String(item?.headline || 'Untitled item').trim(),
    summary: String(item?.summary || '').trim(),
    whyItMatters: String(item?.whyItMatters || '').trim(),
    impactRead: String(item?.impactRead || '').trim(),
    primaryTheme: String(item?.primaryTheme || '').trim(),
    source: String(item?.source || '').trim(),
    url: String(item?.url || '').trim(),
    scope: String(item?.scope || 'unknown').trim(),
    direction: String(item?.direction || 'unclear').trim(),
    confidence: typeof item?.confidence === 'number' ? item.confidence : null,
    confidenceLabel: String(item?.confidenceLabel || '').trim(),
    score: typeof item?.score === 'number' ? item.score : 0,
    highPriority: Boolean(item?.highPriority),
    category: String(item?.category || '').trim(),
    themes: Array.isArray(item?.themes) ? item.themes.map((value) => String(value || '').trim()).filter(Boolean) : [],
    affectedNames: Array.isArray(item?.affectedNames) ? item.affectedNames.map((value) => String(value || '').trim()).filter(Boolean) : [],
    affectedSectors: Array.isArray(item?.affectedSectors) ? item.affectedSectors.map((value) => String(value || '').trim()).filter(Boolean) : [],
    affectedEtfs: Array.isArray(item?.affectedEtfs) ? item.affectedEtfs.map((value) => String(value || '').trim()).filter(Boolean) : [],
    matchedTickers: Array.isArray(item?.matchedTickers) ? item.matchedTickers.map((value) => String(value || '').trim()).filter(Boolean) : [],
    matchedSectors: Array.isArray(item?.matchedSectors) ? item.matchedSectors.map((value) => String(value || '').trim()).filter(Boolean) : [],
    userRelevance: typeof item?.userRelevance === 'number' ? item.userRelevance : 0,
    eventTime: String(item?.eventTime || '').trim(),
  }
}

function normalizeDigestBoardEntry(item, index = 0) {
  return {
    id: String(item?.headline || item?.label || `board-${index}`),
    label: String(item?.label || item?.theme || `Board ${index + 1}`).trim(),
    headline: String(item?.headline || '').trim(),
    summary: String(item?.summary || '').trim(),
    impactRead: String(item?.impactRead || '').trim(),
    score: typeof item?.score === 'number' ? item.score : 0,
    supportingCount: typeof item?.supportingCount === 'number' ? item.supportingCount : 0,
    supportingHeadlines: Array.isArray(item?.supportingHeadlines) ? item.supportingHeadlines.map((value) => String(value || '').trim()).filter(Boolean) : [],
    highPriority: Boolean(item?.highPriority),
    scope: String(item?.scope || '').trim(),
    affectedNames: Array.isArray(item?.affectedNames) ? item.affectedNames.map((value) => String(value || '').trim()).filter(Boolean) : [],
    affectedSectors: Array.isArray(item?.affectedSectors) ? item.affectedSectors.map((value) => String(value || '').trim()).filter(Boolean) : [],
  }
}

function buildStockImpactBoard(digest, items) {
  const storedBoard = Array.isArray(digest?.stockImpactBoard)
    ? digest.stockImpactBoard.map((item, index) => normalizeJournalItem(item, index))
    : []

  if (storedBoard.length) {
    return storedBoard
      .slice(0, 8)
      .map((item) => ({
        id: item.id,
        headline: item.headline,
        whyItMatters: item.whyItMatters,
        impactRead: item.impactRead,
        affectedNames: item.affectedNames,
        affectedSectors: item.affectedSectors,
        affectedEtfs: item.affectedEtfs,
        scope: item.scope,
        score: item.score,
        highPriority: item.highPriority,
        direction: item.direction,
        confidenceLabel: item.confidenceLabel,
        themes: item.themes,
        url: item.url,
        source: item.source,
      }))
  }

  return items
    .filter((item) => item.affectedNames.length > 0 || (item.scope && item.scope !== 'broad'))
    .sort((a, b) => {
      if (b.highPriority !== a.highPriority) return Number(b.highPriority) - Number(a.highPriority)
      return (b.score || 0) - (a.score || 0)
    })
    .slice(0, 8)
    .map((item) => ({
      id: item.id,
      headline: item.headline,
      whyItMatters: item.whyItMatters,
      impactRead: item.impactRead,
      affectedNames: item.affectedNames,
      affectedSectors: item.affectedSectors,
      affectedEtfs: item.affectedEtfs,
      scope: item.scope,
      score: item.score,
      highPriority: item.highPriority,
      direction: item.direction,
      confidenceLabel: item.confidenceLabel,
      themes: item.themes,
      url: item.url,
      source: item.source,
    }))
}

function buildGlobalOverview(digest, items) {
  return {
    totalItems: typeof digest?.totalItems === 'number' ? digest.totalItems : items.length,
    highPriorityCount: typeof digest?.highPriorityCount === 'number' ? digest.highPriorityCount : items.filter((item) => item.highPriority).length,
    totalScore: typeof digest?.totalScore === 'number' ? digest.totalScore : items.reduce((sum, item) => sum + (item.score || 0), 0),
    headlineSummary: String(digest?.headlineSummary || '').trim(),
    topCategories: Array.isArray(digest?.topCategories) ? digest.topCategories : [],
    unresolvedUncertainties: Array.isArray(digest?.unresolvedUncertainties) ? digest.unresolvedUncertainties.map((value) => String(value || '').trim()).filter(Boolean) : [],
    overviewBoard: Array.isArray(digest?.overviewBoard) ? digest.overviewBoard.map((item, index) => normalizeDigestBoardEntry(item, index)) : [],
    watchNext: Array.isArray(digest?.watchNext) ? digest.watchNext.map((value) => String(value || '').trim()).filter(Boolean) : [],
    deltaVsLastRun: {
      summary: String(digest?.deltaVsLastRun?.summary || '').trim(),
      previousGeneratedAt: String(digest?.deltaVsLastRun?.previousGeneratedAt || '').trim(),
      previousLabel: String(digest?.deltaVsLastRun?.previousLabel || '').trim(),
      newThemes: Array.isArray(digest?.deltaVsLastRun?.newThemes) ? digest.deltaVsLastRun.newThemes.map((value) => String(value || '').trim()).filter(Boolean) : [],
      stillLiveThemes: Array.isArray(digest?.deltaVsLastRun?.stillLiveThemes) ? digest.deltaVsLastRun.stillLiveThemes.map((value) => String(value || '').trim()).filter(Boolean) : [],
      cooledThemes: Array.isArray(digest?.deltaVsLastRun?.cooledThemes) ? digest.deltaVsLastRun.cooledThemes.map((value) => String(value || '').trim()).filter(Boolean) : [],
      freshHeadlineCount: typeof digest?.deltaVsLastRun?.freshHeadlineCount === 'number' ? digest.deltaVsLastRun.freshHeadlineCount : 0,
    },
  }
}

function normalizeUserDigest(userDigest, globalItems) {
  if (!userDigest) return null

  const matchedItems = Array.isArray(userDigest?.matchedItems)
    ? userDigest.matchedItems.map((item, index) => normalizeJournalItem(item, index))
    : []

  const watchlistStatus = Array.isArray(userDigest?.watchlistStatus)
    ? userDigest.watchlistStatus.map((item) => ({
      ticker: String(item?.ticker || '').trim(),
      price: typeof item?.price === 'number' ? item.price : null,
      target: typeof item?.target === 'number' ? item.target : null,
      stop: typeof item?.stop === 'number' ? item.stop : null,
      note: String(item?.note || '').trim(),
      importance: String(item?.importance || 'normal').trim(),
      flags: Array.isArray(item?.flags) ? item.flags.map((flag) => String(flag || '').trim()).filter(Boolean) : [],
      checkedAt: String(item?.checkedAt || '').trim(),
    }))
    : []

  const matchedTickers = new Set(watchlistStatus.map((item) => item.ticker).filter(Boolean))
  const derivedMatches = globalItems.filter((item) => item.affectedNames.some((name) => matchedTickers.has(name)))

  return {
    userId: String(userDigest?.userId || '').trim(),
    displayName: String(userDigest?.displayName || userDigest?.userId || '').trim(),
    watchlist: Array.isArray(userDigest?.watchlist) ? userDigest.watchlist.map((value) => String(value || '').trim()).filter(Boolean) : [],
    watchlistStatus,
    watchFlags: typeof userDigest?.watchFlags === 'number' ? userDigest.watchFlags : watchlistStatus.reduce((sum, item) => sum + item.flags.length, 0),
    priceError: String(userDigest?.priceError || '').trim(),
    summaryLine: String(userDigest?.summaryLine || '').trim(),
    watchNext: Array.isArray(userDigest?.watchNext) ? userDigest.watchNext.map((value) => String(value || '').trim()).filter(Boolean) : [],
    matchedItemCount: typeof userDigest?.matchedItemCount === 'number' ? userDigest.matchedItemCount : matchedItems.length,
    matchedItemsShown: typeof userDigest?.matchedItemsShown === 'number' ? userDigest.matchedItemsShown : matchedItems.length,
    matchedItems,
    derivedMatches,
    raw: {
      kind: String(userDigest?.kind || '').trim(),
      generatedAt: String(userDigest?.generatedAt || '').trim(),
      globalGeneratedAt: String(userDigest?.globalGeneratedAt || '').trim(),
      globalDigestPathJson: String(userDigest?.globalDigestPathJson || '').trim(),
      globalDigestPathMd: String(userDigest?.globalDigestPathMd || '').trim(),
    },
  }
}

async function readDigestJsonIfExists(filePath) {
  try {
    const raw = await fs.readFile(filePath, 'utf8')
    return JSON.parse(raw)
  } catch {
    return null
  }
}

async function readMarketJournal() {
  const [usersConfig, dayNames] = await Promise.all([
    readJsonFile(DIGEST_USERS_PATH, { users: [] }),
    fs.readdir(DIGESTS_DIR).catch(() => []),
  ])

  const days = dayNames.filter((name) => /^\d{4}-\d{2}-\d{2}$/.test(name)).sort().reverse()
  const windows = ['morning', 'midday', 'evening', 'close']
  const enabledUsers = Array.isArray(usersConfig?.users)
    ? usersConfig.users
      .filter((user) => user?.enabled !== false)
      .map((user) => ({
        userId: String(user?.userId || '').trim(),
        displayName: String(user?.displayName || user?.userId || '').trim(),
      }))
      .filter((user) => user.userId)
    : []

  const entries = []
  for (const day of days) {
    const dayDir = path.join(DIGESTS_DIR, day)
    const dayEntry = { date: day, windows: [] }

    for (const windowId of windows) {
      const globalPath = path.join(dayDir, `${windowId}.json`)
      const globalDigest = await readDigestJsonIfExists(globalPath)
      if (!globalDigest) continue

      const globalItems = Array.isArray(globalDigest?.items)
        ? globalDigest.items.map((item, index) => normalizeJournalItem(item, index))
        : []

      const userEntries = {}
      for (const user of enabledUsers) {
        const userPath = path.join(dayDir, `${windowId}--user--${user.userId}.json`)
        const userDigest = await readDigestJsonIfExists(userPath)
        userEntries[user.userId] = normalizeUserDigest(userDigest, globalItems)
      }

      dayEntry.windows.push({
        id: windowId,
        label: String(globalDigest?.label || windowId).trim(),
        generatedAt: String(globalDigest?.generatedAt || '').trim(),
        windowStart: String(globalDigest?.windowStart || '').trim(),
        windowEnd: String(globalDigest?.windowEnd || '').trim(),
        global: {
          overview: buildGlobalOverview(globalDigest, globalItems),
          stockImpactBoard: buildStockImpactBoard(globalDigest, globalItems),
          items: globalItems,
          raw: {
            timezone: String(globalDigest?.timezone || '').trim(),
            pathJson: path.relative(WORKSPACE, globalPath),
          },
        },
        users: userEntries,
      })
    }

    if (dayEntry.windows.length) entries.push(dayEntry)
  }

  return {
    users: enabledUsers,
    availableDates: entries.map((entry) => entry.date),
    latestDate: entries[0]?.date || null,
    days: entries,
  }
}

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, sessionId: SESSION_ID, mode: 'single-server', host: HOST, port: PORT })
})

app.get('/api/schedule', async (_req, res) => {
  try {
    const [tasks, events, recurring] = await Promise.all([readTasks(), readEvents(), readJsonFile(RECURRING_PATH, [])])
    const scheduledTasks = tasks.filter((task) => task.scheduledStart && task.lane !== 'archive')
    const scheduledEvents = events.filter((event) => event.scheduledStart && event.status !== 'archived')
    res.json({
      ok: true,
      timeZone: SCHEDULE_TIME_ZONE,
      scheduledTasks,
      scheduledEvents,
      needsScheduling: tasks.filter((task) => !task.scheduledStart && task.lane !== 'archive'),
      recurring,
      fetchedAt: new Date().toISOString(),
    })
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

app.get('/api/protocol', async (_req, res) => {
  try {
    const [protocol, recurring] = await Promise.all([readProtocolItems(), readJsonFile(RECURRING_PATH, [])])
    res.json({ ok: true, protocol, recurring, fetchedAt: new Date().toISOString() })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to load protocol.' })
  }
})

app.get('/api/skills', async (_req, res) => {
  try {
    const skills = await readSkills()
    res.json({ ok: true, skills, fetchedAt: new Date().toISOString() })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to load skills.' })
  }
})

app.get('/api/market-journal', async (_req, res) => {
  try {
    const journal = await readMarketJournal()
    res.json({ ok: true, ...journal, fetchedAt: new Date().toISOString() })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to load market journal.' })
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
  const lane = typeof req.body?.lane === 'string' ? req.body.lane : 'workbench'
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

app.get('/api/events', async (_req, res) => {
  try {
    const events = await readEvents()
    res.json({ ok: true, events })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to load events.' })
  }
})

app.post('/api/events', async (req, res) => {
  const title = typeof req.body?.title === 'string' ? req.body.title.trim() : ''
  const notes = typeof req.body?.notes === 'string' ? req.body.notes.trim() : ''
  const description = typeof req.body?.description === 'string' ? req.body.description.trim() : ''
  const owner = typeof req.body?.owner === 'string' ? req.body.owner.trim() : 'haolun'
  const status = typeof req.body?.status === 'string' ? req.body.status : 'active'
  const scheduledStart = typeof req.body?.scheduledStart === 'string' ? req.body.scheduledStart : ''
  const scheduledEnd = typeof req.body?.scheduledEnd === 'string' ? req.body.scheduledEnd : ''
  if (!title) return res.status(400).json({ ok: false, error: 'Event title is required.' })

  try {
    const events = await readEvents()
    const now = new Date().toISOString()
    const event = normalizeEvent({ id: `event-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`, title, notes, description, owner, status, scheduledStart, scheduledEnd, createdAt: now, updatedAt: now })
    events.unshift(event)
    await writeEvents(events)
    res.json({ ok: true, event })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to create event.' })
  }
})

app.patch('/api/events/:id', async (req, res) => {
  try {
    const events = await readEvents()
    const event = events.find((item) => item.id === req.params.id)
    if (!event) return res.status(404).json({ ok: false, error: 'Event not found.' })

    if (typeof req.body?.title === 'string') event.title = req.body.title.trim() || event.title
    if (typeof req.body?.notes === 'string') event.notes = req.body.notes.trim()
    if (typeof req.body?.description === 'string') event.description = req.body.description.trim()
    if (typeof req.body?.owner === 'string') event.owner = req.body.owner.trim() || event.owner
    if (typeof req.body?.status === 'string') event.status = req.body.status
    if (typeof req.body?.scheduledStart === 'string') event.scheduledStart = req.body.scheduledStart
    if (typeof req.body?.scheduledEnd === 'string') event.scheduledEnd = req.body.scheduledEnd
    event.updatedAt = new Date().toISOString()

    const normalized = normalizeEvent(event)
    const nextEvents = events.map((item) => (item.id === normalized.id ? normalized : item))
    await writeEvents(nextEvents)
    res.json({ ok: true, event: normalized })
  } catch (error) {
    res.status(500).json({ ok: false, error: error.message || 'Failed to update event.' })
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
