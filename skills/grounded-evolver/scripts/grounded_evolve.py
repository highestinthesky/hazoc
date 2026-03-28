#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json


UNDESIRABLE_KINDS = {
    'blocker',
    'correction',
    'friction',
    'repeat-failure',
    'cross-channel',
    'drift',
    'request-friction',
}


def clamp(v: int, lo: int = 1, hi: int = 5) -> int:
    return max(lo, min(hi, int(v)))


def request_friction_signals(args) -> list[str]:
    signals: list[str] = []
    if args.user_correction:
        signals.append('user-correction')
    if args.tool_failure:
        signals.append('tool-failure')
    if args.skipped_step:
        signals.append('skipped-step')
    if args.protocol_failed:
        signals.append('protocol-failed')
    if args.avoidable_detour:
        signals.append('avoidable-detour')
    if args.bad_local_fix:
        signals.append('bad-local-fix')
    if args.repeat_count >= 2:
        signals.append('repeat-friction')
    return signals


def signal_kind(args) -> str:
    if args.category == 'request-friction':
        return 'request-friction'
    if args.meaningful_request and request_friction_signals(args):
        return 'request-friction'
    return args.category


def undesirable_signal(args) -> bool:
    if request_friction_signals(args):
        return True
    return signal_kind(args) in UNDESIRABLE_KINDS


def observed_signals(args) -> list[str]:
    signals: list[str] = []
    if args.meaningful_request:
        signals.append('meaningful-request')
    signals.extend(request_friction_signals(args))
    if args.protocol_existed:
        signals.append('protocol-existed')
    if args.ui:
        signals.append('ui-context')

    seen = set()
    deduped: list[str] = []
    for item in signals:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def protection_state(args) -> str:
    if args.protocol_failed:
        return 'failed-existing-protection'
    if undesirable_signal(args) and args.protocol_existed:
        return 'existing-protection-present'
    if undesirable_signal(args):
        return 'no-known-failed-protection'
    return 'no-protection-issue'


def choose_analysis_branch(args) -> str:
    kind = signal_kind(args)
    if args.protocol_failed:
        return 'repair-pattern'
    if kind == 'repeat-failure':
        return 'repair-pattern'
    if undesirable_signal(args) and (args.protocol_existed or args.repeat_count >= 2):
        return 'repair-pattern'
    return 'build-pattern'


def packet_fields(args) -> list[str]:
    kind = signal_kind(args)
    branch = choose_analysis_branch(args)

    if kind == 'request-friction':
        fields = [
            'signal_kind',
            'request_context',
            'symptom_type',
            'impact',
            'repeat_count',
            'protection_state',
            'loss_risk',
            'blast_radius',
        ]
    elif undesirable_signal(args):
        fields = [
            'signal_kind',
            'context',
            'failure_mode',
            'impact',
            'repeat_count',
            'protection_state',
            'loss_risk',
            'blast_radius',
        ]
    else:
        fields = [
            'signal_kind',
            'context',
            'outcome_type',
            'impact',
            'repeat_count',
            'protection_state',
            'loss_risk',
            'blast_radius',
        ]

    if branch == 'repair-pattern':
        fields.append('failed_layer')
    return fields


def outside_review_required(args) -> bool:
    branch = choose_analysis_branch(args)
    if branch == 'repair-pattern':
        return True
    if undesirable_signal(args):
        return True
    return False


def build_actions(args) -> list[str]:
    branch = choose_analysis_branch(args)
    kind = signal_kind(args)
    actions: list[str] = [
        'state the root cause in plain language',
        'generalize the root cause into a reusable moral before mutating',
    ]

    if branch == 'build-pattern':
        if undesirable_signal(args):
            actions.extend([
                'build a compact problem packet',
                'draft a self-authored prevention/update list',
            ])
            if outside_review_required(args):
                actions.append('get a clean third-party take')
            actions.append('merge the candidate rules/changes into a generalized draft')
        else:
            actions.extend([
                'build a compact signal-capture packet',
                'decide which durable state should absorb this signal',
                'capture the smallest durable update that preserves the gain or state change',
            ])
    else:
        actions.extend([
            'review the protection or workflow that should have prevented the issue',
            'build a compact failure packet',
        ])
        if outside_review_required(args):
            actions.append('get a clean outside diagnosis')
        actions.extend([
            'produce self and third-party change plans',
            'repair the failed protection at the right layer',
        ])

    if args.loss_risk >= 4:
        actions.append('update memory/active-state.md')

    if args.ui:
        actions.append('run a direct UI validation pass in the affected real view/state')

    if args.project or kind in {'request', 'blocker', 'progress', 'cross-channel', 'decision', 'drift', 'request-friction'}:
        actions.append('update mission-control task board')

    if args.impact >= 3 or kind in {'decision', 'progress', 'repeat-failure', 'cross-channel', 'correction', 'request-friction', 'blocker'}:
        actions.append('append memory/YYYY-MM-DD.md')

    if args.preference:
        actions.append('promote durable preference to USER.md')

    if args.rule or kind in {'request-friction', 'correction', 'repeat-failure'} or args.protocol_existed or args.protocol_failed:
        actions.append('promote or revise durable operating rule in AGENTS.md')

    if undesirable_signal(args) or kind in {'request-friction', 'correction', 'repeat-failure'}:
        actions.append('log lesson in .learnings/ or promote stable lesson')

    if args.structure_needed:
        actions.append('add workspace-graph entities/relations')

    if branch == 'repair-pattern':
        if args.blast_radius <= 3:
            actions.append('consider a workflow/skill/helper patch')
        else:
            actions.append('consider a deeper rule-or-workflow repair plan before touching code')

    seen = set()
    deduped = []
    for item in actions:
        if item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def choose_mutation_target(args) -> str:
    kind = signal_kind(args)
    branch = choose_analysis_branch(args)

    if args.preference:
        return 'user-preference'
    if args.structure_needed and args.project:
        return 'graph-plus-task-memory'
    if branch == 'repair-pattern':
        if args.blast_radius <= 3:
            return 'workflow-or-skill-patch'
        return 'rule-or-workflow-repair'
    if args.rule or kind in {'request-friction', 'correction'}:
        return 'operating-rule'
    if args.project:
        return 'task-and-daily-memory'
    if args.loss_risk >= 4:
        return 'active-state-capture'
    return 'daily-memory-capture'


def generalized_moral(args) -> str:
    if args.moral:
        return args.moral

    kind = signal_kind(args)
    branch = choose_analysis_branch(args)

    if branch == 'repair-pattern':
        if kind == 'request-friction':
            return 'When a request reveals that the current protection is insufficient, repair the failed layer instead of repeating the workaround.'
        return 'When the current pattern or protection is insufficient, repair the right layer instead of normalizing the repeat failure.'

    if kind == 'progress':
        return 'Preserve meaningful progress in durable state before context fades.'
    if kind == 'decision':
        return 'Turn important decisions into explicit durable state so future work stays aligned.'
    if kind == 'request-friction':
        return 'Turn request friction into a reusable protection before it repeats.'
    if kind in {'blocker', 'cross-channel', 'drift'}:
        return 'Capture operational risk in a form that makes the next corrective move explicit.'
    if undesirable_signal(args):
        return 'Turn new friction into a reusable protection before it repeats.'
    if args.rule:
        return 'Turn incident-specific friction into a reusable operating rule before changing behavior or code.'
    return 'Turn real signals into durable structure before they drift back into chat.'


def root_cause_summary(args) -> str:
    if args.root_cause:
        return args.root_cause

    kind = signal_kind(args)
    branch = choose_analysis_branch(args)

    if branch == 'repair-pattern':
        return 'A real signal showed that the current protection, workflow, or implementation was missing, skipped, too weak, or applied at the wrong layer.'
    if kind == 'progress':
        return 'Meaningful project state changed, but without durable capture the progress would fade and future work would restart from partial memory.'
    if kind == 'decision':
        return 'The plan changed in a way that future work needs, but that change will drift unless it is written into the right durable state.'
    if kind == 'request-friction':
        return 'A meaningful request exposed avoidable friction that had not yet been turned into a reusable protection.'
    if undesirable_signal(args):
        return 'A real signal exposed a new class of friction that had not yet been captured as durable guidance.'
    return 'A real signal changed the working state, but the durable system had not yet been updated to reflect it.'


def validation_checks(args) -> list[str]:
    kind = signal_kind(args)
    branch = choose_analysis_branch(args)
    checks = [
        'Confirm the signal is concrete, not vague self-improvement language.',
        'State the root cause in plain language before proposing a fix.',
        'Generalize that root cause into a reusable moral, not just an incident-specific patch note.',
        'Check that the moral could help on unrelated future tasks, not only this exact one.',
        'State the smallest safe change before making it.',
        'Choose explicit write destinations instead of leaving it in chat only.',
        'Confirm that exactly one of the two learning branches was selected.',
    ]

    if kind == 'request-friction':
        checks.extend([
            'Confirm the trigger came from a meaningful request rather than generic background learning.',
            'Name the concrete request-friction signals that were observed.',
        ])

    if branch == 'build-pattern':
        if undesirable_signal(args):
            checks.extend([
                'Confirm there is no known failed protection that would make this a repair-pattern case.',
                'Produce one self-authored prevention/update list before promotion.',
                'Use a clean outside take for undesirable first-pass signals instead of trusting only the first draft.',
                'Check that the combined rule/change prevents the class of mistake rather than only this instance.',
            ])
        else:
            checks.extend([
                'Verify the captured update matches the signal kind (progress, decision, blocker, request, etc.).',
                'Do not overreact to a benign signal with an unnecessary workflow/code change.',
                'Verify that future-you could recover the important state from the chosen write destinations.',
            ])
    else:
        checks.extend([
            'Identify the protection or pattern that should have prevented the issue.',
            'Explain exactly how reality diverged from that protection.',
            'Decide whether the fix belongs in memory, rules, workflow, skill code, or implementation rather than defaulting to wording changes.',
            'Compare a self-authored repair plan with a clean outside diagnosis before finalizing the change.',
        ])

    if args.ui:
        checks.extend([
            'Check for visual bugs in the real affected layout/state, not just in isolation.',
            'Test the interaction end to end instead of assuming the UI implies correct behavior.',
            'Verify the control behaves the way it visually suggests (immediate vs saved, safe vs destructive).',
        ])

    target = choose_mutation_target(args)
    if target == 'workflow-or-skill-patch':
        checks.append('Verify the repeated or failed pattern really cannot be solved by memory/task updates alone.')
        checks.append('Test the helper/skill/workflow change directly.')
    elif target == 'graph-plus-task-memory':
        checks.append('Verify the relationship question actually benefits from graph structure.')
        checks.append('Keep the task board updated too so the graph does not become a parallel reality.')
    elif target == 'rule-or-workflow-repair':
        checks.append('Verify that a code patch would be too high-blast-radius before stopping at a rule/workflow repair.')
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
    if undesirable_signal(args):
        score += 1
    if args.protocol_failed:
        score += 1
    score -= args.blast_radius
    return max(1, score)


def next_step(args) -> str:
    branch = choose_analysis_branch(args)
    if branch == 'repair-pattern':
        return 'Review the failed protection, compare self and outside repair plans, then implement the smallest safe fix at the right layer.'
    if undesirable_signal(args):
        return 'Build the problem packet, write a first prevention/update draft, get a clean outside take, then promote the smallest safe generalized change.'
    return 'Capture the signal in the smallest durable state, then validate that future-you could recover from that record.'


def main() -> None:
    p = argparse.ArgumentParser(description='Plan a grounded evolution step')
    p.add_argument('--signal', required=True)
    p.add_argument('--category', default='friction', choices=['request', 'blocker', 'correction', 'friction', 'repeat-failure', 'cross-channel', 'decision', 'progress', 'drift', 'request-friction'])
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
    p.add_argument('--meaningful-request', action='store_true')
    p.add_argument('--user-correction', action='store_true')
    p.add_argument('--tool-failure', action='store_true')
    p.add_argument('--skipped-step', action='store_true')
    p.add_argument('--protocol-existed', action='store_true')
    p.add_argument('--protocol-failed', action='store_true')
    p.add_argument('--avoidable-detour', action='store_true')
    p.add_argument('--bad-local-fix', action='store_true')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    args.repeat_count = max(1, int(args.repeat_count))
    args.impact = clamp(args.impact)
    args.loss_risk = clamp(args.loss_risk)
    args.blast_radius = clamp(args.blast_radius)

    plan = {
        'signal': args.signal,
        'signal_kind': signal_kind(args),
        'category': args.category,
        'analysis_branch': choose_analysis_branch(args),
        'undesirable_signal': undesirable_signal(args),
        'observed_signals': observed_signals(args),
        'protection_state': protection_state(args),
        'outside_review_required': outside_review_required(args),
        'packet_fields': packet_fields(args),
        'root_cause': root_cause_summary(args),
        'generalized_moral': generalized_moral(args),
        'priority_score': priority_score(args),
        'mutation_target': choose_mutation_target(args),
        'recommended_actions': build_actions(args),
        'validation_checks': validation_checks(args),
        'next_step': next_step(args),
    }

    if args.json:
        print(json.dumps(plan, indent=2))
        return

    print('# Grounded Evolution Plan\n')
    print(f"Signal\n- {plan['signal']}\n")
    print(f"Signal Kind\n- {plan['signal_kind']}\n")
    print(f"Category\n- {plan['category']}\n")
    print(f"Analysis Branch\n- {plan['analysis_branch']}\n")
    print(f"Undesirable Signal\n- {plan['undesirable_signal']}\n")
    if plan['observed_signals']:
        print('Observed Signals')
        for item in plan['observed_signals']:
            print(f'- {item}')
        print()
    print(f"Protection State\n- {plan['protection_state']}\n")
    print(f"Outside Review Required\n- {plan['outside_review_required']}\n")
    print('Packet Fields')
    for item in plan['packet_fields']:
        print(f'- {item}')
    print(f"\nRoot Cause\n- {plan['root_cause']}\n")
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
