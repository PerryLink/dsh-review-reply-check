# dsh-review-reply-check — Verificación de cobertura y rastro documental de la tabla de respuestas a los comentarios de revisión

`dsh-review-reply-check` lee una tabla de respuestas a los comentarios de revisión —la cabecera del manuscrito más una fila por comentario— y comprueba la cobertura y el rastro documental de esa propia tabla: que el texto de cada comentario esté registrado, que toda fila con comentario escrito traiga respuesta del autor, que la respuesta indique la modificación hecha y dónde se hizo, que cada estado de tramitación provenga del vocabulario que usted configure, que las fechas de respuesta caigan dentro del plazo de revisión que la propia tabla declara, que la cabecera declare su manuscrito y su ronda de revisión, y que los números de comentario no se repitan.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Una fila trae la respuesta del autor, pero la celda del texto del comentario está vacía. | `RR-001` exige el texto del comentario en cada fila: sin él la respuesta se queda sin objeto y el editor no puede ver a qué comentario corresponde. La regla comprueba solo que la celda esté rellena; no juzga si el comentario es acertado ni si es una discrepancia de juicio académico. |
| El comentario está registrado, pero la celda de respuesta del autor sigue vacía, ¿se informa de ello? | Sí. `RR-002` exige una respuesta en toda fila cuyo comentario esté escrito, porque un comentario pasado por alto no es lo mismo que un desacuerdo que el revisor puede valorar. Comprueba solo que la celda de respuesta esté rellena, no si la respuesta es suficiente o convincente; cuando un comentario realmente no requiere cambios, el paquete aconseja escribir el motivo en esa celda en lugar de dejarla vacía. |
| La respuesta dice que el texto se modificó, pero la nota de revisión y la columna de ubicación están vacías. | `RR-003` exige `revision` y `revisionLocation` en toda fila cuyo campo `response` esté relleno. Comprueba que las dos celdas estén escritas, no que el cambio esté donde ellas dicen: el plugin nunca ve el manuscrito, así que una nota de revisión con página y línea precisas que describe un cambio inexistente también pasa. |
| Todas las filas traen un estado de tramitación. ¿Cómo decide la herramienta si el valor es aceptable? | `RR-004` compara el valor de la columna `status` con la lista que usted configure. Esa lista viene vacía, es decir, sin configurar, así que hasta que la rellene la regla se informa en `skipped` en lugar de pasar en silencio. Comprueba solo que el valor esté en su lista; no decide si un estado dado significa que el comentario quedó bien atendido. Como regla de configuración institucional, su severidad está topada en `info`. |
| La fecha de respuesta es posterior a la columna del plazo, ¿significa que la revisión llegó tarde? | `RR-005` compara `respondedAt` con el `dueAt` que la propia tabla escribe, y un hallazgo solo significa que ambos no concuerdan con el plazo que usted registró, no que la revisión llegara tarde, porque los plazos varían según la revista y el autor puede pedir prórroga. No hay ningún número de días incorporado ni se calcula nada: cuando `dueAt` está vacío la regla se informa en `skipped` en lugar de suponer un plazo. |
| Los comentarios de dos revisores se registraron juntos y ambos numeran desde 1, así que un número de comentario aparece dos veces. | `RR-007` informa de un valor repetido en `commentNo`, porque un duplicado desvirtúa el recuento de cobertura y rompe la correspondencia con el formulario de revisión. Registrarlos con una numeración que lleve al revisor —`R1-3`, `R2-1`— los mantiene únicos; la regla compara los números tal como están escritos y no fusiona ni renumera nada. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-review-reply-check
dsh --profile <name> --dump-config | grep 'dsh-review-reply-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/review-reply-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-review-reply-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-review-reply-check contributors.
