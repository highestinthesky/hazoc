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

STERILE_SUBAGENT_CWD = '/tmp/grounded-evolver-clean-room'
OUTSIDE_REVIEW_HELPER = 'skills/grounded-evolver/scripts/prepare_outside_review.py'
SNAPSHOT_REVERT_HELPER = 'skills/grounded-evolver/scripts/snapshot_revert.py'


def clamp(v: int, lo: int = 1, hi: int = 5) -> int:
    return max(lo, min(hi, int(v)))


def json_block(data) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


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
    if undesirable_signal(args) and args.protocol_caused_problem:
        return 'causal-followed-protocol'
    if undesirable_signal(args) and args.protocol_existed:
        return 'existing-protection-present'
    if undesirable_signal(args):
        return 'no-known-failed-protection'
    return 'no-protection-issue'


def choose_analysis_branch(args) -> str:
    kind = signal_kind(args)
    if args.protocol_failed:
        return 'repair-pattern'
    if undesirable_signal(args) and args.protocol_caused_problem:
        return 'repair-pattern'
    if kind == 'repeat-failure':
        return 'repair-pattern'
    if undesirable_signal(args) and (args.protocol_existed or args.repeat_count >= 2):
        return 'repair-pattern'
    return 'build-pattern'


def branch_reason(args) -> str:
    kind = signal_kind(args)
    if args.protocol_failed:
        return 'an existing protection explicitly failed'
    if undesirable_signal(args) and args.protocol_caused_problem:
        return 'the problem appears to have been caused or amplified by a followed protocol'
    if kind == 'repeat-failure':
        return 'the signal kind itself is repeat-failure'
    if undesirable_signal(args) and args.protocol_existed:
        return 'undesirable friction occurred in a context where a protection already existed'
    if undesirable_signal(args) and args.repeat_count >= 2:
        return 'undesirable friction repeated strongly enough to prove the current pattern is insufficient'
    return 'no failed or clearly insufficient protection is known yet'


def default_symptom_type(args) -> str:
    signals = request_friction_signals(args)
    if signals:
        return ', '.join(signals)
    return 'unspecified-request-friction'


def default_failure_mode(args) -> str:
    signals = [s for s in request_friction_signals(args) if s != 'repeat-friction']
    if signals:
        return ', '.join(signals)
    kind = signal_kind(args)
    if kind == 'repeat-failure':
        return 'repeat-failure'
    return kind


def default_outcome_type(args) -> str:
    kind = signal_kind(args)
    defaults = {
        'progress': 'meaningful-progress',
        'decision': 'plan-or-rule-change',
        'request': 'new-request',
        'blocker': 'new-blocker',
    }
    return defaults.get(kind, kind)


def infer_failed_layer(args) -> str:
    kind = signal_kind(args)
    if args.ui:
        return 'ui-or-interaction-layer'
    if args.tool_failure:
        return 'tool-or-integration-layer'
    if args.skipped_step:
        return 'execution-or-checklist-layer'
    if args.protocol_failed or args.protocol_existed:
        return 'protocol-or-workflow-layer'
    if kind == 'cross-channel':
        return 'cross-channel-continuity-layer'
    return 'unspecified-protection-layer'


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

    if args.protocol_name or args.protocol_existed or args.protocol_failed:
        fields.append('protection_reference')
    if undesirable_signal(args):
        fields.append('protocol_causation_assessment')
    if args.causal_protocol:
        fields.append('causal_protocol_reference')
    if observed_signals(args):
        fields.append('observed_signals')
    if branch == 'repair-pattern':
        fields.append('failed_layer')
    return fields


def outside_review_required(args) -> bool:
    if choose_analysis_branch(args) == 'repair-pattern':
        return True
    return undesirable_signal(args)


def build_problem_packet(args) -> dict:
    kind = signal_kind(args)
    branch = choose_analysis_branch(args)

    packet: dict = {'signal_kind': kind}
    if kind == 'request-friction':
        packet['request_context'] = args.request_context or args.context or args.signal
        packet['symptom_type'] = args.symptom_type or default_symptom_type(args)
    elif undesirable_signal(args):
        packet['context'] = args.context or args.signal
        packet['failure_mode'] = args.failure_mode or default_failure_mode(args)
    else:
        packet['context'] = args.context or args.signal
        packet['outcome_type'] = args.outcome_type or default_outcome_type(args)

    packet['impact'] = args.impact
    packet['repeat_count'] = args.repeat_count
    packet['protection_state'] = protection_state(args)
    packet['loss_risk'] = args.loss_risk
    packet['blast_radius'] = args.blast_radius

    if args.protocol_name or args.protocol_existed or args.protocol_failed:
        packet['protection_reference'] = args.protocol_name or 'unnamed-existing-protection'
    if undesirable_signal(args):
        if args.protocol_caused_problem:
            packet['protocol_causation_assessment'] = 'caused-or-amplified-by-followed-protocol'
        elif args.protocol_failed:
            packet['protocol_causation_assessment'] = 'possible-existing-protocol-failure'
        elif args.protocol_existed:
            packet['protocol_causation_assessment'] = 'check-whether-existing-protocol-contributed'
        else:
            packet['protocol_causation_assessment'] = 'unknown'
    if args.causal_protocol:
        packet['causal_protocol_reference'] = args.causal_protocol
    signals = observed_signals(args)
    if signals:
        packet['observed_signals'] = signals
    if branch == 'repair-pattern':
        packet['failed_layer'] = args.failed_layer or infer_failed_layer(args)

    return packet


def protocol_causation_check(args) -> dict:
    if not undesirable_signal(args):
        return {
            'required': False,
            'question': 'Could this problem have been caused by one of the protocols that I follow?',
            'note': 'Not applicable because the current signal is not a problem/failure case.',
        }

    if args.protocol_caused_problem:
        assessment = 'yes'
    elif args.protocol_failed:
        assessment = 'possible-failed-protocol'
    elif args.protocol_existed:
        assessment = 'possible-existing-protocol-contribution'
    else:
        assessment = 'unknown'

    result = {
        'required': True,
        'question': 'Could this problem have been caused or amplified by one of the protocols currently being followed?',
        'assessment': assessment,
        'if_yes': [
            'Identify the specific protocol, rule, or checklist pattern that appears causal.',
            'Explain how it caused or amplified the problem.',
            'Prefer revising, narrowing, or removing the causal protocol instead of stacking another protocol on top.',
        ],
        'if_no': 'Continue with the normal build/repair logic and treat the issue as missing or insufficient protection rather than protocol-caused.',
    }
    if args.causal_protocol:
        result['causal_protocol_reference'] = args.causal_protocol
    return result


def artifact_checklist(args) -> list[str]:
    branch = choose_analysis_branch(args)
    if branch == 'repair-pattern':
        items = [
            'problem packet',
            'protocol-causation assessment',
            'self-authored repair plan',
            'clean outside diagnosis prompt',
            'clean-room subagent spawn spec',
            'merged repair decision',
            'durable write in the chosen destination',
        ]
    elif undesirable_signal(args):
        items = [
            'problem packet',
            'protocol-causation assessment',
            'self-authored prevention/update list',
            'clean outside review prompt',
            'clean-room subagent spawn spec',
            'merged generalized draft',
            'durable write in the chosen destination',
        ]
    else:
        items = [
            'signal-capture packet',
            'chosen durable write(s)',
            'validation note or proof',
        ]

    if revert_required(args):
        items.append('pre-change snapshot and revert plan')
    return items


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
                'ask whether one of the currently followed protocols caused or amplified the problem',
                'draft a self-authored prevention/update list',
            ])
            if outside_review_required(args):
                actions.append('get a clean third-party take')
                actions.append('spawn a clean-room isolated subagent with the outside_review_prompt as the exact task')
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
            'ask whether one of the currently followed protocols caused or amplified the problem',
        ])
        if outside_review_required(args):
            actions.append('get a clean outside diagnosis')
            actions.append('spawn a clean-room isolated subagent with the outside_review_prompt as the exact task')
        actions.extend([
            'produce self and third-party change plans',
            'repair the failed protection at the right layer',
        ])

    if revert_required(args):
        actions.append('capture exact pre-change text before mutating any protocol/rule/workflow file')
        actions.append('prepare a rollback path for each protocol addition or edit')
        actions.append('revert provisional protocol/workflow changes immediately if vetting or validation fails')

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

    if args.protocol_caused_problem:
        actions.append('prefer revising, narrowing, or removing the causal protocol instead of stacking another protocol on top')

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


def revert_required(args) -> bool:
    target = choose_mutation_target(args)
    return target in {'operating-rule', 'workflow-or-skill-patch', 'rule-or-workflow-repair'} or args.rule or args.protocol_existed or args.protocol_failed


def revert_plan(args) -> dict:
    if not revert_required(args):
        return {}

    target = choose_mutation_target(args)
    plan = {
        'required': True,
        'trigger': 'If safety/security vetting rejects the proposed protocol/workflow change, or if post-change validation shows the mutation was wrong or unsafe.',
        'surface': target,
        'before_change': [
            'Capture the exact pre-change text for every file/block that will be edited.',
            'Prefer surgical edits over whole-file overwrite so rollback can restore the previous state precisely.',
            'For a new inserted rule/block, record the exact inserted text and destination.',
            'For a newly created file, record that it is new so rollback can delete it cleanly if needed.',
        ],
    }

    if target == 'operating-rule':
        plan['rollback_actions'] = [
            'Restore the previous AGENTS/rule text exactly, or remove the newly inserted rule block entirely.',
            'Re-run the relevant validation checks so the reverted state is confirmed stable.',
            'Only then surface the failed proposal and why it was rejected.',
        ]
        plan['success_condition'] = 'The prior rule state is restored exactly and no rejected protocol addition remains active.'
    elif target == 'workflow-or-skill-patch':
        plan['rollback_actions'] = [
            'Restore the exact pre-change contents of the affected skill/workflow/helper files.',
            'Delete any newly created protocol/helper file that was added provisionally.',
            'Re-run smoke tests so the previous behavior is confirmed back in place before reporting the failure.',
        ]
        plan['success_condition'] = 'The skill/workflow returns to the exact prior behavior and no rejected helper/protocol addition remains.'
    else:
        plan['rollback_actions'] = [
            'Restore the prior rule/workflow text or structure exactly.',
            'If multiple files were touched, revert them as one coherent set rather than leaving a mixed state.',
            'Re-run the relevant validation checks before treating the rollback as complete.',
        ]
        plan['success_condition'] = 'The prior workflow/rule set is restored as a coherent whole and the rejected repair does not remain partially active.'

    return plan


def generalized_moral(args) -> str:
    if args.moral:
        return args.moral

    kind = signal_kind(args)
    branch = choose_analysis_branch(args)

    if branch == 'repair-pattern':
        if args.protocol_caused_problem:
            return 'When a followed protocol causes or amplifies a problem, revise or remove the causal protocol instead of layering more protocol on top.'
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
        if args.protocol_caused_problem:
            return 'A real signal suggested that one of the currently followed protocols was itself causing or amplifying the problem, so the protocol set needs revision rather than simple expansion.'
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

    if undesirable_signal(args):
        checks.extend([
            'Ask whether one of the currently followed protocols caused or amplified the problem.',
            'If yes, prefer revising, narrowing, or removing the causal protocol instead of stacking another protocol on top.',
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

    if outside_review_required(args):
        checks.extend([
            'When spawning the outside reviewer, use the outside_review_prompt as the exact task text instead of rewriting it from memory.',
            'Use a clean-room spawn configuration: one-shot run, delete cleanup, sandbox require, and a sterile temp cwd outside the workspace.',
            'Do not attach extra files or prepend parent-session summary when booting the outside reviewer.',
            'Treat literal zero inherited platform context as not guaranteed unless OpenClaw itself exposes a skip-startup-anchor feature; design the prompt so the packet is the only allowed problem context.',
        ])

    if revert_required(args):
        checks.extend([
            'Before mutating protocol/rule/workflow files, capture the exact old text or exact inserted block so rollback is precise.',
            'Do not make a protocol addition you cannot cleanly remove if vetting fails.',
            'If vetting fails after a provisional protocol/workflow mutation, revert the change before treating the run as complete.',
            'If validation fails, restore the pre-change state instead of leaving a half-accepted protocol mutation active.',
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
        if args.protocol_caused_problem:
            return 'Capture the pre-change state first, confirm which followed protocol caused or amplified the problem, use the generated outside-review prompt, then revise/narrow/remove the causal protocol instead of layering more protocol on top and revert immediately if vetting fails.'
        return 'Capture the pre-change state first, use the generated failure packet and the exact outside_review_prompt in a clean-room subagent run, compare self and outside repair plans, then implement the smallest safe fix at the right layer and revert immediately if vetting fails.'
    if undesirable_signal(args):
        return 'Capture the pre-change state first, ask whether one of the followed protocols caused the problem, use the generated problem packet and the exact outside_review_prompt in a clean-room subagent run, write a first prevention/update draft, then promote the smallest safe generalized change and revert immediately if vetting fails.'
    return 'Capture the signal in the smallest durable state, then validate that future-you could recover from that record.'


def self_authored_prompt(args) -> str:
    branch = choose_analysis_branch(args)
    kind = signal_kind(args)
    packet = build_problem_packet(args)

    if branch == 'repair-pattern':
        task_lines = [
            'Review the packet and identify the failed protection or insufficient pattern.',
            'Ask whether one of the currently followed protocols caused or amplified the problem; if yes, name it or describe its pattern.',
            'Write a self-authored repair plan that fixes the issue at the right layer.',
            'Prefer the smallest durable repair that actually addresses the failure class.',
            'Do not default to cosmetic rule rewrites if the workflow, skill, or implementation layer is the real problem.',
            'If a followed protocol appears causal, prefer revising, narrowing, or removing it instead of stacking another protocol on top.',
            'End with: root cause, generalized moral, protocol-causation assessment, repair options, preferred smallest safe change, risks/unknowns.',
        ]
    elif undesirable_signal(args):
        task_lines = [
            'Review the packet and ask whether one of the currently followed protocols caused or amplified the problem.',
            'Draft a self-authored prevention/update list.',
            'Generalize the lesson so it prevents the class of mistake, not just this instance.',
            'Prefer the smallest durable change that would have prevented the friction.',
            'If a followed protocol appears causal, prefer revising, narrowing, or removing it instead of stacking another protocol on top.',
            'End with: root cause, generalized moral, protocol-causation assessment, candidate protections/updates, preferred smallest safe change, risks/unknowns.',
        ]
    else:
        task_lines = [
            'Review the packet and decide which durable state should absorb this signal.',
            'Choose the smallest update that preserves the gain, decision, or state change.',
            'End with: root cause, generalized moral, chosen durable write(s), validation proof, next step.',
        ]

    tasks = '\n'.join(f'- {line}' for line in task_lines)
    return (
        'You are preparing the self-authored first pass for grounded-evolver.\n\n'
        f'Signal kind: {kind}\n'
        f'Chosen branch: {branch}\n'
        f'Branch reason: {branch_reason(args)}\n\n'
        'Problem packet:\n'
        f'{json_block(packet)}\n\n'
        'Task:\n'
        f'{tasks}\n\n'
        'Constraints:\n'
        '- Keep signal kind separate from branch choice.\n'
        '- Prefer the smallest safe change.\n'
        '- Do not assume hidden context beyond the packet.\n'
        '- Do not propose risky autonomy, unsafe access expansion, or secret storage.\n'
        '- If you recommend protocol/rule/workflow changes, keep them reversible and state what would need to be restored if vetting fails.\n'
    )


def outside_review_prompt(args) -> str:
    if not outside_review_required(args):
        return ''

    branch = choose_analysis_branch(args)
    kind = signal_kind(args)
    packet = build_problem_packet(args)

    if branch == 'repair-pattern':
        asks = [
            'Explain why the current protection or pattern still failed.',
            'Assess whether one of the currently followed protocols appears to have caused or amplified the problem.',
            'Identify the layer that most likely needs repair (memory, rule, workflow, skill/helper, implementation, or UI).',
            'Propose the smallest durable repair that addresses the failure class.',
            'Say whether a rule-only change is insufficient and why, if applicable.',
            'If a followed protocol appears causal, say whether it should be revised, narrowed, or removed instead of layering more protocol on top.',
            'Return: diagnosis, protocol-causation assessment, failed layer, repair options, preferred smallest safe change, risks/unknowns.',
        ]
    else:
        asks = [
            'Generalize the packet into a reusable prevention/update pattern.',
            'Assess whether one of the currently followed protocols appears to have caused or amplified the problem.',
            'Propose protections or changes that would prevent this class of friction in the future.',
            'Prefer the smallest durable change that solves the class of problem.',
            'If a followed protocol appears causal, say whether it should be revised, narrowed, or removed instead of layering more protocol on top.',
            'Return: diagnosis, protocol-causation assessment, generalized pattern, candidate protections, preferred smallest safe change, risks/unknowns.',
        ]

    ask_block = '\n'.join(f'- {line}' for line in asks)
    return (
        'You are a clean-room outside reviewer for grounded-evolver.\n'
        'Treat the packet below as the only allowed problem context.\n'
        'Do not assume hidden chat history, current-session memory, task-board context, workspace notes, or prior discussion.\n'
        'Do not read workspace files, daily notes, AGENTS, MEMORY, or other artifacts unless the packet itself explicitly includes them.\n'
        'If any extra ambient context is visible to you, ignore it and continue using only the packet below.\n\n'
        f'Signal kind: {kind}\n'
        f'Chosen branch: {branch}\n'
        f'Branch reason: {branch_reason(args)}\n\n'
        'Problem packet:\n'
        f'{json_block(packet)}\n\n'
        'Review tasks:\n'
        f'{ask_block}\n\n'
        'Constraints:\n'
        '- Stay within the packet.\n'
        '- Do not propose unsafe autonomy or access expansion.\n'
        '- Call out uncertainty instead of inventing facts.\n'
        '- Optimize for generalizable, durable guidance rather than incident-specific wording.\n'
        '- If you recommend protocol/rule/workflow changes, also note how they could be reverted cleanly if vetting rejects them.\n'
    )


def subagent_spawn_plan(args) -> dict:
    if not outside_review_required(args):
        return {}
    return {
        'task': outside_review_prompt(args),
        'label': 'grounded-outside-review',
        'runtime': 'subagent',
        'mode': 'run',
        'cleanup': 'delete',
        'sandbox': 'require',
        'cwd': STERILE_SUBAGENT_CWD,
        'runTimeoutSeconds': 180,
    }


def spawn_isolation_notes() -> list[str]:
    return [
        'Use the outside_review_prompt as the exact subagent task; do not rewrite or summarize it from memory.',
        'Spawn as a one-shot isolated run with delete cleanup.',
        f'Use a sterile temp cwd outside the workspace when possible: {STERILE_SUBAGENT_CWD}.',
        'Do not attach extra files, prior conversation, or parent-session summaries.',
        f'If you already saved the planner JSON, {OUTSIDE_REVIEW_HELPER} can emit the exact preferred/fallback spawn payloads for you.',
        'This creates a best-effort clean room, but literal zero inherited platform context is not guaranteed unless OpenClaw exposes a dedicated skip-startup-anchor capability.',
    ]


def helper_scripts() -> dict:
    return {
        'outside_review_prepare': OUTSIDE_REVIEW_HELPER,
        'snapshot_revert': SNAPSHOT_REVERT_HELPER,
    }


def helper_command_templates() -> dict:
    return {
        'outside_review_prepare': f'python3 {OUTSIDE_REVIEW_HELPER} --plan-file /tmp/grounded-plan.json --json',
        'snapshot': f'python3 {SNAPSHOT_REVERT_HELPER} snapshot --name <change-id> --file <path> [--file <path> ...]',
        'restore': f'python3 {SNAPSHOT_REVERT_HELPER} restore --name <change-id>',
    }


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
    p.add_argument('--context', default='')
    p.add_argument('--request-context', default='')
    p.add_argument('--symptom-type', default='')
    p.add_argument('--failure-mode', default='')
    p.add_argument('--outcome-type', default='')
    p.add_argument('--failed-layer', default='')
    p.add_argument('--protocol-name', default='')
    p.add_argument('--protocol-caused-problem', action='store_true')
    p.add_argument('--causal-protocol', default='')
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
        'branch_reason': branch_reason(args),
        'undesirable_signal': undesirable_signal(args),
        'observed_signals': observed_signals(args),
        'protection_state': protection_state(args),
        'outside_review_required': outside_review_required(args),
        'packet_fields': packet_fields(args),
        'problem_packet': build_problem_packet(args),
        'protocol_causation_check': protocol_causation_check(args),
        'artifact_checklist': artifact_checklist(args),
        'self_authored_prompt': self_authored_prompt(args),
        'outside_review_prompt': outside_review_prompt(args),
        'outside_review_spawn_plan': subagent_spawn_plan(args),
        'outside_review_spawn_notes': spawn_isolation_notes() if outside_review_required(args) else [],
        'revert_required': revert_required(args),
        'revert_plan': revert_plan(args),
        'root_cause': root_cause_summary(args),
        'generalized_moral': generalized_moral(args),
        'priority_score': priority_score(args),
        'mutation_target': choose_mutation_target(args),
        'recommended_actions': build_actions(args),
        'validation_checks': validation_checks(args),
        'helper_scripts': helper_scripts(),
        'helper_command_templates': helper_command_templates(),
        'next_step': next_step(args),
    }

    if args.json:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return

    print('# Grounded Evolution Plan\n')
    print(f"Signal\n- {plan['signal']}\n")
    print(f"Signal Kind\n- {plan['signal_kind']}\n")
    print(f"Category\n- {plan['category']}\n")
    print(f"Analysis Branch\n- {plan['analysis_branch']}\n")
    print(f"Branch Reason\n- {plan['branch_reason']}\n")
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
    print(f"\nProblem Packet\n{json_block(plan['problem_packet'])}\n")
    print(f"Protocol-Causation Check\n{json_block(plan['protocol_causation_check'])}\n")
    print('Artifact Checklist')
    for item in plan['artifact_checklist']:
        print(f'- {item}')
    if plan['revert_required']:
        print(f"Revert Required\n- {plan['revert_required']}\n")
        print(f"Revert Plan\n{json_block(plan['revert_plan'])}\n")
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
    print('\nHelper Scripts')
    for key, value in plan['helper_scripts'].items():
        print(f'- {key}: {value}')
    print('\nHelper Command Templates')
    for key, value in plan['helper_command_templates'].items():
        print(f'- {key}: {value}')
    print(f"\nSelf-Authored Prompt\n{plan['self_authored_prompt']}\n")
    if plan['outside_review_prompt']:
        print(f"Outside Review Prompt\n{plan['outside_review_prompt']}\n")
        print(f"Outside Review Spawn Plan\n{json_block(plan['outside_review_spawn_plan'])}\n")
        print('Outside Review Spawn Notes')
        for item in plan['outside_review_spawn_notes']:
            print(f'- {item}')
        print()
    print(f"Next Step\n- {plan['next_step']}")


if __name__ == '__main__':
    main()
