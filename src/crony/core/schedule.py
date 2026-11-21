"""触发时间计算:跳月 / 跳日 / 跳时的快速推进,避免逐分钟暴力扫描。"""

from __future__ import annotations

from datetime import datetime, timedelta

from crony.core.parser import CronExpr

_SEARCH_LIMIT_DAYS = 366 * 4  # 最多向后搜索约四年(处理 2 月 30 日这类矛盾表达式)


def _cron_weekday(day) -> int:
    """cron 的星期编号:0 = 周日;Python 的 weekday():0 = 周一。"""
    return (day.weekday() + 1) % 7


def _day_matches(expr: CronExpr, day) -> bool:
    """「日」与「星期」的 Vixie 语义:都受限时按「或」。"""
    dom_ok = day.day in expr.doms
    dow_ok = _cron_weekday(day) in expr.dows
    if expr.dom_any and expr.dow_any:
        return True
    if expr.dom_any:
        return dow_ok
    if expr.dow_any:
        return dom_ok
    return dom_ok or dow_ok


def next_fire(expr: CronExpr, after: datetime | None = None) -> datetime:
    """``after`` 之后(不含)的第一次触发时间。

    :param after: 起算时间;缺省为当前本地时间(秒与微秒被忽略)
    :raises ValueError: 四年内没有任何匹配(如「2 月 30 日」这类矛盾表达式)
    """
    base = after or datetime.now()
    candidate = base.replace(second=0, microsecond=0) + timedelta(minutes=1)
    limit = base + timedelta(days=_SEARCH_LIMIT_DAYS)

    while candidate <= limit:
        if candidate.month not in expr.months:
            year, month = candidate.year, candidate.month + 1
            if month > 12:
                year, month = year + 1, 1
            candidate = candidate.replace(year=year, month=month, day=1,
                                          hour=0, minute=0)
            continue
        if not _day_matches(expr, candidate):
            candidate = (candidate + timedelta(days=1)).replace(hour=0, minute=0)
            continue
        if candidate.hour not in expr.hours:
            candidate = candidate.replace(minute=0) + timedelta(hours=1)
            continue
        if candidate.minute in expr.minutes:
            return candidate
        candidate += timedelta(minutes=1)

    raise ValueError(
        f"表达式 {expr.expr!r} 在未来 {_SEARCH_LIMIT_DAYS // 365} 年内没有任何触发时刻"
        "(例如「2 月 30 日」这类不可能的组合)")


def next_fires(expr: CronExpr, count: int = 5, after: datetime | None = None) -> list:
    """接下来 ``count`` 次触发时间。"""
    if count < 1:
        raise ValueError(f"count 至少为 1:{count}")
    fires: list = []
    cursor = after
    for _ in range(count):
        fire = next_fire(expr, after=cursor)
        fires.append(fire)
        cursor = fire + timedelta(minutes=1)
    return fires
