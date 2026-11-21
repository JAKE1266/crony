"""crony 命令行入口。

::

    crony "*/5 * * * *"                  # 未来 5 次触发时间
    crony "0 9 * * 1-5" --next 3         # 工作日每天 9 点
    crony "0 0 1 1 *" --explain          # 人话解释
    crony "0 12 * * *" --after 2026-11-21\ 10:00
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime

from . import __version__
from .core.parser import describe, parse
from .core.schedule import next_fires

_AFTER_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d")


def _parse_after(text: str) -> datetime:
    for fmt in _AFTER_FORMATS:
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"--after 支持 YYYY-MM-DD [HH:MM[:SS]]:{text!r}")


def cmd_next(args) -> int:
    try:
        expr = parse(args.expr)
        after = _parse_after(args.after) if args.after else None
        description = describe(args.expr)
        fires = next_fires(expr, count=args.next, after=after)
    except ValueError as exc:
        print(f"错误:{exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({
            "expr": expr.expr,
            "fields": {
                "minutes": sorted(expr.minutes),
                "hours": sorted(expr.hours),
                "days": sorted(expr.doms),
                "months": sorted(expr.months),
                "weekdays": sorted(expr.dows),
            },
            "explain": description,
            "after": after.isoformat() if after else None,
            "next": [fire.isoformat() for fire in fires],
        }, ensure_ascii=False, indent=2))
        return 0

    label = args.after or "现在"
    print(f"表达式:{expr.expr}")
    print(f"起算:{label}(不含)")
    for fire in fires:
        print(f"  {fire.strftime('%Y-%m-%d %H:%M:%S')}")
    return 0


def cmd_explain(args) -> int:
    try:
        description = describe(args.expr)
    except ValueError as exc:
        print(f"错误:{exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"expr": args.expr, "explain": description},
                         ensure_ascii=False, indent=2))
        return 0
    labels = (("分钟", "minute"), ("小时", "hour"), ("日", "day"),
              ("月", "month"), ("星期", "weekday"))
    print(f"表达式:{args.expr.strip()}")
    for label, key in labels:
        print(f"  {label}  {description[key]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crony",
        description="crony —— cron 表达式解析与下次执行时间计算(零依赖)",
    )
    parser.add_argument("--version", action="version", version=f"crony {__version__}")
    parser.add_argument("expr", help='cron 表达式(5 字段),如 "*/5 * * * 1-5"')
    parser.add_argument("--next", type=int, default=5, metavar="N",
                        help="列出未来 N 次触发(默认 5)")
    parser.add_argument("--after", default=None, metavar="时间",
                        help="起算时间(YYYY-MM-DD [HH:MM[:SS]],默认现在)")
    parser.add_argument("--explain", action="store_true", help="用人话解释表达式")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.next < 1:
        print("错误:--next 至少为 1", file=sys.stderr)
        return 1
    handler = cmd_explain if args.explain else cmd_next
    try:
        return handler(args)
    except KeyboardInterrupt:
        print("\n已取消。")
        return 130
    except BrokenPipeError:
        return 0
    except (ValueError, TypeError, OSError) as exc:
        print(f"错误:{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
