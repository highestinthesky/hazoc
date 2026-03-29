#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT_DIR = '.learnings/snapshots'


def now_local_iso() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def atomic_write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    with tmp.open('w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2)
        fh.write('\n')
    tmp.replace(path)


def snapshot_store(root: Path, name: str) -> Path:
    return root / SNAPSHOT_DIR / f'{name}.json'


def normalize_path(root: Path, raw: str) -> tuple[str, Path]:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    else:
        candidate = candidate.resolve()
    try:
        rel = candidate.relative_to(root)
    except ValueError as exc:
        raise SystemExit(f'Path escapes workspace root: {raw}') from exc
    return rel.as_posix(), candidate


def read_snapshot(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f'Snapshot not found: {path}')
    return json.loads(path.read_text(encoding='utf-8'))


def hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cmd_snapshot(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    store = snapshot_store(root, args.name)
    rows: list[dict[str, Any]] = []
    for raw in args.file:
        rel, abs_path = normalize_path(root, raw)
        if abs_path.exists() and abs_path.is_dir():
            raise SystemExit(f'Directories are not supported in snapshots: {rel}')
        if abs_path.exists():
            data = abs_path.read_bytes()
            rows.append({
                'path': rel,
                'existed': True,
                'sha256': hash_bytes(data),
                'encoding': 'base64',
                'content': base64.b64encode(data).decode('ascii'),
            })
        else:
            rows.append({
                'path': rel,
                'existed': False,
            })
    payload = {
        'name': args.name,
        'createdAt': now_local_iso(),
        'note': args.note,
        'root': str(root),
        'files': rows,
    }
    atomic_write_json(store, payload)
    out = {
        'ok': True,
        'name': args.name,
        'snapshotFile': str(store),
        'fileCount': len(rows),
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"Snapshot saved: {store}")
        for row in rows:
            status = 'existing' if row.get('existed') else 'missing'
            print(f"- {row['path']} ({status})")
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    store = snapshot_store(root, args.name)
    payload = read_snapshot(store)
    restored: list[str] = []
    deleted: list[str] = []
    for row in payload.get('files', []):
        rel = row['path']
        abs_path = root / rel
        if row.get('existed'):
            data = base64.b64decode(row['content'])
            ensure_parent(abs_path)
            abs_path.write_bytes(data)
            restored.append(rel)
        else:
            if abs_path.exists():
                abs_path.unlink()
                deleted.append(rel)
    if args.drop_after_restore and store.exists():
        store.unlink()
    out = {
        'ok': True,
        'name': args.name,
        'restored': restored,
        'deleted': deleted,
        'snapshotFile': str(store),
        'dropped': bool(args.drop_after_restore),
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"Restored snapshot: {store}")
        for item in restored:
            print(f"- restored {item}")
        for item in deleted:
            print(f"- deleted {item}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    store = snapshot_store(root, args.name)
    payload = read_snapshot(store)
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    print(f"Snapshot: {payload['name']}")
    print(f"Created: {payload.get('createdAt','')}")
    if payload.get('note'):
        print(f"Note: {payload['note']}")
    for row in payload.get('files', []):
        status = 'existing' if row.get('existed') else 'missing'
        print(f"- {row['path']} ({status})")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    directory = root / SNAPSHOT_DIR
    directory.mkdir(parents=True, exist_ok=True)
    names = sorted(p.stem for p in directory.glob('*.json'))
    if args.json:
        print(json.dumps({'snapshots': names}, indent=2))
    else:
        for name in names:
            print(name)
    return 0


def cmd_drop(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    store = snapshot_store(root, args.name)
    if not store.exists():
        raise SystemExit(f'Snapshot not found: {store}')
    store.unlink()
    out = {'ok': True, 'dropped': args.name}
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"Dropped snapshot: {args.name}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description='Create and restore small workspace snapshots for reversible protocol/workflow edits.')
    p.add_argument('--root', default=str(WORKSPACE_ROOT))
    p.add_argument('--json', action='store_true')
    sub = p.add_subparsers(dest='command', required=True)

    snap = sub.add_parser('snapshot')
    snap.add_argument('--name', required=True)
    snap.add_argument('--file', action='append', required=True, help='Workspace-relative or absolute file path. Repeat for multiple files.')
    snap.add_argument('--note', default='')

    restore = sub.add_parser('restore')
    restore.add_argument('--name', required=True)
    restore.add_argument('--drop-after-restore', action='store_true')

    show = sub.add_parser('show')
    show.add_argument('--name', required=True)

    drop = sub.add_parser('drop')
    drop.add_argument('--name', required=True)

    sub.add_parser('list')

    args = p.parse_args()
    if args.command == 'snapshot':
        return cmd_snapshot(args)
    if args.command == 'restore':
        return cmd_restore(args)
    if args.command == 'show':
        return cmd_show(args)
    if args.command == 'list':
        return cmd_list(args)
    if args.command == 'drop':
        return cmd_drop(args)
    raise SystemExit(f'Unknown command: {args.command}')


if __name__ == '__main__':
    raise SystemExit(main())
