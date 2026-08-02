# Diff Test Cases

Three before/after pairs. Each pair is a **single** complete, self-contained, styled Japanese
document, and every test case is a section inside it with a stable `id`. Diffing a pair once
exercises every pattern at the same time — cheaper to run than a fixture pair per case, and a
stricter test, since a bug in one section has to coexist with twenty others rather than being
isolated.

| Set | Files | Document | Purpose |
|---|---|---|---|
| 1 | `all-cases-{before,after}.html` | 資産台帳統合プロジェクト 進捗報告 | The core diff patterns |
| 2 | `backend-design-{before,after}.html` | 注文管理サービス バックエンド設計書 | The same patterns in **deliberately different HTML** |
| 3 | `edge-cases-{before,after}.html` | 社内申請ワークフロー 移行仕様書 | The **idioms and patterns the first two miss** |

Sets 2 and 3 exist because a diff engine can pass every pattern in one document's idiom and still
fall over on another's. Each set is written to share as little as possible with the others:

| | Set 1 | Set 2 | Set 3 |
|---|---|---|---|
| Palette | light | **dark** | light, serif, print-like |
| Layout | flex + left sidebar nav (`ul`/`li`/`a`) | grid + **horizontal top nav** | single sheet + boxed index, **`column-count`** prose |
| Sectioning | `<section>` drawn as cards | `<article>` separated by `<hr>` | `<section>` with a ruled heading |
| Tables | `<thead>` + column headers | no `<thead>`, `th scope="row"`, `colspan`, `rowspan` | **`colgroup`/`col`**, **multiple `<tbody>`**, **`<tfoot>`**, **a table inside a cell** |
| Other | `dl` / `ul.tree` / `ol.steps` | `details`/`summary`, inline SVG, `figure`, `abbr[title]`, `data-*` | **forms**, **`time`/`ruby`/`sup`/`sub`/`mark`/`kbd`**, **emoji**, **data: URI images**, **`hidden`**, **HTML comments**, **the document's own `ins`/`del`**, **`dir="rtl"`/`bdi`**, **`display:table`/`display:contents`/`float`** |

All three are emitted by a generator ([`generate.py`](generate.py),
[`generate-backend.py`](generate-backend.py), [`generate-edge.py`](generate-edge.py)) from a single
source, so the `<style>` block is byte-identical within a pair by construction and can never drift:

```
python3 diff-testcases/generate.py
python3 diff-testcases/generate-backend.py
python3 diff-testcases/generate-edge.py
```

## Opening them

[`open-all-cases.html`](open-all-cases.html), [`open-backend-design.html`](open-backend-design.html)
and [`open-edge-cases.html`](open-edge-cases.html) are single links that open a pair already loaded
the right way round, through a Diff URL with both files embedded. Nothing to drag, so there is no pane to get wrong. **Regenerate them whenever the
fixtures change** — the file contents are carried inline in the URL.

All three documents open with a `sec-direction` section that states which file it is, so the render
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

## Set 3 — 社内申請ワークフロー 移行仕様書

| Section id | Idiom / pattern under test | What a correct rendering shows |
|---|---|---|
| `sec-direction` | diff の向きそのもの | `BEFORE` red, `AFTER` green, 第 3 版→第 4 版. |
| `sec-form` | **フォームの状態**（`input value` / `option selected` / `checkbox checked` / `textarea`） | Each state change carries `data-diff-attr`; the rendered form holds the **after** values. |
| `sec-table-parts` | **`colgroup`/`col`**, **複数 `<tbody>`**, **`<tfoot>`** | `colgroup` and both `tbody` survive, one row added, the `tfoot` total partially marked. |
| `sec-table-nested` | **セルの中の表** | The inner table keeps **its own** 2 columns — it must not be padded out to the outer table's width — and gains one marked row. |
| `sec-col-reorder` | **列の入れ替え**（増減なし） | Shown as delete+insert of the moved column, table still rectangular, the untouched columns unmarked. |
| `sec-col-rename` | **列名だけの変更**（データ同一） | The table stays **4 columns**, only the header cell is partially marked, and **no data cell is touched**. |
| `sec-dup-blocks` | 完全に同一のブロックが 3 つ | Exactly one marked deleted; the rest unmarked. |
| `sec-dup-text` | 同一の段落が 3 つ、真ん中だけ編集 | One inserted and one deleted paragraph. Which of three identical paragraphs was edited is not decidable, so this is the honest rendering. |
| `sec-inline-semantics` | `time[datetime]` / `ruby` / `sup` / `sub` / `mark` / `kbd` | `datetime` carries `data-diff-attr` **even though the text changed too**; the untouched `kbd` stays unmarked. |
| `sec-emoji` | **絵文字**（肌色修飾・国旗・ZWJ 連結） | No `U+FFFD` anywhere; untouched emoji survive intact; swapped emoji and words are marked. |
| `sec-style-attr` | インライン `style` 属性だけ | `TD[style]` marked, zero text-level markers. |
| `sec-img` | **data: URI の画像** | Two images, one `src` change and one `alt`-only change marked, untouched caption unmarked. |
| `sec-hidden` | `hidden` 属性の付け外し | `P[hidden]` marked, zero text-level markers. |
| `sec-comment` | HTML コメントの変更 | The comment text never appears as content and produces no markers. |
| `sec-authors-insdel` | **文書が元から持つ `ins`/`del`** | The author's own `ins`/`del` survive and stay distinguishable from the tool's markers. |
| `sec-move-across` | 項目が別のリストへ移る | Deleted in the source list, inserted in the destination list. |
| `sec-replace-all` | 節の中身を丸ごと差し替え | Whole `p` and `table` delete plus insert, **zero** word-level interleaving. |
| `sec-deep` | 6 階層の入れ子 | The change at the bottom is visible and the added leaf is marked. |
| `sec-rtl` | `dir="rtl"` と `bdi` | Direction preserved, `bdi` intact, both edits marked. |
| `sec-css-layout` | `display:table` / `display:contents` / `float` / `column-count` | All four structures survive and each carries its own edit. |
| `sec-misc-containers` | `hgroup` と `address` | Both survive; the time and extension changes are marked. |
| `sec-legacy-approval` / `sec-delegation` | 節そのものの増減（目次とセット） | Whole `del` / whole `ins`, nav gains and loses exactly one item. |

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
edge-cases-before.html       edge-cases-after.html         set 3
generate.py  generate-backend.py  generate-edge.py         emit each pair from one source
open-all-cases.html  open-backend-design.html  open-edge-cases.html
                                                           one-click launchers (Diff URL inline)
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
  edge-cases-diff.png                     set 3 through the tool
  edge-legend-and-direction.png           set 3 with the legend visible
  case2-reported-scenarios.png            the originally reported document, after the fixes
```

## Known coarseness

These are representations the engine chooses deliberately, not defects:

- A **moved but otherwise unchanged** element renders as delete plus insert. Collapsing it into one
  element would hide the move, which is usually the point of the edit.
- A **moved column** does the same, so its data appears twice — once struck, once added.
- When several **identical** blocks or paragraphs sit together and one of them is edited, which one
  was edited is not decidable, so the result is one insert plus one delete rather than an in-place
  edit.
- A **CSS-only change** produces no markers. The diff is over the DOM, so a rule change with no
  effect on content has nothing to mark.
- A document with **no element children at all** (plain text, whitespace) is refused with
  「HTML として解釈できる要素がありません」.

Reference renders are captured so a rendering problem can be attributed: if a table looks ragged
through the tool but is uniform in both reference renders, the fault is in the diff, not the fixture.
Both sets are confirmed free of horizontal overflow, with every span-free table uniform.
