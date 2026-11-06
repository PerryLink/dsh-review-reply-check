#!/usr/bin/env python3
"""README visuals for dsh-review-reply-check, read off the shipped pipeline.

Sources used for every label, so nothing here is invented:

  src/index.ts             `review_reply_check`; `file | material` -> readMaterial;
                           `rulesFile` -> resolvePackageFile -> loadRulesetFile;
                           parseMaterial -> runCheck -> buildView.
  src/model.ts             the table contract: header keys, the 12 column
                           alias groups, `requireAnyOf`, canonical field names.
  src/shared/rows.ts       one handler per `check.kind`; `skip(reason)` when a
                           check cannot run; `locatorOf(row, field)` writes the
                           report field `column` (not `field`); conditionalPresence
                           skips when no row meets its condition.
  src/shared/ruleset.ts    basis kinds and the severity ceiling each imposes;
                           the pack is validated on load, not trusted.
  rules/review-reply-check.yaml
                           seven rules: RR-001 presence(comment),
                           RR-002 conditionalPresence(comment -> response),
                           RR-003 conditionalPresence(response -> revision,
                           revisionLocation), RR-004 enum(status, values []),
                           RR-005 date(respondedAt not after dueAt),
                           RR-006 headerPresence(manuscriptNo, round),
                           RR-007 unique(commentNo).
  src/view.ts              issues + skipped + summary + markdown/reportJson.

Outputs (idempotent overwrite):

  docs/assets/dsh-review-reply-check-hero-{zh,en}-{light,dark}.webp
      1440x576, Pillow.  The left column is the wordmark block; the right is a
      four-row response ledger.  Comments and responses are drawn as paired
      cells with a beam between them; an incomplete pair keeps its gap and is
      stamped with the rule that reports it.  The rail under the ledger shows
      the four checks that sit outside the pairing (header, numbering, status
      vocabulary, deadline), including the one that reports in `skipped`.

  docs/assets/dsh-review-reply-check-flow-v5-{light,dark}.svg
      1100x660, hand-written SVG.  Grammar: a COVERAGE LADDER plus a separate
      CHECK BENCH -- not a row of five arrowed boxes.  Material and rule pack
      enter a single engine seam; the ladder carries the three coverage rules
      as condition -> requirement -> locator rungs, while the bench carries the
      four orthogonal rules and their scopes; the report tray carries the real
      `issues[]` / `skipped[]` split and the summary.

The worked example is the one measured against the built plugin:

  4 rows, header manuscriptNo + round + dueAt
    R1-1 complete                      -> no issue
    R1-2 response, revision, no location -> RR-003, row 2, column response
    R1-3 comment, no response          -> RR-002, row 3, column comment
    R1-4 no comment                    -> RR-001, row 4, column comment
  RR-004 values [] -> skipped; RR-005 compared (responses inside dueAt); RR-006,
  RR-007 ran and found nothing.  Summary: warn 3, info 0, skipped 1.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow and the Windows fonts msyh.ttc, msyhbd.ttc, consola.ttf,
           consolab.ttf, segoeui.ttf, segoeuib.ttf.
Every label is measured before it is drawn; a label that would overflow aborts
the run instead of shipping clipped text.
"""
from __future__ import annotations

import os
import sys
from functools import lru_cache
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

NAME = "dsh-review-reply-check"

FONTS = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_b": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_b": r"C:\Windows\Fonts\consolab.ttf",
    "en": r"C:\Windows\Fonts\segoeui.ttf",
    "en_b": r"C:\Windows\Fonts\segoeuib.ttf",
}
for _path in FONTS.values():
    if not os.path.exists(_path):
        sys.exit(f"FATAL: font missing: {_path}")

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8", card="#ffffff", edge="#e3e0ee",
        text="#14161f", sub="#4d5261", faint="#8b90a0", accent="#4B67B4",
        accent_soft="#eceffa", warn="#b0490e", warn_soft="#fdf1e7",
        green="#16794a", green_soft="#e8f5ee", line="#e8e5f1",
        pill="#ece7f9", column="#f5f3fb", shadow=(38, 30, 72), glow=52,
        svg_shadow="#241f3d", svg_shadow_op="0.10",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016", card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#788093", accent="#8496f5",
        accent_soft="#232c42", warn="#d29922", warn_soft="#2d2637",
        green="#3fb950", green_soft="#1c2f24", line="#242d3e",
        pill="#242d42", column="#1f2839", shadow=(0, 0, 0), glow=26,
        svg_shadow="#000000", svg_shadow_op="0.45",
    ),
}


# ------------------------------------------------------------------ primitives --
def hx(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


@lru_cache(maxsize=None)
def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS[kind], size)


_SCRATCH = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def mw(text: str, kind: str, size: int) -> float:
    return _SCRATCH.textlength(text, font=font(kind, size))


def fit_size(text: str, kind: str, max_w: float, size: int, floor: int) -> int:
    """Largest size <= `size` at which `text` fits in `max_w`."""
    while size > floor and mw(text, kind, size) > max_w:
        size -= 1
    return size


def require_width(text: str, kind: str, size: int, max_w: float,
                  where: str) -> None:
    got = mw(text, kind, size)
    if got > max_w + 0.5:
        sys.exit(f"FATAL: {where}: {text!r} needs {got:.1f}px, "
                 f"only {max_w:.1f}px — refusing to clip")


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(base)
    a, b = hx(c1), hx(c2)
    for y in range(h):
        t = 0.25 * (y / h) + 0.75 * (y / h) ** 1.6
        d.line([(0, y), (w, y)],
               fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base.convert("RGBA")


def glow(img: Image.Image, cx: int, cy: int, r: int,
         rgb: tuple[int, int, int], alpha: int,
         blur: int = 100) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse((cx - r, cy - r, cx + r, cy + r),
                                  fill=rgb + (alpha,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    return img


def shadow(img: Image.Image, box: tuple[int, int, int, int], radius: int,
           rgb: tuple[int, int, int], alpha: int, blur: int, dy: int) -> None:
    x0, y0, x1, y1 = box
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(
        (x0, y0 + dy, x1, y1 + dy), radius, fill=rgb + (alpha,))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def card(img: Image.Image, box: tuple[int, int, int, int], radius: int,
         s: dict, blur: int = 16, dy: int = 9, alpha: int = 30) -> None:
    shadow(img, box, radius, s["shadow"], alpha, blur, dy)
    ImageDraw.Draw(img).rounded_rectangle(box, radius, fill=s["card"],
                                          outline=s["edge"], width=1)


def text(d: ImageDraw.ImageDraw, x: float, y: float, s: str, kind: str,
         size: int, fill: str, anchor: str = "lt") -> None:
    d.text((x, y), s, font=font(kind, size), fill=hx(fill), anchor=anchor)


def pill(img: Image.Image, x: float, y: float, label: str, s: dict, kind: str,
         size: int, h: int, fg: str | None = None, bg: str | None = None,
         edge: str | None = None, padx: float = 14) -> tuple[float, float]:
    d = ImageDraw.Draw(img)
    w = mw(label, kind, size) + padx * 2
    d.rounded_rectangle((x, y, x + w, y + h), h / 2,
                        fill=hx(bg or s["pill"]),
                        outline=hx(edge) if edge else None, width=1)
    text(d, x + w / 2, y + h / 2, label, kind, size, fg or s["accent"],
         anchor="mm")
    return x + w, y + h


def dashed(img: Image.Image, x0: float, y0: float, x1: float, y1: float,
           color: str, width: int = 2, dash: int = 6, gap: int = 5) -> None:
    """Dashed straight line (used for an unfilled cell / an unpaired beam)."""
    d = ImageDraw.Draw(img)
    c = hx(color)
    if y0 == y1:
        x = x0
        while x < x1:
            d.line([(x, y0), (min(x + dash, x1), y1)], fill=c, width=width)
            x += dash + gap
        return
    y = y0
    while y < y1:
        d.line([(x0, y), (x1, min(y + dash, y1))], fill=c, width=width)
        y += dash + gap


def arrow(d: ImageDraw.ImageDraw, x0: float, y0: float, x1: float, y1: float,
          color: str, width: int = 2, head: int = 5) -> None:
    c = hx(color)
    d.line([(x0, y0), (x1, y1)], fill=c, width=width)
    d.line([(x1, y1), (x1 - head, y1 - head)], fill=c, width=width)
    d.line([(x1, y1), (x1 - head, y1 + head)], fill=c, width=width)


def double_arrow(d: ImageDraw.ImageDraw, x0: float, y: float, x1: float,
                 color: str, width: int = 2, head: int = 4) -> None:
    c = hx(color)
    d.line([(x0 + head, y), (x1 - head, y)], fill=c, width=width)
    d.line([(x0, y), (x0 + head, y - head)], fill=c, width=width)
    d.line([(x0, y), (x0 + head, y + head)], fill=c, width=width)
    d.line([(x1, y), (x1 - head, y - head)], fill=c, width=width)
    d.line([(x1, y), (x1 - head, y + head)], fill=c, width=width)


# ------------------------------------------------------------------------ hero --
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 审稿回应核对",
        value=["逐条核对意见与回应，", "把缺口落到行号与栏名。"],
        sub=["读一份回应表：意见是否抄录、回应是否在、修改是否写明、",
             "状态与日期是否自洽——只提示差异，不判断回应是否充分。"],
        meta="review_reply_check · RR-001…RR-007 · issues + skipped",
        foot="Apache-2.0 · 只读 · 不联网 · 不调用模型",
        sheet_title="审稿意见逐条回应表",
        sheet_sub="4 行 · comment → response → revision",
        readonly="只读",
        header_label="表头",
        header_fields=[("manuscriptNo", "XYZ-2026-0186"),
                       ("round", "第 1 轮"),
                       ("dueAt", "2026-05-10")],
        header_rule="RR-006",
        headers=["commentNo", "comment", "response", "result"],
        rows=[
            ("R1-1", "样本量未说明估算依据", "已补充，见 3.2 节末",
             ("revision · location", None), "no issue"),
            ("R1-2", "表 2 的单位应统一", "已统一为 mmol/L",
             ("revision · location ", "—"), "RR-003"),
            ("R1-3", "讨论需补充局限", "",
             ("", None), "RR-002"),
            ("R1-4", "", "",
             ("", None), "RR-001"),
        ],
        rail_label="cross-checks",
        rail=[("RR-006 ran", "accent"), ("RR-007 ran", "accent"),
              ("RR-004 skipped", "warn"), ("values: []", "faint"),
              ("RR-005 ran", "accent")],
        rail_note="skipped ≠ pass",
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · review-response check",
        value=["Pair each comment with its answer,", "then name the row and column."],
        sub=["Reads one response table, applies a versioned rule pack,",
             "and reports coverage and paper-trail gaps — never a verdict."],
        meta="review_reply_check · RR-001…RR-007 · issues + skipped",
        foot="Apache-2.0 · read-only · no network · no model call",
        sheet_title="Review-comment response table",
        sheet_sub="4 rows · comment → response → revision",
        readonly="read-only",
        header_label="header",
        header_fields=[("manuscriptNo", "XYZ-2026-0186"),
                       ("round", "round 1"),
                       ("dueAt", "2026-05-10")],
        header_rule="RR-006",
        headers=["No.", "comment", "response", "result"],
        rows=[
            ("R1-1", "sample size has no basis", "added, see end of 3.2",
             ("revision · location", None), "no issue"),
            ("R1-2", "Table 2 units differ", "unified to mmol/L",
             ("revision · location ", "—"), "RR-003"),
            ("R1-3", "discussion needs limits", "",
             ("", None), "RR-002"),
            ("R1-4", "", "",
             ("", None), "RR-001"),
        ],
        rail_label="cross-checks",
        rail=[("RR-006 ran", "accent"), ("RR-007 ran", "accent"),
              ("RR-004 skipped", "warn"), ("values: []", "faint"),
              ("RR-005 ran", "accent")],
        rail_note="skipped ≠ pass",
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    h = HERO[lang]
    cjk = lang == "zh"
    bold = "cjk_b" if cjk else "en_b"
    body = "cjk" if cjk else "en"
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1110, 64, 430, hx(s["accent"]), s["glow"], 120)
    img = glow(img, 120, 600, 320, hx(s["accent"]), max(8, s["glow"] // 3), 120)
    d = ImageDraw.Draw(img)
    left_x, left_w = 56, 650

    # ---- left column --------------------------------------------------------
    pill(img, left_x, 48, h["kicker"], s, bold, 14, 32, fg=s["accent"])

    title_size = fit_size(NAME, "mono_b", left_w, 54, 48)
    require_width(NAME, "mono_b", title_size, left_w, "hero title")
    text(d, left_x - 2, 92, NAME, "mono_b", title_size, s["text"])

    value_size = 33 if cjk else 30
    while value_size > 26 and any(
            mw(line, bold, value_size) > left_w for line in h["value"]):
        value_size -= 1
    for line in h["value"]:
        require_width(line, bold, value_size, left_w, "hero value line")
    for i, line in enumerate(h["value"]):
        text(d, left_x, 174 + i * 50, line, bold, value_size, s["text"])

    d.rounded_rectangle((left_x, 278, left_x + 68, 282), 2, fill=hx(s["accent"]))

    sub_size = 19
    while sub_size > 16 and any(
            mw(line, body, sub_size) > left_w for line in h["sub"]):
        sub_size -= 1
    for line in h["sub"]:
        require_width(line, body, sub_size, left_w, "hero subtitle")
    for i, line in enumerate(h["sub"]):
        text(d, left_x, 302 + i * 30, line, body, sub_size, s["sub"])

    require_width(h["meta"], "mono", 15, left_w, "hero meta")
    text(d, left_x, 392, h["meta"], "mono", 15, s["faint"])

    require_width(h["foot"], body, 14, left_w, "hero footer")
    text(d, left_x, 500, h["foot"], body, 14, s["faint"])

    # ---- right: the response ledger ----------------------------------------
    px0, py0, px1, py1 = 724, 40, 1384, 528
    card(img, (px0, py0, px1, py1), 22, s, blur=26, dy=14,
         alpha=34 if skin == "light" else 120)
    d = ImageDraw.Draw(img)
    ix0, ix1 = px0 + 24, px1 - 24

    text(d, ix0, 62, h["sheet_title"], bold, 16, s["text"])
    ro_w = mw(h["readonly"], body, 10) + 18
    d.rounded_rectangle((ix1 - ro_w, 62, ix1, 82), 10,
                        fill=hx(s["accent_soft"]), outline=hx(s["accent"]),
                        width=1)
    text(d, ix1 - ro_w / 2, 72, h["readonly"], body, 10, s["accent"],
         anchor="mm")

    text(d, ix0, 88, h["sheet_sub"], "mono", 11, s["faint"])
    require_width(h["rail_note"], "mono", 10, 130, "hero subline note")
    text(d, ix1, 88, h["rail_note"], "mono", 10, s["warn"], anchor="rt")

    # header band: the one declaration RR-006 reads
    d.rounded_rectangle((ix0, 104, ix1, 144), 11, fill=hx(s["pill"]),
                        outline=hx(s["edge"]), width=1)
    text(d, ix0 + 12, 124, h["header_label"], body, 9.5, s["faint"],
         anchor="lm")
    fx = ix0 + 58
    for field, value in h["header_fields"]:
        fw = mw(field, "mono", 9.5) + 12
        d.rounded_rectangle((fx, 113, fx + fw, 133), 5, fill=hx(s["card"]),
                            outline=hx(s["edge"]), width=1)
        text(d, fx + fw / 2, 123, field, "mono", 9.5, s["accent"], anchor="mm")
        vw = mw(value, "mono" if field != "round" else body, 10.5)
        if fx + fw + 6 + vw > ix1 - 76:
            sys.exit(f"FATAL: hero header field {field!r} overflows")
        text(d, fx + fw + 6, 123, value,
             "mono" if field != "round" else body, 10.5, s["text"], anchor="lm")
        fx += fw + 8 + vw + 18
    rw = mw(h["header_rule"], "mono_b", 10) + 14
    d.rounded_rectangle((ix1 - rw, 113, ix1 - 2, 133), 6,
                        fill=hx(s["accent_soft"]), outline=hx(s["accent"]),
                        width=1)
    text(d, ix1 - rw / 2 - 1, 123, h["header_rule"], "mono_b", 10,
         s["accent"], anchor="mm")

    # column header: the comment and response columns are the pair
    cx_no0, cx_no1 = ix0, ix0 + 52
    cx_c0, cx_c1 = ix0 + 78, ix0 + 288
    gut0, gut1 = cx_c1, cx_c1 + 26
    cx_r0, cx_r1 = gut1, gut1 + 222
    cx_t0, cx_t1 = cx_r1 + 8, ix1
    d.rounded_rectangle((ix0, 152, ix1, 176), 8, fill=hx(s["column"]))
    text(d, cx_no0 + 6, 164, h["headers"][0], "mono", 10.5, s["sub"],
         anchor="lm")
    text(d, cx_c0 + 6, 164, h["headers"][1], "mono", 10.5, s["sub"],
         anchor="lm")
    double_arrow(d, gut0 + 5, 164, gut1 - 5, s["accent"], 2, 4)
    text(d, cx_r0 + 6, 164, h["headers"][2], "mono", 10.5, s["sub"],
         anchor="lm")
    text(d, cx_t0, 164, h["headers"][3], "mono", 10.5, s["sub"],
         anchor="lm")

    row_top = 180
    row_h, row_gap = 66, 4
    for i, (cno, comment, response, sub, tag) in enumerate(h["rows"]):
        y = row_top + i * (row_h + row_gap)
        filled_c = comment != ""
        filled_r = response != ""

        # comment number
        d.rounded_rectangle((cx_no0 + 4, y + 21, cx_no1 - 4, y + 45), 6,
                            fill=hx(s["pill"]))
        text(d, (cx_no0 + cx_no1) / 2, y + 33, cno, "mono", 10.5,
             s["sub"], anchor="mm")

        # comment cell
        fill = s["accent_soft"] if filled_c else s["warn_soft"]
        edge = s["edge"] if filled_c else s["warn"]
        d.rounded_rectangle((cx_c0, y + 6, cx_c1, y + 60), 10, fill=hx(fill),
                            outline=hx(edge), width=1)
        if filled_c:
            size = 12.5
            if mw(comment, body, size) > cx_c1 - cx_c0 - 16:
                size = 11.5
            require_width(comment, body, size, cx_c1 - cx_c0 - 16,
                          f"hero comment {cno}")
            text(d, cx_c0 + 9, y + 20, comment, body, size, s["text"])
        else:
            dashed(img, cx_c0 + 12, y + 34, cx_c1 - 12, y + 34, s["faint"],
                   2, 6, 5)
            text(d, cx_c0 + 9, y + 48, "—", "mono", 11, s["warn"], anchor="lt")

        # response cell.  When the comment is empty too, RR-002 never fires
        # (its condition is the filled comment), so the empty response is
        # drawn neutral rather than as a second finding.
        response_is_finding = filled_c and not filled_r
        fill_r = (s["accent_soft"] if filled_r else
                  (s["warn_soft"] if response_is_finding else s["card"]))
        edge_r = (s["edge"] if filled_r else
                  (s["warn"] if response_is_finding else s["edge"]))
        d.rounded_rectangle((cx_r0, y + 6, cx_r1, y + 60), 10, fill=hx(fill_r),
                            outline=hx(edge_r), width=1)
        if filled_r:
            size_r = 12.5
            if mw(response, body, size_r) > cx_r1 - cx_r0 - 16:
                size_r = 11.5
            require_width(response, body, size_r, cx_r1 - cx_r0 - 16,
                          f"hero response {cno}")
            text(d, cx_r0 + 9, y + 20, response, body, size_r, s["text"])
        else:
            dashed(img, cx_r0 + 12, y + 30, cx_r1 - 12, y + 30, s["faint"],
                   2, 6, 5)
            if response_is_finding:
                text(d, cx_r0 + 9, y + 44, "—", "mono", 11, s["warn"])

        # revision / location sub-line: the paper trail under the response
        sub_a, sub_b = sub
        if filled_r and sub_a != "":
            tone = s["green"] if sub_b is None else s["warn"]
            d.ellipse((cx_r0 + 9, y + 44, cx_r0 + 14, y + 49), fill=hx(tone))
            text(d, cx_r0 + 20, y + 42, sub_a, "mono", 10, s["sub"])
            if sub_b is not None:
                text(d, cx_r0 + 20 + mw(sub_a, "mono", 10), y + 42, sub_b,
                     "mono", 10, s["warn"])

        # pairing beam: solid when both sides carry text, otherwise a gap
        beam_y = y + 33
        if filled_c and filled_r:
            arrow(d, cx_c1 + 2, beam_y, gut1 - 2, beam_y,
                  s["green"] if tag == "no issue" else s["accent"], 2, 4)
        elif filled_c:
            arrow(d, cx_c1 + 2, beam_y, gut1 - 2, beam_y, s["warn"], 2, 4)
        else:
            dashed(img, cx_c1 + 2, beam_y, gut1 - 2, beam_y, s["faint"], 2, 4, 4)

        # outcome stamp
        tone = s["green"] if tag == "no issue" else s["warn"]
        tone_bg = s["green_soft"] if tag == "no issue" else s["warn_soft"]
        tw = cx_t1 - cx_t0
        d.rounded_rectangle((cx_t0, y + 21, cx_t0 + tw, y + 45), 12,
                            fill=hx(tone_bg), outline=hx(tone), width=1)
        require_width(tag, "mono", 9.5, tw - 6, f"hero tag {tag}")
        text(d, cx_t0 + tw / 2, y + 33, tag, "mono", 9.5, tone, anchor="mm")

    # rail: the checks that sit outside the comment/response pair
    rail_y0, rail_y1 = 468, 508
    d.rounded_rectangle((ix0, rail_y0, ix1, rail_y1), 11, fill=hx(s["column"]),
                        outline=hx(s["edge"]), width=1)
    text(d, ix0 + 12, rail_y0 + 25, h["rail_label"], "mono", 10, s["faint"],
         anchor="lm")
    tx = ix0 + 12 + mw(h["rail_label"], "mono", 10) + 18
    for i, (label, tone) in enumerate(h["rail"]):
        colour = s["accent"] if tone == "accent" else (
            s["warn"] if tone == "warn" else s["faint"])
        require_width(label, "mono", 10.5, 180, f"hero rail {label}")
        text(d, tx, rail_y0 + 25, label, "mono", 10.5, colour, anchor="lm")
        tx += mw(label, "mono", 10.5) + 8
        if i < len(h["rail"]) - 1:
            text(d, tx, rail_y0 + 25, "·", "mono", 10.5, s["faint"],
                 anchor="lm")
            tx += 12
    if tx > ix1 - 10:
        sys.exit(f"FATAL: hero rail overflows by {tx - (ix1 - 10):.1f}px")

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{NAME}-hero-{lang}-{skin}.webp")
    img.convert("RGB").save(path, "WEBP", quality=90, method=6)
    print(f"wrote {os.path.relpath(path, ROOT)}  "
          f"({os.path.getsize(path) // 1024} KiB)")


# ------------------------------------------------------------------------ flow --
SVG = {
    "light": dict(bg="#f9f6fd", bg2="#e4eaf8", card="#ffffff", edge="#e3e0ee",
                  text="#15161f", sub="#4f5463", faint="#8b90a0",
                  accent="#4B67B4", accent_soft="#eceffa", warn="#b0490e",
                  warn_soft="#fdf1e7", green="#16794a", green_soft="#e8f5ee",
                  line="#e8e5f1", pill="#ece7f9", column="#f5f3fb",
                  shadow="#241f3d", shadow_op="0.10"),
    "dark": dict(bg="#131a2a", bg2="#0c1016", card="#1b2231", edge="#2e374b",
                 text="#f1f4fa", sub="#a9b2c5", faint="#788093",
                 accent="#8496f5", accent_soft="#232c42", warn="#d29922",
                 warn_soft="#2d2637", green="#3fb950", green_soft="#1c2f24",
                 line="#242d3e", pill="#242d42", column="#1f2839",
                 shadow="#000000", shadow_op="0.45"),
}

MONO_STACK = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS_STACK = "ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif"


def sw(text: str, size: float) -> float:
    """Conservative mono advance width measured with the closest local font."""
    return mw(text, "mono", int(round(size))) * 1.06


def sa(text: str, size: float) -> float:
    """Conservative sans advance width."""
    return mw(text, "en", int(round(size))) * 1.06


class Fig:
    def __init__(self, skin: str):
        self.s = SVG[skin]
        self.parts: list[str] = []

    # -- raw ----------------------------------------------------------------
    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def text(self, x: float, y: float, content: str, size: float, fill: str,
             mono: bool = True, weight: int = 400, anchor: str = "start",
             opacity: float = 1.0) -> None:
        family = MONO_STACK if mono else SANS_STACK
        extra = f' opacity="{opacity}"' if opacity < 1 else ""
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}"'
            f' text-anchor="{anchor}"{extra}>{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, radius: float,
             fill: str, stroke: str | None = None, width: float = 1,
             dash: str | None = None, shadow: bool = False) -> None:
        stroke_attr = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        filt = ' filter="url(#sh)"' if shadow else ""
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" '
                 f'height="{h:.1f}" rx="{radius}" fill="{fill}"'
                 f'{stroke_attr}{dash_attr}{filt}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, stroke: str,
             width: float = 1, dash: str | None = None,
             opacity: float = 1.0) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        op = f' opacity="{opacity}"' if opacity < 1 else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
                 f'y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"'
                 f'{dash_attr}{op}/>')

    def path(self, d: str, stroke: str, width: float = 1,
             fill: str = "none", dash: str | None = None) -> None:
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="{width}" stroke-linecap="round" '
                 f'stroke-linejoin="round"{dash_attr}/>')

    def dot(self, cx: float, cy: float, r: float, fill: str,
            opacity: float = 1.0) -> None:
        op = f' opacity="{opacity}"' if opacity < 1 else ""
        self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" '
                 f'fill="{fill}"{op}/>')

    # -- composed -----------------------------------------------------------
    def chip(self, x: float, y: float, h: float, label: str, size: float,
             fg: str, bg: str, stroke: str | None = None,
             width: float | None = None, mono: bool = True,
             weight: int = 400, padx: float = 9,
             dash: str | None = None) -> float:
        need = (sw(label, size) if mono else sa(label, size)) + padx * 2
        cw = width if width is not None else need
        if need > cw + 0.5:
            sys.exit(f"FATAL: flow chip {label!r} needs {need:.1f}px, "
                     f"box is {cw:.1f}px")
        self.rect(x, y, cw, h, h / 2, bg, stroke, 1, dash)
        self.text(x + cw / 2, y + h / 2 + size * 0.35, label, size, fg, mono,
                  weight, "middle")
        return cw

    def two_line_chip(self, x: float, y: float, w: float, h: float,
                      top: str, bottom: str, accent: str, bg: str,
                      dash: str | None = None) -> None:
        self.rect(x, y, w, h, 10, bg, accent, 1, dash)
        for line, size, fill, dy, weight in (
                (top, 13, accent, 19, 700),
                (bottom, 11, self.s["sub"], 35, 400)):
            need = sw(line, size)
            if need > w - 10:
                sys.exit(f"FATAL: flow chip line {line!r} needs {need:.1f}px "
                         f"in {w:.1f}px")
            self.text(x + w / 2, y + dy, line, size, fill, True, weight,
                      "middle")

    def pill(self, x: float, y: float, w: float, h: float, label: str,
             size: float, fg: str, bg: str, stroke: str | None = None,
             dash: str | None = None) -> None:
        need = sw(label, size)
        if need > w - 8:
            sys.exit(f"FATAL: flow pill {label!r} needs {need:.1f}px of {w:.1f}")
        self.rect(x, y, w, h, h / 2, bg, stroke, 1, dash)
        self.text(x + w / 2, y + h / 2 + size * 0.35, label, size, fg, True,
                  400, "middle")


def flow_svg(skin: str) -> str:
    s = SVG[skin]
    W, H = 1100, 660
    f = Fig(skin)

    f.add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
          f'viewBox="0 0 {W} {H}" role="img" '
          f'aria-labelledby="fig-title fig-desc">')
    f.add('<title id="fig-title">dsh-review-reply-check structure: a coverage '
          'ladder beside the four orthogonal checks</title>')
    f.add('<desc id="fig-desc">A response table (file or inline material) and a '
          'validated rule pack enter runTableCheck. Three coverage rules form '
          'a ladder: every row needs a comment, a comment needs a response, and a '
          'response needs a revision and its location. Four further rules read the '
          'header, the comment numbering, the status vocabulary and the deadline. '
          'Findings leave with locator row and column; a check that cannot run is '
          'listed in skipped with its reason.</desc>')
    f.add('<defs>'
          '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
          f'<stop offset="0" stop-color="{s["bg"]}"/>'
          f'<stop offset="1" stop-color="{s["bg2"]}"/></linearGradient>'
          '<radialGradient id="glow">'
          f'<stop offset="0" stop-color="{s["accent"]}" stop-opacity="0.16"/>'
          f'<stop offset="1" stop-color="{s["accent"]}" stop-opacity="0"/>'
          '</radialGradient>'
          '<filter id="sh" x="-25%" y="-25%" width="150%" height="170%">'
          f'<feDropShadow dx="0" dy="6" stdDeviation="9" '
          f'flood-color="{s["shadow"]}" flood-opacity="{s["shadow_op"]}"/>'
          '</filter></defs>')
    f.rect(0, 0, W, H, 20, "url(#bg)")
    f.add(f'<circle cx="1000" cy="30" r="290" fill="url(#glow)"/>')
    f.add(f'<circle cx="80" cy="640" r="230" fill="url(#glow)"/>')

    # ---- title strip -------------------------------------------------------
    f.text(32, 38, f"{NAME} · structure", 18, s["text"], False, 700)
    right = "review_reply_check · 7 rules · rules/review-reply-check.yaml"
    if sw(right, 11) > 620:
        sys.exit("FATAL: flow title right token overflows")
    f.text(1068, 38, right, 11, s["faint"], True, 400, "end")

    # ---- supply band -------------------------------------------------------
    ax0, ay0, ax1, ay1 = 32, 62, 548, 182
    bx0, by0, bx1, by1 = 564, 62, 1068, 182
    f.rect(ax0, ay0, ax1 - ax0, ay1 - ay0, 18, s["card"], s["edge"], 1,
           shadow=True)
    f.rect(bx0, by0, bx1 - bx0, by1 - by0, 18, s["card"], s["edge"], 1,
           shadow=True)

    f.text(ax0 + 16, ay0 + 22, "MATERIAL", 11.5, s["accent"], True, 700)
    f.text(ax1 - 16, ay0 + 22, "parseMaterial", 11, s["faint"], True, 400,
           "end")
    mx = ax0 + 16
    mx += f.chip(mx, ay0 + 34, 22, "file", 11.5, s["accent"], s["pill"],
                 s["edge"], padx=8) + 7
    f.chip(mx, ay0 + 34, 22, "material", 11.5, s["accent"], s["pill"],
           s["edge"], padx=8)
    f.text(ax1 - 16, ay0 + 50, "JSON / YAML", 11, s["faint"], True, 400, "end")

    f.text(ax0 + 16, ay0 + 80, "header", 11, s["accent"], True, 700)
    f.text(ax0 + 74, ay0 + 80, "manuscriptNo · round · dueAt", 11.5,
           s["sub"], True)
    f.text(ax0 + 16, ay0 + 100, "rows[]", 11, s["accent"], True, 700)
    f.text(ax0 + 74, ay0 + 100, "12 column aliases · requireAnyOf", 11.5,
           s["sub"], True)

    f.text(bx0 + 16, by0 + 22, "RULE PACK", 11.5, s["accent"], True, 700)
    f.text(bx1 - 16, by0 + 22, "loadRuleset", 11, s["faint"], True, 400, "end")
    f.chip(bx0 + 16, by0 + 34, 22, "rulesFile", 11.5, s["accent"], s["pill"],
           s["edge"], padx=8)
    f.text(bx1 - 16, by0 + 50, "validated on load", 11, s["faint"], True, 400,
           "end")
    f.text(bx0 + 16, by0 + 80, "basis", 11, s["accent"], True, 700)
    f.text(bx0 + 62, by0 + 80, "document · number · clause · excerpt · kind · source",
           11.5, s["sub"], True)
    f.text(bx0 + 16, by0 + 100, "cap", 11, s["accent"], True, 700)
    f.text(bx0 + 50, by0 + 100, "derived-from-principle ≤ warn · institutional ≤ info",
           11.5, s["sub"], True)

    # ---- engine seam -------------------------------------------------------
    sy0, sy1 = 190, 228
    f.rect(32, sy0, 1036, sy1 - sy0, 12, s["accent_soft"], s["accent"], 1)
    f.text(48, sy0 + 25, "runTableCheck(material, ruleset)", 13, s["accent"],
           True, 700)
    mid = "each rule: applicable? check : skip(reason)"
    f.text(430, sy0 + 25, mid, 11, s["sub"], True)
    right = "locator { row, column }"
    if sw(right, 11) > 220:
        sys.exit("FATAL: seam right token overflows")
    f.text(1052, sy0 + 25, right, 11, s["sub"], True, 400, "end")
    # seam feeds both lower panels
    for x in (390, 908):
        f.line(x, sy1, x, sy1 + 8, s["sub"], 1.2)
        f.path(f"M{x - 4:.1f} {sy1 + 4:.1f}L{x:.1f} {sy1 + 9:.1f}"
               f"L{x + 4:.1f} {sy1 + 4:.1f}", s["sub"], 1.2)

    # ---- ladder ------------------------------------------------------------
    lx0, ly0, lx1, ly1 = 32, 244, 740, 532
    f.rect(lx0, ly0, lx1 - lx0, ly1 - ly0, 18, s["card"], s["edge"], 1,
           shadow=True)
    f.text(lx0 + 16, ly0 + 26, "COVERAGE LADDER", 11.5, s["accent"], True, 700)
    f.text(lx0 + 158, ly0 + 26, "· coverage checks", 11, s["faint"], True)
    f.text(lx1 - 16, ly0 + 26, "each check runs independently", 11, s["faint"],
           True, 400, "end")

    rungs = [
        ("01", "every row", ["comment"], "RR-001", "presence",
         "issue · row r · column comment"),
        ("02", "comment filled", ["response"], "RR-002", "conditionalPresence",
         "issue · row r · column comment"),
        ("03", "response filled", ["revision", "revisionLocation"], "RR-003",
         "conditionalPresence", "issue · row r · column response"),
    ]
    rung_y = [282, 356, 430]
    rung_h = 70
    for i, ((idx, condition, fields, rule, kind, tail),
            ry) in enumerate(zip(rungs, rung_y)):
        x0 = lx0 + 16 + i * 16
        x1 = lx1 - 16
        f.rect(x0, ry, x1 - x0, rung_h, 12, s["column"], s["edge"], 1)
        # rung index + condition
        f.text(x0 + 12, ry + 18, idx, 11, s["faint"], True, 700)
        f.text(x0 + 38, ry + 18, "if", 11, s["faint"], True)
        f.text(x0 + 58, ry + 18, condition, 13, s["text"], True, 700)
        # requirement fields
        cx = x0 + 38
        for field in fields:
            cx += f.chip(cx, ry + 34, 22, field, 13, s["accent"],
                         s["accent_soft"], s["accent"], padx=5) + 6
        # finding tail, on the requirement line but clear of both the fields
        # and the rule chip on the right
        tail_x = x0 + 254
        chip_x = x1 - 144
        if sw(tail, 11) > chip_x - (tail_x + 10) - 2:
            sys.exit(f"FATAL: ladder tail {tail!r} overflows")
        if tail_x - cx > 26:
            f.line(cx + 4, ry + 45, tail_x - 7, ry + 45, s["faint"], 1,
                   "2 4", 0.45)
        f.dot(tail_x, ry + 45, 3, s["warn"])
        f.text(tail_x + 10, ry + 49, tail, 11, s["warn"], True)
        # rule chip
        f.two_line_chip(chip_x, ry + 11, 134, 48, rule, kind, s["accent"],
                        s["accent_soft"])
        # stair connector
        if i < len(rungs) - 1:
            nx0 = lx0 + 16 + (i + 1) * 16
            f.path(f"M{x0 + 20:.1f} {ry + rung_h:.1f}"
                   f"V{ry + rung_h + 4:.1f}H{nx0 + 20:.1f}"
                   f"V{ry + rung_h + 8:.1f}", s["accent"], 1.4)
            f.dot(x0 + 20, ry + rung_h + 8, 2, s["accent"])
            f.dot(nx0 + 20, ry + rung_h + 8, 2, s["accent"])

    f.text(lx0 + 16, ly1 - 12,
           "a row may fail several rungs · the pack evaluates all three checks",
           11, s["faint"], True)

    # ---- check bench -------------------------------------------------------
    bx0, by0, bx1, by1 = 756, 244, 1068, 532
    f.rect(bx0, by0, bx1 - bx0, by1 - by0, 18, s["card"], s["edge"], 1,
           shadow=True)
    f.text(bx0 + 16, by0 + 26, "CHECK BENCH", 11.5, s["accent"], True, 700)
    f.text(bx0 + 112, by0 + 26, "· outside the ladder", 11, s["faint"], True)

    bench = [
        ("RR-006", "headerPresence", "header { manuscriptNo, round }",
         "no issue", False),
        ("RR-007", "unique", "rows[].commentNo", "no issue", False),
        ("RR-004", "enum", "rows[].status · values: []", "skipped", True),
        ("RR-005", "date", "respondedAt ≤ dueAt", "no issue", False),
    ]
    for i, (rule, kind, scope, state, skipped) in enumerate(bench):
        y = by0 + 38 + i * 56
        f.rect(bx0 + 16, y, bx1 - bx0 - 32, 50, 10, s["column"], s["edge"], 1)
        f.text(bx0 + 26, y + 17, rule, 13, s["accent"], True, 700)
        f.text(bx0 + 92, y + 17, kind, 11, s["sub"], True)
        f.text(bx0 + 26, y + 39, scope, 11, s["sub"], True)
        tone = s["warn"] if skipped else s["green"]
        tone_bg = s["warn_soft"] if skipped else s["green_soft"]
        f.pill(bx1 - 92, y + 8, 66, 22, state, 11, tone, tone_bg, tone,
               "4 3" if skipped else None)

    f.text(bx0 + 16, by1 - 12, "skipped ≠ pass · it names why", 11, s["warn"],
           True, 700)

    # ---- report tray -------------------------------------------------------
    tx0, ty0, tx1, ty1 = 32, 544, 1068, 628
    f.rect(tx0, ty0, tx1 - tx0, ty1 - ty0, 14, s["card"], s["edge"], 1,
           shadow=True)
    f.text(tx0 + 16, ty0 + 22, "issues[]", 11.5, s["accent"], True, 700)
    f.text(tx0 + 84, ty0 + 22, "· locator { row, column }", 11, s["faint"],
           True)

    def issue_entry(x: float, y: float, rule: str, rest: str) -> None:
        f.text(x, y, rule, 11, s["warn"], True, 700)
        f.text(x + sw(rule, 11) + 6, y, rest, 11, s["text"], True)

    issue_entry(tx0 + 16, ty0 + 42, "RR-001", "· row 4 · column comment")
    issue_entry(tx0 + 236, ty0 + 42, "RR-002", "· row 3 · column comment")
    issue_entry(tx0 + 16, ty0 + 62, "RR-003", "· row 2 · column response")
    f.text(tx0 + 304, ty0 + 62, "warn 3 · info 0 · skipped 1", 11, s["sub"],
           True)

    f.line(636, ty0 + 12, 636, ty1 - 12, s["line"], 1)
    f.text(652, ty0 + 22, "skipped[]", 11.5, s["warn"], True, 700)
    issue_entry(652, ty0 + 42, "RR-004", "· values: []")
    f.text(652, ty0 + 62, "status vocabulary unset", 11, s["faint"], True)

    f.line(872, ty0 + 12, 872, ty1 - 12, s["line"], 1)
    f.text(888, ty0 + 22, "buildView", 11.5, s["accent"], True, 700)
    f.text(888, ty0 + 42, "markdown + reportJson", 11, s["sub"], True)
    f.text(888, ty0 + 62, "rulesetVersion 2026.1", 11, s["faint"], True)

    # ---- footer ------------------------------------------------------------
    f.text(32, 650, "Apache-2.0 · pure ESM · read-only · no network · "
                    "no model call · no native code", 11, s["faint"], True)

    f.add("</svg>")
    return "\n".join(f.parts) + "\n"


# ------------------------------------------------------------------------ main --
def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for lang in ("zh", "en"):
        for skin in ("light", "dark"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        path = os.path.join(OUT, f"{NAME}-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {os.path.relpath(path, ROOT)}")


if __name__ == "__main__":
    main()
