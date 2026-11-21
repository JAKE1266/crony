"""解析器与人话描述单元测试。"""

import unittest

from crony.core.parser import CronExpr, describe, parse


class ParseTest(unittest.TestCase):
    def test_wildcard_all_sets(self):
        expr = parse("* * * * *")
        self.assertEqual(len(expr.minutes), 60)
        self.assertEqual(len(expr.hours), 24)
        self.assertEqual(len(expr.doms), 31)
        self.assertEqual(len(expr.months), 12)
        self.assertEqual(len(expr.dows), 7)
        self.assertTrue(expr.dom_any and expr.dow_any)

    def test_steps_and_ranges(self):
        expr = parse("*/5 9-17 1-15/2 JAN-MAR MON-FRI")
        self.assertEqual(expr.minutes, frozenset(range(0, 60, 5)))
        self.assertEqual(expr.hours, frozenset(range(9, 18)))
        self.assertEqual(expr.doms, frozenset({1, 3, 5, 7, 9, 11, 13, 15}))
        self.assertEqual(expr.months, frozenset({1, 2, 3}))
        self.assertEqual(expr.dows, frozenset({1, 2, 3, 4, 5}))
        self.assertFalse(expr.dom_any)
        self.assertFalse(expr.dow_any)

    def test_lists_and_single_values(self):
        expr = parse("0,30 1,9,17 1 1,7 *")
        self.assertEqual(expr.minutes, frozenset({0, 30}))
        self.assertEqual(expr.hours, frozenset({1, 9, 17}))
        self.assertEqual(expr.months, frozenset({1, 7}))

    def test_step_on_single_value_is_just_value(self):
        expr = parse("15/1 * * * *")
        self.assertEqual(expr.minutes, frozenset({15}))

    def test_zero_step_rejected(self):
        with self.assertRaises(ValueError):
            parse("15/0 * * * *")

    def test_dow_7_is_sunday(self):
        expr = parse("0 0 * * 7")
        self.assertEqual(expr.dows, frozenset({0}))

    def test_dow_any_flag(self):
        self.assertTrue(parse("0 0 * * *").dow_any)
        self.assertFalse(parse("0 0 * * 1").dow_any)
        self.assertTrue(parse("0 0 * * 1").dom_any)      # 日位仍是 *
        self.assertTrue(parse("0 0 1 * *").dow_any)      # 星期位仍是 *
        self.assertFalse(parse("0 0 1 * *").dom_any)     # 日位已受限

    def test_names(self):
        self.assertEqual(parse("* * * JAN-MAR *").months, frozenset({1, 2, 3}))
        self.assertEqual(parse("* * * * SUN,TUE").dows, frozenset({0, 2}))

    def test_invalid_inputs(self):
        cases = [
            ("* * * *", "5 个字段"),
            ("* * * * * *", "5 个字段"),
            ("*/0 * * * *", "步长"),
            ("75 * * * *", "越界"),
            ("* 24 * * *", "越界"),
            ("* * 32 * *", "越界"),
            ("* * * 13 *", "越界"),
            ("* * * * 8", "越界"),
            ("5-2 * * * *", "颠倒"),
            ("1,,2 * * * *", "空项"),
            ("* * * FOO *", "不是合法的值"),
            ("* * * * FOO", "不是合法的值"),
        ]
        for expr, message in cases:
            with self.subTest(expr=expr):
                with self.assertRaises(ValueError) as ctx:
                    parse(expr)
                self.assertIn(message, str(ctx.exception))

    def test_type_check(self):
        with self.assertRaises(TypeError):
            parse(None)


class DescribeTest(unittest.TestCase):
    def test_full_wildcard(self):
        d = describe("* * * * *")
        self.assertEqual(d["minute"], "每分钟")
        self.assertEqual(d["hour"], "每小时")
        self.assertEqual(d["day"], "每天")
        self.assertEqual(d["month"], "每月")
        self.assertEqual(d["weekday"], "不限星期")

    def test_specific(self):
        d = describe("*/5 9 1 3 MON")
        self.assertEqual(d["minute"], "第 0、5、10、15、20、25、30、35、40、45、50、55 分")
        self.assertEqual(d["hour"], "第 9 点")
        self.assertEqual(d["day"], "每月 1 日")
        self.assertEqual(d["month"], "三月")
        self.assertEqual(d["weekday"], "周一")

    def test_range_description(self):
        d = describe("0 9-17 * * MON-FRI")
        self.assertEqual(d["hour"], "第 9-17 点")
        self.assertEqual(d["weekday"], "周一、周二、周三、周四、周五")


if __name__ == "__main__":
    unittest.main()
