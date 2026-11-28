# crony

> cron 表达式解析 + 下次执行时间计算,零依赖、带中文人话解释。
> "这行 cron 到底啥意思?下次什么时候跑?"——一条命令搞定。

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)
![Tests](https://img.shields.io/badge/tests-33%20passing-success)

## ✨ 特性

- 🧠 **完整解析**:5 字段(分 时 日 月 星期),支持 `*`、`*/n`、`a-b`、`a-b/n`、
  列表,以及月/星期英文缩写(`JAN`、`MON`);星期 `7` 自动视为周日
- 🗓 **Vixie 标准语义**:「日」与「星期」都受限时取**或**——这是最容易搞错的一
  条规则,本工具严格遵循并有测试锚定
- 🚀 **快速推进**:跳月 / 跳日 / 跳时,不做逐分钟暴力扫描;
  「2 月 30 日」这类矛盾表达式在搜索上限后明确报错而不是装死
- 🗣 **人话解释**:`--explain` 把 `*/5 * * * 1-5` 翻译成
  "每 5 分钟、周一到周五"
- 📤 **可脚本化**:`--json` 输出字段集合与触发时刻;`--after` 注入起算时间
  (确定性,适合测试与回放)
- 🧪 **33 个单元测试**;GitHub Actions 三系统 × 三 Python 版本 CI

## 📦 安装

```bash
git clone https://github.com/JAKE1266/crony.git
cd crony
python -m crony --help          # 克隆即用

pip install .                   # 或安装为命令(获得 crony 命令)
```

## 🚀 快速上手

```bash
crony "*/5 * * * 1-5"                    # 未来 5 次触发
crony "0 9 * * 1-5" --next 3             # 工作日每天 9 点,接下来 3 次
crony "0 0 1 1 *" --after 2026-11-21     # 从指定时刻起算
crony "0 9 * * MON-FRI" --explain        # 人话解释
crony "*/10 * * * *" --json              # 给脚本用
```

### 效果预览

```
$ crony "*/5 * * * 1-5" --after 2026-11-21 10:03
表达式:*/5 * * * 1-5
起算:2026-11-21 10:03(不含)
  2026-11-23 00:00:00      ← 周六不触发,直接跳到周一
  2026-11-23 00:05:00
  2026-11-23 00:10:00

$ crony "0 9 * * 1-5" --explain
表达式:0 9 * * 1-5
  分钟  第 0 分
  小时  第 9 点
  日  每天
  月  每月
  星期  周一、周二、周三、周四、周五
```

## 🧰 参数一览

```
crony "表达式" [选项]
  --next N      列出未来 N 次触发(默认 5)
  --after 时间  起算时间(YYYY-MM-DD [HH:MM[:SS]];默认现在,不含该时刻)
  --explain     人话解释(不计算触发时间)
  --json        字段集合 + 触发时刻 + 解释,一起输出
```

## ❓ 常见问题

**Q: 「日」和「星期」同时写会怎样?**
按 Vixie cron 标准:**两者都受限时,日期命中其中之一即触发**(或的关系);
只有一个受限时,必须命中它。`*` 表示不受限。例:`0 0 13 * 5` = 每月 13 日
**或**每周五。

**Q: `0 0 30 2 *`(2 月 30 日)会怎样?**
永远不可能触发。本工具在向后搜索约四年后明确报错,而不是无限等待。

**Q: 支持秒与 @hourly 这类简写吗?**
不支持。5 字段 + 上述语法是 crontab 文件的事实标准;秒级调度建议用
真正的调度器。简写别名在路线图里。

**Q: 想发布到 PyPI?**
`crony` 是占位名,发布前请在 `pyproject.toml` 换一个未被占用的名字。

## 📁 项目结构

```
crony/
├── .github/workflows/ci.yml   # CI:三系统 × Python 3.9-3.13
├── src/crony/
│   ├── core/
│   │   ├── parser.py          # 表达式解析、校验、人话描述
│   │   └── schedule.py        # 跳月/跳日/跳时的触发时间计算
│   └── cli.py                 # 命令行入口
├── tests/                     # 33 个单元测试(after 注入,完全确定)
└── pyproject.toml
```

## 🧪 开发与测试

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## 🗺 路线图

- [ ] `@hourly` / `@daily` 等别名
- [ ] 6 字段(含秒)模式
- [ ] `--table` 输出 crontab 行说明

## 📄 许可证

[MIT](LICENSE) —— 可自由使用、修改与分发。

---

*同系列项目:[PyToolBox](https://github.com/JAKE1266/py-toolbox) 多功能工具箱 · [CashBook](https://github.com/JAKE1266/cashbook) 命令行记账本 · [gitdash](https://github.com/JAKE1266/gitdash) Git 终端仪表盘 · [DevBox](https://github.com/JAKE1266/devbox) 前端开发工具箱 · [csvq](https://github.com/JAKE1266/csvq) SQL 查 CSV · [cjktable](https://github.com/JAKE1266/cjktable) CJK 排版微库 · [duviz](https://github.com/JAKE1266/duviz) 磁盘占用可视化 · [httpoke](https://github.com/JAKE1266/httpoke) HTTP 调试工具 · [mdown](https://github.com/JAKE1266/mdown) Markdown→HTML · [msite](https://github.com/JAKE1266/msite) 静态文档站 · [pomo](https://github.com/JAKE1266/pomo) 番茄钟 · [termplot](https://github.com/JAKE1266/termplot) 终端数据图表 · [filewatch](https://github.com/JAKE1266/filewatch) 目录变更监控 · [packpeek](https://github.com/JAKE1266/packpeek) 压缩包检查与安全解压 · [statline](https://github.com/JAKE1266/statline) 统计摘要 · [difftool](https://github.com/JAKE1266/difftool) 文本差异 · [wordfreq](https://github.com/JAKE1266/wordfreq) 词频统计 · [hexview](https://github.com/JAKE1266/hexview) 十六进制查看器 · [quicktodo](https://github.com/JAKE1266/quicktodo) 待办清单 · [envcheck](https://github.com/JAKE1266/envcheck) .env 校验 · [ipcalc](https://github.com/JAKE1266/ipcalc) 子网计算器 · [quickjournal](https://github.com/JAKE1266/quickjournal) 速记日志 · [csv2md](https://github.com/JAKE1266/csv2md) CSV→Markdown · [namecase](https://github.com/JAKE1266/namecase) 命名风格转换 · [dirsinc](https://github.com/JAKE1266/dirsinc) 目录增量同步 · [stopwatch](https://github.com/JAKE1266/stopwatch) 正计时秒表 · [wordwrap](https://github.com/JAKE1266/wordwrap) 按显示宽度换行 · [mdtoc](https://github.com/JAKE1266/mdtoc) Markdown 目录生成 · [checksum](https://github.com/JAKE1266/checksum) 批量校验和 · [gitignore-gen](https://github.com/JAKE1266/gitignore-gen) .gitignore 模板 · [filefind](https://github.com/JAKE1266/filefind) 文件搜索 · [filedupe](https://github.com/JAKE1266/filedupe) 重复文件查找 · [passgen](https://github.com/JAKE1266/passgen) 密码/口令生成 · [logparse](https://github.com/JAKE1266/logparse) 访问日志分析 · [batchrename](https://github.com/JAKE1266/batchrename) 批量重命名 · [srttool](https://github.com/JAKE1266/srttool) SRT 字幕工具 · [unitconv](https://github.com/JAKE1266/unitconv) 单位换算 · [csvlint](https://github.com/JAKE1266/csvlint) CSV 数据校验 · [datecalc](https://github.com/JAKE1266/datecalc) 日期计算 · [jsonfmt](https://github.com/JAKE1266/jsonfmt) JSON 格式化 · [colortool](https://github.com/JAKE1266/colortool) 颜色换算与对比度 · [codec](https://github.com/JAKE1266/codec) 编解码工具 · [emoji](https://github.com/JAKE1266/emoji) emoji 处理*
