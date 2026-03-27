#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json


def clamp(v: int, lo: int = 1, hi: int = 5) -> int:
    return max(lo, min(hi, int(v)))


def build_actions(args) -> list[str]:
    actions: list[str] = [
        'state the root cause in plain language',
        'generalize the root cause into a reusable moral before mutating',
    ]

    if args.loss_risk >= 4:
        actions.append('update memory/active-state.md')

    if args.ui:
        actions.append('run a direct UI validation pass in the affected real view/state')

    if args.project or args.category in {'request', 'blocker', 'progress', 'cross-channel', 'decision', 'drift'}:
        actions.append('update mission-control task board')

    if args.impact >= 3 or args.category in {'decision', 'progress', 'repeat-failure', 'cross-channel', 'correction'}:
        actions.append('append memory/YYYY-MM-DD.md')

    if args.preference:
        actions.append('promote durable preference to USER.md')

    if args.rule:
        actions.append('promote durable operating rule to AGENTS.md')

    if args.repeat_count >= 2 or args.category in {'correction', 'repeat-failure'}:
        actions.append('log lesson in .learnings/ or promote stable lesson')

    if args.structure_needed:
        actions.append('add workspace-graph entities/relations')

    if args.repeat_count >= 2 and args.blast_radius <= 3:
        actions.append('consider a small workflow/skill/helper patch')

    seen = set()
    deduped = []
    for item in actions:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def choose_mutation_target(args) -> str:
    if args.preference:
        return 'user-preference'
    if args.rule:
        return 'operating-rule'
    if args.structure_needed and args.project:
        return 'graph-plus-task-memory'
    if args.repeat_count >= 2 and args.blast_radius <= 3:
        return 'workflow-or-skill-patch'
    if args.project:
        return 'task-and-daily-memory'
    if args.loss_risk >= 4:
        return 'active-state-capture'
    return 'daily-memory-capture'


def generalized_moral(args) -> str:
    if args.moral:
        return args.moral
    if args.ui:
        return 'Do not trust visual improvement alone; validate the real interaction model and behavior before accepting UI work.'
    if args.repeat_count >= 2:
        return 'When the same friction repeats, fix the class of mistake instead of patching one more instance.'
    if args.rule:
        return 'Turn incident-specific friction into a reusable operating rule before changing behavior or code.'
    return 'Identify the broader failure mode before mutating so the fix applies beyond the current incident.'


def root_cause_summary(args) -> str:
    if args.root_cause:
        return args.root_cause
    if args.ui:
        return 'The visible symptom was treated before the underlying interaction model and real-state behavior were fully tested.'
    if args.repeat_count >= 2:
        return 'The same failure pattern was allowed to recur without being generalized into a durable rule or workflow fix.'
    return 'The local incident was clearer than the underlying failure mode, so the first fix risked being too narrow.'


def validation_checks(args) -> list[str]:
    checks = [
        'Confirm the signal is concrete, not vague self-improvement language.',
        'State the root cause in plain language before proposing a fix.',
        'Generalize that root cause into a reusable moral, not just an incident-specific patch note.',
        'Check that the moral could help on unrelated future tasks, not only this exact one.',
        'State the smallest safe change before making it.',
        'Choose explicit write destinations instead of leaving it in chat only.',
    ]

    if args.ui:
        checks.extend([
            'Check for visual bugs in the real affected layout/state, not just in isolation.',
            'Test the interaction end to end instead of assuming the UI implies correct behavior.',
            'Verify the control behaves the way it visually suggests (immediate vs saved, safe vs destructive).',
        ])

    target = choose_mutation_target(args)
    if target == 'workflow-or-skill-patch':
        checks.append('Verify the repeated friction really cannot be solved by memory/task updates alone.')
        checks.append('Test the helper/skill/workflow change directly.')
    elif target == 'graph-plus-task-memory':
        checks.append('Verify the relationship question actually benefits from graph structure.')
        checks.append('Keep the task board updated too so the graph does not become a parallel reality.')
    else:
        checks.append('Verify that the chosen memory/task updates would let future-you recover quickly.')

    return checks


def priority_score(args) -> int:
    score = args.impact + args.loss_risk + min(args.repeat_count, 3)
    if args.cross_channel:
        score += 2
    if args.project:
        score += 1
    if args.structure_needed:
        score += 1
    score -= args.blast_radius
    return max(1, score)


def main() -> None:
    p = argparse.ArgumentParser(description='Plan a grounded evolution step')
    p.add_argument('--signal', required=True)
    p.add_argument('--category', default='friction', choices=['request', 'blocker', 'correction', 'friction', 'repeat-failure', 'cross-channel', 'decision', 'progress', 'drift'])
    p.add_argument('--repeat-count', type=int, default=1)
    p.add_argument('--impact', type=int, default=3)
    p.add_argument('--loss-risk', type=int, default=3)
    p.add_argument('--blast-radius', type=int, default=2)
    p.add_argument('--cross-channel', action='store_true')
    p.add_argument('--project', action='store_true')
    p.add_argument('--structure-needed', action='store_true')
    p.add_argument('--ui', action='store_true')
    p.add_argument('--root-cause', default='')
    p.add_argument('--moral', default='')
    p.add_argument('--preference', action='store_true')
    p.add_argument('--rule', action='store_true')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    args.repeat_count = max(1, int(args.repeat_count))
    args.impact = clamp(args.impact)
    args.loss_risk = clamp(args.loss_risk)
    args.blast_radius = clamp(args.blast_radius)

    plan = {
        'signal': args.signal,
        'category': args.category,
        'root_cause': root_cause_summary(args),
        'generalized_moral': generalized_moral(args),
        'priority_score': priority_score(args),
        'mutation_target': choose_mutation_target(args),
        'recommended_actions': build_actions(args),
        'validation_checks': validation_checks(args),
        'next_step': 'Generalize first, then make the smallest safe change, then record the outcome in task memory or daily notes.',
    }

    if args.json:
        print(json.dumps(plan, indent=2))
        return

    print('# Grounded Evolution Plan\n')
    print(f"Signal\n- {plan['signal']}\n")
    print(f"Category\n- {plan['category']}\n")
    print(f"Root Cause\n- {plan['root_cause']}\n")
    print(f"Generalized Moral\n- {plan['generalized_moral']}\n")
    print(f"Priority Score\n- {plan['priority_score']}\n")
    print(f"Mutation Target\n- {plan['mutation_target']}\n")
    print('Recommended Actions')
    for item in plan['recommended_actions']:
        print(f'- {item}')
    print('\nValidation Checks')
    for item in plan['validation_checks']:
        print(f'- {item}')
    print(f"\nNext Step\n- {plan['next_step']}")


if __name__ == '__main__':
    main()
