#!/usr/bin/env python3
"""Guarded desktop automation CLI. Mutating actions require --live."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import pyautogui
except ImportError as exc:  # pragma: no cover
    raise SystemExit('Missing dependency: pyautogui. Install with: pip install pyautogui pillow opencv-python pygetwindow pyperclip') from exc

pyautogui.FAILSAFE = True


def require_live(args: argparse.Namespace, action: str) -> None:
    if not getattr(args, 'live', False):
        print(json.dumps({'mode': 'dry-run', 'action': action, 'message': 'Add --live to actually perform this desktop action.'}, indent=2))
        raise SystemExit(0)


def cmd_position(_args: argparse.Namespace) -> None:
    pos = pyautogui.position()
    print(json.dumps({'x': pos.x, 'y': pos.y}, indent=2))


def cmd_screenshot(args: argparse.Namespace) -> None:
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    img = pyautogui.screenshot()
    img.save(output)
    print(json.dumps({'saved': str(output)}, indent=2))


def cmd_move(args: argparse.Namespace) -> None:
    require_live(args, 'move')
    pyautogui.moveTo(args.x, args.y, duration=args.duration)
    print(json.dumps({'ok': True, 'action': 'move', 'x': args.x, 'y': args.y}, indent=2))


def cmd_click(args: argparse.Namespace) -> None:
    require_live(args, 'click')
    pyautogui.click(x=args.x, y=args.y, clicks=args.clicks, button=args.button)
    print(json.dumps({'ok': True, 'action': 'click', 'x': args.x, 'y': args.y, 'button': args.button, 'clicks': args.clicks}, indent=2))


def cmd_type(args: argparse.Namespace) -> None:
    require_live(args, 'type')
    pyautogui.write(args.text, interval=args.interval)
    print(json.dumps({'ok': True, 'action': 'type', 'length': len(args.text)}, indent=2))


def cmd_press(args: argparse.Namespace) -> None:
    require_live(args, 'press')
    pyautogui.press(args.key, presses=args.presses, interval=args.interval)
    print(json.dumps({'ok': True, 'action': 'press', 'key': args.key, 'presses': args.presses}, indent=2))


def cmd_hotkey(args: argparse.Namespace) -> None:
    require_live(args, 'hotkey')
    pyautogui.hotkey(*args.keys, interval=args.interval)
    print(json.dumps({'ok': True, 'action': 'hotkey', 'keys': args.keys}, indent=2))


def cmd_windows(_args: argparse.Namespace) -> None:
    try:
        import pygetwindow as gw
    except ImportError as exc:  # pragma: no cover
        raise SystemExit('Missing dependency: pygetwindow. Install with: pip install pygetwindow') from exc
    titles = [w.title for w in gw.getAllWindows() if getattr(w, 'title', '')]
    print(json.dumps({'windows': titles}, indent=2, ensure_ascii=False))


def cmd_clipboard_get(_args: argparse.Namespace) -> None:
    try:
        import pyperclip
    except ImportError as exc:  # pragma: no cover
        raise SystemExit('Missing dependency: pyperclip. Install with: pip install pyperclip') from exc
    print(json.dumps({'text': pyperclip.paste()}, indent=2, ensure_ascii=False))


def cmd_clipboard_set(args: argparse.Namespace) -> None:
    require_live(args, 'clipboard-set')
    try:
        import pyperclip
    except ImportError as exc:  # pragma: no cover
        raise SystemExit('Missing dependency: pyperclip. Install with: pip install pyperclip') from exc
    pyperclip.copy(args.text)
    print(json.dumps({'ok': True, 'action': 'clipboard-set', 'length': len(args.text)}, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Guarded desktop automation CLI')
    sub = parser.add_subparsers(dest='command', required=True)

    position = sub.add_parser('position')
    position.set_defaults(func=cmd_position)

    screenshot = sub.add_parser('screenshot')
    screenshot.add_argument('--output', required=True)
    screenshot.set_defaults(func=cmd_screenshot)

    move = sub.add_parser('move')
    move.add_argument('x', type=int)
    move.add_argument('y', type=int)
    move.add_argument('--duration', type=float, default=0)
    move.add_argument('--live', action='store_true')
    move.set_defaults(func=cmd_move)

    click = sub.add_parser('click')
    click.add_argument('--x', type=int)
    click.add_argument('--y', type=int)
    click.add_argument('--button', default='left', choices=['left', 'right', 'middle'])
    click.add_argument('--clicks', type=int, default=1)
    click.add_argument('--live', action='store_true')
    click.set_defaults(func=cmd_click)

    type_cmd = sub.add_parser('type')
    type_cmd.add_argument('text')
    type_cmd.add_argument('--interval', type=float, default=0.02)
    type_cmd.add_argument('--live', action='store_true')
    type_cmd.set_defaults(func=cmd_type)

    press = sub.add_parser('press')
    press.add_argument('key')
    press.add_argument('--presses', type=int, default=1)
    press.add_argument('--interval', type=float, default=0.05)
    press.add_argument('--live', action='store_true')
    press.set_defaults(func=cmd_press)

    hotkey = sub.add_parser('hotkey')
    hotkey.add_argument('keys', nargs='+')
    hotkey.add_argument('--interval', type=float, default=0.05)
    hotkey.add_argument('--live', action='store_true')
    hotkey.set_defaults(func=cmd_hotkey)

    windows = sub.add_parser('windows')
    windows.set_defaults(func=cmd_windows)

    clip_get = sub.add_parser('clipboard-get')
    clip_get.set_defaults(func=cmd_clipboard_get)

    clip_set = sub.add_parser('clipboard-set')
    clip_set.add_argument('text')
    clip_set.add_argument('--live', action='store_true')
    clip_set.set_defaults(func=cmd_clipboard_set)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
