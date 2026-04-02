# Token Window Audit

- Start: 2026-04-02T10:47:11-04:00
- End: 2026-04-02T11:52:39-04:00

## Totals
- totalTokens delta: 228,539
- inputTokens delta: 286,379
- outputTokens delta: 8,376
- cacheRead delta: 687,872

Notes:
- This is a session-store delta audit, not a raw provider billing export.
- `cacheRead` reflects cached context reads and is not necessarily additional billed usage.

## By agent
- main: total 228,539 | input 286,379 | output 8,376 | cacheRead 687,872

## By route kind
- cron: total 228,539 | input 204,668 | output 8,376 | cacheRead 687,872
- main: total 0 | input 81,711 | output 0 | cacheRead 0

## Sessions with token movement
- `agent:main:cron:f6839000-f802-4bba-9d8c-30249ce732c5:run:dcb07dc6-f27f-4d7d-a121-a99684d933cc` — Cron: maintain-workspace-hourly
  - agent: main | route: cron
  - total 47,461 | input 42,273 | output 4,667 | cacheRead 315,136
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:16e529af-2f41-4f2a-82d2-c40c1a14f170` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,946 | input 10,399 | output 192 | cacheRead 30,720
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:2c0c4068-6402-42c6-9f6a-0185eea33375` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,945 | input 12,445 | output 191 | cacheRead 28,672
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:8a8b8750-74e2-4dba-8d09-ad1648603393` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,935 | input 13,961 | output 181 | cacheRead 27,136
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:eda4a272-44c5-4c45-ac4a-312131fce769` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,929 | input 11,389 | output 175 | cacheRead 29,696
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:16b64e60-e5bf-4b92-8ab6-ffa7d48f9aab` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,928 | input 21,115 | output 174 | cacheRead 19,968
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:e211fbf5-e0e5-4a6b-b200-336e93de5892` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,928 | input 10,363 | output 174 | cacheRead 30,720
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:07c4aef5-d716-4e86-b049-20b7e1a090a1` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,927 | input 13,945 | output 173 | cacheRead 27,136
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:e58d3e59-824c-41ba-9821-5862019c7a70` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,925 | input 10,357 | output 171 | cacheRead 30,720
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:81fd56e5-1ed8-4c72-9b05-b1a969f76812` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,924 | input 10,355 | output 170 | cacheRead 30,720
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:1a4a4de5-ef7a-450d-85d9-bc270508aafb` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,923 | input 13,937 | output 169 | cacheRead 27,136
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:4e2a4212-b114-4931-9739-aa4e63d272d3` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,923 | input 10,353 | output 169 | cacheRead 30,720
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:9cd6fc78-de46-4973-91c4-8c948a6a2345` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,921 | input 10,349 | output 167 | cacheRead 30,720
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe:run:f73394d2-0684-4539-abf1-650c80c40755` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 13,920 | input 12,395 | output 166 | cacheRead 28,672
- `agent:main:cron:fa5ffaf8-8bf5-418b-8309-71412602f9fe` — Cron: recover-main-task-closeouts
  - agent: main | route: cron
  - total 4 | input 1,032 | output 4 | cacheRead 0
- `agent:main:main` — Main — facility manager
  - agent: main | route: main
  - total 0 | input 81,711 | output 0 | cacheRead 0
- `agent:main:cron:f6839000-f802-4bba-9d8c-30249ce732c5` — Cron: maintain-workspace-hourly
  - agent: main | route: cron
  - total 0 | input 0 | output 1,433 | cacheRead 0
