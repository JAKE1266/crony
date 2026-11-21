# 更新日志

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 格式,
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-11-21

### 新增
- 5 字段 cron 表达式解析:`*`、`*/n`、范围 `a-b`、步进范围 `a-b/n`、列表、
  月与星期英文缩写(JAN…DEC / SUN…SAT)、星期 7 = 周日
- 严格校验:越界、范围颠倒、步长为 0、字段数量错误均给出带字段名的错误信息
- 「日」与「星期」按 Vixie cron 标准语义:都受限时取「或」
- 调度计算:跳月 / 跳日 / 跳时快速推进(不逐分钟暴力扫描);
  「2 月 30 日」这类矛盾表达式在搜索上限后明确报错
- `--next N` 未来 N 次触发;`--after` 注入起算时间(测试确定性);
  `--explain` 中文人话解释;`--json` 结构化输出
- 33 个单元测试;GitHub Actions 三系统 × 三 Python 版本 CI
