#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_CLEAN_ROOM_CWD = '/tmp/grounded-evolver-clean-room'


def load_plan(path: str | None, from_stdin: bool) -> dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding='utf-8'))
    if from_stdin or not sys.stdin.isatty():
        raw = sys.stdin.read().strip()
        if not raw:
            raise SystemExit('No plan JSON provided on stdin.')
        return json.loads(raw)
    raise SystemExit('Provide --plan-file <path> or pipe plan JSON on stdin.')


def build_variants(plan: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    base = dict(plan.get('outside_review_spawn_plan') or {})
    if not base:
        prompt = plan.get('outside_review_prompt', '')
        if not prompt:
            raise SystemExit('Plan does not contain outside_review_prompt or outside_review_spawn_plan.')
        base = {
            'task': prompt,
            'label': 'grounded-outside-review',
            'runtime': 'subagent',
            'mode': 'run',
            'cleanup': 'delete',
            'sandbox': 'require',
            'cwd': DEFAULT_CLEAN_ROOM_CWD,
            'runTimeoutSeconds': 180,
        }

    base.setdefault('task', plan.get('outside_review_prompt', ''))
    if not base.get('task'):
        raise SystemExit('No outside_review_prompt found in plan.')
    base.setdefault('label', 'grounded-outside-review')
    base.setdefault('runtime', 'subagent')
    base.setdefault('mode', 'run')
    base.setdefault('cleanup', 'delete')
    base.setdefault('sandbox', 'require')
    base.setdefault('cwd', DEFAULT_CLEAN_ROOM_CWD)
    base.setdefault('runTimeoutSeconds', 180)
    base.setdefault('timeoutSeconds', base['runTimeoutSeconds'])

    fallback = dict(base)
    fallback['sandbox'] = 'inherit'
    fallback.setdefault('timeoutSeconds', fallback['runTimeoutSeconds'])
    return base, fallback


def notes(plan: dict[str, Any]) -> list[str]:
    out = list(plan.get('outside_review_spawn_notes') or [])
    extra = 'If the runtime rejects sandbox=require for subagents, retry once with the fallback spawn payload that switches sandbox to inherit.'
    if extra not in out:
        out.append(extra)
    return out


def main() -> int:
    p = argparse.ArgumentParser(description='Prepare the exact clean-room outside-review spawn payload from grounded_evolve.py JSON output.')
    p.add_argument('--plan-file', default='')
    p.add_argument('--stdin', action='store_true', help='Read plan JSON from stdin even if stdin is a TTY.')
    p.add_argument('--json', action='store_true')
    p.add_argument('--task-only', action='store_true')
    args = p.parse_args()

    plan = load_plan(args.plan_file or None, args.stdin)

    if not plan.get('outside_review_required') and not plan.get('outside_review_prompt'):
        payload = {
            'outsideReviewRequired': False,
            'message': 'Plan does not require outside review.',
        }
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(payload['message'])
        return 0

    prompt = plan.get('outside_review_prompt', '')
    if args.task_only:
        print(prompt)
        return 0

    preferred, fallback = build_variants(plan)
    payload = {
        'outsideReviewRequired': bool(plan.get('outside_review_required', True)),
        'signalKind': plan.get('signal_kind', ''),
        'analysisBranch': plan.get('analysis_branch', ''),
        'preferredSpawn': preferred,
        'fallbackSpawn': fallback,
        'notes': notes(plan),
        'nextAction': 'Use preferredSpawn as the exact sessions_spawn payload. If the runtime rejects sandbox=require, retry once with fallbackSpawn.',
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print('# Outside Review Bundle\n')
    if payload['signalKind']:
        print(f"Signal kind: {payload['signalKind']}")
    if payload['analysisBranch']:
        print(f"Branch: {payload['analysisBranch']}")
    print('\nPreferred spawn payload:')
    print(json.dumps(preferred, indent=2, ensure_ascii=False))
    print('\nFallback spawn payload:')
    print(json.dumps(fallback, indent=2, ensure_ascii=False))
    print('\nNotes:')
    for item in payload['notes']:
        print(f'- {item}')
    print(f"\nNext action: {payload['nextAction']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
