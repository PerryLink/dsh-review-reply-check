# dsh-review-reply-check — Review comment response table coverage and paper-trail check

`dsh-review-reply-check` reads one review-comment response table — the manuscript header plus one row per comment — and checks that table's own coverage and paper trail: that each comment's text is recorded, that every row carrying a comment also carries an author response, that a response states the revision made and where it was made, that each handling status comes from the vocabulary you configure, that response dates fall inside the revision deadline the table itself states, that the table header declares its manuscript and review round, and that comment numbers are not repeated.

## What it answers

| You ask | What it answers |
|---|---|
| A row carries an author response but the cell holding the comment text is empty. | `RR-001` requires the comment text on every row: without it the response has no object, and the editor cannot see which comment it answers. The rule checks only that the cell is filled — it does not judge whether the comment holds or whether it is a matter of academic disagreement. |
| A comment is recorded but the author response cell is still empty — is that reported? | Yes. `RR-002` requires a response on every row whose comment cell is filled, because a comment passed over in silence is not the same as a disagreement a reviewer can weigh. It checks only that the response cell is filled, not whether the response is adequate or convincing; when a comment genuinely needs no change, the pack advises writing the reason in that cell rather than leaving it blank. |
| The response says the text was revised, but the revision note and the location column are blank. | `RR-003` requires both `revision` and `revisionLocation` on every row whose `response` is filled. It checks that the two cells are written, not that the change is where they say it is — the plugin never sees the manuscript, so a precisely located revision note describing a change that was never made still passes. |
| Every row has a handling status filled in. How does the tool decide whether the value is acceptable? | `RR-004` compares the value in the `status` column against the list you configure. That list ships empty, meaning not configured, so until you fill it in the rule reports itself in `skipped` rather than passing silently. It checks only that the value is on your list; it does not decide whether a given status means the comment was properly handled. As an institutional-configuration rule it is capped at `info`. |
| The response date is later than the deadline column — does that mean the revision was overdue? | `RR-005` compares `respondedAt` against the `dueAt` the table itself writes, and a hit means only that the two disagree with the deadline you recorded — not that the revision was late, since periods differ by journal and authors may ask for extensions. No number of days is built in and nothing is inferred for you: when `dueAt` is empty the rule reports itself in `skipped` instead of assuming a deadline. |
| Two reviewers' comments were merged into one sheet and both number from 1, so a comment number appears twice. | `RR-007` reports a repeated value in `commentNo`, because a duplicate makes the coverage count wrong and breaks the correspondence with the review form. Registering merged comments under a numbering that carries the reviewer — `R1-3`, `R2-1` — keeps them unique; the rule compares the numbers as written and does not merge or renumber anything. |

## Standards it follows

| Document | Number | Cited by rules |
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

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a full response letter use `ptc` |

## What it does

Registers the `review_reply_check` tool. It reads one response table — the manuscript header plus one row per
comment — applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `RR-001` | the comment text is recorded | warn | principle |
| `RR-002` | every comment carries a response | warn | principle |
| `RR-003` | a response states the revision and its location | warn | principle |
| `RR-004` | the status comes from your vocabulary (off by default) | info | local |
| `RR-005` | the response date falls inside the recorded deadline | info | local |
| `RR-006` | the sheet names its manuscript and round | warn | principle |
| `RR-007` | comment numbers are unique | warn | principle |

## Install

```sh
dsh plugin --profile <name> add dsh-review-reply-check
dsh --profile <name> --dump-config | grep 'dsh-review-reply-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/review-reply-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `RR-004` `values` — your status vocabulary, e.g. `[已修改, 部分修改, 不修改并说明理由, 已删除]`. Empty means
  no check.
- `RR-005` reads the register's 返修期限 / `dueAt` column. The plugin never derives a deadline from a day count.
- `RR-002` and `RR-003` use `conditionField` / `requiredFields` — what triggers each requirement.
- `RR-007` keys on the comment-number column. When several reviewers' comments are merged, number them per
  reviewer (`R1-3`, `R2-1`) so the rule can tell them apart.

## Material format

The tool accepts JSON or YAML:

```yaml
manuscriptNo: XYZ-2026-0186
title: 某某研究
journal: 某某学报
round: 第 1 轮
dueAt: 2026-05-10
rows:
  - { 序号: R1-1, 审稿人: 审稿人一, 意见类型: 方法, 指向位置: 第 3 节 3.2,
      审稿意见: 3.2 节的样本量未说明估算依据，请补充。,
      作者回应: 同意补充。已在 3.2 节末增加样本量估算说明，并引用既往研究作为依据。,
      修改说明: 新增一段样本量估算依据，引用两项既往研究并给出效应量假设。,
      修改位置: 第 8 页第 12—18 行（修订稿 3.2 节末）,
      处理状态: 已修改, 回应人: 通讯作者, 回应日期: 2026-05-06 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the table's own column
names are kept, so a finding names the column it read.

## Rule sources

Rule data lives in `rules/review-reply-check.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an excerpt
must be a real quotation of at least eight characters" cannot tell a quotation from a description — so this pack
leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`RR-003` passed a revision note describing a change that was never made.** It checks that a location is
  *stated*, never that the change is there. Comparing needs the manuscript, which the plugin does not see.
- **`RR-002` fires on a comment I chose not to act on.** Record the reason in the response cell. A reviewer can
  accept a reasoned disagreement; a blank cell reads as "not addressed".
- **`RR-005` reports itself as skipped.** The register records no revision deadline, and the plugin will not
  invent one.
- **`RR-004` never runs.** Its vocabulary is empty; fill it with your journal's statuses.
- **`RR-007` fires on comments from different reviewers.** Number them per reviewer so the merged table stays
  unambiguous.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-review-reply-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-review-reply-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and the
check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-review-reply-check contributors.
