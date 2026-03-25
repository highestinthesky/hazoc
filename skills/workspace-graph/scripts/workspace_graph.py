#!/usr/bin/env python3
import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DIR = Path('memory/workspace-graph')
DEFAULT_GRAPH = DEFAULT_DIR / 'graph.jsonl'
DEFAULT_SCHEMA = DEFAULT_DIR / 'schema.json'

DEFAULT_SCHEMA_DATA = {
    'types': {
        'Project': {
            'required': ['name', 'status'],
            'enums': {'status': ['planning', 'active', 'paused', 'archived']},
        },
        'Task': {
            'required': ['title', 'status'],
            'enums': {
                'status': ['open', 'in_progress', 'blocked', 'done', 'cancelled'],
                'priority': ['low', 'medium', 'high', 'urgent'],
            },
        },
        'Decision': {
            'required': ['title', 'status'],
            'enums': {'status': ['proposed', 'active', 'superseded', 'rejected']},
        },
        'Channel': {
            'required': ['name', 'platform'],
        },
        'Session': {
            'required': ['title', 'status'],
            'enums': {'status': ['active', 'paused', 'ended']},
        },
        'Document': {
            'required': ['title'],
        },
        'Person': {
            'required': ['name'],
        },
    },
    'relations': {
        'has_task': {'from': ['Project'], 'to': ['Task']},
        'has_decision': {'from': ['Project'], 'to': ['Decision']},
        'depends_on': {'from': ['Task', 'Project'], 'to': ['Task', 'Project', 'Decision']},
        'raised_in': {'from': ['Task', 'Decision'], 'to': ['Channel', 'Session']},
        'decided_in': {'from': ['Decision'], 'to': ['Channel', 'Session']},
        'about': {'from': ['Document', 'Session'], 'to': ['Project', 'Task', 'Decision']},
        'references': {'from': ['Document'], 'to': ['Document', 'Task', 'Decision']},
        'involves': {'from': ['Session', 'Project'], 'to': ['Person']},
        'assigned_to': {'from': ['Task'], 'to': ['Person']},
    },
    'forbidden_property_names': ['password', 'secret', 'token', 'api_key'],
}


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def safe_path(path_str: str) -> Path:
    root = Path.cwd().resolve()
    p = Path(path_str).expanduser()
    if not p.is_absolute():
        p = root / p
    p = p.resolve(strict=False)
    p.relative_to(root)
    return p


def ensure_defaults(graph_path: Path, schema_path: Path):
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    if not schema_path.exists():
        schema_path.write_text(json.dumps(DEFAULT_SCHEMA_DATA, indent=2) + '\n')
    if not graph_path.exists():
        graph_path.write_text('')


def load_schema(schema_path: Path):
    ensure_defaults(DEFAULT_GRAPH if schema_path == DEFAULT_SCHEMA else schema_path.parent / 'graph.jsonl', schema_path)
    return json.loads(schema_path.read_text())


def load_graph(graph_path: Path):
    entities = {}
    relations = []
    if not graph_path.exists():
        return entities, relations
    for line in graph_path.read_text().splitlines():
        if not line.strip():
            continue
        op = json.loads(line)
        kind = op.get('op')
        if kind == 'create':
            entity = op['entity']
            entities[entity['id']] = entity
        elif kind == 'update':
            entity = entities.get(op['id'])
            if entity:
                entity['properties'].update(op.get('properties', {}))
                entity['updated'] = op.get('timestamp', now_iso())
        elif kind == 'delete':
            entities.pop(op['id'], None)
            relations = [r for r in relations if r['from'] != op['id'] and r['to'] != op['id']]
        elif kind == 'relate':
            relations.append({'from': op['from'], 'rel': op['rel'], 'to': op['to'], 'properties': op.get('properties', {})})
        elif kind == 'unrelate':
            relations = [r for r in relations if not (r['from'] == op['from'] and r['rel'] == op['rel'] and r['to'] == op['to'])]
    return entities, relations


def append_op(graph_path: Path, record: dict):
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    with graph_path.open('a') as f:
        f.write(json.dumps(record) + '\n')


def new_id(type_name: str):
    return f"{type_name.lower()[:4]}_{uuid.uuid4().hex[:8]}"


def validate_properties(type_name: str, props: dict, schema: dict):
    errors = []
    type_schema = schema.get('types', {}).get(type_name)
    if not type_schema:
        return [f'Unknown type: {type_name}']
    for key in type_schema.get('required', []):
        if key not in props:
            errors.append(f"Missing required property '{key}' for {type_name}")
    enums = type_schema.get('enums', {})
    for key, allowed in enums.items():
        if key in props and props[key] not in allowed:
            errors.append(f"Invalid {type_name}.{key}: expected one of {allowed}, got {props[key]!r}")
    forbidden = set(schema.get('forbidden_property_names', []))
    for key in props:
        if key.lower() in forbidden:
            errors.append(f"Forbidden property name: {key}")
    return errors


def validate_relation(from_entity: dict, rel: str, to_entity: dict, schema: dict):
    rel_schema = schema.get('relations', {}).get(rel)
    if not rel_schema:
        return [f'Unknown relation: {rel}']
    errors = []
    if from_entity['type'] not in rel_schema.get('from', []):
        errors.append(f"Relation {rel} cannot start from {from_entity['type']}")
    if to_entity['type'] not in rel_schema.get('to', []):
        errors.append(f"Relation {rel} cannot point to {to_entity['type']}")
    return errors


def cmd_init(args):
    graph_path = safe_path(args.graph)
    schema_path = safe_path(args.schema)
    ensure_defaults(graph_path, schema_path)
    print(json.dumps({'graph': str(graph_path), 'schema': str(schema_path)}, indent=2))


def cmd_create(args):
    graph_path = safe_path(args.graph)
    schema_path = safe_path(args.schema)
    ensure_defaults(graph_path, schema_path)
    schema = json.loads(schema_path.read_text())
    props = json.loads(args.props)
    errors = validate_properties(args.type, props, schema)
    if errors:
        raise SystemExit('\n'.join(errors))
    entity = {
        'id': args.id or new_id(args.type),
        'type': args.type,
        'properties': props,
        'created': now_iso(),
        'updated': now_iso(),
    }
    append_op(graph_path, {'op': 'create', 'entity': entity, 'timestamp': now_iso()})
    print(json.dumps(entity, indent=2))


def cmd_update(args):
    graph_path = safe_path(args.graph)
    schema_path = safe_path(args.schema)
    ensure_defaults(graph_path, schema_path)
    schema = json.loads(schema_path.read_text())
    entities, _ = load_graph(graph_path)
    entity = entities.get(args.id)
    if not entity:
        raise SystemExit(f'Entity not found: {args.id}')
    props = json.loads(args.props)
    merged = dict(entity['properties'])
    merged.update(props)
    errors = validate_properties(entity['type'], merged, schema)
    if errors:
        raise SystemExit('\n'.join(errors))
    append_op(graph_path, {'op': 'update', 'id': args.id, 'properties': props, 'timestamp': now_iso()})
    entity['properties'] = merged
    entity['updated'] = now_iso()
    print(json.dumps(entity, indent=2))


def cmd_get(args):
    entities, _ = load_graph(safe_path(args.graph))
    entity = entities.get(args.id)
    if not entity:
        raise SystemExit(f'Entity not found: {args.id}')
    print(json.dumps(entity, indent=2))


def cmd_list(args):
    entities, _ = load_graph(safe_path(args.graph))
    items = list(entities.values())
    if args.type:
        items = [e for e in items if e['type'] == args.type]
    print(json.dumps(items, indent=2))


def cmd_query(args):
    entities, _ = load_graph(safe_path(args.graph))
    where = json.loads(args.where)
    items = []
    for entity in entities.values():
        if args.type and entity['type'] != args.type:
            continue
        ok = True
        for key, value in where.items():
            if entity['properties'].get(key) != value:
                ok = False
                break
        if ok:
            items.append(entity)
    print(json.dumps(items, indent=2))


def cmd_delete(args):
    graph_path = safe_path(args.graph)
    entities, _ = load_graph(graph_path)
    if args.id not in entities:
        raise SystemExit(f'Entity not found: {args.id}')
    append_op(graph_path, {'op': 'delete', 'id': args.id, 'timestamp': now_iso()})
    print(json.dumps({'deleted': args.id}, indent=2))


def cmd_relate(args):
    graph_path = safe_path(args.graph)
    schema_path = safe_path(args.schema)
    ensure_defaults(graph_path, schema_path)
    schema = json.loads(schema_path.read_text())
    entities, _ = load_graph(graph_path)
    from_entity = entities.get(args.from_id)
    to_entity = entities.get(args.to_id)
    if not from_entity or not to_entity:
        raise SystemExit('Both related entities must exist first')
    errors = validate_relation(from_entity, args.rel, to_entity, schema)
    if errors:
        raise SystemExit('\n'.join(errors))
    props = json.loads(args.props)
    append_op(graph_path, {'op': 'relate', 'from': args.from_id, 'rel': args.rel, 'to': args.to_id, 'properties': props, 'timestamp': now_iso()})
    print(json.dumps({'from': args.from_id, 'rel': args.rel, 'to': args.to_id, 'properties': props}, indent=2))


def cmd_related(args):
    entities, relations = load_graph(safe_path(args.graph))
    out = []
    for rel in relations:
        if args.dir in ('outgoing', 'both') and rel['from'] == args.id:
            if not args.rel or rel['rel'] == args.rel:
                target = entities.get(rel['to'])
                if target:
                    out.append({'direction': 'outgoing', 'relation': rel['rel'], 'entity': target})
        if args.dir in ('incoming', 'both') and rel['to'] == args.id:
            if not args.rel or rel['rel'] == args.rel:
                source = entities.get(rel['from'])
                if source:
                    out.append({'direction': 'incoming', 'relation': rel['rel'], 'entity': source})
    print(json.dumps(out, indent=2))


def cmd_timeline(args):
    graph_path = safe_path(args.graph)
    if not graph_path.exists():
        print('[]')
        return
    lines = [json.loads(line) for line in graph_path.read_text().splitlines() if line.strip()]
    limit = args.limit or len(lines)
    print(json.dumps(lines[-limit:], indent=2))


def deep_merge(base, incoming):
    for key, value in incoming.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def cmd_schema_merge(args):
    schema_path = safe_path(args.schema)
    ensure_defaults(DEFAULT_GRAPH if schema_path == DEFAULT_SCHEMA else schema_path.parent / 'graph.jsonl', schema_path)
    schema = json.loads(schema_path.read_text())
    incoming = json.loads(args.data)
    merged = deep_merge(schema, incoming)
    schema_path.write_text(json.dumps(merged, indent=2) + '\n')
    print(json.dumps(merged, indent=2))


def cmd_validate(args):
    graph_path = safe_path(args.graph)
    schema_path = safe_path(args.schema)
    ensure_defaults(graph_path, schema_path)
    schema = json.loads(schema_path.read_text())
    entities, relations = load_graph(graph_path)
    errors = []
    for entity in entities.values():
        errors.extend(validate_properties(entity['type'], entity['properties'], schema))
    for rel in relations:
        from_entity = entities.get(rel['from'])
        to_entity = entities.get(rel['to'])
        if not from_entity or not to_entity:
            errors.append(f"Dangling relation: {rel['from']} -[{rel['rel']}]-> {rel['to']}")
            continue
        errors.extend(validate_relation(from_entity, rel['rel'], to_entity, schema))
    if errors:
        print('Validation errors:')
        for err in errors:
            print(f'- {err}')
        raise SystemExit(1)
    print('Graph is valid.')


def main():
    p = argparse.ArgumentParser(description='Lightweight workspace graph')
    sub = p.add_subparsers(dest='cmd', required=True)

    def add_common(sp):
        sp.add_argument('--graph', default=str(DEFAULT_GRAPH))
        sp.add_argument('--schema', default=str(DEFAULT_SCHEMA))

    sp = sub.add_parser('init')
    add_common(sp)
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser('create')
    sp.add_argument('--type', required=True)
    sp.add_argument('--props', default='{}')
    sp.add_argument('--id')
    add_common(sp)
    sp.set_defaults(func=cmd_create)

    sp = sub.add_parser('update')
    sp.add_argument('--id', required=True)
    sp.add_argument('--props', required=True)
    add_common(sp)
    sp.set_defaults(func=cmd_update)

    sp = sub.add_parser('get')
    sp.add_argument('--id', required=True)
    sp.add_argument('--graph', default=str(DEFAULT_GRAPH))
    sp.set_defaults(func=cmd_get)

    sp = sub.add_parser('list')
    sp.add_argument('--type')
    sp.add_argument('--graph', default=str(DEFAULT_GRAPH))
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser('query')
    sp.add_argument('--type')
    sp.add_argument('--where', default='{}')
    sp.add_argument('--graph', default=str(DEFAULT_GRAPH))
    sp.set_defaults(func=cmd_query)

    sp = sub.add_parser('delete')
    sp.add_argument('--id', required=True)
    sp.add_argument('--graph', default=str(DEFAULT_GRAPH))
    sp.set_defaults(func=cmd_delete)

    sp = sub.add_parser('relate')
    sp.add_argument('--from', dest='from_id', required=True)
    sp.add_argument('--rel', required=True)
    sp.add_argument('--to', dest='to_id', required=True)
    sp.add_argument('--props', default='{}')
    add_common(sp)
    sp.set_defaults(func=cmd_relate)

    sp = sub.add_parser('related')
    sp.add_argument('--id', required=True)
    sp.add_argument('--rel')
    sp.add_argument('--dir', choices=['outgoing', 'incoming', 'both'], default='outgoing')
    sp.add_argument('--graph', default=str(DEFAULT_GRAPH))
    sp.set_defaults(func=cmd_related)

    sp = sub.add_parser('timeline')
    sp.add_argument('--limit', type=int, default=20)
    sp.add_argument('--graph', default=str(DEFAULT_GRAPH))
    sp.set_defaults(func=cmd_timeline)

    sp = sub.add_parser('schema-merge')
    sp.add_argument('--data', required=True)
    sp.add_argument('--schema', default=str(DEFAULT_SCHEMA))
    sp.set_defaults(func=cmd_schema_merge)

    sp = sub.add_parser('validate')
    add_common(sp)
    sp.set_defaults(func=cmd_validate)

    args = p.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
