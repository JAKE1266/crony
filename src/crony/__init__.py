"""crony —— cron 表达式解析与下次执行时间计算(零依赖)。

::

    from crony import parse, next_fires, describe

    expr = parse("*/5 * * * 1-5")
    print(next_fires(expr, count=3))
"""

from crony.core.parser import CronExpr, describe, parse
from crony.core.schedule import next_fire, next_fires

__version__ = "1.0.0"

__all__ = ["CronExpr", "describe", "next_fire", "next_fires", "parse", "__version__"]
