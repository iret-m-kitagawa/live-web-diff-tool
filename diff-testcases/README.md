# Diff Test Cases

Fourteen before/after HTML fixture pairs for exercising a rich HTML-diff tool. Each pair is a
complete, self-contained, styled HTML document (no external assets, no scripts). Within a pair, the
CSS is byte-identical and the only differences are the specific change pattern each case is designed
to exercise. All content is realistic Japanese business/technical prose.

Verified for every pair: `diff before after` shows only the intended lines, both files parse with
balanced tags (Python `html.parser`), the `<style>` blocks are byte-identical between before/after,
and every `href="#..."` fragment link has a matching `id` in the same document.

Cases **01–08** were authored to cover the diff-engine's structural failure modes in the abstract.
Cases **09–14** were added later, modelled directly on six breakage patterns observed on real
documents, so each one reproduces a shape that actually broke the renderer:

| Observed breakage | Reproduced by |
|---|---|
| Table grew extra cells; adjacent money values fused (`$2,800` + `$8,000`) | 09, 10 |
| Cards from different items merged into one box | 11 |
| Ordered steps interleaved after a reorder | 12 |
| Sidebar nav list items rendered inline / links destroyed | 13 |
| Definition-list terms and quotes rewritten in place | 14 |
| `class` changed with no text change (attribute-only) | 04, 07, 11 |

Screenshot evidence for every case lives in [`evidence/`](evidence/): `<slug>-1-before.png` and
`-2-after.png` are plain reference renders of the fixtures, `-3-diff.png` is the tool's HTML View
output, and `metrics.json` holds the per-case marker counts and table-geometry numbers.

## Summary table

| # | Case (file stem) | Change pattern exercised | What a correct diff rendering should show |
|---|---|---|---|
| 01 | `01-table-structure` | Table churn: row insert, row delete, single-cell value edit, whole column added | `app-02` row shown as **added**; `mail-01` row shown as **removed**; `db-01` memory cell `32GB→64GB` shown as **changed**; new `担当者` header + one new cell per surviving row shown as **added**. Everything else in the table (web-01, web-02, app-01, batch-01, cache-01 and their untouched cells) unmarked. |
| 02 | `02-nested-list-restructure` | Nested-list restructuring: level promotion, level demotion, `<ul>`→`<ol>` conversion, sibling reorder, nested-item deletion | `顧客レビュー` shown **moved** up a level (not delete+insert of unrelated text); `外部インターフェース設計` shown **moved** down a level under データベース設計; `実装`'s list shown as a **structural/style change** (bullets→numbers) with its 3 items unmarked; `リリースノート作成`/`受入テスト` shown **reordered**; `社内レビュー` shown **removed**. All other items (現行業務ヒアリング, 要求一覧の作成, 画面設計, データベース設計, 本番反映) unmarked. |
| 03 | `03-heading-and-section-reorder` | Whole-section swap + heading-level promotion + light body-text edit | `背景` and `リスクと対策` sections shown **moved** (swapped position; アーキテクチャ stays sandwiched between them) with their inner text unmarked; `データフロー` heading shown as a **level/style change** (h3→h2, identical text) not a text delete+insert; in 概要, only the inserted clause `およびカート機能` shown **added**. アーキテクチャ's own text, コンポーネント構成, and the schedule table unmarked. |
| 04 | `04-inline-markup-only` | Attribute/markup-only changes; visible text is byte-identical | Zero text characters marked inserted/deleted anywhere (verified programmatically — see Case 04 detail). Only formatting/attribute signals: a phrase gains **bold** (`<strong>`), another loses *italic* (`<em>` removed), a link's underlying `href` changes while its text doesn't, and a phrase gains a **highlight** background via a new `class`. |
| 05 | `05-code-block-edit` | Multi-line `<pre><code>` edit (2 changed, 1 added, 1 deleted, indentation-sensitive) + one inline `<code>` change in prose | Inline `app-blue`→`app-green` shown **changed**. In the script: `SLOT="blue"→"green"` and the `HEALTHCHECK_URL` host shown **changed**; `docker rm …` line shown **removed**; new `--env RELEASE_TAG=...` line shown **added** with indentation matching its sibling flags, with no reflow of surrounding untouched lines. |
| 06 | `06-repeated-similar-rows` | Ambiguous-alignment stress test: 10 near-identical log rows, one middle row deleted, one distant cell changed | Exactly the `sato.k`/11:20:09 login row shown **removed**, without misaligning the other 4 look-alike login rows. Exactly the `tanaka.r`/権限設定 row's result cell shown **changed** (成功→失敗), without being confused with the pre-existing unrelated `tanaka.r` failed-login row. The 3 summary stat numbers changing is an expected derived consequence, not a stray diff. All other 8 rows unmarked. |
| 07 | `07-card-grid-churn` | Card grid churn: delete, add, reorder swap, class-only state change with unchanged text | `通知基盤移行` card shown **removed**; `データ基盤PoC` card shown **added**; `決済API連携`/`監視体制強化` cards shown **moved** (swapped) with unmarked content; `管理画面リニューアル` card shown with a **style/state change only** (class `card`→`card done`, driving a CSS ribbon + strikethrough) — its title/description/owner/date text must show zero markers. `認証基盤刷新` untouched. |
| 08 | `08-longform-small-edits` | Longform prose (8 paragraphs), exactly 3 tiny edits — the "don't over-mark" check | Only `38%→42%`, `2026年9月30日→2026年10月15日`, and `課題→懸念` shown as tight, word/phrase-level **changed** spans. Every other sentence across all 8 paragraphs must render with **zero** insert/delete/change markers — no paragraph- or sentence-level over-marking. |
| 09 | `09-column-inserted` | **Column inserted mid-table** (5→6 cols), plus 4 scattered cell edits, 10 data rows | New `管理担当` header + one new cell per row shown as **added**. Every rendered row must have **exactly 6 cells** — no row wider than the header, and no cell holding two columns' values fused together (`12`+`情報システム課` must not become one cell). `数量` `12→15` / `2→4`, `故障中→廃棄予定`, `2F事務エリア→3F事務エリア` shown as **changed**; the 6 untouched rows unmarked except for their one new cell. |
| 10 | `10-pricing-table-revision` | Money-heavy table: 5 amount edits + 1 row deleted + 1 row added, comma-formatted values | `$290→$350`, `$2,800→$3,600`, `$8,000→$8,400`, `20ユーザー→25ユーザー`, `$1,980→$2,180`, `$20,000→$22,000` shown as **changed** at value level. `Classic` row shown **removed** as a whole `<tr>`; `Pro Plus` row shown **added** as a whole `<tr>`. No two amounts may ever appear inside one cell (`$2,8003,600` and friends are the failure signature). |
| 11 | `11-status-cards-swap` | Same-class card grid: 1 deleted, 1 added, 2 lightly edited (text + badge class) | `通知サービス（メール／Push）` card shown **removed** as one whole `.card` inside the grid; `レポート生成サービス` card shown **added** as one whole `.card`. `認証基盤` shown with only its description tail and 稼働率 `99.95%→99.97%` **changed**; `決済システム` shown with badge `warn→ok`, description and 稼働率/時刻 **changed**. **No `.card` may contain two `<h3>` titles** — that is the interleaving breakage this case exists to catch. |
| 12 | `12-flow-steps-reorder` | `<ol>` step **moved** (2nd → 4th) + one step's body rewritten; CSS-counter numbering | `障害対応チームの招集` shown **moved** (delete+insert of the whole `<li>`, or an explicit move) — its `<h3>` and `<p>` must stay together in one `<li>`, never spliced into a neighbouring step. `暫定対処の実施`'s paragraph shown **changed** with the appended clause marked. The other steps unmarked; the CSS-counter numbers shifting is a derived consequence, not a stray diff. |
| 13 | `13-nav-and-footer-churn` | Sidebar `<nav>` list churn (delete/add/rename) with matching section changes + footer edits | `権限管理` nav item shown **removed** and `外部連携` **added**, each as a whole `<li>`; `よくある質問→FAQ・トラブルシューティング` shown as a **rename** inside the link text. Every `nav li` must keep the **same computed `display`** — one item rendering `inline` while its siblings are `list-item` is the reported breakage. Anchors must still resolve (`#section-integration` exists). Footer `2025→2026` and `18:00→19:00に延長` shown as tight **changed** spans. |
| 14 | `14-definition-list-and-blockquote` | `<dl>` term add/delete + definition rewritten, `<blockquote>` quote edited | `SLO（サービスレベル目標）` `<dt>`+`<dd>` shown **added** as a pair; `オンコール` `<dt>`+`<dd>` shown **removed** as a pair — a `<dt>` must never end up paired with an unrelated `<dd>`. `エスカレーション`'s `<dd>` shown with only its appended sentence marked. In the quote, `30分以内→15分以内` and the appended clause shown as tight **changed** spans, with the surrounding quotation unmarked. |

## Files

```
01-table-structure-before.html            01-table-structure-after.html
02-nested-list-restructure-before.html    02-nested-list-restructure-after.html
03-heading-and-section-reorder-before.html 03-heading-and-section-reorder-after.html
04-inline-markup-only-before.html         04-inline-markup-only-after.html
05-code-block-edit-before.html            05-code-block-edit-after.html
06-repeated-similar-rows-before.html      06-repeated-similar-rows-after.html
07-card-grid-churn-before.html            07-card-grid-churn-after.html
08-longform-small-edits-before.html       08-longform-small-edits-after.html
09-column-inserted-before.html            09-column-inserted-after.html
10-pricing-table-revision-before.html     10-pricing-table-revision-after.html
11-status-cards-swap-before.html          11-status-cards-swap-after.html
12-flow-steps-reorder-before.html         12-flow-steps-reorder-after.html
13-nav-and-footer-churn-before.html       13-nav-and-footer-churn-after.html
14-definition-list-and-blockquote-before.html
14-definition-list-and-blockquote-after.html

evidence/                                 screenshots + metrics.json (see top of this file)
```

## Case detail

### 01 — table-structure
`INFRA-2026-014` server migration inventory. `<table>` has `<thead>`/`<tbody>`.

- **Added:** row `app-02` (inserted between `app-01` and `db-01`); new `担当者` column — its `<th>`
  plus one new `<td>` in every surviving row (`web-01`, `web-02`, `app-01`, `db-01`, `batch-01`,
  `cache-01`) and in the new `app-02` row.
- **Removed:** row `mail-01` (廃止予定).
- **Changed:** `db-01`'s memory cell `32GB` → `64GB`.
- **Must NOT be marked:** every other cell of `web-01`, `web-02`, `app-01`, `batch-01`, `cache-01`
  (name, role, CPU, memory, status badge), section headings, notes list, badge colors/styling.

### 02 — nested-list-restructure
Work breakdown for a system-introduction project, four phases in a tree list.

- **Promoted a level:** `顧客レビュー` moves from being nested two levels under 要件定義 (inside
  優先度の確認's sub-list) to being a direct child of 要件定義 (sibling of 優先度の確認, which
  becomes a childless leaf item since both its children left).
- **Demoted a level:** `外部インターフェース設計` moves from a direct child of 設計 to a new
  nested child under データベース設計.
- **`<ul>` → `<ol>`:** the 実装 phase's list changes tag; its three items
  (フロントエンド実装/バックエンド実装/単体テスト) are textually unchanged.
- **Reordered siblings:** under リリース, `リリースノート作成` and `受入テスト` swap order
  (`本番反映` stays last).
- **Deleted:** `社内レビュー`.
- **Must NOT be marked:** 現行業務ヒアリング, 要求一覧の作成, 画面設計, データベース設計 (as text),
  本番反映, and the tree's card/connector styling.

### 03 — heading-and-section-reorder
`DES-0231` product-recommendation feature design doc, 5 sections.

- **Sections swapped:** `背景` (was #2) and `リスクと対策` (was #4) exchange positions; `アーキテクチャ`
  stays physically between them either way (new order: 概要, リスクと対策, アーキテクチャ, 背景,
  今後のスケジュール).
- **Heading promoted:** `<h3>データフロー</h3>` → `<h2>データフロー</h2>`, same text, same
  position inside アーキテクチャ. (Section numbering in the design is CSS-counter–driven, so this
  promotion visually renumbers subsequent headings without any text edits — a good secondary signal
  to check in a screenshot.)
- **Body text lightly edited:** in 概要, `...商品検索機能には影響を与えない。` gains the clause
  `およびカート機能` → `...商品検索機能およびカート機能には影響を与えない。`.
- **Must NOT be marked:** アーキテクチャ's intro paragraph, `コンポーネント構成` (still `<h3>`),
  リスクと対策's risk list text, the schedule table.

### 04 — inline-markup-only
Notice memo about a batch job's execution-time change. **The rendered text is byte-identical
before/after** (verified with an `HTMLParser`-based text extraction — see self-check below).

- `通知バッチの実行時刻を早めました` gains `<strong>`.
- `対象は本番環境のみ` loses its `<em>` (text kept, unwrapped).
- The `<a>` around `リリースノート` keeps its anchor text but its `href` changes
  (`.../2026-07/notes` → `.../2026-08/notes`).
- The `<span>` around `実行間隔の設定値` gains `class="highlight"` (adds a yellow background via
  existing, unmodified CSS).
- **Must NOT be marked:** any character of visible text anywhere in the document. A tool that shows
  insert/delete text markers on this pair is misfiring — the only legitimate signal here is
  formatting/attribute change, not content change.

### 05 — code-block-edit
Blue-green deploy runbook `RB-118`. Script is 24 lines.

- **Inline `<code>` in prose:** `app-blue` → `app-green`.
- **Changed lines in the script:** `SLOT="blue"` → `SLOT="green"`; `HEALTHCHECK_URL` host
  `blue.internal` → `green.internal`.
- **Deleted line:** `docker rm app-${SLOT} || true`.
- **Added line:** `  --env RELEASE_TAG=${RELEASE_TAG} \` inserted among the `docker run` flags,
  2-space indent matching its siblings exactly.
- **Must NOT be marked:** every other line of the script (shebang, `set -euo pipefail`,
  `RELEASE_TAG`, echoes, `docker pull`, `docker stop`, remaining flags, `sleep`/`curl`/final echo),
  and none of the untouched lines should show whitespace-only diffs.

### 06 — repeated-similar-rows
Operation audit log, 10 rows, dark console styling. This is the ambiguous-alignment stress case:
five rows share the identical shape (`ログイン`, target `-`, badge 成功) differing only in ID/time/user.

- **Deleted:** the middle `sato.k` login row (`LOG-0728-112009`, 11:20:09) — one of the five
  look-alike login rows.
- **Changed:** the `tanaka.r` / 設定変更 / 権限設定 row's result cell `成功` → `失敗` (badge turns
  from green to red). Do not confuse this with the *other*, pre-existing `tanaka.r` login row that
  was already `失敗` before any edits (`LOG-0728-134122`) — that row is untouched.
  Also do not confuse it with `LOG-0728-134140`, the immediately following successful re-login by the
  same user — that row is untouched too.
- **Derived (expected) change:** the summary stat bar (表示件数 10→9, 成功 9→7, 失敗 1→2) — a direct
  numeric consequence of the two edits above, not an independent stray change.
- **Must NOT be marked:** the other 8 rows verbatim, including the 4 remaining look-alike login rows.

### 07 — card-grid-churn
Project status board, CSS grid of cards.

- **Deleted:** `通知基盤移行` card (entire block).
- **Added:** `データ基盤PoC` card (entire block, appended at the end).
- **Reordered:** `決済API連携` and `監視体制強化` swap grid position.
- **State-class-only change:** `管理画面リニューアル` card's wrapping `<div>` gains `done`
  (`class="card"` → `class="card done"`); its title, description, owner and date text are **100%
  unchanged** (verified by diff — only the class attribute line changed). The `done` class alone
  drives a CSS-generated "完了" ribbon, a color change, and a strikethrough title.
- **Must NOT be marked:** `認証基盤刷新` (untouched, stays first); no text inside the
  管理画面リニューアル card.

### 08 — longform-small-edits
Project retrospective report, 8 paragraphs (はじめに / 背景 / 体制 / うまくいった点 / 課題 /
定量的な成果 / 今後のスケジュール / 総括), each 3+ sentences. This is the "don't over-mark" check.

- **Number:** `38%` → `42%` (定量的な成果).
- **Date:** `2026年9月30日` → `2026年10月15日` (今後のスケジュール).
- **Word swap:** `課題` → `懸念`, mid-sentence (総括).
- **Must NOT be marked:** literally every other sentence in all 8 paragraphs. A correct rich diff
  highlights only the three narrow spans above; any tool that flags whole paragraphs, whole
  sentences, or nearby unchanged words as changed fails this case.

### 09 — column-inserted
Office-equipment inventory, `<table>` with `<thead>`/`<tbody>`, 10 data rows. The table-geometry case.

- **Column inserted in the middle:** `管理担当` is added **between `設置場所` and `数量`**, not
  appended at the end (5 columns → 6). This is what breaks index-based cell alignment: every cell
  after position 4 shifts by one, so a naive diff pairs `設置場所` with `管理担当` and `数量` with
  `設置場所`, fusing unrelated values.
- **Changed cells:** `数量` `12→15` and `2→4`; status badge `故障中`(warn) → `廃棄予定`(bad);
  `設置場所` `2F事務エリア→3F事務エリア`.
- **Must NOT be marked:** the other 6 rows' name/type/location/quantity/status cells, headings, notes.
- **Hard requirement:** every rendered `<tr>` has exactly **6** cells. A row with 7 or 8 cells, or a
  cell reading `12情報システム課` / `情報システム課15`, is the failure this case detects.

### 10 — pricing-table-revision
External-SaaS price comparison, 5 columns, 6 plan rows. The "adjacent money values must not fuse" case.

- **Amounts changed:** Lite `$290→$350` and `$2,800→$3,600`; Standard `$8,000→$8,400` and
  `20ユーザー→25ユーザー`; Business `$1,980→$2,180` and `$20,000→$22,000`.
- **Removed:** the `Classic`(受付終了) row in full.
- **Added:** the `Pro Plus`(新設) row in full (`$1,280` / `$13,000` / `35ユーザー` / チャット・電話サポート).
- **Why the values look like this:** monthly and annual prices sit in **adjacent cells**, both
  comma-formatted. If cell alignment slips by one, the result is instantly visible as a single cell
  containing two amounts (`$2,8003,600`, `$8,00013,000`). Net row count is unchanged (6→6) so a
  tool cannot pass by simply counting rows.
- **Must NOT be marked:** the plan-name cells that did not change, the support-tier cells of
  untouched plans, the notes below the table.

### 11 — status-cards-swap
Service status board, CSS-grid of identically-classed `.card` blocks. The card-interleaving case.

- **Removed:** `通知サービス（メール／Push）` card (head + description + footer, whole block).
- **Added:** `レポート生成サービス` card (whole block).
- **Lightly changed:** `認証基盤` — description gains `応答時間を一部改善した。`, 稼働率
  `99.95%→99.97%`. `決済システム` — badge `warn`→`ok` with text `注意`→`正常`, description
  rewritten, 稼働率 `99.60%→99.94%`, 最終確認 `09:45→11:35`.
- **Must NOT be marked:** the remaining untouched cards.
- **Hard requirement:** no `.card` element may contain **two** `<h3>` titles. Because all cards share
  one class and one internal shape, a flattened diff pairs the deleted card with an unrelated added
  card and packs both titles, both descriptions and both footers into a single box — the exact
  breakage reported on real documents.

### 12 — flow-steps-reorder
Incident first-response procedure, `<ol>` with CSS-counter numbering, each `<li>` holding `<h3>`+`<p>`.

- **Step moved:** `障害対応チームの招集` moves from 2nd to 4th position, unchanged in content.
- **Body rewritten:** `暫定対処の実施`'s paragraph gains `負荷分散設定の変更等` inside the
  parenthetical and a whole appended sentence about recording actions in the incident ticket.
- **Derived (expected):** the CSS-counter numbers of the intervening steps shift — a consequence of
  the move, not an independent change.
- **Must NOT be marked:** the other steps' headings and bodies.
- **Hard requirement:** the moved step's `<h3>` and `<p>` stay inside **one** `<li>`. A diff that
  emits the heading into one step and the paragraph into another produces the interleaved,
  unreadable output this case exists to catch.

### 13 — nav-and-footer-churn
Internal-tool manual: sidebar `<nav>` (`ul`/`li`/`a` with fragment links), body sections, footer.

- **Nav item removed:** `権限管理` (`#section-permission`), together with its `<section>`.
- **Nav item added:** `外部連携` (`#section-integration`), together with a new `<section>` whose body
  text is entirely new.
- **Nav item renamed:** `よくある質問` → `FAQ・トラブルシューティング`; the link's `href`
  (`#section-faq`) and the section `id` are unchanged, only the visible text and the `<h2>` change.
- **Footer:** `© 2025` → `© 2026`; `平日 9:00〜18:00` → `平日 9:00〜19:00に延長`.
- **Must NOT be marked:** the other 5 nav items, the untouched sections, the mail address.
- **Hard requirements:** (a) every `nav li` keeps the **same computed `display`** — the reported bug
  was the last item alone rendering `inline` after the diff rewrote its link; (b) all fragment links
  still resolve to an existing `id` (verified: no dangling anchors in either file).

### 14 — definition-list-and-blockquote
Operations-policy glossary: `<dl>` of `<dt>`/`<dd>` pairs plus a `<blockquote>` policy statement.

- **Term added:** `SLO（サービスレベル目標）` — a `<dt>`+`<dd>` pair inserted mid-list.
- **Term removed:** `オンコール` — its `<dt>`+`<dd>` pair.
- **Definition extended:** `エスカレーション`'s `<dd>` gains an appended sentence
  (`一次対応者の判断のみに委ねず…`).
- **Quote changed:** `30分以内` → `15分以内`, and `顧客影響を最小化することを` →
  `顧客影響を最小化したうえで迅速に復旧することを`.
- **Must NOT be marked:** the other terms and definitions, the attribution line under the quote.
- **Hard requirement:** a `<dt>` must never be paired with an unrelated `<dd>`. `<dl>` alternates two
  different tags at the same level, so a diff that aligns children by position alone will shift the
  term/definition pairing by one from the insertion point onward.

## Self-check summary

All pairs confirmed via `diff` + Python `html.parser` (tag-balance check) + a text-extraction
byte-equality check for Case 04. Per-pair changed-line counts (`diff` added/removed lines):

| Case | Lines added (`>`) | Lines removed (`<`) |
|---|---|---|
| 01-table-structure | 16 | 8 |
| 02-nested-list-restructure | 10 | 11 |
| 03-heading-and-section-reorder | 14 | 14 |
| 04-inline-markup-only | 3 | 3 |
| 05-code-block-edit | 4 | 4 |
| 06-repeated-similar-rows | 4 | 12 |
| 07-card-grid-churn | 12 | 12 |
| 08-longform-small-edits | 3 | 3 |
| 09-column-inserted | 15 | 4 |
| 10-pricing-table-revision | 13 | 13 |
| 11-status-cards-swap | 10 | 10 |
| 12-flow-steps-reorder | 5 | 5 |
| 13-nav-and-footer-churn | 8 | 8 |
| 14-definition-list-and-blockquote | 5 | 5 |

No pair has any CSS/style-block or whitespace-only differences beyond what's listed above; the
`<style>` block is byte-identical within every pair. One deliberate design note rather than a
compromise: Case 01 intentionally has **no** literal sequential row-number column, because
inserting/deleting a row in a numbered table would cascade into renumbering every subsequent row's
number cell — a stray diff unrelated to the four changes the case is meant to exercise.

Cases 09–14 were additionally re-verified independently of the script that generated them: single
`<style>` block byte-identical per pair, zero `<script>` tags, zero external `src`/`href`/`url()`
references, `<!DOCTYPE html>` + `charset` present, and no `href="#..."` link without a matching `id`.
Structural counts were checked against each case's intent — 09 is confirmed 5→6 columns with **all
11 rows uniform** in both files (so any non-uniform row in the output comes from the diff, not the
fixture), and 10/11 keep their row/card counts constant across a delete+add pair so a tool cannot
pass them by counting elements alone.
