export const lanes = [
  { id: 'capture', title: 'Capture Tray', analogy: 'New requests that just landed on the desk.' },
  { id: 'workbench', title: 'Workbench', analogy: 'Things hazoc is actively shaping right now.' },
  { id: 'parking', title: 'Parking Lot', analogy: 'Postponed, blocked, or waiting for a later moment.' },
  { id: 'archive', title: 'Archive Shelf', analogy: 'Done, settled, or remembered well enough to shelve.' },
]

export const descriptionTemplate = `Project memory\n\nGoal\n- \n\nWhat is known\n- \n\nWhat has been done\n- \n\nBlockers / unknowns\n- \n\nNext steps\n- `
export const scheduleTimeZone = 'America/New_York'

export const storageKeys = {
  page: 'mission-control:page',
  selectedTaskId: 'mission-control:selected-task-id',
  calendarMonth: 'mission-control:calendar-month',
  selectedMemoryId: 'mission-control:selected-memory-id',
}

export function readStorage(key, fallback) {
  if (typeof window === 'undefined') return fallback
  try {
    return window.localStorage.getItem(key) ?? fallback
  } catch {
    return fallback
  }
}

export function writeStorage(key, value) {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(key, value)
  } catch {
    // ignore storage failures
  }
}

export function getTimeZoneParts(input, timeZone) {
  const date = input instanceof Date ? input : new Date(input)
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone,
    hour12: false,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })

  const parts = {}
  for (const part of formatter.formatToParts(date)) {
    if (part.type !== 'literal') parts[part.type] = part.value
  }

  return parts
}

export function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString([], { month: 'short', day: 'numeric' })
}

export function formatDateTime(dateString) {
  if (!dateString) return 'No time set'
  return new Intl.DateTimeFormat([], {
    timeZone: scheduleTimeZone,
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(dateString))
}

export function toInputValueInZone(dateString, timeZone) {
  if (!dateString) return ''
  const parts = getTimeZoneParts(dateString, timeZone)
  return `${parts.year}-${parts.month}-${parts.day}T${parts.hour}:${parts.minute}`
}

export function fromInputValueInZone(value, timeZone) {
  if (!value) return ''
  const [datePart, timePart] = value.split('T')
  const [year, month, day] = datePart.split('-').map(Number)
  const [hour, minute] = timePart.split(':').map(Number)
  let guess = Date.UTC(year, month - 1, day, hour, minute)
  const target = Date.UTC(year, month - 1, day, hour, minute)

  for (let i = 0; i < 4; i += 1) {
    const parts = getTimeZoneParts(new Date(guess), timeZone)
    const got = Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day), Number(parts.hour), Number(parts.minute))
    const diff = target - got
    if (diff === 0) break
    guess += diff
  }

  return new Date(guess).toISOString()
}

export function startOfCalendarGrid(monthDate) {
  const first = new Date(monthDate.getFullYear(), monthDate.getMonth(), 1)
  const start = new Date(first)
  start.setDate(first.getDate() - first.getDay())
  return start
}

export function laneMeta(laneId) {
  return lanes.find((lane) => lane.id === laneId) || lanes[0]
}

export function calendarCellKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function dateKeyInZone(dateString, timeZone) {
  const parts = getTimeZoneParts(dateString, timeZone)
  return `${parts.year}-${parts.month}-${parts.day}`
}

export function sortTasks(a, b) {
  const aScheduled = a.scheduledStart ? new Date(a.scheduledStart).getTime() : null
  const bScheduled = b.scheduledStart ? new Date(b.scheduledStart).getTime() : null
  if (aScheduled !== null && bScheduled !== null && aScheduled !== bScheduled) return aScheduled - bScheduled
  if (aScheduled !== null) return -1
  if (bScheduled !== null) return 1
  return new Date(b.updatedAt || b.createdAt).getTime() - new Date(a.updatedAt || a.createdAt).getTime()
}

export function nextRecurringDue(item) {
  if (item.everyMinutes && item.everyMinutes > 0) {
    const now = new Date()
    const intervalMs = item.everyMinutes * 60 * 1000
    const anchorMinute = Number.isFinite(item.anchorMinute) ? item.anchorMinute : 0
    const anchor = new Date(now)
    anchor.setSeconds(0, 0)
    anchor.setMinutes(anchorMinute)

    if (now <= anchor) return formatDateTime(anchor.toISOString())

    const elapsed = now.getTime() - anchor.getTime()
    const next = new Date(anchor.getTime() + Math.ceil(elapsed / intervalMs) * intervalMs)
    return formatDateTime(next.toISOString())
  }

  if (!item.everyHours || item.everyHours <= 0) return 'Continuous'
  const now = new Date()
  const hourMs = item.everyHours * 60 * 60 * 1000
  const next = new Date(Math.ceil(now.getTime() / hourMs) * hourMs)
  return formatDateTime(next.toISOString())
}

export async function requestJson(url, options) {
  const response = await fetch(url, options)
  const text = await response.text()
  let data = null

  try {
    data = text ? JSON.parse(text) : null
  } catch {
    throw new Error(`Expected JSON from ${url}, got ${text.slice(0, 80)}`)
  }

  if (!response.ok || (data && data.ok === false)) {
    throw new Error(data?.error || `Request failed for ${url}`)
  }

  return data
}
