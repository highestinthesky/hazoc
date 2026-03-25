#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime


def main() -> None:
    p = argparse.ArgumentParser(description='Draft a compact safe-evolution report')
    p.add_argument('--signal', default='')
    p.add_argument('--change', default='')
    p.add_argument('--validation', default='')
    p.add_argument('--outcome', default='')
    p.add_argument('--next', dest='next_step', default='')
    args = p.parse_args()

    now = datetime.now().isoformat(timespec='seconds')
    print(f"# Safe Evolution Report\n\nGenerated: {now}\n")
    print('Signal')
    print(f"- {args.signal or '[describe the trigger]'}\n")
    print('Change')
    print(f"- {args.change or '[describe the smallest safe change]'}\n")
    print('Validation')
    print(f"- {args.validation or '[describe how it was checked]'}\n")
    print('Outcome')
    print(f"- {args.outcome or '[describe what improved or failed]'}\n")
    print('Next')
    print(f"- {args.next_step or '[describe the next action]'}")


if __name__ == '__main__':
    main()
