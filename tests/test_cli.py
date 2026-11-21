"""命令行端到端测试。"""

import contextlib
import io
import json
import unittest

from crony.cli import main


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_human_next(self):
        code, out, err = self.run_cli("*/5 * * * *", "--next", "3",
                                      "--after", "2026-11-21 10:03")
        self.assertEqual(code, 0, err)
        self.assertIn("表达式:*/5 * * * *", out)
        self.assertIn("2026-11-21 10:05:00", out)
        self.assertIn("2026-11-21 10:10:00", out)

    def test_explain(self):
        code, out, _ = self.run_cli("*/5 * * * 1-5", "--explain")
        self.assertEqual(code, 0)
        self.assertIn("第 0、5、10、15、20、25、30、35、40、45、50、55 分", out)
        self.assertIn("周一", out)

    def test_explain_json(self):
        code, out, _ = self.run_cli("0 9 * * MON", "--explain", "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["explain"]["hour"], "第 9 点")
        self.assertEqual(data["explain"]["weekday"], "周一")

    def test_json_output(self):
        code, out, _ = self.run_cli("0 0 1 1 *", "--after", "2026-11-21", "--next", "1",
                                    "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["next"], ["2027-01-01T00:00:00"])
        self.assertEqual(data["fields"]["months"], [1])

    def test_invalid_expression(self):
        code, _, err = self.run_cli("*/0 * * * *")
        self.assertEqual(code, 1)
        self.assertIn("步长", err)

    def test_wrong_field_count(self):
        code, _, err = self.run_cli("* * * *")
        self.assertEqual(code, 1)
        self.assertIn("5 个字段", err)

    def test_bad_after_format(self):
        code, _, err = self.run_cli("* * * * *", "--after", "昨天")
        self.assertEqual(code, 1)
        self.assertIn("--after", err)

    def test_negative_next(self):
        code, _, err = self.run_cli("* * * * *", "--next", "0")
        self.assertEqual(code, 1)
        self.assertIn("至少为 1", err)

    def test_impossible_combo(self):
        code, _, err = self.run_cli("0 0 30 2 *")
        self.assertEqual(code, 1)
        self.assertIn("没有任何触发", err)


if __name__ == "__main__":
    unittest.main()
