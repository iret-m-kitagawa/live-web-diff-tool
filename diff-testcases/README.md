# Diff Test Cases

Two before/after pairs. Each pair is a **single** complete, self-contained, styled Japanese document,
and every test case is a section inside it with a stable `id`. Diffing a pair once exercises every
pattern at the same time — cheaper to run than a fixture pair per case, and a stricter test, since a
bug in one section has to coexist with eighteen others rather than being isolated.

| Set | Files | Document | Purpose |
|---|---|---|---|
| 1 | `all-cases-{before,after}.html` | 資産台帳統合プロジェクト 進捗報告 | The core diff patterns |
| 2 | `backend-design-{before,after}.html` | 注文管理サービス バックエンド設計書 | The same patterns written in **deliberately different HTML** |

Set 2 exists because a diff engine can pass every pattern in one document's idiom and still fall over
on another's. It differs from set 1 on purpose:

| | Set 1 | Set 2 |
|---|---|---|
| Palette | light | **dark** (are the diff colours legible on a dark page?) |
| Layout | flex + left sidebar nav (`ul`/`li`/`a`) | grid + **horizontal top nav** (bare `a` children) |
| Sectioning | `<section>` drawn as cards | `<article>` separated by `<hr>` |
| Tables | `<thead>` + column headers | **no `<thead>`**, **`th scope="row"`**, **`colspan`**, **`rowspan`** |
| Other | `dl` / `ul.tree` / `ol.steps` | **`details`/`summary`**, **inline SVG**, **`figure`/`figcaption`**, `abbr[title]`, `data-*` |

Both sets are emitted by a generator ([`generate.py`](generate.py),
[`generate-backend.py`](generate-backend.py)) from a single source, so the `<style>` block is
byte-identical within a pair by construction and can never drift:

```
python3 diff-testcases/generate.py
python3 diff-testcases/generate-backend.py
```

## Opening them

[`open-all-cases.html`](open-all-cases.html) and [`open-backend-design.html`](open-backend-design.html)
are single links that open a pair already loaded the right way round, through a Diff URL with both
files embedded. Nothing to drag, so there is no pane to get wrong. **Regenerate them whenever the
fixtures change** — the file contents are carried inline in the URL.

Both documents open with a `sec-direction` section that states which file it is, so the render
describes its own direction: **`BEFORE（旧）` red and `AFTER（新）` green** means the panes are the
right way round. If it reads the other way, every other section will look inverted too, with
additions marked red.

Each section's lead line states **what each file contains** ("BEFORE は4列。AFTER は末尾に「備考」列が
増えて5列。") rather than an action ("末尾に列を追加"). An action reads as a claim about the render, so
with the files in the wrong panes the text and the colours appear to contradict each other; a
statement about file content stays true either way.

## Set 1 — 資産台帳統合プロジェクト 進捗報告

| Section id | Pattern exercised | What a correct rendering shows |
|---|---|---|
| `sec-direction` | diff の向きそのもの | `BEFORE（旧）` red, `AFTER（新）` green, `v1.2`→`v1.3`. |
| `sec-col-add-tail` | 表：末尾に列を追加（4→5列） | New `備考` header and one new cell per row marked **added**; every row still 5 cells; the four pre-existing columns unmarked. |
| `sec-col-add-mid` | 表：途中に列を追加 | New `管理担当` column marked **added at index 3**; the `数量` column shifts right without being marked — index-based cell pairing would instead pair `数量` with `管理担当` and fuse their values. |
| `sec-col-del-mid` | 表：途中の列を削除 | The removed column is put **back in place** marked **deleted**, values intact, so the table renders 5 wide with one struck column. Silently dropping it would make a column deletion invisible. |
| `sec-col-del-tail` | 表：末尾の列を削除 | Same, at the last position. |
| `sec-row-churn` | 表：行を1本削除・1本追加、金額を6箇所変更 | `Classic` row **deleted at its original 3rd position** (not flushed to the end), `Pro Plus` row **added**; each changed amount marked at value level; the unchanged `$780` unmarked; no cell ever holds three `$`. |
| `sec-lookalike` | 表：同型の行が5本並ぶ中から1本削除＋別行の1セル変更 | Exactly the `sato.k` login row **deleted**, exactly one other row with exactly one changed cell. |
| `sec-cards` | カード：削除・追加・入れ替え・移動しつつ本文も変更 | 5 cards render (4 after + 1 deleted). `決済APIの連携` shown **once** with its edits visible — it moved *and* changed, which a run-local diff renders as an unrelated delete plus insert. No card holds two `<h4>`. |
| `sec-card-attr` | カード：`class` だけの変更 | `data-diff-attr="class"` at a lighter green; no text-level markers. |
| `sec-list-nest` | 入れ子リスト：昇格・降格・`ul`→`ol`・並べ替え・削除 | `実装`'s list marked `data-diff-attr="tagName"` with its three items **not** duplicated. No `<li>` mixes two items' text. |
| `sec-steps` | 手順：ステップの移動＋別ステップの本文書き換え | The moved step stays **delete+insert** (its content is unchanged, so collapsing it would hide the move), `<h3>` and `<p>` together in one `<li>`. |
| `sec-glossary` | 用語集：`dt`/`dd` の増減と定義の書き換え | Added and removed terms each as a `dt`+`dd` **pair**; `dl` children stay strictly alternating. |
| `sec-prose` | 長文6段落にごく小さな修正3箇所 | At most 3 paragraphs touched, no block-level replacement, every marked span ≤12 characters. |
| `sec-inline` | インライン記法・属性のみ | **Zero** text-level markers. Only `A[href]` and `SPAN[class]` carry `data-diff-attr`. |
| `sec-code` | `pre`/`code` の行編集 | Indentation preserved, the block not replaced wholesale. |
| `sec-quote` | `blockquote` の部分修正 | Tight partial markers. |
| `sec-hlevel` | 見出しレベルの昇格（`h3`→`h2`） | Renders as `<h2>` carrying `data-diff-attr="tagName"`; no text-level markers. |
| `sec-swap` | 小見出しブロックの前後入れ替え | Delete+insert of the moved block. |
| `sec-legacy-permission` / `sec-integration` | 節そのものの増減（目次項目とセット） | Whole `del` / whole `ins` block, and the nav gains and loses exactly one item each. |

## Set 2 — 注文管理サービス バックエンド設計書

| Section id | Idiom under test | What a correct rendering shows |
|---|---|---|
| `sec-direction` | diff の向きそのもの | `BEFORE` red, `AFTER` green, `r14`→`r15`. |
| `sec-overview` | 長文5段落に4箇所の修正 | At most 3 paragraphs touched, no block-level replacement, tight spans. |
| `sec-endpoints` | **`<thead>` の無い表** ・途中に列追加 | New `認証` column marked added at index 3, every row 5 cells, the `応答` column unmarked despite shifting right. |
| `sec-errors` | **`th scope="row"` の行見出し** ・末尾の列削除 | `旧コード` column restored in place marked deleted; the first cell of every row **stays a `<th>`**. |
| `sec-schema` | **`colspan` を含む表** ・行の増減 | The spanning header survives intact (2 cells then 5), `memo` row deleted, `canceled_at` row added, only `status`'s type cell partially marked. |
| `sec-limits` | **`rowspan` を含む表** ・セル値の変更 | Row structure unchanged (4/4/3/4/3 cells), no row marked, exactly two cells changed, the 管理者 rows untouched. |
| `sec-audit` | 同型の行が並ぶ中での1行削除 | Exactly one row deleted, exactly one other row with exactly one changed cell. |
| `sec-services` | ブロックの増減・移動しつつ本文も変更 | 5 blocks (4 after + 1 deleted); `payment-service` shown once with its timeout and SLO edits visible. |
| `sec-flag` | **`data-*` 属性だけの変更** | `data-diff-attr="data-state"`; no text-level markers. |
| `sec-sequence` | **入れ子 `ol`** の並べ替えと階層追加 | The moved step delete+insert; the new nested list marked on the `ol` itself; no `<li>` mixes two steps' text. |
| `sec-runbook` | 手順の移動＋本文書き換え | `<h4>` and `<p>` stay in one `<li>`; only the rewritten step carries inline markers. |
| `sec-terms` | **`details`/`summary`** の増減 | One deleted, one added, one with its body partially marked. |
| `sec-inline` | `abbr[title]` ・リンク先・`em`→`strong` | Zero text-level markers; `ABBR[title]` and `A[href]` carry `data-diff-attr`; the deleted `<em>` sits **immediately before** the inserted `<strong>`, not at the end of the paragraph. |
| `sec-payload` | `pre` の中の JSON 編集 | Indentation preserved, partial markers only. |
| `sec-note` | `blockquote` + `cite` | Partial markers in both the quote and the citation. |
| `sec-diagram` | **インライン SVG** | The SVG is not duplicated, the new `outbox` shape and its label are present and outlined, and the caption's revision is partially marked. |
| `sec-figure` | **`figure`/`figcaption`** の中の表 | One `figure`, all rows 3 cells, only the availability value partially marked, caption partially marked. |
| `sec-hlevel` | 見出しレベルの昇格（`h4`→`h3`） | Renders as `<h3>` carrying `data-diff-attr="tagName"`; no text-level markers. |
| `sec-swap` | 小見出しブロックの前後入れ替え | Delete+insert of the moved block. |
| `sec-legacy-batch` / `sec-webhook` | 節そのものの増減（ナビとセット） | Whole `del` / whole `ins` block, nav gains and loses exactly one item each. |

## Colour scheme

Two hues, one strength, no borders — so a word-level insertion and a whole-column insertion are the
same green, and a marker's meaning never depends on which part of the page it is on:

| | Insertion | Deletion |
|---|---|---|
| Word / phrase (`ins` / `del`) | `rgba(26,159,71,.38)` | `rgba(229,50,45,.36)` |
| Whole element (`data-diff-block`) | `rgba(26,159,71,.38)` | `rgba(229,50,45,.36)` |
| Attribute or tag change (`data-diff-attr`) | `rgba(26,159,71,.15)` | — |
| **Inside `<svg>`** | 2px green outline | 2px red outline |

Deleted content is drawn at full opacity. SVG is the one exception to the fill-only rule: `background`
does not paint SVG shapes, and overriding `fill` would destroy the diagram's own colours, so shapes
get an outline instead — without it, adding or removing a shape changed nothing on screen.

The rendered output also carries a legend in its bottom-right corner — a red 「左 BEFORE で削除」 chip
and a green 「右 AFTER で追加」 chip — so the meaning of the colours and the direction of the
comparison are readable from the render itself. It is `pointer-events:none`, hidden when printing,
and opaque so it stays legible on both light and dark pages.

## Invariants checked across both documents

- Every `<table>` without `colspan`/`rowspan` is rectangular: all rows have the same cell count.
  (Tables that do use spans are legitimately non-uniform and are excluded.)
- No orphan bin (`#__diff_removed__`) is created and nothing is dumped at `body` level.
- The pasted `<style>` survives, so the diff is shown in the document's own design.
- No diff marker renders with `text-decoration: line-through`.
- Every nav item keeps the **same computed `display`** — one item alone rendering `inline` was a real
  reported bug — and every surviving item's `href="#..."` still resolves.
- No unexpected page errors while rendering.

## Files

```
all-cases-before.html        all-cases-after.html          set 1
backend-design-before.html   backend-design-after.html     set 2
generate.py                  generate-backend.py           emit each pair from one source
open-all-cases.html          open-backend-design.html      one-click launchers (Diff URL inline)
evidence/
  all-cases-{1-before,2-after}.png        reference renders of set 1
  all-cases-diff.png                      set 1 through the tool
  direction-correct.png / -swapped.png    what each pane ordering looks like
  section-cols.png / section-cards.png    set 1 close-ups
  legend-and-direction.png                set 1 with the legend visible
  backend-design-{1-before,2-after}.png   reference renders of set 2
  backend-design-diff.png                 set 2 through the tool
  backend-tables.png                      set 2 close-up: thead-less / th scope=row / colspan / rowspan
  backend-blocks.png                      set 2 close-up: block churn and data-* attribute change
  backend-svg.png                         set 2 close-up: inline SVG and figure
  backend-legend-and-direction.png        set 2 with the legend visible
  case2-reported-scenarios.png            the originally reported document, after the fixes
```

Reference renders are captured so a rendering problem can be attributed: if a table looks ragged
through the tool but is uniform in both reference renders, the fault is in the diff, not the fixture.
Both sets are confirmed free of horizontal overflow, with every span-free table uniform.
