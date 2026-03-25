#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

ROOT = Path.cwd()
MEMORY_DIR = ROOT / 'memory'
ACTIVE_PATH = MEMORY_DIR / 'active-state.md'

ACTIVE_TEMPLATE = """# Active State

## Current Task
{task}

## Key Context
- none yet

## Blockers
- none

## Next Steps
- {next_step}

## Last Updated
- {timestamp}
"""

DAILY_TEMPLATE = """# {date}

- New day started.
"""


def today_str() -> str:
    return datetime.now().strftime('%Y-%m-%d')


def timestamp() -> str:
    return datetime.now().isoformat(timespec='seconds')


def ensure_daily_file() -> Path:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    path = MEMORY_DIR / f'{today_str()}.md'
    if not path.exists():
        path.write_text(DAILY_TEMPLATE.format(date=today_str()))
    return path


def init_files(task: str = '[None]', next_step: str = 'none'):
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not ACTIVE_PATH.exists():
        ACTIVE_PATH.write_text(ACTIVE_TEMPLATE.format(task=task, next_step=next_step, timestamp=timestamp()))
    ensure_daily_file()


def status():
    daily = ensure_daily_file()
    print('Workspace Memory Stack')
    print(f'- active-state: {"present" if ACTIVE_PATH.exists() else "missing"} ({ACTIVE_PATH})')
    print(f'- today: {daily}')
    print(f'- MEMORY.md: {"present" if (ROOT / "MEMORY.md").exists() else "missing"}')
    print(f'- USER.md: {"present" if (ROOT / "USER.md").exists() else "missing"}')
    print(f'- AGENTS.md: {"present" if (ROOT / "AGENTS.md").exists() else "missing"}')


def touch_active(task: str, next_step: str):
    init_files(task=task or '[None]', next_step=next_step or 'none')
    ACTIVE_PATH.write_text(ACTIVE_TEMPLATE.format(task=task or '[None]', next_step=next_step or 'none', timestamp=timestamp()))
    print(f'Updated {ACTIVE_PATH}')


def main():
    p = argparse.ArgumentParser(description='Workspace memory stack helper')
    sub = p.add_subparsers(dest='cmd', required=True)

    sub.add_parser('init')
    sub.add_parser('status')
    sub.add_parser('today')

    t = sub.add_parser('touch-active')
    t.add_argument('--task', default='[None]')
    t.add_argument('--next', dest='next_step', default='none')

    args = p.parse_args()

    if args.cmd == 'init':
        init_files()
        print('Initialized workspace memory stack files.')
    elif args.cmd == 'status':
        status()
    elif args.cmd == 'today':
        path = ensure_daily_file()
        print(path)
    elif args.cmd == 'touch-active':
        touch_active(args.task, args.next_step)


if __name__ == '__main__':
    main()
