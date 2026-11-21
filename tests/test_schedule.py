"""触发时间计算测试(注入固定 after,保证确定性)。"""

import unittest
from datetime import datetime

from crony.core.parser import parse
from crony.core.schedule import next_fire, next_fires

# 2026-11-21 是周六;2026-11-23 是周一
AFTER = datetime(2026, 11, 21, 10, 3)


class NextFireTest(unittest.TestCase):
    def test_every_five_minutes(self):
        fires = next_fires(parse("*/5 * * * *"), count=3, after=AFTER)
        self.assertEqual(fires, [
            datetime(2026, 11, 21, 10, 5),
            datetime(2026, 11, 21, 10, 10),
            datetime(2026, 11, 21, 10, 15),
        ])

    def test_daily_midnight_skips_to_next_day(self):
        fire = next_fire(parse("0 0 * * *"), after=AFTER)
        self.assertEqual(fire, datetime(2026, 11, 22, 0, 0))

    def test_hour_jump_ignores_earlier_minute(self):
        fire = next_fire(parse("30 10 * * *"), after=datetime(2026, 11, 21, 10, 31))
        self.assertEqual(fire, datetime(2026, 11, 22, 10, 30))

    def test_weekday_range_skips_weekend(self):
        fire = next_fire(parse("0 12 * * 1-5"), after=datetime(2026, 11, 20, 13, 0))
        # 周五 13:00 之后 → 周一 12:00
        self.assertEqual(fire, datetime(2026, 11, 23, 12, 0))

    def test_monthly(self):
        fire = next_fire(parse("30 2 1 * *"), after=AFTER)
        self.assertEqual(fire, datetime(2026, 12, 1, 2, 30))

    def test_year_rollover(self):
        fire = next_fire(parse("0 0 1 1 *"), after=datetime(2026, 11, 21, 10, 0))
        self.assertEqual(fire, datetime(2027, 1, 1, 0, 0))

    def test_dom_dow_or_semantics(self):
        # 「13 日 或 周五」:17 日(周二)之后 → 20 日(周五)先到
        fire = next_fire(parse("0 9 13 * 5"), after=datetime(2026, 11, 17, 10, 0))
        self.assertEqual(fire, datetime(2026, 11, 20, 9, 0))
        # 21 日(周六)之后 → 23 日周一? 不:27 日周五 vs 12 月 13 日…… 下一个周五是 27 日
        fire = next_fire(parse("0 9 13 * 5"), after=datetime(2026, 11, 21, 10, 0))
        self.assertEqual(fire, datetime(2026, 11, 27, 9, 0))

    def test_impossible_combo_raises(self):
        with self.assertRaises(ValueError) as ctx:
            next_fire(parse("0 0 30 2 *"), after=AFTER)  # 2 月 30 日
        self.assertIn("没有任何触发", str(ctx.exception))

    def test_second_microsecond_ignored(self):
        fire = next_fire(parse("*/10 * * * *"),
                         after=datetime(2026, 11, 21, 10, 3, 7, 999))
        self.assertEqual(fire, datetime(2026, 11, 21, 10, 10))

    def test_count_validation(self):
        expr = parse("* * * * *")
        with self.assertRaises(ValueError):
            next_fires(expr, count=0)

    def test_next_fires_sequential(self):
        fires = next_fires(parse("0 12 * * *"), count=3,
                           after=datetime(2026, 11, 21, 13, 0))
        self.assertEqual(fires, [
            datetime(2026, 11, 22, 12, 0),
            datetime(2026, 11, 23, 12, 0),
            datetime(2026, 11, 24, 12, 0),
        ])


if __name__ == "__main__":
    unittest.main()
