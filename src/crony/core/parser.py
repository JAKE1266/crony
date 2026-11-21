"""cron 表达式解析(5 字段:分 时 日 月 星期,Vixie cron 常用子集)。

语法:每字段由逗号分隔的项组成,每项支持:

- ``*``(全部)/ ``*/n``(步进)
- ``a-b``(范围)/ ``a-b/n``(步进范围)/ 单值 ``a``
- 月与星期支持英文缩写(JAN…DEC、SUN…SAT);星期 7 视为周日(0)

语义:日 与 星期 都受限时按「或」匹配(Vixie cron 标准);只受限其一时按「且」。
"""

from __future__ import annotations

import re
from dataclasses import dataclass

FIELD_NAMES = ("分钟", "小时", "日", "月", "星期")
RANGES = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))

MONTH_NAMES = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
               "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}
WEEKDAY_NAMES = {"SUN": 0, "MON": 1, "TUE": 2, "WED": 3, "THU": 4, "FRI": 5, "SAT": 6}
WEEKDAY_CN = ("周日", "周一", "周二", "周三", "周四", "周五", "周六")
MONTH_CN = ("", "一月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "十一月", "十二月")


@dataclass(frozen=True)
class CronExpr:
    """解析后的表达式:各字段为允许值的集合。

    ``dom_any`` / ``dow_any`` 表示「日」「星期」字段写的是 ``*``(未受限)——
    两者都受限时按「或」匹配,这是 Vixie cron 的标准语义。
    """

    minutes: frozenset
    hours: frozenset
    doms: frozenset
    months: frozenset
    dows: frozenset
    dom_any: bool
    dow_any: bool
    expr: str


def _value(token: str, index: int) -> int:
    if not token:
        raise ValueError(f"{FIELD_NAMES[index]}字段存在空值")
    token = token.strip().upper()
    if token.isdigit():
        return int(token)
    if index == 3 and token in MONTH_NAMES:
        return MONTH_NAMES[token]
    if index == 4 and token in WEEKDAY_NAMES:
        return WEEKDAY_NAMES[token]
    raise ValueError(f"{FIELD_NAMES[index]}字段不是合法的值:{token!r}")


def _parse_field(raw: str, index: int) -> frozenset:
    lo, hi = RANGES[index]
    values: set = set()
    for term in raw.split(","):
        term = term.strip()
        if not term:
            raise ValueError(f"{FIELD_NAMES[index]}字段存在空项:{raw!r}")
        step = 1
        if "/" in term:
            term, step_text = term.split("/", 1)
            if not step_text.isdigit() or int(step_text) == 0:
                raise ValueError(f"{FIELD_NAMES[index]}字段步长必须为正整数:{step_text!r}")
            step = int(step_text)
            if term in ("", "*"):
                term = f"{lo}-{hi}"
        if "-" in term and not term.startswith("-"):
            start_text, end_text = term.split("-", 1)
            start, end = _value(start_text, index), _value(end_text, index)
            if start > end:
                raise ValueError(f"{FIELD_NAMES[index]}字段范围起止颠倒:{start}-{end}")
            base = list(range(start, end + 1))
        elif term == "*":
            base = list(range(lo, hi + 1))
        else:
            base = [_value(term, index)]
        values.update(base[::step])

    if index == 4:  # 星期 7 = 周日(0)
        if 7 in values:
            values.discard(7)
            values.add(0)
    for value in values:
        if not lo <= value <= hi:
            raise ValueError(f"{FIELD_NAMES[index]}字段值越界:{value}(允许 {lo}-{hi})")
    return frozenset(values)


def parse(expr: str) -> CronExpr:
    """解析 5 字段 cron 表达式,非法输入抛 ``ValueError``。"""
    if not isinstance(expr, str):
        raise TypeError(f"expr 必须是字符串,得到:{type(expr).__name__}")
    fields = expr.split()
    if len(fields) != 5:
        raise ValueError(
            f"cron 表达式应为 5 个字段(分 时 日 月 星期),得到 {len(fields)} 个:{expr!r}")
    sets = [_parse_field(field, index) for index, field in enumerate(fields)]
    return CronExpr(
        minutes=sets[0], hours=sets[1], doms=sets[2], months=sets[3], dows=sets[4],
        dom_any=fields[2] == "*",
        dow_any=fields[4] == "*",
        expr=" ".join(fields),
    )


def _fmt_values(values) -> str:
    """整数值集合:连续段压缩为 a-b,其余顿号连接。"""
    ordered = sorted(values)
    if len(ordered) > 1 and ordered == list(range(ordered[0], ordered[-1] + 1)):
        return f"{ordered[0]}-{ordered[-1]}"
    return "、".join(str(v) for v in ordered)


def describe(expr: str) -> dict:
    """把表达式翻译成人话,返回各字段描述(供 ``--explain``)。"""
    parsed = parse(expr)
    minute_desc = ("每分钟" if len(parsed.minutes) == 60
                   else "第 " + _fmt_values(parsed.minutes) + " 分")
    hour_desc = ("每小时" if len(parsed.hours) == 24
                 else "第 " + _fmt_values(parsed.hours) + " 点")
    day_desc = "每天" if parsed.dom_any else \
        "每月 " + _fmt_values(parsed.doms) + " 日"
    month_desc = "每月" if len(parsed.months) == 12 else \
        "、".join(MONTH_CN[v] for v in sorted(parsed.months))
    weekday_desc = "不限星期" if parsed.dow_any else \
        "、".join(WEEKDAY_CN[v] for v in sorted(parsed.dows))
    return {
        "minute": minute_desc,
        "hour": hour_desc,
        "day": day_desc,
        "month": month_desc,
        "weekday": weekday_desc,
    }
