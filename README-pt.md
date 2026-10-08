# dsh-review-reply-check — Verificação da cobertura e do rasto documental da tabela de respostas aos comentários de revisão

`dsh-review-reply-check` lê uma tabela de respostas aos comentários de revisão —o cabeçalho do manuscrito mais uma linha por comentário— e verifica a cobertura e o rasto documental dessa própria tabela: que o texto de cada comentário esteja registado, que toda linha com comentário preenchido traga resposta do autor, que a resposta indique a alteração feita e onde foi feita, que cada estado de tratamento venha do vocabulário que você configurar, que as datas de resposta caiam dentro do prazo de revisão que a própria tabela declara, que o cabeçalho declare o seu manuscrito e a sua ronda de revisão, e que os números de comentário não se repitam.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Uma linha traz a resposta do autor, mas a célula com o texto do comentário está vazia. | `RR-001` exige o texto do comentário em cada linha: sem ele a resposta fica sem objeto e o editor não consegue ver a que comentário corresponde. A regra verifica apenas se a célula está preenchida; não julga se o comentário procede nem se é uma divergência de juízo académico. |
| O comentário está registado, mas a célula de resposta do autor continua vazia — isso é reportado? | Sim. `RR-002` exige uma resposta em toda linha cujo comentário esteja preenchido, porque um comentário ignorado não é o mesmo que uma discordância que o revisor pode avaliar. Verifica apenas se a célula de resposta está preenchida, não se a resposta é suficiente ou convincente; quando um comentário realmente não exigir alterações, o pacote aconselha escrever o motivo nessa célula em vez de a deixar vazia. |
| A resposta diz que o texto foi alterado, mas a nota de revisão e a coluna de localização estão vazias. | `RR-003` exige `revision` e `revisionLocation` em toda linha cujo campo `response` esteja preenchido. Verifica que as duas células estejam escritas, não que a alteração esteja onde elas dizem: o plugin nunca vê o manuscrito, pelo que uma nota de revisão com página e linha precisas a descrever uma alteração inexistente também passa. |
| Todas as linhas trazem um estado de tratamento. Como decide a ferramenta se o valor serve? | `RR-004` compara o valor da coluna `status` com a lista que você configurar. Essa lista vem vazia, ou seja, por configurar, pelo que até a preencher a regra reporta-se em `skipped` em vez de passar em silêncio. Verifica apenas se o valor consta da sua lista; não decide se um dado estado significa que o comentário foi bem atendido. Sendo regra de configuração institucional, a sua severidade está limitada a `info`. |
| A data de resposta é posterior à coluna do prazo — isso significa que a revisão chegou tarde? | `RR-005` compara `respondedAt` com o `dueAt` que a própria tabela escreve, e um achado significa apenas que ambos não concordam com o prazo que você registou, não que a revisão tenha chegado tarde, porque os prazos variam com a revista e o autor pode pedir prorrogação. Não há qualquer número de dias incorporado nem nada é calculado: quando `dueAt` está vazio a regra reporta-se em `skipped` em vez de presumir um prazo. |
| Os comentários de dois revisores foram registados juntos e ambos numeram a partir de 1, pelo que um número de comentário aparece duas vezes. | `RR-007` reporta um valor repetido em `commentNo`, porque um duplicado distorce a contagem da cobertura e quebra a correspondência com o formulário de revisão. Registá-los com uma numeração que inclua o revisor —`R1-3`, `R2-1`— mantém-nos únicos; a regra compara os números tal como estão escritos e não funde nem renumera nada. |

## Normas que segue

| Documento | Número | Regras que o citam |
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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-review-reply-check
dsh --profile <name> --dump-config | grep 'dsh-review-reply-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/review-reply-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-review-reply-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-review-reply-check contributors.
