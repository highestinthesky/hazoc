#!/usr/bin/env python3
"""Load a long-lived agent identity bundle from agent-namecards/ and stamp anchor metadata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]


def now_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as fh:
        return json.load(fh)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)
        fh.write('\n')
    tmp.replace(path)


def normalize_rel(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def load_index(root: Path) -> dict[str, Any]:
    return read_json(root / 'agent-namecards' / 'index.json')


def bootstrap(root: Path, card_id: str, source: str, note: str) -> dict[str, Any]:
    index = load_index(root)
    entry = index.get(card_id)
    if not entry:
        raise SystemExit(f'Unknown agent card id: {card_id}')

    namecard_path = root / entry['namecard']
    state_path = root / entry['state']
    if not namecard_path.exists():
        raise SystemExit(f'Namecard not found: {namecard_path}')
    if not state_path.exists():
        raise SystemExit(f'State file not found: {state_path}')

    namecard = read_json(namecard_path)
    state = read_json(state_path)
    if namecard.get('cardId') != card_id:
        raise SystemExit(f'Namecard id mismatch: expected {card_id}, got {namecard.get("cardId")}')
    if state.get('cardId') != card_id:
        raise SystemExit(f'State id mismatch: expected {card_id}, got {state.get("cardId")}')

    stamp = now_iso()
    state['lastAnchoredAt'] = stamp
    state['lastWakeSource'] = source
    state['lastWakeNote'] = note
    state['anchorCount'] = int(state.get('anchorCount') or 0) + 1
    state['lastAction'] = 'bootstrap'
    state['lastActionAt'] = stamp
    write_json(state_path, state)

    bundle = {
      'cardId': card_id,
      'displayName': namecard.get('displayName', card_id),
      'sessionKey': entry.get('sessionKey'),
      'surface': entry.get('surface'),
      'bootstrapStamp': stamp,
      'paths': {
        'index': normalize_rel(root, root / 'agent-namecards' / 'index.json'),
        'namecard': normalize_rel(root, namecard_path),
        'state': normalize_rel(root, state_path),
      },
      'namecard': namecard,
      'state': state,
    }
    return bundle


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', default=str(WORKSPACE_ROOT))
    p.add_argument('--card-id', required=True)
    p.add_argument('--source', default='manual')
    p.add_argument('--note', default='')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    root = Path(args.root).expanduser().resolve()
    bundle = bootstrap(root, args.card_id.strip(), args.source.strip() or 'manual', args.note.strip())
    if args.json:
        print(json.dumps(bundle, indent=2))
    else:
        print(f"Agent identity: {bundle['displayName']} ({bundle['cardId']})")
        print(f"Surface: {bundle.get('surface')}")
        print(f"Session key: {bundle.get('sessionKey')}")
        print(f"Bootstrap stamp: {bundle['bootstrapStamp']}")
        print('Paths:')
        for key, value in bundle['paths'].items():
            print(f'- {key}: {value}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
