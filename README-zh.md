# dsh-review-reply-check — 审稿意见逐条回应覆盖核对

`dsh-review-reply-check` 读取一份审稿意见逐条回应表——稿件表头加每条意见一行——核对这份台账自身的覆盖完整性与留痕：每条意见的意见内容是否已抄录、凡填了意见内容的行是否都有作者回应、回应是否写明修改说明与修改位置、每行的处理状态是否取自你配置的状态口径、回应日期是否落在表内写明的返修期限之内、表头是否声明稿件编号与审稿轮次、意见序号是否重复。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 某行填了作者回应，但意见内容栏是空的。 | `RR-001` 要求每行都抄录意见内容：缺了它，回应就失去了对象，编辑也无从判断这条回应针对哪一条意见。本条只核对意见栏是否填写，不判断该意见是否成立、是否属于学术判断分歧。 |
| 意见已抄录，但作者回应栏还空着，会被报出吗？ | 会。`RR-002` 对凡是意见栏已填写的行都要求有回应——意见被略过与审稿人可接受的不同意是两件不同的事。它只核对回应栏是否填写，不判断回应是否充分、是否说服得了审稿人；确实无需修改的意见，规则库建议在回应栏写明理由，而不是留空。 |
| 回应里写了已修改，但修改说明栏与修改位置栏都是空的。 | `RR-003` 对凡是回应栏已填写的行，都要求同时填写 `revision` 与 `revisionLocation`。它只核对这两栏是否写明，不核对所写位置是否真有该处改动——本插件看不到稿件本身，一份把页码行号写得清清楚楚、却并无其事的修改说明同样会通过。 |
| 每行都填了处理状态，工具怎么判断这个取值行不行？ | `RR-004` 拿 `status` 栏的取值与你自己配置的清单比对。这份清单出厂为空，表示未配置，在你填入之前本条报告「无法执行」（`skipped`），而不是静默通过。它只核对所填值是否在册，不判断某一状态是否意味着该意见已被妥善处理。作为机构口径类规则，它的严重度封顶 `info`。 |
| 回应日期晚于表内写的返修期限，是不是就算逾期了？ | `RR-005` 拿 `respondedAt` 与台账自己写的 `dueAt` 相比，命中只表示「与你写在台账里的期限不一致」，不表示已经逾期——返修期限由各期刊规定，作者也可以申请延期。本插件不内置任何天数，也不替使用方推算：`dueAt` 为空时本条报告「无法执行」（`skipped`），不会假定任何期限。 |
| 两位审稿人的意见合并登记，序号都从 1 开始，于是同一个意见序号出现了两次。 | `RR-007` 会报出 `commentNo` 重复，因为序号重复会让覆盖率统计失真，也无法与审稿单上的编号对应。合并登记时把审稿人写进编号（如 `R1-3`、`R2-1`）即可保持唯一；本条只按填写的序号比较，不做合并、也不重新编号。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
|---|---|---|
| 《中国高校科技期刊编排规范》 | 现行版本与条号本次未核实 | RR-001, RR-002, RR-003, RR-006, RR-007 |
| 本期刊同行评议与返修规定（本机构配置） | 无统一标准（本条依据为本机构配置的状态口径） | RR-004 |
| 本期刊同行评议与返修规定（本机构配置） | 无统一标准（本条依据为台账写明的返修期限） | RR-005 |

**Boundary:** this plugin checks a **审稿意见逐条回应表** for coverage and evidence — that every comment is
recorded, that every comment carries an author response, that a response states the revision made and where it was
made, that the handling status comes from your vocabulary, that response dates fall inside the revision deadline
the register states, that the sheet names its manuscript and review round, and that comment numbers are unique. It
does **not** decide whether a response is adequate, whether the revision is sufficient, or whether the manuscript
should be accepted.

> ### ⚠️ What this plugin can and cannot see
>
> **It never sees the manuscript.** It can check that a response says *where* a change was made — never that the
> change is there, and never that it addresses the comment. `RR-003`'s note and the troubleshooting section say
> so: a confident, well-located, entirely fictional revision note passes this plugin.
>
> The relation between "no response" and "disagreement" is the point of `RR-002`: a reviewer can accept an author's
> disagreement but not a comment passed over in silence, so **coverage** is the most direct indicator of revision
> quality. The rule therefore fires on an empty response cell — and its note advises recording the reason rather
> than leaving the cell blank when a comment genuinely needs no change.
>
> **No revision deadline is built in.** Periods differ by journal and authors may ask for extensions, so `RR-005`
> compares the response date against the **deadline written in the register**, and reports itself in `skipped`
> when that column is empty. A finding means "this disagrees with the deadline you recorded", never "you were
> late". The status vocabulary ships **empty** for the same reason.
>
> **Every `excerpt` in the rule pack says, in so many words, that the clause text was not obtained.** The regime
> lives in GB/T 7713.1, the Chinese university journal editing standard, and each journal's peer-review rules. The
> verification pass could not retrieve verbatim clause text, so the pack states the gap in the `excerpt` field
> itself and keeps every rule at `warn` or `info`. **When the texts are in hand, replace each `excerpt` with the
> real clause and raise `kind` to `direct`.**

## Compatibility

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-review-reply-check
dsh --profile <name> --dump-config | grep 'dsh-review-reply-check'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/review-reply-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-review-reply-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-review-reply-check contributors.
