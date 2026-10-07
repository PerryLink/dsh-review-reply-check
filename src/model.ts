/**
 * dsh-review-reply-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'review_reply_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  commentNo: ['序号', '意见编号', '编号', 'commentNo'],
  reviewer: ['审稿人', '评审人', '专家', 'reviewer'],
  commentType: ['意见类型', '类别', '类型', 'commentType'],
  section: ['指向位置', '所在章节', '稿件位置', 'section'],
  comment: ['审稿意见', '意见内容', '评审意见', 'comment'],
  severity: ['重要程度', '优先级', '等级', 'severity'],
  response: ['作者回应', '回应内容', '答复', 'response'],
  revision: ['修改说明', '稿件改动', '修订内容', 'revision'],
  revisionLocation: ['修改位置', '改动位置', '所在页行', 'revisionLocation'],
  status: ['处理状态', '状态', 'status'],
  owner: ['回应人', '责任人', '通讯作者', 'owner'],
  respondedAt: ['回应日期', '答复日期', 'respondedAt'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'comments', '意见'],
  columns: COLUMNS,
  header: {
  manuscriptNo: ['manuscriptNo', '稿件编号', '投稿编号'],
  title: ['title', '稿件标题'],
  journal: ['journal', '期刊', '拟投期刊'],
  round: ['round', '审稿轮次', '轮次'],
  decision: ['decision', '审稿结论', '处理决定'],
  dueAt: ['dueAt', '返修期限', '回应期限'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '审稿意见',
  'comment',
  '作者回应',
  'response',
  '修改说明',
  'revision',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
