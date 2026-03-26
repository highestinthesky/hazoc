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
      <p>{children}</p>
    </article>
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
        <HeroCard label="Task model" title="Dense task library" primary>
          New requests should go straight into the real section they belong to. Workbench is for active project work, On Hold is for parked context, Archived keeps finished memory, and Protocol now holds standing duties plus recurring operational rhythm.
        </HeroCard>
        <HeroCard label="Live tasks" title={String(sortedTasks.filter((task) => task.lane !== 'archive').length)}>
          Shared between haolun and hazoc.
        </HeroCard>
        <HeroCard label="Need scheduling" title={String(unscheduledActiveTasks.length)}>
          Active items that still do not have a future date or time.
        </HeroCard>
      </div>

      <section className="panel task-sections-panel">
        <div className="panel-header task-sections-header">
          <div>
            <p className="panel-kicker">task sections</p>
            <h2>Choose a subsection</h2>
          </div>
          <p className="task-sections-note">Capture Tray is gone, and standing duties are no longer pretending to be project work here. Protocol now owns operational rules and recurring rhythm.</p>
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

      <section className="workspace-grid tasks-workspace-grid">
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
              const preview = task.notes || compactTextPreview(task.description, 220)
              return (
                <article
                  key={task.id}
                  className={`task-card task-card-dense ${selectedTaskId === task.id ? 'active' : ''}`}
                  onClick={() => setSelectedTaskId(task.id)}
                >
                  <div className="task-card-main">
                    <div className="task-card-header">
                      <strong>{task.title}</strong>
                      <span>{formatDate(task.updatedAt || task.createdAt)}</span>
                    </div>

                    <div className="task-card-meta-row">
                      <span className={`meta-chip lane-chip lane-${task.lane}`}>{laneMeta(task.lane).title}</span>
                      {task.scheduledStart ? <span className="meta-chip">🗓 {formatDateTime(task.scheduledStart)}</span> : null}
                      <span className="meta-chip">Updated {formatDate(task.updatedAt || task.createdAt)}</span>
                    </div>

                    {preview ? <p className="task-preview">{preview}</p> : null}
                  </div>

                  <div className="task-card-footer task-card-footer-dense" onClick={(event) => event.stopPropagation()}>
                    <select value={task.lane} onChange={(event) => moveTask(task.id, event.target.value)}>
                      {lanes.map((option) => (
                        <option key={option.id} value={option.id}>{option.title}</option>
                      ))}
                    </select>
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
                  <p className="detail-hero-copy">Compact project memory, scheduling, and context for this task live here.</p>
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
                    <label className="field-block">
                      <span>Section</span>
                      <select value={detailLane} onChange={(event) => setDetailLane(event.target.value)}>
                        {lanes.map((lane) => (
                          <option key={lane.id} value={lane.id}>{lane.title}</option>
                        ))}
                      </select>
                    </label>
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
                  <div className="save-note">Save after updating title, section, schedule, or project memory.</div>
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
        <HeroCard label="Protocol model" title="Operating rules" primary>
          Protocol holds standing rules and recurring operational rhythm so Workbench can stay focused on real project work.
        </HeroCard>
        <HeroCard label="Standing protocol" title={String(protocolItems.length)}>
          Message triage, harm checks, cross-channel continuity, and other default behaviors live here.
        </HeroCard>
        <HeroCard label="Recurring rhythm" title={String(recurring.length)}>
          GitHub pushes, memory optimization, uptime, and similar repeating duties belong here instead of the workbench.
        </HeroCard>
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

          <section className="panel protocol-panel protocol-panel-note">
            <div className="panel-header">
              <div>
                <p className="panel-kicker">why this exists</p>
                <h2>Keep workbench clean</h2>
              </div>
            </div>
            <div className="protocol-note-copy">
              Duties like message triage, hourly memory optimization, GitHub push rhythm, and uptime checks are real, but they are not project backlog. Protocol gives them a visible home without making the workbench feel bloated or misleading.
            </div>
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
        <HeroCard label="Schedule model" title="Events calendar" primary>
          This calendar now reflects scheduled events separately from work tasks.
        </HeroCard>
        <HeroCard label="Scheduled events" title={String(scheduledEvents.length)}>
          Shown in {scheduleTimeZone} so dates and times stay anchored.
        </HeroCard>
        <HeroCard label="Next event" title={nextScheduledEvent ? formatDateTime(nextScheduledEvent.scheduledStart) : 'None yet'}>
          {nextScheduledEvent ? nextScheduledEvent.title : 'Future events will land here once they get scheduled.'}
        </HeroCard>
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

            <div className="schedule-intake-copy">
              Type event requests here. If something is unclear, hazoc can answer in this panel and ask the minimum follow-up needed.
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
        <HeroCard label="Events model" title="Separate from tasks" primary>
          User-scheduled events live here as calendar items, separate from hazoc work tasks.
        </HeroCard>
        <HeroCard label="Upcoming events" title={String(upcomingEvents.length)}>
          Active scheduled items for people, plans, and reminders.
        </HeroCard>
        <HeroCard label="Archived events" title={String(archivedEvents.length)}>
          Older events stay stored here instead of cluttering the live schedule.
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
                    <strong>{event.title}</strong>
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
                    <strong>{event.title}</strong>
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
                  <p className="detail-hero-copy">Events live separately from tasks so personal schedule items can stay organized and archived cleanly.</p>
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
                    <label className="field-block">
                      <span>Status</span>
                      <select value={eventStatus} onChange={(event) => setEventStatus(event.target.value)}>
                        <option value="active">Active</option>
                        <option value="archived">Archived</option>
                      </select>
                    </label>
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
                  <div className="save-note">Save after updating title, owner, archive state, timing, or event notes.</div>
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
        <HeroCard label="Memory model" title="Hazoc journal" primary>
          Important things get written into workspace memory so future responses can recover context instead of starting from nothing.
        </HeroCard>
        <HeroCard label="Memory sources" title={String(memoryEntries.length)}>
          Active state, curated context, and recent journal files shown together.
        </HeroCard>
        <HeroCard label="Boosting responses" title="On">
          This page reflects the same memory sources hazoc should use to re-anchor and answer better later.
        </HeroCard>
      </div>

      {error ? <div className="error-banner">{error}</div> : null}

      <section className="workspace-grid memory-grid">
        <section className="board-grid memory-board">
          {memoryEntries.map((entry) => (
            <article key={entry.id} className={`task-card memory-card ${selectedMemoryId === entry.id ? 'active' : ''}`} onClick={() => setSelectedMemoryId(entry.id)}>
              <div className="task-card-header">
                <strong>{entry.title}</strong>
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
  const [recurring, setRecurring] = useState([])
  const [protocolItems, setProtocolItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [memoryLoaded, setMemoryLoaded] = useState(false)
  const [scheduleLoaded, setScheduleLoaded] = useState(false)
  const [protocolLoaded, setProtocolLoaded] = useState(false)
  const [detailSaving, setDetailSaving] = useState(false)
  const [error, setError] = useState('')
  const [selectedTaskId, setSelectedTaskId] = useState(() => readStorage(storageKeys.selectedTaskId, ''))
  const [selectedEventId, setSelectedEventId] = useState(() => readStorage(storageKeys.selectedEventId, ''))
  const [activeLaneId, setActiveLaneId] = useState(() => readStorage(storageKeys.activeTaskLane, 'workbench'))
  const [selectedMemoryId, setSelectedMemoryId] = useState(() => readStorage(storageKeys.selectedMemoryId, ''))
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
    if (page === 'protocol') await loadProtocol()
    if (page === 'schedule') await loadScheduleExtras()
  }, [loadEvents, loadMemory, loadProtocol, loadScheduleExtras, loadTasks, page])

  useEffect(() => {
    loadTasks()
    loadEvents()
  }, [loadEvents, loadTasks])

  useEffect(() => {
    writeStorage(storageKeys.page, page)
    if (page === 'memory' && !memoryLoaded) loadMemory()
    if (page === 'protocol' && !protocolLoaded) loadProtocol()
    if (page === 'schedule' && !scheduleLoaded) loadScheduleExtras()
  }, [loadMemory, loadProtocol, loadScheduleExtras, memoryLoaded, page, protocolLoaded, scheduleLoaded])

  useEffect(() => { writeStorage(storageKeys.selectedTaskId, selectedTaskId) }, [selectedTaskId])
  useEffect(() => { writeStorage(storageKeys.selectedEventId, selectedEventId) }, [selectedEventId])
  useEffect(() => { writeStorage(storageKeys.activeTaskLane, activeLaneId) }, [activeLaneId])
  useEffect(() => { writeStorage(storageKeys.selectedMemoryId, selectedMemoryId) }, [selectedMemoryId])
  useEffect(() => { writeStorage(storageKeys.scheduleDraft, scheduleDraft) }, [scheduleDraft])
  useEffect(() => { writeStorage(storageKeys.scheduleMessages, JSON.stringify(scheduleMessages)) }, [scheduleMessages])
  useEffect(() => { writeStorage(storageKeys.calendarMonth, calendarMonth.toISOString()) }, [calendarMonth])

  const sortedTasks = useMemo(() => [...tasks].sort(sortTasks), [tasks])
  const sortedEvents = useMemo(() => [...events].sort(sortTasks), [events])
  const selectedTask = useMemo(() => sortedTasks.find((task) => task.id === selectedTaskId) || null, [selectedTaskId, sortedTasks])
  const selectedEvent = useMemo(() => sortedEvents.find((event) => event.id === selectedEventId) || null, [selectedEventId, sortedEvents])
  const selectedMemory = useMemo(() => memoryEntries.find((entry) => entry.id === selectedMemoryId) || null, [memoryEntries, selectedMemoryId])

  useEffect(() => {
    if (sortedTasks.length && (!selectedTaskId || !selectedTask)) setSelectedTaskId(sortedTasks[0].id)
  }, [selectedTask, selectedTaskId, sortedTasks])

  useEffect(() => {
    if (memoryEntries.length && (!selectedMemoryId || !selectedMemory)) setSelectedMemoryId(memoryEntries[0].id)
  }, [memoryEntries, selectedMemory, selectedMemoryId])

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
    } catch (err) {
      setTasks(snapshot)
      setError(err.message)
    }
  }, [replaceTaskInState, selectedTaskId, tasks])

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
            <button className={`nav-item ${page === 'protocol' ? 'active' : ''}`} type="button" onClick={() => setPage('protocol')}><span className="nav-dot" />Protocol</button>
            <button className={`nav-item ${page === 'schedule' ? 'active' : ''}`} type="button" onClick={() => setPage('schedule')}><span className="nav-dot" />Schedule</button>
            <button className={`nav-item ${page === 'events' ? 'active' : ''}`} type="button" onClick={() => setPage('events')}><span className="nav-dot" />Events</button>
            <button className={`nav-item ${page === 'memory' ? 'active' : ''}`} type="button" onClick={() => setPage('memory')}><span className="nav-dot" />Memory</button>
          </div>
        </section>

        <div className="sidebar-footer">
          <span>time zone</span>
          <strong>{scheduleTimeZone}</strong>
        </div>
      </aside>

      <main className="main-panel">
        <header className="topbar">
          <div className="breadcrumbs">Mission Control &nbsp;›&nbsp; <strong>{page === 'protocol' ? 'Protocol' : page === 'schedule' ? 'Schedule' : page === 'events' ? 'Events' : page === 'memory' ? 'Memory' : 'Tasks'}</strong></div>
          <div className="topbar-actions">
            <div className="search-pill">{page === 'protocol' ? 'Standing rules and recurring operational rhythm' : page === 'schedule' ? 'Calendar for scheduled events' : page === 'events' ? 'Stored and archived events' : page === 'memory' ? 'Journal and memory context' : 'Shared memory for active project work'}</div>
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
            setDetailLane={setDetailLane}
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
            setEventStatus={setEventStatus}
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
      </main>
    </div>
  )
}
