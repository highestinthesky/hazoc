#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

WORKSPACE = Path(__file__).resolve().parent.parent
CLASS_INDEX_PATH = WORKSPACE / "subagent-classes" / "index.json"

DEFAULT_GUARDRAILS = [
    "Treat only the included task packet and attached excerpts/files as available context.",
    "Do not assume workspace-global memory, task board state, active-state, or protocol refs unless they are explicitly attached.",
    "If a key piece of context is missing, say so instead of inventing it.",
]


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


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


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


def load_class_index() -> Dict[str, Any]:
    if not CLASS_INDEX_PATH.exists():
        return {"classes": {}, "aliases": {}}
    return read_json(CLASS_INDEX_PATH)


def resolve_class_entry(raw_class_id: str) -> Tuple[str, str]:
    index = load_class_index()
    classes = index.get("classes", {})
    aliases = index.get("aliases", {})

    class_id = raw_class_id.strip()
    if class_id in aliases:
        class_id = aliases[class_id]
    rel_path = classes.get(class_id)
    if rel_path:
        return class_id, rel_path

    fallback = WORKSPACE / "subagent-classes" / f"{class_id}.json"
    if fallback.exists():
        return class_id, relative_to_workspace(fallback)

    known = ", ".join(sorted(classes.keys())) or "none"
    raise SystemExit(f"Unknown class id '{raw_class_id}'. Known classes: {known}")


def load_class_spec(raw_class_id: str) -> Dict[str, Any]:
    class_id, rel_path = resolve_class_entry(raw_class_id)
    path = resolve_path(rel_path)
    spec = read_json(path)
    file_class_id = spec.get("classId")
    if file_class_id != class_id:
        raise SystemExit(
            f"Class id mismatch for {path}: expected '{class_id}', got '{file_class_id}'"
        )
    return {
        "classId": class_id,
        "path": relative_to_workspace(path),
        "spec": spec,
    }


def unique_lines(*groups: List[str]) -> List[str]:
    seen: set[str] = set()
    merged: List[str] = []
    for group in groups:
        for item in group:
            if item not in seen:
                merged.append(item)
                seen.add(item)
    return merged


def pick_context_mode(args: argparse.Namespace, class_bundle: Dict[str, Any] | None) -> str:
    if args.context_mode:
        return args.context_mode
    if class_bundle:
        return class_bundle["spec"].get("contextPolicy", {}).get("defaultMode", "minimal")
    return "minimal"


def require_fields(args: argparse.Namespace, class_bundle: Dict[str, Any] | None) -> None:
    if not class_bundle:
        return
    required = class_bundle["spec"].get("packetRules", {}).get("mustInclude", [])
    values = {
        "goal": args.goal.strip(),
        "expectedOutput": args.expected_output.strip(),
        "constraints": args.constraint,
        "acceptanceChecks": args.acceptance_check,
        "notes": args.note,
    }
    missing = [field for field in required if not values.get(field)]
    if missing:
        raise SystemExit(
            f"Class '{class_bundle['classId']}' requires fields that were not provided: {', '.join(missing)}"
        )


def enforce_context_policy(
    args: argparse.Namespace,
    class_bundle: Dict[str, Any] | None,
    attachments: List[Dict[str, Any]],
    context_mode: str,
) -> Dict[str, Any]:
    if args.include_file and context_mode != "extended":
        raise SystemExit("--include-file is only allowed with --context-mode extended")

    if not class_bundle:
        return {"totalAttachmentChars": sum(len(item["content"]) for item in attachments)}

    policy = class_bundle["spec"].get("contextPolicy", {})
    if args.include_file and not policy.get("allowFullFiles", False):
        raise SystemExit(
            f"Class '{class_bundle['classId']}' does not allow full-file attachments; use excerpts or a different class."
        )

    max_attachments = policy.get("maxAttachments")
    if max_attachments is not None and len(attachments) > int(max_attachments):
        raise SystemExit(
            f"Class '{class_bundle['classId']}' allows at most {max_attachments} attachments; got {len(attachments)}."
        )

    total_attachment_chars = sum(len(item["content"]) for item in attachments)
    max_attachment_chars = policy.get("maxAttachmentChars")
    if max_attachment_chars is not None and total_attachment_chars > int(max_attachment_chars):
        raise SystemExit(
            f"Class '{class_bundle['classId']}' allows at most {max_attachment_chars} attachment chars; got {total_attachment_chars}."
        )

    return {"totalAttachmentChars": total_attachment_chars}


def build_policy_guardrails(class_bundle: Dict[str, Any] | None) -> List[str]:
    if not class_bundle:
        return []
    policy = class_bundle["spec"].get("contextPolicy", {})
    denied: List[str] = []
    if policy.get("allowWorkspaceReads") is False:
        denied.append("Do not read arbitrary workspace files beyond the attached excerpts/files.")
    if policy.get("allowMemorySearch") is False:
        denied.append("Do not rely on memory_search or unseen memory layers unless the parent explicitly widened context.")
    if policy.get("allowTaskBoardReads") is False:
        denied.append("Do not assume or inspect task board state unless it is attached.")
    if policy.get("allowActiveStateReads") is False:
        denied.append("Do not rely on memory/active-state.md unless it is explicitly attached.")
    if policy.get("allowProtocolReads") is False:
        denied.append("Do not pull extra protocol/reference files unless the parent explicitly attached them.")
    return denied


def build_brief(args: argparse.Namespace) -> Dict[str, Any]:
    class_bundle = load_class_spec(args.class_id) if args.class_id else None
    require_fields(args, class_bundle)

    context_mode = pick_context_mode(args, class_bundle)

    attachments: List[Dict[str, Any]] = []
    attachments.extend(load_excerpt(spec) for spec in args.excerpt)
    attachments.extend(load_file_attachment(path) for path in args.include_file)

    budget_info = enforce_context_policy(args, class_bundle, attachments, context_mode)

    relevant_paths = [relative_to_workspace(resolve_path(path)) for path in args.path]
    class_spec = class_bundle["spec"] if class_bundle else {}
    output_contract = class_spec.get("outputContract", {})
    packet_rules = class_spec.get("packetRules", {})
    guardrail_lines = unique_lines(
        DEFAULT_GUARDRAILS,
        build_policy_guardrails(class_bundle),
        class_spec.get("guardrails", []),
    )

    lines: List[str] = []
    lines.append("# Subagent Task Packet")
    lines.append("")
    if class_bundle:
        lines.append("## Class")
        lines.append(f"- classId: {class_bundle['classId']}")
        if class_spec.get("displayName"):
            lines.append(f"- displayName: {class_spec['displayName']}")
        if class_spec.get("purpose"):
            lines.append(f"- purpose: {class_spec['purpose']}")
        lines.append("")

    lines.append(f"Context mode: {context_mode}")
    lines.append("")

    if class_bundle and class_spec.get("spawnDefaults"):
        lines.append("## Spawn Defaults")
        for key, value in class_spec["spawnDefaults"].items():
            lines.append(f"- {key}: {value}")
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

    if class_bundle and (output_contract or packet_rules):
        lines.append("## Output Contract")
        if output_contract.get("format"):
            lines.append(f"- format: {output_contract['format']}")
        required_sections = output_contract.get("requiredSections", [])
        if required_sections:
            lines.append("- required sections:")
            for item in required_sections:
                lines.append(f"  - {item}")
        missing_context_behavior = packet_rules.get("missingContextBehavior")
        if missing_context_behavior:
            lines.append(f"- missing context behavior: {missing_context_behavior}")
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
    lines.append(
        "Work from the narrowest sufficient context. If the packet is not enough, report the gap instead of assuming hidden memory."
    )

    brief = "\n".join(lines).strip() + "\n"

    return {
        "classId": class_bundle["classId"] if class_bundle else None,
        "classPath": class_bundle["path"] if class_bundle else None,
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
        "spawnDefaults": class_spec.get("spawnDefaults", {}) if class_bundle else {},
        "metadata": {
            "goal": args.goal,
            "expectedOutput": args.expected_output,
            "relevantPaths": relevant_paths,
            "constraints": args.constraint,
            "acceptanceChecks": args.acceptance_check,
            "notes": args.note,
            "outputContract": output_contract,
            "packetRules": packet_rules,
            "totalAttachmentChars": budget_info["totalAttachmentChars"],
        },
    }


def command_build(args: argparse.Namespace) -> int:
    result = build_brief(args)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["classId"]:
            print(f"Class: {result['classId']} ({result['classPath']})\n")
        print(result["brief"])
        if result["spawnDefaults"]:
            print("# Spawn Defaults")
            for key, value in result["spawnDefaults"].items():
                print(f"- {key}: {value}")
        if result["attachments"]:
            print("\n# Attachments")
            for item in result["attachments"]:
                print(f"- {item['name']} ({len(item['content'])} chars)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build minimal-by-default subagent task packets.")
    parser.add_argument("--class-id", help="Resolve a one-shot helper class from subagent-classes/ before compiling the packet.")
    parser.add_argument("--goal", required=True)
    parser.add_argument("--expected-output", required=True)
    parser.add_argument("--context-mode", choices=["minimal", "targeted", "extended"], default=None)
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
