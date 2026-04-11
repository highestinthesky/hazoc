import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  calendarCellKey,
  compactTextPreview,
  dateKeyInZone,
  descriptionTemplate,
  formatDate,
  formatDateTime,
  formatTime,
  fromInputValueInZone,
  laneMeta,
  lanes,
  nextRecurringDue,
  readStorage,
  requestJson,
  scheduleTimeZone,
  sortTasks,
  startOfCalendarGrid,
  storageKeys,
  toInputValueInZone,
  writeStorage,
} from './lib/mission-control'

function HeroCard({ label, title, children, primary = false }) {
  return (
    <article className={`hero-card ${primary ? 'primary' : ''}`}>
      <span className="hero-label">{label}</span>
      <strong>{title}</strong>
      {children ? <p>{children}</p> : null}
    </article>
  )
}

function SegmentedControl({ ariaLabel, className = '', onChange, options, value }) {
  return (
    <div className={`segmented-control ${className}`.trim()} role="radiogroup" aria-label={ariaLabel}>
      {options.map((option) => {
        const active = option.value === value
        return (
          <button
            key={option.value}
            type="button"
            role="radio"
            aria-checked={active}
            className={`segmented-control-option tone-${option.value} ${active ? 'active' : ''}`}
            onClick={(event) => {
              event.stopPropagation()
              if (!active) onChange(option.value)
            }}
          >
            <span className="segmented-control-dot" aria-hidden="true" />
            <span className="segmented-control-label">{option.label}</span>
          </button>
        )
      })}
    </div>
  )
}

const FLOWCHART_KEY = [
  { kind: 'terminator', label: 'Terminator' },
  { kind: 'process', label: 'Process' },
  { kind: 'data', label: 'Data / record' },
  { kind: 'decision', label: 'Decision' },
]

const GRAPHABLE_SKILLS = new Set([
  'grounded-evolver',
  'learning-loop',
  'safe-evolution-loop',
  'workspace-continuity',
  'workspace-memory-stack',
  'workspace-graph',
])

const SKILL_FLOWCHARTS = {
  'grounded-evolver': {
    title: 'Grounded-evolver algorithm',
    subtitle: 'Signal → generalize → score → mutate → validate → record',
    cols: 6,
    rows: 8,
    nodes: [
      { id: 'start', label: 'Start', kind: 'terminator', col: 1, row: 1 },
      { id: 'signal', label: 'Observe signal', kind: 'process', col: 2.2, row: 1 },
      { id: 'root', label: 'State root cause', kind: 'process', col: 3.5, row: 1 },
      { id: 'moral', label: 'Generalize reusable moral', kind: 'data', col: 4.8, row: 1 },
      { id: 'score', label: 'Score impact / loss / repeat / structure', kind: 'process', col: 4.8, row: 2.35 },
      { id: 'decision', label: 'Memory / task / rule enough?', kind: 'decision', col: 4.8, row: 3.7 },
      { id: 'small', label: 'Choose smallest safe mutation', kind: 'process', col: 2.7, row: 5 },
      { id: 'patch', label: 'Patch workflow / skill', kind: 'process', col: 6, row: 5 },
      { id: 'validate', label: 'Fix follows\nthat moral?', kind: 'decision', col: 4.8, row: 6.2 },
      { id: 'record', label: 'Record + re-anchor', kind: 'data', col: 4.8, row: 7.4 },
      { id: 'stop', label: 'Stop', kind: 'terminator', col: 6, row: 7.4 },
    ],
    edges: [
      { from: 'start', to: 'signal', fromAnchor: 'right', toAnchor: 'left' },
      { from: 'signal', to: 'root', fromAnchor: 'right', toAnchor: 'left' },
      { from: 'root', to: 'moral', fromAnchor: 'right', toAnchor: 'left' },
      { from: 'moral', to: 'score', fromAnchor: 'bottom', toAnchor: 'top' },
      { from: 'score', to: 'decision', fromAnchor: 'bottom', toAnchor: 'top' },
      { from: 'decision', to: 'small', fromAnchor: 'left', toAnchor: 'top', turn: 'hv', label: 'Yes', labelAt: [3.12, 3.5] },
      { from: 'decision', to: 'patch', fromAnchor: 'right', toAnchor: 'top', turn: 'hv', label: 'No', labelAt: [5.72, 3.5] },
      { from: 'small', to: 'validate', fromAnchor: 'bottom', toAnchor: 'left', turn: 'vh' },
      { from: 'patch', to: 'validate', fromAnchor: 'bottom', toAnchor: 'right', turn: 'vh' },
      { from: 'validate', to: 'record', fromAnchor: 'bottom', toAnchor: 'top', label: 'Pass', labelAt: [5.15, 6.8] },
      { from: 'record', to: 'stop', fromAnchor: 'right', toAnchor: 'left' },
    ],
  },
  'learning-loop': {
    title: 'Learning-loop algorithm',
    subtitle: 'Notice friction → route lesson → promote when stable',
    cols: 6,
    rows: 9,
    nodes: [
      { id: 'start', label: 'Start', kind: 'terminator', col: 1, row: 1 },
      { id: 'trigger', label: 'Notice correction / failure / request', kind: 'process', col: 2.35, row: 1 },
      { id: 'exists', label: 'Existing\nlesson fits?', kind: 'decision', col: 3.9, row: 1 },
      { id: 'merge', label: 'Merge into existing lesson', kind: 'process', col: 2.3, row: 3.1 },
      { id: 'route', label: 'Choose smallest durable destination', kind: 'process', col: 5.35, row: 3.1 },
      { id: 'stable', label: 'Ready to\npromote?', kind: 'decision', col: 3.9, row: 4.9 },
      { id: 'promote', label: 'Promote to durable home', kind: 'process', col: 2.4, row: 6.8 },
      { id: 'log', label: 'Log raw lesson / daily note', kind: 'data', col: 5.4, row: 6.8 },
      { id: 'stop', label: 'Stop', kind: 'terminator', col: 3.9, row: 8.1 },
    ],
    edges: [
      { from: 'start', to: 'trigger', fromAnchor: 'right', toAnchor: 'left' },
      { from: 'trigger', to: 'exists', fromAnchor: 'right', toAnchor: 'left' },
      { from: 'exists', to: 'merge', fromAnchor: 'bottom', toAnchor: 'top', turn: 'vh', label: 'Yes', labelAt: [2.7, 1.55] },
      { from: 'exists', to: 'route', fromAnchor: 'right', toAnchor: 'top', turn: 'hv', label: 'No', labelAt: [5.05, 1.35] },
      { from: 'merge', to: 'stable', fromAnchor: 'bottom', toAnchor: 'left', turn: 'vh' },
      { from: 'route', to: 'stable', fromAnchor: 'bottom', toAnchor: 'right', turn: 'vh' },
      { from: 'stable', to: 'promote', fromAnchor: 'left', toAnchor: 'top', turn: 'hv', label: 'Yes', labelAt: [2.72, 5.2] },
      { from: 'stable', to: 'log', fromAnchor: 'right', toAnchor: 'top', turn: 'hv', label: 'No', labelAt: [5.08, 5.2] },
      { from: 'promote', to: 'stop', fromAnchor: 'bottom', toAnchor: 'left', turn: 'vh' },
      { from: 'log', to: 'stop', fromAnchor: 'bottom', toAnchor: 'right', turn: 'vh' },
    ],
  },
  'workspace-memory-stack': {
    title: 'Workspace-memory-stack routing',
    subtitle: 'Capture fragile context in the smallest layer that will survive the next interruption',
    cols: 6,
    rows: 9,
    nodes: [
      { id: 'start', label: 'Start', kind: 'terminator', col: 1, row: 1 },
      { id: 'detail', label: 'New detail / progress appears', kind: 'process', col: 2.4, row: 1 },
      { id: 'fragile', label: 'Easy to lose\nbefore replying?', kind: 'decision', col: 4, row: 1 },
      { id: 'active', label: 'Write active state', kind: 'data', col: 2.2, row: 3.05 },
      { id: 'project', label: 'Project work\nor follow-up?', kind: 'decision', col: 5.5, row: 3.05 },
      { id: 'tasks', label: 'Update task board', kind: 'data', col: 5.5, row: 4.6 },
      { id: 'meaningful', label: 'Meaningful\nprogress / decision?', kind: 'decision', col: 3.9, row: 5.9 },
      { id: 'daily', label: 'Append daily note', kind: 'data', col: 2.2, row: 7.3 },
      { id: 'durable', label: 'Curated-memory\nworthy?', kind: 'decision', col: 5.45, row: 7.3 },
      { id: 'curated', label: 'Promote to USER / MEMORY / AGENTS', kind: 'data', col: 5.45, row: 8.65 },
      { id: 'stop', label: 'Stop / handoff', kind: 'terminator', col: 3.9, row: 8.65 },
    ],
    edges: [
      { from: 'start', to: 'detail', fromAnchor: 'right', toAnchor: 'left' },
      { from: 'detail', to: 'fragile', fromAnchor: 'right', toAnchor: 'left' },
      { from: 'fragile', to: 'active', fromAnchor: 'bottom', toAnchor: 'top', turn: 'vh', label: 'Yes', labelAt: [2.8, 1.55] },
      { from: 'fragile', to: 'project', fromAnchor: 'right', toAnchor: 'top', turn: 'hv', label: 'No', labelAt: [5.12, 1.35] },
      { from: 'active', to: 'meaningful', fromAnchor: 'bottom', toAnchor: 'left', turn: 'vh' },
      { from: 'project', to: 'tasks', fromAnchor: 'bottom', toAnchor: 'top', label: 'Yes', labelAt: [5.86, 3.82] },
      { from: 'project', to: 'meaningful', fromAnchor: 'left', toAnchor: 'top', turn: 'hv', label: 'No', labelAt: [4.18, 3.25] },
      { from: 'tasks', to: 'meaningful', fromAnchor: 'bottom', toAnchor: 'right', turn: 'vh' },
      { from: 'meaningful', to: 'daily', fromAnchor: 'left', toAnchor: 'top', turn: 'hv', label: 'Yes', labelAt: [2.62, 6.12] },
      { from: 'meaningful', to: 'durable', fromAnchor: 'right', toAnchor: 'top', turn: 'hv', label: 'No', labelAt: [5.1, 6.12] },
      { from: 'daily', to: 'stop', fromAnchor: 'bottom', toAnchor: 'left', turn: 'vh' },
      { from: 'durable', to: 'curated', fromAnchor: 'bottom', toAnchor: 'top', label: 'Yes', labelAt: [5.82, 8.0] },
      { from: 'durable', to: 'stop', fromAnchor: 'left', toAnchor: 'top', turn: 'hv', label: 'No', labelAt: [4.15, 7.55] },
      { from: 'curated', to: 'stop', fromAnchor: 'left', toAnchor: 'right' },
    ],
  },
}

function getFlowchartMetrics(chart) {
  const cellWidth = chart.cellWidth || 122
  const cellHeight = chart.cellHeight || 74
  const paddingX = chart.paddingX || 62
  const paddingY = chart.paddingY || 60

  let width = paddingX * 2 + (chart.cols - 1) * cellWidth
  let height = paddingY * 2 + (chart.rows - 1) * cellHeight

  for (const node of chart.nodes) {
    const { width: nodeWidth, height: nodeHeight } = getNodeDimensions(node.kind)
    const centerX = paddingX + (node.col - 1) * cellWidth
    const centerY = paddingY + (node.row - 1) * cellHeight
    width = Math.max(width, centerX + nodeWidth / 2 + paddingX)
    height = Math.max(height, centerY + nodeHeight / 2 + paddingY)
  }

  return { cellWidth, cellHeight, paddingX, paddingY, width, height }
}

function getNodeDimensions(kind) {
  if (kind === 'terminator') return { width: 96, height: 40 }
  if (kind === 'process') return { width: 128, height: 56 }
  if (kind === 'data') return { width: 126, height: 54 }
  if (kind === 'decision') return { width: 84, height: 84 }
  return { width: 140, height: 60 }
}

function gridToCanvasPoint(point, metrics) {
  const [col, row] = point
  return {
    x: metrics.paddingX + (col - 1) * metrics.cellWidth,
    y: metrics.paddingY + (row - 1) * metrics.cellHeight,
  }
}

function nodeAnchorPoint(node, anchor, metrics) {
  const center = gridToCanvasPoint([node.col, node.row], metrics)
  const { width, height } = getNodeDimensions(node.kind)

  if (anchor === 'left') return { x: center.x - width / 2, y: center.y }
  if (anchor === 'right') return { x: center.x + width / 2, y: center.y }
  if (anchor === 'top') return { x: center.x, y: center.y - height / 2 }
  if (anchor === 'bottom') return { x: center.x, y: center.y + height / 2 }
  return center
}

function buildEdgePoints(fromPoint, toPoint, turn) {
  if (fromPoint.x === toPoint.x || fromPoint.y === toPoint.y || !turn) return [fromPoint, toPoint]
  if (turn === 'hv') return [fromPoint, { x: toPoint.x, y: fromPoint.y }, toPoint]
  if (turn === 'vh') return [fromPoint, { x: fromPoint.x, y: toPoint.y }, toPoint]
  return [fromPoint, toPoint]
}

function orthogonalizePoints(points) {
  const cleaned = []

  for (const point of points) {
    if (!point) continue
    const last = cleaned[cleaned.length - 1]
    if (!last) {
      cleaned.push(point)
      continue
    }

    if (last.x === point.x && last.y === point.y) continue

    if (last.x !== point.x && last.y !== point.y) {
      cleaned.push({ x: point.x, y: last.y })
    }

    cleaned.push(point)
  }

  return cleaned.filter((point, index, array) => {
    if (index === 0 || index === array.length - 1) return true
    const prev = array[index - 1]
    const next = array[index + 1]
    const sameVertical = prev.x === point.x && point.x === next.x
    const sameHorizontal = prev.y === point.y && point.y === next.y
    return !sameVertical && !sameHorizontal
  })
}

function buildRoundedOrthogonalPath(points, radius = 12) {
  const routed = orthogonalizePoints(points)
  if (routed.length < 2) return ''

  let path = `M ${routed[0].x} ${routed[0].y}`

  for (let i = 1; i < routed.length - 1; i += 1) {
    const prev = routed[i - 1]
    const curr = routed[i]
    const next = routed[i + 1]

    const inDx = curr.x - prev.x
    const inDy = curr.y - prev.y
    const outDx = next.x - curr.x
    const outDy = next.y - curr.y

    const inLen = Math.abs(inDx) + Math.abs(inDy)
    const outLen = Math.abs(outDx) + Math.abs(outDy)

    if (!inLen || !outLen) continue

    const sameDirection = (inDx === 0 && outDx === 0) || (inDy === 0 && outDy === 0)
    if (sameDirection) {
      path += ` L ${curr.x} ${curr.y}`
      continue
    }

    const trim = Math.min(radius, inLen / 2, outLen / 2)
    const inUnit = { x: Math.sign(inDx), y: Math.sign(inDy) }
    const outUnit = { x: Math.sign(outDx), y: Math.sign(outDy) }
    const entry = { x: curr.x - inUnit.x * trim, y: curr.y - inUnit.y * trim }
    const exit = { x: curr.x + outUnit.x * trim, y: curr.y + outUnit.y * trim }

    path += ` L ${entry.x} ${entry.y} Q ${curr.x} ${curr.y} ${exit.x} ${exit.y}`
  }

  const last = routed[routed.length - 1]
  path += ` L ${last.x} ${last.y}`
  return path
}

function FlowchartLegend() {
  return (
    <div className="flowchart-legend-card">
      <p className="panel-kicker">flowchart key</p>
      <div className="flowchart-legend-list">
        {FLOWCHART_KEY.map((item) => (
          <div key={item.kind} className="flowchart-legend-item">
            <span className={`flowchart-legend-shape kind-${item.kind}`} aria-hidden="true" />
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function SkillFlowchart({ chart }) {
  const metrics = getFlowchartMetrics(chart)
  const nodesById = Object.fromEntries(chart.nodes.map((node) => [node.id, node]))
  const viewportRef = useRef(null)
  const [scale, setScale] = useState(1)

  useEffect(() => {
    if (!viewportRef.current) return undefined

    const updateScale = () => {
      const width = viewportRef.current?.clientWidth || 0
      if (!width) return
      const gutter = Math.max(56, Math.min(110, width * 0.1))
      const usableWidth = Math.max(width - gutter * 2, width * 0.78)
      setScale(Math.max(0.82, usableWidth / metrics.width))
    }

    updateScale()
    const observer = new ResizeObserver(() => updateScale())
    observer.observe(viewportRef.current)
    return () => observer.disconnect()
  }, [metrics.width])

  return (
    <div className="flowchart-stage">
      <div className="flowchart-stage-header">
        <div>
          <p className="panel-kicker">algorithm chart</p>
          <h3>{chart.title}</h3>
          <p className="flowchart-subtitle">{chart.subtitle}</p>
        </div>
        <FlowchartLegend />
      </div>

      <div ref={viewportRef} className="flowchart-viewport">
        <div className="flowchart-scale-wrap">
          <div className="flowchart-canvas" style={{ width: metrics.width * scale, height: metrics.height * scale }}>
            <div className="flowchart-canvas-inner" style={{ width: metrics.width, height: metrics.height, transform: `scale(${scale})` }}>
              <svg className="flowchart-svg" viewBox={`0 0 ${metrics.width} ${metrics.height}`} preserveAspectRatio="xMidYMid meet" aria-hidden="true">
              <defs>
                <marker id="flowchart-arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto" markerUnits="strokeWidth">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
                </marker>
              </defs>

              {chart.edges.map((edge) => {
                const fromNode = nodesById[edge.from]
                const toNode = nodesById[edge.to]
                if (!fromNode || !toNode) return null
                const points = buildEdgePoints(
                  nodeAnchorPoint(fromNode, edge.fromAnchor, metrics),
                  nodeAnchorPoint(toNode, edge.toAnchor, metrics),
                  edge.turn,
                )
                const edgePath = buildRoundedOrthogonalPath(points)
                const labelPoint = edge.labelAt ? gridToCanvasPoint(edge.labelAt, metrics) : null

                return (
                  <g key={`${edge.from}-${edge.to}-${edge.label || 'path'}`} className="flowchart-edge-group">
                    <path className="flowchart-edge" d={edgePath} markerEnd="url(#flowchart-arrow)" />
                    {edge.label && labelPoint ? (
                      <g className="flowchart-edge-label" transform={`translate(${labelPoint.x}, ${labelPoint.y})`}>
                        <rect x="-18" y="-11" width="36" height="22" rx="11" />
                        <text textAnchor="middle" dominantBaseline="central">{edge.label}</text>
                      </g>
                    ) : null}
                  </g>
                )
              })}
              </svg>

              {chart.nodes.map((node) => {
                const point = gridToCanvasPoint([node.col, node.row], metrics)
                return (
                  <div key={node.id} className={`flowchart-node kind-${node.kind}`} style={{ left: point.x, top: point.y }}>
                    <div className="flowchart-node-label">{node.label}</div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function TasksView({
  activeLaneId,
  activeLaneTasks,
  error,
  loading,
  selectedTask,
  selectedTaskId,
  detailTitle,
  setDetailTitle,
  detailNotes,
  setDetailNotes,
  detailDescription,
  setDetailDescription,
  detailLane,
  setDetailLane,
  detailScheduledStart,
  setDetailScheduledStart,
  detailScheduledEnd,
  setDetailScheduledEnd,
  detailSaving,
  laneCounts,
  moveTask,
  saveTaskDetails,
  setActiveLaneId,
  setSelectedTaskId,
  sortedTasks,
  unscheduledActiveTasks,
}) {
  const activeLaneMeta = laneMeta(activeLaneId)

  return (
    <section className="tasks-layout">
      <div className="hero-row hero-row-tasks">
        <HeroCard label="Live tasks" title={String(sortedTasks.filter((task) => task.lane !== 'archive').length)} primary />
        <HeroCard label="Workbench" title={String(laneCounts.get('workbench') || 0)} />
        <HeroCard label="Need scheduling" title={String(unscheduledActiveTasks.length)} />
      </div>

      <section className="panel task-sections-panel">
        <div className="panel-header task-sections-header">
          <div>
            <p className="panel-kicker">task sections</p>
            <h2>Choose a subsection</h2>
          </div>
        </div>

        <div className="lane-tabs" role="tablist" aria-label="Task sections">
          {lanes.map((lane) => (
            <button
              key={lane.id}
              type="button"
              className={`lane-tab lane-${lane.id} ${activeLaneId === lane.id ? 'active' : ''}`}
              onClick={() => setActiveLaneId(lane.id)}
            >
              <span className="lane-tab-kicker">{lane.title}</span>
              <strong>{laneCounts.get(lane.id) || 0}</strong>
              <small>{lane.analogy}</small>
            </button>
          ))}
        </div>
      </section>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className={`workspace-grid tasks-workspace-grid tasks-workspace-grid-${activeLaneId}`}>
        <section className={`panel lane-detail-stack lane-${activeLaneId}`}>
          <div className="lane-header lane-header-dense">
            <div>
              <p className="panel-kicker">{activeLaneMeta.title}</p>
              <h2>{activeLaneMeta.analogy}</h2>
            </div>
            <span className="lane-count">{activeLaneTasks.length}</span>
          </div>

          <div className="task-list task-list-dense">
            {!loading && !activeLaneTasks.length ? <div className="lane-empty">Nothing here right now.</div> : null}
            {activeLaneTasks.map((task) => {
              const isArchiveCard = activeLaneId === 'archive'
              const preview = isArchiveCard ? task.notes : task.notes || compactTextPreview(task.description, 220)
              return (
                <article
                  key={task.id}
                  className={`task-card task-card-dense ${selectedTaskId === task.id ? 'active' : ''} ${isArchiveCard ? 'task-card-archive' : ''}`}
                  onClick={() => setSelectedTaskId(task.id)}
                >
                  <div className="task-card-main">
                    <div className="task-card-header">
                      <div className="task-card-title-wrap">
                        <strong>{task.title}</strong>
                      </div>
                      <span>{formatDate(task.updatedAt || task.createdAt)}</span>
                    </div>

                    <div className="task-card-meta-row">
                      <span className={`meta-chip lane-chip lane-${task.lane}`}>{laneMeta(task.lane).title}</span>
                      {task.scheduledStart ? <span className="meta-chip">🗓 {formatDateTime(task.scheduledStart)}</span> : null}
                      {!isArchiveCard ? <span className="meta-chip">Updated {formatDate(task.updatedAt || task.createdAt)}</span> : null}
                    </div>

                    {preview ? <p className="task-preview">{preview}</p> : null}
                  </div>

                  <div className="task-card-footer task-card-footer-dense" onClick={(event) => event.stopPropagation()}>
                    <SegmentedControl
                      ariaLabel={`Move ${task.title} to section`}
                      className="task-lane-control"
                      value={task.lane}
                      options={lanes.map((option) => ({ value: option.id, label: option.title }))}
                      onChange={(nextLane) => moveTask(task.id, nextLane)}
                    />
                  </div>
                </article>
              )
            })}
          </div>
        </section>

        <aside className="detail-panel panel task-detail-panel">
          {selectedTask ? (
            <>
              <section className="detail-hero">
                <div>
                  <p className="panel-kicker">task memory</p>
                  <h2>{selectedTask.title}</h2>
                </div>
                <div className="detail-chip-row">
                  <span className={`meta-chip lane-chip lane-${detailLane}`}>{laneMeta(detailLane).title}</span>
                  <span className="meta-chip">Created {formatDate(selectedTask.createdAt)}</span>
                  <span className="meta-chip">Updated {formatDate(selectedTask.updatedAt || selectedTask.createdAt)}</span>
                  <span className="meta-chip">{detailScheduledStart ? formatDateTime(fromInputValueInZone(detailScheduledStart, scheduleTimeZone)) : 'No scheduled time'}</span>
                </div>
              </section>

              <div className="detail-form detail-form-polished">
                <section className="form-section form-section-soft">
                  <div className="section-heading">
                    <p className="panel-kicker">essentials</p>
                    <h3>Core task details</h3>
                  </div>
                  <div className="detail-grid two-up">
                    <label className="field-block field-block-wide">
                      <span>Title</span>
                      <input value={detailTitle} onChange={(event) => setDetailTitle(event.target.value)} />
                    </label>
                    <div className="field-block">
                      <span>Section</span>
                      <SegmentedControl
                        ariaLabel="Task section"
                        className="detail-segmented-control"
                        value={detailLane}
                        options={lanes.map((lane) => ({ value: lane.id, label: lane.title }))}
                        onChange={setDetailLane}
                      />
                    </div>
                    <label className="field-block field-block-wide">
                      <span>Short notes</span>
                      <textarea value={detailNotes} onChange={(event) => setDetailNotes(event.target.value)} rows={4} />
                    </label>
                  </div>
                </section>

                <section className="form-section form-section-accent">
                  <div className="section-heading">
                    <p className="panel-kicker">schedule</p>
                    <h3>Timing in {scheduleTimeZone}</h3>
                  </div>
                  <div className="schedule-edit-grid refined-grid">
                    <label className="field-block">
                      <span>Scheduled start</span>
                      <input type="datetime-local" value={detailScheduledStart} onChange={(event) => setDetailScheduledStart(event.target.value)} />
                    </label>
                    <label className="field-block">
                      <span>Scheduled end</span>
                      <input type="datetime-local" value={detailScheduledEnd} onChange={(event) => setDetailScheduledEnd(event.target.value)} />
                    </label>
                  </div>
                  <div className="schedule-preview-row">
                    <div className="schedule-preview-card">
                      <span className="schedule-preview-label">Starts</span>
                      <strong>{detailScheduledStart ? formatDateTime(fromInputValueInZone(detailScheduledStart, scheduleTimeZone)) : 'Not set yet'}</strong>
                    </div>
                    <div className="schedule-preview-card">
                      <span className="schedule-preview-label">Ends</span>
                      <strong>{detailScheduledEnd ? formatDateTime(fromInputValueInZone(detailScheduledEnd, scheduleTimeZone)) : 'Not set yet'}</strong>
                    </div>
                  </div>
                </section>

                <section className="form-section form-section-memory">
                  <div className="section-heading">
                    <p className="panel-kicker">project memory</p>
                    <h3>Long-form context</h3>
                  </div>
                  <label className="field-block field-block-wide">
                    <span>Detailed project memory</span>
                    <textarea className="memory-textarea" value={detailDescription} onChange={(event) => setDetailDescription(event.target.value)} rows={18} />
                  </label>
                </section>

                <div className="detail-save-row">
                  <div className="save-note">Section changes apply immediately. Save after updating title, notes, schedule, or project memory.</div>
                  <button type="button" className="save-button" onClick={saveTaskDetails} disabled={detailSaving}>
                    {detailSaving ? 'Saving…' : 'Save task memory'}
                  </button>
                </div>
              </div>
            </>
          ) : <div className="lane-empty">Select a task to open its project memory.</div>}
        </aside>
      </section>
    </section>
  )
}

function ProtocolView({ error, protocolItems, protocolLoaded, recurring }) {
  return (
    <section className="tasks-layout">
      <div className="hero-row">
        <HeroCard label="Standing protocol" title={String(protocolItems.length)} primary />
        <HeroCard label="Recurring rhythm" title={String(recurring.length)} />
        <HeroCard label="Continuous items" title={String(protocolItems.filter((item) => item.cadence === 'continuous').length)} />
      </div>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="workspace-grid protocol-grid">
        <section className="panel protocol-panel protocol-panel-standing">
          <div className="lane-header lane-header-dense">
            <div>
              <p className="panel-kicker">standing protocol</p>
              <h2>Default operating rules</h2>
            </div>
            <span className="lane-count">{protocolItems.length}</span>
          </div>
          {!protocolLoaded && !protocolItems.length ? (
            <div className="lane-empty">Loading protocol…</div>
          ) : !protocolItems.length ? (
            <div className="lane-empty">No standing protocol items are stored yet.</div>
          ) : (
            <div className="upcoming-list">
              {protocolItems.map((item) => (
                <article key={item.id} className="upcoming-card protocol-card">
                  <div className="task-card-header">
                    <strong>{item.title}</strong>
                    <span>{item.category}</span>
                  </div>
                  <p>{item.summary}</p>
                  <small>Cadence: {item.cadence}</small>
                </article>
              ))}
            </div>
          )}
        </section>

        <aside className="protocol-stack">
          <section className="panel protocol-panel protocol-panel-recurring">
            <div className="lane-header lane-header-dense">
              <div>
                <p className="panel-kicker">recurring rhythm</p>
                <h2>Repeating duties</h2>
              </div>
              <span className="lane-count">{recurring.length}</span>
            </div>
            {!protocolLoaded && !recurring.length ? (
              <div className="lane-empty">Loading recurring duties…</div>
            ) : !recurring.length ? (
              <div className="lane-empty">No recurring duties are configured right now.</div>
            ) : (
              <div className="upcoming-list compact-list">
                {recurring.map((item) => (
                  <article key={item.id} className="upcoming-card compact recurring-card">
                    <div className="task-card-header">
                      <strong>{item.title}</strong>
                      <span>{item.cadence}</span>
                    </div>
                    <p>{item.summary}</p>
                    <small>Next due: {nextRecurringDue(item)}</small>
                  </article>
                ))}
              </div>
            )}
          </section>

        </aside>
      </section>
    </section>
  )
}

function ScheduleView({
  calendarDays,
  calendarMonth,
  error,
  nextScheduledEvent,
  onScheduleDraftKeyDown,
  openEvent,
  openTask,
  scheduleDraft,
  scheduleMessages,
  scheduleSending,
  scheduleThreadRef,
  scheduledEvents,
  scheduledTasks,
  scheduleLoaded,
  sendScheduleRequest,
  setCalendarMonth,
  setScheduleDraft,
  unscheduledActiveTasks,
}) {
  const hasSchedule = scheduledEvents.length > 0

  return (
    <section className="tasks-layout">
      <div className="hero-row">
        <HeroCard label="Scheduled events" title={String(scheduledEvents.length)} primary />
        <HeroCard label="Next event" title={nextScheduledEvent ? formatDateTime(nextScheduledEvent.scheduledStart) : 'None yet'}>
          {nextScheduledEvent ? nextScheduledEvent.title : null}
        </HeroCard>
        <HeroCard label="Unplaced work" title={String(unscheduledActiveTasks.length)} />
      </div>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="workspace-grid schedule-layout-grid">
        <section className="panel calendar-panel">
          <div className="calendar-toolbar">
            <button
              type="button"
              className="icon-button"
              onClick={() => setCalendarMonth(new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() - 1, 1))}
            >
              ←
            </button>
            <div>
              <p className="panel-kicker">planned calendar</p>
              <h2>{calendarMonth.toLocaleDateString([], { month: 'long', year: 'numeric' })}</h2>
            </div>
            <div className="calendar-toolbar-actions">
              <button type="button" className="toolbar-button" onClick={() => setCalendarMonth(new Date())}>Today</button>
              <button
                type="button"
                className="icon-button"
                onClick={() => setCalendarMonth(new Date(calendarMonth.getFullYear(), calendarMonth.getMonth() + 1, 1))}
              >
                →
              </button>
            </div>
          </div>

          <div className="calendar-weekdays">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((day) => <span key={day}>{day}</span>)}
          </div>

          <div className="calendar-grid calendar-grid-large">
            {calendarDays.map((day) => (
              <article key={day.key} className={`calendar-cell ${day.inMonth ? '' : 'muted'} ${day.isToday ? 'today' : ''} ${day.entries.length ? 'has-events' : ''}`}>
                <div className="calendar-date-row">
                  <div className="calendar-date">{day.date.getDate()}</div>
                  {day.entries.length ? <div className="calendar-date-count">{day.entries.length}</div> : null}
                </div>
                <div className="calendar-events">
                  {day.entries.slice(0, 4).map((event) => (
                    <button key={event.id} type="button" className="calendar-pill calendar-pill-event" onClick={() => openEvent(event.id)}>
                      <span className="calendar-pill-time">{formatTime(event.scheduledStart)}</span>
                      <span className="calendar-pill-title">{event.title}</span>
                    </button>
                  ))}
                  {day.entries.length > 4 ? <span className="calendar-more">+{day.entries.length - 4} more</span> : null}
                </div>
              </article>
            ))}
          </div>
        </section>

        <aside className="schedule-sidebar-grid">
          <section className="panel schedule-side-panel schedule-side-panel-intake">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">direct to hazoc</p>
                <h2>Schedule requests</h2>
              </div>
            </div>

            <div className="schedule-chat-thread" ref={scheduleThreadRef}>
              {scheduleMessages.map((message) => (
                <article key={message.id} className={`schedule-chat-bubble ${message.role === 'assistant' ? 'assistant' : 'user'}`}>
                  <div className="schedule-chat-meta">{message.role === 'assistant' ? 'Hazoc' : 'You'}</div>
                  <p>{message.text}</p>
                </article>
              ))}
            </div>

            <div className="schedule-intake-form">
              <label className="field-block field-block-wide">
                <span>Message to hazoc</span>
                <textarea
                  value={scheduleDraft}
                  onChange={(event) => setScheduleDraft(event.target.value)}
                  onKeyDown={onScheduleDraftKeyDown}
                  rows={5}
                  placeholder="e.g. add dinner with haolun tomorrow at 7:30 PM"
                />
              </label>
              <div className="schedule-intake-actions">
                <small>Send with Ctrl/Cmd + Enter if you want.</small>
                <button type="button" className="save-button" onClick={sendScheduleRequest} disabled={scheduleSending || !scheduleDraft.trim()}>
                  {scheduleSending ? 'Sending…' : 'Create / clarify event'}
                </button>
              </div>
            </div>
          </section>

          <section className="panel schedule-side-panel schedule-side-panel-upcoming">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">upcoming events</p>
                <h2>Scheduled events</h2>
              </div>
            </div>
            {!scheduleLoaded && !hasSchedule ? (
              <div className="lane-empty">Loading events…</div>
            ) : !hasSchedule ? (
              <div className="lane-empty">No events are scheduled yet. New schedule entries from this panel should land as events, not tasks.</div>
            ) : (
              <div className="upcoming-list">
                {scheduledEvents.map((event) => (
                  <article key={event.id} className="upcoming-card clickable" onClick={() => openEvent(event.id)}>
                    <div className="task-card-header">
                      <strong>{event.title}</strong>
                      <span>{event.owner}</span>
                    </div>
                    <p>{formatDateTime(event.scheduledStart)}</p>
                    {event.notes ? <small>{event.notes}</small> : null}
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="panel schedule-side-panel schedule-side-panel-tasks">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">scheduled tasks</p>
                <h2>Hazoc work items</h2>
              </div>
            </div>
            {!scheduledTasks.length ? (
              <div className="lane-empty">No work tasks are date-anchored right now.</div>
            ) : (
              <div className="upcoming-list compact-list">
                {scheduledTasks.slice(0, 8).map((task) => (
                  <article key={task.id} className="upcoming-card compact clickable" onClick={() => openTask(task.id)}>
                    <div className="task-card-header">
                      <strong>{task.title}</strong>
                      <span>{laneMeta(task.lane).title}</span>
                    </div>
                    <p>{formatDateTime(task.scheduledStart)}</p>
                  </article>
                ))}
              </div>
            )}
          </section>

          <section className="panel schedule-side-panel schedule-side-panel-unscheduled">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">needs scheduling</p>
                <h2>Unplaced work</h2>
              </div>
            </div>
            {!unscheduledActiveTasks.length ? (
              <div className="lane-empty">All active non-archived tasks either have a date or are intentionally parked.</div>
            ) : (
              <div className="upcoming-list compact-list">
                {unscheduledActiveTasks.slice(0, 8).map((task) => (
                  <article key={task.id} className="upcoming-card compact clickable" onClick={() => openTask(task.id)}>
                    <div className="task-card-header">
                      <strong>{task.title}</strong>
                      <span>{laneMeta(task.lane).title}</span>
                    </div>
                    {task.notes ? <p>{task.notes}</p> : null}
                  </article>
                ))}
              </div>
            )}
          </section>
        </aside>
      </section>
    </section>
  )
}

function EventsView({
  archivedEvents,
  error,
  eventDescription,
  eventNotes,
  eventOwner,
  eventScheduledEnd,
  eventScheduledStart,
  eventSaving,
  eventStatus,
  eventTitle,
  events,
  saveEventDetails,
  selectedEvent,
  selectedEventId,
  setEventDescription,
  setEventNotes,
  setEventOwner,
  setEventScheduledEnd,
  setEventScheduledStart,
  setEventStatus,
  setEventTitle,
  setSelectedEventId,
  upcomingEvents,
}) {
  return (
    <section className="tasks-layout">
      <div className="hero-row">
        <HeroCard label="Live events" title={String(upcomingEvents.length)} primary />
        <HeroCard label="Archived events" title={String(archivedEvents.length)} />
        <HeroCard label="Next event" title={upcomingEvents[0] ? formatDateTime(upcomingEvents[0].scheduledStart) : 'None yet'}>
          {upcomingEvents[0] ? upcomingEvents[0].title : null}
        </HeroCard>
      </div>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="workspace-grid events-grid">
        <section className="board-grid events-board">
          <section className="panel events-column">
            <div className="lane-header lane-header-dense">
              <div>
                <p className="panel-kicker">upcoming</p>
                <h2>Live events</h2>
              </div>
              <span className="lane-count">{upcomingEvents.length}</span>
            </div>
            <div className="task-list task-list-dense events-list">
              {!upcomingEvents.length ? <div className="lane-empty">No active events yet.</div> : null}
              {upcomingEvents.map((event) => (
                <article key={event.id} className={`task-card ${selectedEventId === event.id ? 'active' : ''}`} onClick={() => setSelectedEventId(event.id)}>
                  <div className="task-card-header">
                    <div className="task-card-title-wrap">
                      <strong>{event.title}</strong>
                    </div>
                    <span>{formatDate(event.updatedAt || event.createdAt)}</span>
                  </div>
                  <div className="task-card-meta-row">
                    <span className="meta-chip">{event.owner}</span>
                    <span className="meta-chip">{formatDateTime(event.scheduledStart)}</span>
                  </div>
                  {event.notes ? <p className="task-preview">{event.notes}</p> : null}
                </article>
              ))}
            </div>
          </section>

          <section className="panel events-column events-column-archive">
            <div className="lane-header lane-header-dense">
              <div>
                <p className="panel-kicker">archive</p>
                <h2>Past / stored events</h2>
              </div>
              <span className="lane-count">{archivedEvents.length}</span>
            </div>
            <div className="task-list task-list-dense events-list">
              {!archivedEvents.length ? <div className="lane-empty">No archived events yet.</div> : null}
              {archivedEvents.map((event) => (
                <article key={event.id} className={`task-card ${selectedEventId === event.id ? 'active' : ''}`} onClick={() => setSelectedEventId(event.id)}>
                  <div className="task-card-header">
                    <div className="task-card-title-wrap">
                      <strong>{event.title}</strong>
                    </div>
                    <span>{formatDate(event.updatedAt || event.createdAt)}</span>
                  </div>
                  <div className="task-card-meta-row">
                    <span className="meta-chip">{event.owner}</span>
                    <span className="meta-chip">{event.scheduledStart ? formatDateTime(event.scheduledStart) : 'No time set'}</span>
                  </div>
                  {event.notes ? <p className="task-preview">{event.notes}</p> : null}
                </article>
              ))}
            </div>
          </section>
        </section>

        <aside className="detail-panel panel task-detail-panel">
          {selectedEvent ? (
            <>
              <section className="detail-hero">
                <div>
                  <p className="panel-kicker">event details</p>
                  <h2>{selectedEvent.title}</h2>
                </div>
                <div className="detail-chip-row">
                  <span className="meta-chip">{eventOwner || 'haolun'}</span>
                  <span className="meta-chip">{eventStatus === 'archived' ? 'Archived' : 'Active'}</span>
                  <span className="meta-chip">Created {formatDate(selectedEvent.createdAt)}</span>
                  <span className="meta-chip">Updated {formatDate(selectedEvent.updatedAt || selectedEvent.createdAt)}</span>
                </div>
              </section>

              <div className="detail-form detail-form-polished">
                <section className="form-section form-section-soft">
                  <div className="section-heading">
                    <p className="panel-kicker">essentials</p>
                    <h3>Core event details</h3>
                  </div>
                  <div className="detail-grid two-up">
                    <label className="field-block field-block-wide">
                      <span>Title</span>
                      <input value={eventTitle} onChange={(event) => setEventTitle(event.target.value)} />
                    </label>
                    <label className="field-block">
                      <span>Owner</span>
                      <input value={eventOwner} onChange={(event) => setEventOwner(event.target.value)} placeholder="haolun" />
                    </label>
                    <div className="field-block">
                      <span>Status</span>
                      <SegmentedControl
                        ariaLabel="Event status"
                        className="detail-segmented-control detail-segmented-control-status"
                        value={eventStatus}
                        options={[
                          { value: 'active', label: 'Active' },
                          { value: 'archived', label: 'Archived' },
                        ]}
                        onChange={setEventStatus}
                      />
                    </div>
                    <label className="field-block field-block-wide">
                      <span>Short notes</span>
                      <textarea value={eventNotes} onChange={(event) => setEventNotes(event.target.value)} rows={4} />
                    </label>
                  </div>
                </section>

                <section className="form-section form-section-accent">
                  <div className="section-heading">
                    <p className="panel-kicker">timing</p>
                    <h3>Event timing in {scheduleTimeZone}</h3>
                  </div>
                  <div className="schedule-edit-grid refined-grid">
                    <label className="field-block">
                      <span>Starts</span>
                      <input type="datetime-local" value={eventScheduledStart} onChange={(event) => setEventScheduledStart(event.target.value)} />
                    </label>
                    <label className="field-block">
                      <span>Ends</span>
                      <input type="datetime-local" value={eventScheduledEnd} onChange={(event) => setEventScheduledEnd(event.target.value)} />
                    </label>
                  </div>
                  <div className="schedule-preview-row">
                    <div className="schedule-preview-card">
                      <span className="schedule-preview-label">Starts</span>
                      <strong>{eventScheduledStart ? formatDateTime(fromInputValueInZone(eventScheduledStart, scheduleTimeZone)) : 'Not set yet'}</strong>
                    </div>
                    <div className="schedule-preview-card">
                      <span className="schedule-preview-label">Ends</span>
                      <strong>{eventScheduledEnd ? formatDateTime(fromInputValueInZone(eventScheduledEnd, scheduleTimeZone)) : 'Not set yet'}</strong>
                    </div>
                  </div>
                </section>

                <section className="form-section form-section-memory">
                  <div className="section-heading">
                    <p className="panel-kicker">event memory</p>
                    <h3>Context</h3>
                  </div>
                  <label className="field-block field-block-wide">
                    <span>Detailed event notes</span>
                    <textarea className="memory-textarea" value={eventDescription} onChange={(event) => setEventDescription(event.target.value)} rows={16} />
                  </label>
                </section>

                <div className="detail-save-row">
                  <div className="save-note">Status changes apply immediately. Save after updating title, owner, timing, or event notes.</div>
                  <button type="button" className="save-button" onClick={saveEventDetails} disabled={eventSaving}>
                    {eventSaving ? 'Saving…' : 'Save event'}
                  </button>
                </div>
              </div>
            </>
          ) : <div className="lane-empty">Select an event to open its details.</div>}
        </aside>
      </section>
    </section>
  )
}

function MemoryView({ error, loading, memoryEntries, memoryLoaded, selectedMemory, selectedMemoryId, setSelectedMemoryId }) {
  return (
    <section className="tasks-layout">
      <div className="hero-row">
        <HeroCard label="Memory entries" title={String(memoryEntries.length)} primary />
        <HeroCard label="Daily notes" title={String(memoryEntries.filter((entry) => entry.kind === 'daily-note').length)} />
        <HeroCard label="Curated files" title={String(memoryEntries.filter((entry) => entry.kind === 'curated').length)} />
      </div>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="workspace-grid memory-grid">
        <section className="board-grid memory-board">
          {memoryEntries.map((entry) => (
            <article key={entry.id} className={`task-card memory-card ${selectedMemoryId === entry.id ? 'active' : ''}`} onClick={() => setSelectedMemoryId(entry.id)}>
              <div className="task-card-header">
                <div className="task-card-title-wrap">
                  <strong>{entry.title}</strong>
                </div>
                <span>{entry.kind.replace('-', ' ')}</span>
              </div>
              <p>{entry.excerpt}</p>
              <div className="task-badge">{entry.lineCount} non-empty lines</div>
            </article>
          ))}
        </section>

        <aside className="detail-panel panel">
          {!memoryLoaded && loading ? (
            <div className="lane-empty">Loading memory…</div>
          ) : selectedMemory ? (
            <>
              <div className="panel-header sticky-panel-header">
                <div>
                  <p className="panel-kicker">memory entry</p>
                  <h2>{selectedMemory.title}</h2>
                </div>
              </div>
              <div className="detail-meta">
                <span>{selectedMemory.kind.replace('-', ' ')}</span>
                <span>{selectedMemory.filePath.replace('/home/haolun/.openclaw/workspace/', '')}</span>
              </div>
              <div className="memory-entry-view">
                <pre>{selectedMemory.content}</pre>
              </div>
            </>
          ) : (
            <div className="lane-empty">Select a memory entry to read its full content.</div>
          )}
        </aside>
      </section>
    </section>
  )
}

const SKILL_SUMMARIES = {
  'grounded-evolver': [
    'Start from a real signal like progress, friction, a blocker, or a decision worth preserving.',
    'Choose exactly one branch: `build-pattern` when no failed protection is known yet, or `repair-pattern` when an existing protection failed or repeated friction proves the pattern is insufficient.',
    'Generalize the root cause, pick the smallest safe mutation, and prefer memory/task/rule fixes before heavier code changes.',
    'If a protocol or workflow is being changed, require rollback, validation, and a durable write before the run counts as complete.',
  ],
  'learning-loop': [
    'Act as the logging and promotion backend after grounded-evolver identifies a learning-worthy signal.',
    'Route the outcome to the smallest durable destination instead of leaving it trapped in chat.',
    'For completed learning runs, write the full artifact pack: daily error detail, day-note summary, lessons, and protocol outcomes.',
    'Promote stable rules into canonical homes like AGENTS, TOOLS, MEMORY, or skill docs when they stop being provisional.',
  ],
  'workspace-memory-stack': [
    'Capture fragile current context in `memory/active-state.md` before it gets lost.',
    'Keep real project work in the mission-control task board and meaningful timeline events in today’s daily note.',
    'Promote only durable facts, preferences, and rules into curated memory files.',
    'On interruption or session end, refresh active state, update the task, and leave the next step explicit.',
  ],
  'workspace-continuity': [
    'Treat the workspace itself as the memory system instead of creating a second parallel brain.',
    'Notice when new information is durable, then write it to the smallest correct home in the same work session.',
    'Keep mission-control tasks current enough that future-you can relearn the project quickly.',
    'Mirror important Discord or Telegram work back into main project memory so cross-channel context does not drift.',
  ],
  'workspace-graph': [
    'Use a lightweight typed graph only when relationships between projects, tasks, decisions, sessions, or documents matter.',
    'Prefer the normal memory stack for day-to-day work, and add graph structure only when it improves retrieval or dependency tracking.',
    'Keep the graph practical and workspace-local instead of turning it into a giant abstract ontology.',
  ],
  'safe-evolution-loop': [
    'Observe a real failure, friction point, or request instead of chasing abstract self-improvement.',
    'Choose the smallest safe improvement, validate it, and record the result so behavior changes compound over time.',
    'Keep the whole loop human-supervised and avoid autonomous repair, external hubs, or risky self-modification.',
  ],
}

function buildSkillSummary(skill) {
  const curated = SKILL_SUMMARIES[skill.name]
  if (curated?.length) return curated

  const steps = Array.isArray(skill.flow) ? skill.flow.filter(Boolean).slice(0, 4) : []
  if (steps.length) return steps.map((step) => step.endsWith('.') ? step : `${step}.`)

  return [
    'Read the skill instructions and use the smallest relevant extra references or scripts.',
    'Follow the workflow the skill defines instead of improvising a separate system around it.',
    'Record durable results in the right workspace destination when the work matters later.',
  ]
}

function SkillsView({ error, loading, selectedSkill, selectedSkillId, setSelectedSkillId, skills, skillsLoaded }) {
  const workspaceSkills = skills.filter((skill) => skill.source === 'workspace')
  const systemSkills = skills.filter((skill) => skill.source === 'system')
  const selectedSummary = selectedSkill ? buildSkillSummary(selectedSkill) : []

  const renderSkillSection = (title, kicker, items) => (
    <section className="skills-group">
      <div className="skills-group-header">
        <div>
          <p className="panel-kicker">{kicker}</p>
          <h3>{title}</h3>
        </div>
        <span className="task-badge">{items.length}</span>
      </div>

      <div className="skills-card-stack">
        {items.map((skill) => {
          return (
            <article key={skill.id} className={`task-card skill-list-card ${selectedSkillId === skill.id ? 'active' : ''}`} onClick={() => setSelectedSkillId(skill.id)}>
              <div className="task-card-header skill-list-card-header">
                <div className="task-card-title-wrap">
                  <strong>{skill.name}</strong>
                </div>
                <span>{skill.sourceLabel}</span>
              </div>
              <p className="skill-list-description">{skill.description}</p>
              <div className="task-card-meta-row skill-list-meta-row">
                <span className="meta-chip">{skill.flow.length} steps</span>
                <span className="meta-chip">{skill.referencesCount} refs</span>
                <span className="meta-chip">{skill.scriptsCount} scripts</span>
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )

  return (
    <section className="tasks-layout">
      <div className="hero-row">
        <HeroCard label="Skills" title={String(skills.length)} primary />
        <HeroCard label="Workspace" title={String(workspaceSkills.length)} />
        <HeroCard label="System" title={String(systemSkills.length)} />
      </div>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="workspace-grid skills-grid">
        <section className="skills-board panel">
          {renderSkillSection('User-edited / created', 'workspace skills', workspaceSkills)}
          {renderSkillSection('System', 'system skills', systemSkills)}
        </section>

        <aside className="detail-panel panel skills-detail-panel">
          {!skillsLoaded && loading ? (
            <div className="lane-empty">Loading skills…</div>
          ) : selectedSkill ? (
            <>
              <div className="panel-header sticky-panel-header">
                <div>
                  <p className="panel-kicker">skill summary</p>
                  <h2>{selectedSkill.name}</h2>
                </div>
              </div>
              <div className="detail-meta">
                <span>{selectedSkill.sourceLabel}</span>
                <span>{selectedSkill.skillPath}</span>
              </div>
              <section className="form-section form-section-soft skill-summary-block">
                <div className="section-heading">
                  <p className="panel-kicker">trigger</p>
                  <h3>When this skill activates</h3>
                </div>
                <p className="skill-description">{selectedSkill.description}</p>
              </section>
              <section className="form-section form-section-accent skill-flow-panel">
                <div className="section-heading">
                  <p className="panel-kicker">how it works</p>
                  <h3>Concise summary</h3>
                </div>
                <div className="skill-fallback-block">
                  <p className="skill-fallback-copy">Short version of the current workflow, without forcing a formal chart.</p>
                  <div className="skill-flow-list compact-skill-flow-list">
                    {selectedSummary.map((step, index) => (
                      <div key={`${selectedSkill.id}-${index}`} className="skill-flow-step-wrap">
                        <article className="skill-flow-step compact-skill-flow-step">
                          <span className="skill-flow-index">{index + 1}</span>
                          <div className="skill-flow-copy">{step}</div>
                        </article>
                        {index < selectedSummary.length - 1 ? <div className="skill-flow-connector" aria-hidden="true" /> : null}
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            </>
          ) : (
            <div className="lane-empty">Select a skill to inspect its concise summary.</div>
          )}
        </aside>
      </section>
    </section>
  )
}

function formatJournalNumber(value, digits = 1) {
  return typeof value === 'number' && Number.isFinite(value) ? value.toFixed(digits) : '—'
}

function formatJournalDateLabel(dateString) {
  if (!dateString) return 'Unknown day'
  const date = new Date(`${dateString}T12:00:00`)
  return date.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' })
}

function MarketJournalView({
  error,
  journal,
  journalLoaded,
  journalLens,
  journalDate,
  setJournalDate,
  setJournalLens,
}) {
  const selectedDay = journal.days.find((day) => day.date === journalDate) || journal.days[0] || null
  const lensOptions = [{ value: 'global', label: 'Global' }, ...journal.users.map((user) => ({ value: user.userId, label: user.displayName })), { value: 'all-users', label: 'All users' }]

  return (
    <section className="tasks-layout market-journal-layout">
      <div className="hero-row">
        <HeroCard label="Archive days" title={String(journal.availableDates.length)} primary />
        <HeroCard label="Selected day" title={selectedDay ? formatJournalDateLabel(selectedDay.date) : 'No digests'}>
          {selectedDay?.date || 'No market digest artifacts found yet.'}
        </HeroCard>
        <HeroCard label="Lens" title={lensOptions.find((option) => option.value === journalLens)?.label || 'Global'} />
      </div>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="workspace-grid market-journal-grid">
        <aside className="panel market-journal-sidebar">
          <div className="panel-header sticky-panel-header">
            <div>
              <p className="panel-kicker">archive</p>
              <h2>Market journal</h2>
            </div>
          </div>

          <div className="form-section form-section-soft market-journal-filter-block">
            <label className="field-block">
              <span>Day</span>
              <select value={journalDate} onChange={(event) => setJournalDate(event.target.value)}>
                {journal.availableDates.map((date) => <option key={date} value={date}>{formatJournalDateLabel(date)} · {date}</option>)}
              </select>
            </label>
            <div className="field-block">
              <span>User lens</span>
              <SegmentedControl ariaLabel="Market journal user lens" value={journalLens} options={lensOptions} onChange={setJournalLens} />
            </div>
          </div>

          <div className="market-journal-day-list">
            {journal.availableDates.map((date) => (
              <button key={date} type="button" className={`market-journal-day-card ${date === journalDate ? 'active' : ''}`} onClick={() => setJournalDate(date)}>
                <strong>{formatJournalDateLabel(date)}</strong>
                <span>{date}</span>
              </button>
            ))}
          </div>
        </aside>

        <section className="market-journal-main">
          {!journalLoaded && !selectedDay ? <div className="panel lane-empty">Loading market journal…</div> : null}
          {journalLoaded && !selectedDay ? <div className="panel lane-empty">No digest artifacts found yet.</div> : null}
          {selectedDay ? selectedDay.windows.map((windowEntry) => {
            const activeUser = journalLens === 'global' || journalLens === 'all-users' ? null : windowEntry.users?.[journalLens] || null
            const allUsers = journal.users
              .map((user) => ({ user, entry: windowEntry.users?.[user.userId] || null }))
              .filter(({ entry }) => entry)

            return (
              <article key={`${selectedDay.date}-${windowEntry.id}`} className="panel market-window-card">
                <div className="market-window-header">
                  <div>
                    <p className="panel-kicker">{windowEntry.id}</p>
                    <h2>{windowEntry.label}</h2>
                  </div>
                  <div className="detail-chip-row">
                    <span className="meta-chip">{windowEntry.generatedAt ? formatDateTime(windowEntry.generatedAt) : 'No timestamp'}</span>
                    <span className="meta-chip">{windowEntry.global.overview.totalItems} items</span>
                    <span className="meta-chip">{windowEntry.global.overview.highPriorityCount} high priority</span>
                    <span className="meta-chip">Score {formatJournalNumber(windowEntry.global.overview.totalScore)}</span>
                  </div>
                </div>

                <div className="market-window-sections">
                  <section className="form-section form-section-soft">
                    <div className="section-heading">
                      <p className="panel-kicker">shared overview</p>
                      <h3>Global market read</h3>
                    </div>
                    {windowEntry.global.overview.headlineSummary ? <p>{windowEntry.global.overview.headlineSummary}</p> : null}
                    <div className="market-summary-grid">
                      <div className="schedule-preview-card">
                        <span className="schedule-preview-label">Top categories</span>
                        <strong>{windowEntry.global.overview.topCategories.length ? windowEntry.global.overview.topCategories.map((item) => `${item.category} (${item.count})`).join(' · ') : 'No category rollup'}</strong>
                      </div>
                      <div className="schedule-preview-card">
                        <span className="schedule-preview-label">Delta vs last run</span>
                        <strong>{windowEntry.global.overview.deltaVsLastRun.summary || 'No prior digest comparison stored'}</strong>
                      </div>
                    </div>
                    {windowEntry.global.overview.overviewBoard.length ? (
                      <div className="market-impact-list">
                        {windowEntry.global.overview.overviewBoard.map((item) => (
                          <article key={item.id} className="upcoming-card market-impact-card">
                            <div className="task-card-header">
                              <strong>{item.label}</strong>
                              <span>{item.supportingCount ? `${item.supportingCount} headlines` : item.scope || 'theme'}</span>
                            </div>
                            {item.headline ? <p><strong>{item.headline}</strong></p> : null}
                            {item.summary ? <p>{item.summary}</p> : null}
                            {item.impactRead ? <p>{item.impactRead}</p> : null}
                            {item.supportingHeadlines.length ? (
                              <div className="task-card-meta-row">
                                {item.supportingHeadlines.slice(0, 3).map((headline) => <span key={headline} className="meta-chip">{headline}</span>)}
                              </div>
                            ) : null}
                          </article>
                        ))}
                      </div>
                    ) : <p className="market-muted-copy">No shared overview board was stored for this window.</p>}
                    {windowEntry.global.overview.watchNext.length ? (
                      <>
                        <h4>Watch next</h4>
                        <ul className="market-bullet-list">
                          {windowEntry.global.overview.watchNext.map((item) => <li key={item}>{item}</li>)}
                        </ul>
                      </>
                    ) : null}
                    {windowEntry.global.overview.unresolvedUncertainties.length ? (
                      <>
                        <h4>Open questions</h4>
                        <ul className="market-bullet-list">
                          {windowEntry.global.overview.unresolvedUncertainties.map((item) => <li key={item}>{item}</li>)}
                        </ul>
                      </>
                    ) : <p className="market-muted-copy">No unresolved uncertainty list was stored for this window.</p>}
                  </section>

                  <section className="form-section form-section-accent">
                    <div className="section-heading">
                      <p className="panel-kicker">stock-impact board</p>
                      <h3>Names and narrower slices worth watching</h3>
                    </div>
                    {!windowEntry.global.stockImpactBoard.length ? <p className="market-muted-copy">No name-level or narrower-scope items were captured in this window.</p> : (
                      <div className="market-impact-list">
                        {windowEntry.global.stockImpactBoard.map((item) => (
                          <article key={item.id} className="upcoming-card market-impact-card">
                            <div className="task-card-header">
                              <strong>{item.headline}</strong>
                              <span>{item.highPriority ? 'High priority' : item.scope}</span>
                            </div>
                            <div className="task-card-meta-row">
                              {item.affectedNames.length ? <span className="meta-chip">Names: {item.affectedNames.join(', ')}</span> : null}
                              {item.affectedSectors.length ? <span className="meta-chip">Sectors: {item.affectedSectors.slice(0, 2).join(', ')}</span> : null}
                              {item.themes.length ? <span className="meta-chip">Themes: {item.themes.join(', ')}</span> : null}
                            </div>
                            {item.impactRead ? <p>{item.impactRead}</p> : null}
                            {item.whyItMatters ? <p>{item.whyItMatters}</p> : null}
                          </article>
                        ))}
                      </div>
                    )}
                  </section>

                  {journalLens !== 'global' ? (
                    <section className="form-section form-section-memory">
                      <div className="section-heading">
                        <p className="panel-kicker">user lens</p>
                        <h3>{journalLens === 'all-users' ? 'All user watchlists' : `${activeUser?.displayName || journalLens} watchlist view`}</h3>
                      </div>

                      {journalLens === 'all-users' ? (
                        <div className="market-user-grid">
                          {allUsers.length ? allUsers.map(({ user, entry }) => (
                            <article key={`${windowEntry.id}-${user.userId}`} className="upcoming-card market-user-card">
                              <div className="task-card-header">
                                <strong>{entry?.displayName || user.displayName}</strong>
                                <span>{entry?.matchedItemCount || 0} matched items</span>
                              </div>
                              <div className="task-card-meta-row">
                                <span className="meta-chip">Watchlist: {(entry?.watchlist || []).join(', ') || 'None stored'}</span>
                                <span className="meta-chip">Flags: {entry?.watchFlags || 0}</span>
                              </div>
                              {entry?.priceError ? <p>{entry.priceError}</p> : null}
                            </article>
                          )) : <p className="market-muted-copy">No user digests were stored for this window.</p>}
                        </div>
                      ) : activeUser ? (
                        <>
                          <div className="task-card-meta-row">
                            <span className="meta-chip">Watchlist: {activeUser.watchlist.join(', ') || 'None stored'}</span>
                            <span className="meta-chip">Matches: {activeUser.matchedItemCount}</span>
                            <span className="meta-chip">Shown: {activeUser.matchedItemsShown}</span>
                            <span className="meta-chip">Flags: {activeUser.watchFlags}</span>
                          </div>
                          {activeUser.summaryLine ? <p>{activeUser.summaryLine}</p> : null}
                          {activeUser.priceError ? <p className="market-muted-copy">Price note: {activeUser.priceError}</p> : null}
                          {activeUser.watchNext.length ? (
                            <ul className="market-bullet-list">
                              {activeUser.watchNext.map((item) => <li key={item}>{item}</li>)}
                            </ul>
                          ) : null}
                          <div className="market-watch-status-list">
                            {activeUser.watchlistStatus.map((item) => (
                              <article key={`${windowEntry.id}-${activeUser.userId}-${item.ticker}`} className="task-card market-watch-status-card">
                                <div className="task-card-header">
                                  <strong>{item.ticker}</strong>
                                  <span>{item.price == null ? 'Price unavailable' : `$${item.price}`}</span>
                                </div>
                                <div className="task-card-meta-row">
                                  <span className="meta-chip">Importance: {item.importance}</span>
                                  {item.flags.length ? <span className="meta-chip">Flags: {item.flags.join(', ')}</span> : null}
                                </div>
                                {item.note ? <p>{item.note}</p> : null}
                              </article>
                            ))}
                          </div>
                          {(activeUser.matchedItems.length || activeUser.derivedMatches.length) ? (
                            <details className="market-details-block" open={activeUser.matchedItems.length > 0}>
                              <summary>Matched / derived watchlist relevance</summary>
                              <div className="market-evidence-list">
                                {[...activeUser.matchedItems, ...activeUser.derivedMatches.filter((item) => !activeUser.matchedItems.some((matched) => matched.id === item.id))].map((item) => (
                                  <article key={`match-${item.id}`} className="upcoming-card compact">
                                    <div className="task-card-header">
                                      <strong>{item.headline}</strong>
                                      <span>{item.highPriority ? 'High priority' : item.scope}</span>
                                    </div>
                                    <div className="task-card-meta-row">
                                      {item.matchedTickers?.length ? <span className="meta-chip">Tickers: {item.matchedTickers.join(', ')}</span> : null}
                                      {item.matchedSectors?.length ? <span className="meta-chip">Sectors: {item.matchedSectors.join(', ')}</span> : null}
                                    </div>
                                    {item.impactRead ? <p>{item.impactRead}</p> : null}
                                    {item.whyItMatters ? <p>{item.whyItMatters}</p> : null}
                                  </article>
                                ))}
                              </div>
                            </details>
                          ) : <p className="market-muted-copy">No direct watchlist matches were stored or derived for this window.</p>}
                        </>
                      ) : <p className="market-muted-copy">No user digest stored for this lens in this window.</p>}
                    </section>
                  ) : null}

                  <details className="market-details-block">
                    <summary>Everything collected / evidence</summary>
                    <div className="market-evidence-list">
                      {windowEntry.global.items.length ? windowEntry.global.items.map((item) => (
                        <article key={item.id} className="upcoming-card market-evidence-card">
                          <div className="task-card-header">
                            <strong>{item.headline}</strong>
                            <span>{item.source || item.category || 'Item'}</span>
                          </div>
                          <div className="task-card-meta-row">
                            {item.highPriority ? <span className="meta-chip">High priority</span> : null}
                            {item.scope ? <span className="meta-chip">Scope: {item.scope}</span> : null}
                            {item.direction ? <span className="meta-chip">Direction: {item.direction}</span> : null}
                            {item.confidenceLabel ? <span className="meta-chip">Confidence: {item.confidenceLabel}</span> : null}
                            {item.affectedNames.length ? <span className="meta-chip">Names: {item.affectedNames.join(', ')}</span> : null}
                            {item.themes.length ? <span className="meta-chip">Themes: {item.themes.join(', ')}</span> : null}
                          </div>
                          {item.summary ? <p>{item.summary}</p> : null}
                          {item.impactRead ? <p>{item.impactRead}</p> : null}
                          {item.whyItMatters ? <p>{item.whyItMatters}</p> : null}
                          {item.url ? <a className="market-link" href={item.url} target="_blank" rel="noreferrer">Open source ↗</a> : null}
                        </article>
                      )) : <p className="market-muted-copy">No global items were stored for this window.</p>}
                    </div>
                  </details>
                </div>
              </article>
            )
          }) : null}
        </section>
      </section>
    </section>
  )
}

function parseStoredMessages(raw) {
  try {
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : null
  } catch {
    return null
  }
}

function createScheduleMessage(role, text) {
  return {
    id: `${role}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`,
    role,
    text,
  }
}

function stripReplyTag(text) {
  return String(text || '').replace(/^\[\[[^\]]+\]\]\s*/, '').trim()
}

const defaultScheduleMessages = [
  createScheduleMessage('assistant', 'Send event requests here. If anything is ambiguous, I’ll ask the minimum follow-up question in this panel before I act.'),
]

export default function App() {
  const [page, setPage] = useState(() => readStorage(storageKeys.page, 'tasks'))
  const [tasks, setTasks] = useState([])
  const [events, setEvents] = useState([])
  const [memoryEntries, setMemoryEntries] = useState([])
  const [skills, setSkills] = useState([])
  const [recurring, setRecurring] = useState([])
  const [protocolItems, setProtocolItems] = useState([])
  const [marketJournal, setMarketJournal] = useState({ users: [], availableDates: [], days: [], latestDate: null })
  const [loading, setLoading] = useState(true)
  const [memoryLoaded, setMemoryLoaded] = useState(false)
  const [skillsLoaded, setSkillsLoaded] = useState(false)
  const [scheduleLoaded, setScheduleLoaded] = useState(false)
  const [protocolLoaded, setProtocolLoaded] = useState(false)
  const [marketJournalLoaded, setMarketJournalLoaded] = useState(false)
  const [detailSaving, setDetailSaving] = useState(false)
  const [error, setError] = useState('')
  const [selectedTaskId, setSelectedTaskId] = useState(() => readStorage(storageKeys.selectedTaskId, ''))
  const [selectedEventId, setSelectedEventId] = useState(() => readStorage(storageKeys.selectedEventId, ''))
  const [activeLaneId, setActiveLaneId] = useState(() => readStorage(storageKeys.activeTaskLane, 'workbench'))
  const [selectedMemoryId, setSelectedMemoryId] = useState(() => readStorage(storageKeys.selectedMemoryId, ''))
  const [selectedSkillId, setSelectedSkillId] = useState(() => readStorage(storageKeys.selectedSkillId, ''))
  const [detailTitle, setDetailTitle] = useState('')
  const [detailNotes, setDetailNotes] = useState('')
  const [detailDescription, setDetailDescription] = useState('')
  const [detailLane, setDetailLane] = useState('workbench')
  const [detailScheduledStart, setDetailScheduledStart] = useState('')
  const [detailScheduledEnd, setDetailScheduledEnd] = useState('')
  const [eventTitle, setEventTitle] = useState('')
  const [eventNotes, setEventNotes] = useState('')
  const [eventDescription, setEventDescription] = useState('')
  const [eventOwner, setEventOwner] = useState('haolun')
  const [eventStatus, setEventStatus] = useState('active')
  const [eventScheduledStart, setEventScheduledStart] = useState('')
  const [eventScheduledEnd, setEventScheduledEnd] = useState('')
  const [eventSaving, setEventSaving] = useState(false)
  const [scheduleDraft, setScheduleDraft] = useState(() => readStorage(storageKeys.scheduleDraft, ''))
  const [scheduleMessages, setScheduleMessages] = useState(() => parseStoredMessages(readStorage(storageKeys.scheduleMessages, '')) || defaultScheduleMessages)
  const [scheduleSending, setScheduleSending] = useState(false)
  const [journalDate, setJournalDate] = useState(() => readStorage(storageKeys.marketJournalDate, ''))
  const [journalLens, setJournalLens] = useState(() => readStorage(storageKeys.marketJournalLens, 'global'))
  const scheduleThreadRef = useRef(null)
  const [calendarMonth, setCalendarMonth] = useState(() => {
    const stored = readStorage(storageKeys.calendarMonth, '')
    return stored ? new Date(stored) : new Date()
  })

  const replaceTaskInState = useCallback((nextTask) => {
    setTasks((current) => current.map((task) => (task.id === nextTask.id ? nextTask : task)))
  }, [])

  const replaceEventInState = useCallback((nextEvent) => {
    setEvents((current) => current.map((event) => (event.id === nextEvent.id ? nextEvent : event)))
  }, [])

  const loadTasks = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const result = await requestJson('/api/tasks')
      setTasks(result.tasks)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  const loadEvents = useCallback(async () => {
    try {
      const result = await requestJson('/api/events')
      setEvents(result.events)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  const loadMemory = useCallback(async () => {
    try {
      const result = await requestJson('/api/memory')
      setMemoryEntries(result.entries)
      setMemoryLoaded(true)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  const loadSkills = useCallback(async () => {
    try {
      const result = await requestJson('/api/skills')
      setSkills(result.skills || [])
      setSkillsLoaded(true)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  const loadProtocol = useCallback(async () => {
    try {
      const result = await requestJson('/api/protocol')
      setProtocolItems(result.protocol || [])
      setRecurring(result.recurring || [])
      setProtocolLoaded(true)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  const loadMarketJournal = useCallback(async () => {
    try {
      const result = await requestJson('/api/market-journal')
      setMarketJournal({
        users: result.users || [],
        availableDates: result.availableDates || [],
        days: result.days || [],
        latestDate: result.latestDate || '',
      })
      setMarketJournalLoaded(true)
      setJournalDate((current) => (current && (result.availableDates || []).includes(current) ? current : (result.latestDate || '')))
    } catch (err) {
      setError(err.message)
    }
  }, [])

  const loadScheduleExtras = useCallback(async () => {
    try {
      await requestJson('/api/schedule')
      setScheduleLoaded(true)
    } catch (err) {
      setError(err.message)
    }
  }, [])

  const refreshCurrentPage = useCallback(async () => {
    await Promise.all([loadTasks(), loadEvents()])
    if (page === 'memory') await loadMemory()
    if (page === 'skills') await loadSkills()
    if (page === 'protocol') await loadProtocol()
    if (page === 'schedule') await loadScheduleExtras()
    if (page === 'market-journal') await loadMarketJournal()
  }, [loadEvents, loadMarketJournal, loadMemory, loadProtocol, loadScheduleExtras, loadSkills, loadTasks, page])

  useEffect(() => {
    loadTasks()
    loadEvents()
  }, [loadEvents, loadTasks])

  useEffect(() => {
    writeStorage(storageKeys.page, page)
    if (page === 'memory' && !memoryLoaded) loadMemory()
    if (page === 'skills' && !skillsLoaded) loadSkills()
    if (page === 'protocol' && !protocolLoaded) loadProtocol()
    if (page === 'schedule' && !scheduleLoaded) loadScheduleExtras()
    if (page === 'market-journal' && !marketJournalLoaded) loadMarketJournal()
  }, [loadMarketJournal, loadMemory, loadProtocol, loadScheduleExtras, loadSkills, marketJournalLoaded, memoryLoaded, page, protocolLoaded, scheduleLoaded, skillsLoaded])

  useEffect(() => { writeStorage(storageKeys.selectedTaskId, selectedTaskId) }, [selectedTaskId])
  useEffect(() => { writeStorage(storageKeys.selectedEventId, selectedEventId) }, [selectedEventId])
  useEffect(() => { writeStorage(storageKeys.activeTaskLane, activeLaneId) }, [activeLaneId])
  useEffect(() => { writeStorage(storageKeys.selectedMemoryId, selectedMemoryId) }, [selectedMemoryId])
  useEffect(() => { writeStorage(storageKeys.selectedSkillId, selectedSkillId) }, [selectedSkillId])
  useEffect(() => { writeStorage(storageKeys.scheduleDraft, scheduleDraft) }, [scheduleDraft])
  useEffect(() => { writeStorage(storageKeys.scheduleMessages, JSON.stringify(scheduleMessages)) }, [scheduleMessages])
  useEffect(() => { writeStorage(storageKeys.calendarMonth, calendarMonth.toISOString()) }, [calendarMonth])
  useEffect(() => { writeStorage(storageKeys.marketJournalDate, journalDate) }, [journalDate])
  useEffect(() => { writeStorage(storageKeys.marketJournalLens, journalLens) }, [journalLens])

  const sortedTasks = useMemo(() => [...tasks].sort(sortTasks), [tasks])
  const sortedEvents = useMemo(() => [...events].sort(sortTasks), [events])
  const selectedTask = useMemo(() => sortedTasks.find((task) => task.id === selectedTaskId) || null, [selectedTaskId, sortedTasks])
  const selectedEvent = useMemo(() => sortedEvents.find((event) => event.id === selectedEventId) || null, [selectedEventId, sortedEvents])
  const selectedMemory = useMemo(() => memoryEntries.find((entry) => entry.id === selectedMemoryId) || null, [memoryEntries, selectedMemoryId])
  const selectedSkill = useMemo(() => skills.find((skill) => skill.id === selectedSkillId) || null, [selectedSkillId, skills])

  useEffect(() => {
    if (sortedTasks.length && (!selectedTaskId || !selectedTask)) setSelectedTaskId(sortedTasks[0].id)
  }, [selectedTask, selectedTaskId, sortedTasks])

  useEffect(() => {
    if (memoryEntries.length && (!selectedMemoryId || !selectedMemory)) setSelectedMemoryId(memoryEntries[0].id)
  }, [memoryEntries, selectedMemory, selectedMemoryId])

  useEffect(() => {
    if (!skills.length || (selectedSkillId && selectedSkill)) return
    const preferredSkill = skills[0]
    setSelectedSkillId(preferredSkill.id)
  }, [selectedSkill, selectedSkillId, skills])

  useEffect(() => {
    if (sortedEvents.length && (!selectedEventId || !selectedEvent)) setSelectedEventId(sortedEvents[0].id)
  }, [selectedEvent, selectedEventId, sortedEvents])

  useEffect(() => {
    if (!selectedTask) return
    setDetailTitle(selectedTask.title || '')
    setDetailNotes(selectedTask.notes || '')
    setDetailDescription(selectedTask.description || descriptionTemplate)
    setDetailLane(selectedTask.lane || 'workbench')
    setDetailScheduledStart(toInputValueInZone(selectedTask.scheduledStart, scheduleTimeZone))
    setDetailScheduledEnd(toInputValueInZone(selectedTask.scheduledEnd, scheduleTimeZone))
  }, [selectedTask])

  useEffect(() => {
    if (!selectedEvent) return
    setEventTitle(selectedEvent.title || '')
    setEventNotes(selectedEvent.notes || '')
    setEventDescription(selectedEvent.description || '')
    setEventOwner(selectedEvent.owner || 'haolun')
    setEventStatus(selectedEvent.status || 'active')
    setEventScheduledStart(toInputValueInZone(selectedEvent.scheduledStart, scheduleTimeZone))
    setEventScheduledEnd(toInputValueInZone(selectedEvent.scheduledEnd, scheduleTimeZone))
  }, [selectedEvent])

  useEffect(() => {
    if (!lanes.some((lane) => lane.id === activeLaneId)) setActiveLaneId('workbench')
  }, [activeLaneId])

  useEffect(() => {
    const validLens = journalLens === 'global' || journalLens === 'all-users' || marketJournal.users.some((user) => user.userId === journalLens)
    if (!validLens) setJournalLens('global')
  }, [journalLens, marketJournal.users])

  const laneCounts = useMemo(() => {
    const map = new Map(lanes.map((lane) => [lane.id, 0]))
    for (const task of sortedTasks) {
      if (!map.has(task.lane)) continue
      map.set(task.lane, (map.get(task.lane) || 0) + 1)
    }
    return map
  }, [sortedTasks])

  const activeLaneTasks = useMemo(() => sortedTasks.filter((task) => task.lane === activeLaneId), [activeLaneId, sortedTasks])

  useEffect(() => {
    if (!activeLaneTasks.length) return
    if (!activeLaneTasks.some((task) => task.id === selectedTaskId)) setSelectedTaskId(activeLaneTasks[0].id)
  }, [activeLaneTasks, selectedTaskId])

  const scheduledTasks = useMemo(() => sortedTasks.filter((task) => task.scheduledStart && task.lane !== 'archive'), [sortedTasks])
  const unscheduledActiveTasks = useMemo(() => sortedTasks.filter((task) => !task.scheduledStart && task.lane !== 'archive'), [sortedTasks])
  const scheduledEvents = useMemo(() => sortedEvents.filter((event) => event.scheduledStart && event.status !== 'archived'), [sortedEvents])
  const archivedEvents = useMemo(() => sortedEvents.filter((event) => event.status === 'archived'), [sortedEvents])
  const upcomingEvents = scheduledEvents
  const nextScheduledEvent = scheduledEvents[0] || null

  const eventsByScheduleDay = useMemo(() => {
    const map = new Map()
    for (const event of scheduledEvents) {
      const key = dateKeyInZone(event.scheduledStart, scheduleTimeZone)
      if (!map.has(key)) map.set(key, [])
      map.get(key).push(event)
    }
    return map
  }, [scheduledEvents])

  const todayKey = calendarCellKey(new Date())

  const calendarDays = useMemo(() => {
    const start = startOfCalendarGrid(calendarMonth)
    return Array.from({ length: 42 }, (_, index) => {
      const date = new Date(start)
      date.setDate(start.getDate() + index)
      const key = calendarCellKey(date)
      return {
        date,
        key,
        entries: eventsByScheduleDay.get(key) || [],
        inMonth: date.getMonth() === calendarMonth.getMonth(),
        isToday: key === todayKey,
      }
    })
  }, [calendarMonth, eventsByScheduleDay, todayKey])

  const moveTask = useCallback(async (id, lane) => {
    const snapshot = tasks
    setTasks((current) => current.map((task) => (task.id === id ? { ...task, lane } : task)))

    try {
      const result = await requestJson(`/api/tasks/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lane }),
      })
      replaceTaskInState(result.task)
      if (selectedTaskId === id) setActiveLaneId(result.task.lane)
      return result.task
    } catch (err) {
      setTasks(snapshot)
      setError(err.message)
      return null
    }
  }, [replaceTaskInState, selectedTaskId, tasks])

  const applyDetailLaneChange = useCallback(async (nextLane) => {
    setDetailLane(nextLane)
    if (!selectedTask || nextLane === selectedTask.lane) return
    await moveTask(selectedTask.id, nextLane)
  }, [moveTask, selectedTask])

  const sendScheduleRequest = useCallback(async () => {
    const message = scheduleDraft.trim()
    if (!message) return

    const userMessage = createScheduleMessage('user', message)
    setScheduleMessages((current) => [...current, userMessage])
    setScheduleDraft('')
    setScheduleSending(true)
    setError('')

    try {
      const result = await requestJson('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `Mission-control schedule intake panel. Treat this as an event request from haolun, not a task-board task, unless the message is clearly about hazoc's own work tracking instead of a personal/shared calendar event.

Primary storage target for scheduled events: /home/haolun/.openclaw/workspace/mission-control/data/events.json
Event schema fields: id, title, notes, description, owner, status, scheduledStart, scheduledEnd, createdAt, updatedAt
Status values: active | archived
Default owner: haolun

Behavior:
- Reply briefly and specifically for event intake.
- If the request is ambiguous or missing something important, ask the minimum clarifying follow-up question.
- If the request is clear enough, confirm the event intent in plain language.
- Do not claim something was scheduled unless you actually updated the relevant event state.
- Prefer creating/updating an event in events.json instead of creating a task in tasks.json for user-entered schedule items.

User request:\n\n${message}`,
        }),
      })

      const assistantText = stripReplyTag(result.reply) || 'I read that, but I do not have a clean reply yet.'
      setScheduleMessages((current) => [...current, createScheduleMessage('assistant', assistantText)])
      await Promise.all([loadTasks(), loadEvents(), loadScheduleExtras()])
    } catch (err) {
      setScheduleMessages((current) => [...current, createScheduleMessage('assistant', `I hit a snag sending that through the schedule panel: ${err.message}`)])
      setError(err.message)
    } finally {
      setScheduleSending(false)
    }
  }, [loadEvents, loadScheduleExtras, loadTasks, scheduleDraft])

  const onScheduleDraftKeyDown = useCallback((event) => {
    if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
      event.preventDefault()
      sendScheduleRequest()
    }
  }, [sendScheduleRequest])

  useEffect(() => {
    const node = scheduleThreadRef.current
    if (node) node.scrollTop = node.scrollHeight
  }, [scheduleMessages])

  const saveEventDetails = useCallback(async () => {
    if (!selectedEvent) return
    setEventSaving(true)
    setError('')

    try {
      const result = await requestJson(`/api/events/${selectedEvent.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: eventTitle,
          notes: eventNotes,
          description: eventDescription,
          owner: eventOwner,
          status: eventStatus,
          scheduledStart: fromInputValueInZone(eventScheduledStart, scheduleTimeZone),
          scheduledEnd: fromInputValueInZone(eventScheduledEnd, scheduleTimeZone),
        }),
      })
      replaceEventInState(result.event)
    } catch (err) {
      setError(err.message)
    } finally {
      setEventSaving(false)
    }
  }, [eventDescription, eventNotes, eventOwner, eventScheduledEnd, eventScheduledStart, eventStatus, eventTitle, replaceEventInState, selectedEvent])

  const applyEventStatusChange = useCallback(async (nextStatus) => {
    setEventStatus(nextStatus)
    if (!selectedEvent || nextStatus === selectedEvent.status) return
    setEventSaving(true)
    setError('')

    try {
      const result = await requestJson(`/api/events/${selectedEvent.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: nextStatus }),
      })
      replaceEventInState(result.event)
    } catch (err) {
      setError(err.message)
    } finally {
      setEventSaving(false)
    }
  }, [replaceEventInState, selectedEvent])

  const saveTaskDetails = useCallback(async () => {
    if (!selectedTask) return
    setDetailSaving(true)
    setError('')

    try {
      const result = await requestJson(`/api/tasks/${selectedTask.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: detailTitle,
          notes: detailNotes,
          description: detailDescription,
          lane: detailLane,
          scheduledStart: fromInputValueInZone(detailScheduledStart, scheduleTimeZone),
          scheduledEnd: fromInputValueInZone(detailScheduledEnd, scheduleTimeZone),
        }),
      })
      replaceTaskInState(result.task)
      setActiveLaneId(result.task.lane)
    } catch (err) {
      setError(err.message)
    } finally {
      setDetailSaving(false)
    }
  }, [detailDescription, detailLane, detailNotes, detailScheduledEnd, detailScheduledStart, detailTitle, replaceTaskInState, selectedTask])

  const openTask = useCallback((taskId) => {
    const task = tasks.find((item) => item.id === taskId)
    if (task) setActiveLaneId(task.lane)
    setSelectedTaskId(taskId)
    setPage('tasks')
  }, [tasks])

  const openEvent = useCallback((eventId) => {
    setSelectedEventId(eventId)
    setPage('events')
  }, [])

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">🦀</div>
          <div>
            <p className="brand-kicker">control</p>
            <h1>Hazoc Mission Control</h1>
          </div>
        </div>

        <section className="nav-group">
          <p className="nav-label">Dashboard</p>
          <div className="nav-items">
            <button className={`nav-item ${page === 'tasks' ? 'active' : ''}`} type="button" onClick={() => setPage('tasks')}><span className="nav-dot" />Tasks</button>
            <button className={`nav-item ${page === 'market-journal' ? 'active' : ''}`} type="button" onClick={() => setPage('market-journal')}><span className="nav-dot" />Market Journal</button>
            <button className={`nav-item ${page === 'protocol' ? 'active' : ''}`} type="button" onClick={() => setPage('protocol')}><span className="nav-dot" />Protocol</button>
            <button className={`nav-item ${page === 'schedule' ? 'active' : ''}`} type="button" onClick={() => setPage('schedule')}><span className="nav-dot" />Schedule</button>
            <button className={`nav-item ${page === 'events' ? 'active' : ''}`} type="button" onClick={() => setPage('events')}><span className="nav-dot" />Events</button>
            <button className={`nav-item ${page === 'memory' ? 'active' : ''}`} type="button" onClick={() => setPage('memory')}><span className="nav-dot" />Memory</button>
            <button className={`nav-item ${page === 'skills' ? 'active' : ''}`} type="button" onClick={() => setPage('skills')}><span className="nav-dot" />Skills</button>
          </div>
        </section>

        <div className="sidebar-footer">
          <span>time zone</span>
          <strong>{scheduleTimeZone}</strong>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div className="breadcrumbs">Mission Control &nbsp;›&nbsp; <strong>{page === 'market-journal' ? 'Market Journal' : page === 'protocol' ? 'Protocol' : page === 'schedule' ? 'Schedule' : page === 'events' ? 'Events' : page === 'memory' ? 'Memory' : page === 'skills' ? 'Skills' : 'Tasks'}</strong></div>
          <div className="topbar-actions">
            <div className="search-pill">{page === 'market-journal' ? 'Artifact-backed market archive with global and user lenses' : page === 'protocol' ? 'Standing rules and recurring operational rhythm' : page === 'schedule' ? 'Calendar for scheduled events' : page === 'events' ? 'Stored and archived events' : page === 'memory' ? 'Journal and memory context' : page === 'skills' ? 'Concise skill summaries and workflow notes' : 'Shared memory for active project work'}</div>
            <button type="button" className="icon-button accent" onClick={refreshCurrentPage} disabled={loading}>{loading ? '…' : '⟳'}</button>
          </div>
        </header>

        {page === 'tasks' ? (
          <TasksView
            activeLaneId={activeLaneId}
            activeLaneTasks={activeLaneTasks}
            error={error}
            loading={loading}
            selectedTask={selectedTask}
            selectedTaskId={selectedTaskId}
            detailTitle={detailTitle}
            setDetailTitle={setDetailTitle}
            detailNotes={detailNotes}
            setDetailNotes={setDetailNotes}
            detailDescription={detailDescription}
            setDetailDescription={setDetailDescription}
            detailLane={detailLane}
            setDetailLane={applyDetailLaneChange}
            detailScheduledStart={detailScheduledStart}
            setDetailScheduledStart={setDetailScheduledStart}
            detailScheduledEnd={detailScheduledEnd}
            setDetailScheduledEnd={setDetailScheduledEnd}
            detailSaving={detailSaving}
            laneCounts={laneCounts}
            moveTask={moveTask}
            saveTaskDetails={saveTaskDetails}
            setActiveLaneId={setActiveLaneId}
            setSelectedTaskId={setSelectedTaskId}
            sortedTasks={sortedTasks}
            unscheduledActiveTasks={unscheduledActiveTasks}
          />
        ) : null}

        {page === 'market-journal' ? (
          <MarketJournalView
            error={error}
            journal={marketJournal}
            journalLoaded={marketJournalLoaded}
            journalLens={journalLens}
            journalDate={journalDate}
            setJournalDate={setJournalDate}
            setJournalLens={setJournalLens}
          />
        ) : null}

        {page === 'protocol' ? (
          <ProtocolView
            error={error}
            protocolItems={protocolItems}
            protocolLoaded={protocolLoaded}
            recurring={recurring}
          />
        ) : null}

        {page === 'schedule' ? (
          <ScheduleView
            calendarDays={calendarDays}
            calendarMonth={calendarMonth}
            error={error}
            nextScheduledEvent={nextScheduledEvent}
            onScheduleDraftKeyDown={onScheduleDraftKeyDown}
            openEvent={openEvent}
            openTask={openTask}
            scheduleDraft={scheduleDraft}
            scheduleMessages={scheduleMessages}
            scheduleSending={scheduleSending}
            scheduleThreadRef={scheduleThreadRef}
            scheduledEvents={scheduledEvents}
            scheduledTasks={scheduledTasks}
            scheduleLoaded={scheduleLoaded}
            sendScheduleRequest={sendScheduleRequest}
            setCalendarMonth={setCalendarMonth}
            setScheduleDraft={setScheduleDraft}
            unscheduledActiveTasks={unscheduledActiveTasks}
          />
        ) : null}

        {page === 'events' ? (
          <EventsView
            archivedEvents={archivedEvents}
            error={error}
            eventDescription={eventDescription}
            eventNotes={eventNotes}
            eventOwner={eventOwner}
            eventScheduledEnd={eventScheduledEnd}
            eventScheduledStart={eventScheduledStart}
            eventSaving={eventSaving}
            eventStatus={eventStatus}
            eventTitle={eventTitle}
            events={events}
            saveEventDetails={saveEventDetails}
            selectedEvent={selectedEvent}
            selectedEventId={selectedEventId}
            setEventDescription={setEventDescription}
            setEventNotes={setEventNotes}
            setEventOwner={setEventOwner}
            setEventScheduledEnd={setEventScheduledEnd}
            setEventScheduledStart={setEventScheduledStart}
            setEventStatus={applyEventStatusChange}
            setEventTitle={setEventTitle}
            setSelectedEventId={setSelectedEventId}
            upcomingEvents={upcomingEvents}
          />
        ) : null}

        {page === 'memory' ? (
          <MemoryView
            error={error}
            loading={loading}
            memoryEntries={memoryEntries}
            memoryLoaded={memoryLoaded}
            selectedMemory={selectedMemory}
            selectedMemoryId={selectedMemoryId}
            setSelectedMemoryId={setSelectedMemoryId}
          />
        ) : null}

        {page === 'skills' ? (
          <SkillsView
            error={error}
            loading={loading}
            selectedSkill={selectedSkill}
            selectedSkillId={selectedSkillId}
            setSelectedSkillId={setSelectedSkillId}
            skills={skills}
            skillsLoaded={skillsLoaded}
          />
        ) : null}
      </main>
    </div>
  )
}
