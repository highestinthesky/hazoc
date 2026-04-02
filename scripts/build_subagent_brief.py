#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

WORKSPACE = Path(__file__).resolve().parent.parent


def resolve_path(raw: str) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = WORKSPACE / path
    return path.resolve()


def relative_to_workspace(path: Path) -> str:
    try:
        return str(path.relative_to(WORKSPACE))
    except ValueError:
        return str(path)


def parse_excerpt_spec(spec: str) -> Tuple[Path, int, int]:
    parts = spec.rsplit(":", 2)
    if len(parts) != 3:
        raise ValueError(f"Bad excerpt spec '{spec}'. Use path:start:end or path:start:+lines")
    raw_path, raw_start, raw_end = parts
    path = resolve_path(raw_path)
    start = int(raw_start)
    if start < 1:
        raise ValueError("Excerpt start line must be >= 1")
    if raw_end.startswith("+"):
        length = int(raw_end[1:])
        if length < 1:
            raise ValueError("Excerpt length must be >= 1")
        end = start + length - 1
    else:
        end = int(raw_end)
    if end < start:
        raise ValueError("Excerpt end line must be >= start line")
    return path, start, end


def load_excerpt(spec: str) -> Dict[str, Any]:
    path, start, end = parse_excerpt_spec(spec)
    lines = path.read_text(encoding="utf-8").splitlines()
    selected = lines[start - 1 : end]
    content = "\n".join(selected)
    rel = relative_to_workspace(path)
    name = f"excerpt__{rel.replace('/', '__')}__L{start}-L{end}.md"
    return {
        "name": name,
        "path": rel,
        "startLine": start,
        "endLine": end,
        "content": content,
        "mimeType": "text/plain",
    }


def load_file_attachment(raw_path: str) -> Dict[str, Any]:
    path = resolve_path(raw_path)
    rel = relative_to_workspace(path)
    return {
        "name": rel.replace("/", "__"),
        "path": rel,
        "startLine": None,
        "endLine": None,
        "content": path.read_text(encoding="utf-8"),
        "mimeType": "text/plain",
    }


def build_brief(args: argparse.Namespace) -> Dict[str, Any]:
    attachments: List[Dict[str, Any]] = []
    attachments.extend(load_excerpt(spec) for spec in args.excerpt)
    attachments.extend(load_file_attachment(path) for path in args.include_file)

    relevant_paths = [relative_to_workspace(resolve_path(path)) for path in args.path]
    context_mode = args.context_mode

    guardrail_lines = [
        "Treat only the included task packet and attached excerpts/files as available context.",
        "Do not assume workspace-global memory, task board state, active-state, or protocol refs unless they are explicitly attached.",
        "If a key piece of context is missing, say so instead of inventing it.",
    ]

    lines: List[str] = []
    lines.append("# Subagent Task Packet")
    lines.append("")
    lines.append(f"Context mode: {context_mode}")
    lines.append("")
    lines.append("## Goal")
    lines.append(args.goal.strip())
    lines.append("")

    if args.constraint:
        lines.append("## Constraints")
        for item in args.constraint:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("## Expected Output")
    lines.append(args.expected_output.strip())
    lines.append("")

    if relevant_paths:
        lines.append("## Relevant Paths")
        for item in relevant_paths:
            lines.append(f"- {item}")
        lines.append("")

    if args.note:
        lines.append("## Notes")
        for item in args.note:
            lines.append(f"- {item}")
        lines.append("")

    if args.acceptance_check:
        lines.append("## Acceptance Checks")
        for item in args.acceptance_check:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("## Guardrails")
    for item in guardrail_lines:
        lines.append(f"- {item}")
    lines.append("")

    if attachments:
        lines.append("## Included Context")
        for item in attachments:
            if item["startLine"] is not None:
                lines.append(f"- {item['path']} lines {item['startLine']}-{item['endLine']}")
            else:
                lines.append(f"- {item['path']} (full file)")
        lines.append("")
    else:
        lines.append("## Included Context")
        lines.append("- none attached")
        lines.append("")

    lines.append("## Execution Rule")
    lines.append("Work from the narrowest sufficient context. If the packet is not enough, report the gap instead of assuming hidden memory.")

    brief = "\n".join(lines).strip() + "\n"

    return {
        "contextMode": context_mode,
        "brief": brief,
        "attachments": [
            {
                "name": item["name"],
                "content": item["content"],
                "mimeType": item["mimeType"],
            }
            for item in attachments
        ],
        "metadata": {
            "goal": args.goal,
            "expectedOutput": args.expected_output,
            "relevantPaths": relevant_paths,
            "constraints": args.constraint,
            "acceptanceChecks": args.acceptance_check,
        },
    }


def command_build(args: argparse.Namespace) -> int:
    if args.include_file and args.context_mode != "extended":
        raise SystemExit("--include-file is only allowed with --context-mode extended")
    result = build_brief(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["brief"])
        if result["attachments"]:
            print("\n# Attachments")
            for item in result["attachments"]:
                print(f"- {item['name']} ({len(item['content'])} chars)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build minimal-by-default subagent task packets.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--expected-output", required=True)
    parser.add_argument("--context-mode", choices=["minimal", "targeted", "extended"], default="minimal")
    parser.add_argument("--constraint", action="append", default=[])
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--excerpt", action="append", default=[], help="path:start:end or path:start:+lines")
    parser.add_argument("--include-file", action="append", default=[])
    parser.add_argument("--acceptance-check", action="append", default=[])
    parser.add_argument("--note", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.set_defaults(func=command_build)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
