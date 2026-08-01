# Diff Test Cases

**One** before/after pair — `all-cases-before.html` / `all-cases-after.html` — instead of a fixture pair
per case. Both files are one complete, self-contained, styled Japanese document ("資産台帳統合プロジェクト
進捗報告"), and every test case is a `<section>` inside it with a stable `id`. Diffing the pair once
exercises every pattern at the same time, which is both cheaper to run and a stricter test: a bug in
one section has to coexist with seventeen others rather than being isolated.

Both files are emitted by [`generate.py`](generate.py) from a single source, so the `<style>` block is
byte-identical by construction and can never drift. Regenerate with:

```
python3 diff-testcases/generate.py
```

## Cases

| Section id | Pattern exercised | What a correct rendering shows |
|---|---|---|
| `sec-col-add-tail` | 表：末尾に列を追加（4→5列） | New `備考` header and one new cell per row marked **added**; every row still 5 cells; the four pre-existing columns unmarked. |
| `sec-col-add-mid` | 表：途中に列を追加（`設置場所` と `数量` の間） | New `管理担当` column marked **added at index 3**; the `数量` column shifts right without being marked — index-based cell pairing would instead pair `数量` with `管理担当` and fuse their values. |
| `sec-col-del-mid` | 表：途中の列を削除（`取得年度`） | The removed column is put **back in place** marked **deleted**, values intact, so the table renders 5 wide with one struck column. Silently dropping it would make a column deletion invisible. |
| `sec-col-del-tail` | 表：末尾の列を削除（`旧管理番号`） | Same, at the last position. |
| `sec-row-churn` | 表：行を1本削除・1本追加、金額を6箇所変更 | `Classic` row **deleted at its original 3rd position** (not flushed to the end), `Pro Plus` row **added**; each changed amount marked at value level; the unchanged `$780` unmarked; no cell ever holds three `$`. |
| `sec-lookalike` | 表：同型の行が5本並ぶ中から1本削除＋別行の1セル変更 | Exactly the `sato.k` login row **deleted**, exactly one other row with exactly one changed cell (`成功`→`失敗`). The other look-alike rows unmarked. |
| `sec-cards` | カード：1枚削除・1枚追加・2枚入れ替え・1枚は移動しつつ本文も変更 | 5 cards render (4 after + 1 deleted). `通知基盤の移行` **deleted**, `データ基盤のPoC` **added**, `決済APIの連携` shown **once** with its badge/description/date edits visible — it moved *and* changed, which a run-local diff renders as an unrelated delete plus insert. No card holds two `<h4>`. |
| `sec-card-attr` | カード：`class` だけの変更（テキスト完全同一） | The card carries `data-diff-attr="class"` and a dashed outline; **no** text-level markers. |
| `sec-list-nest` | 入れ子リスト：昇格・降格・`ul`→`ol`・並べ替え・削除 | `顧客レビュー` promoted (old nested `<ul>` deleted whole, new item added a level up), `外部インターフェース設計` demoted (old flat item deleted, new nested `<ul>` added), `実装`'s list marked `data-diff-attr="tagName"` with its three items **not** duplicated, `リリースノート作成` swap shown as delete+insert. No `<li>` mixes two items' text. |
| `sec-steps` | 手順：2番目のステップを4番目へ移動＋別ステップの本文を書き換え | The moved step stays **delete+insert** (its content is unchanged, so collapsing it would hide the move) with `<h3>` and `<p>` together in one `<li>`; only `暫定対処の実施` carries inline markers. |
| `sec-glossary` | 用語集：`dt`/`dd` を1組追加・1組削除、定義を1つ書き換え | `SLO` added as a `dt`+`dd` **pair**, `オンコール` deleted as a pair, `エスカレーション` の `dd` に部分的な印のみ. `dl` の子は最後まで `dt`/`dd` の交互のまま。 |
| `sec-prose` | 長文6段落にごく小さな修正3箇所 | At most 3 paragraphs touched, no block-level replacement, every marked span ≤12 characters. The "don't over-mark" check. |
| `sec-inline` | インライン記法・属性のみ（可視テキストは完全同一） | **Zero** text-level markers. Only `A[href]` and `SPAN[class]` carry `data-diff-attr`. |
| `sec-code` | `pre`/`code`：1行変更・1行追加・1行削除 | Indentation preserved, changes marked inside the block, the block not replaced wholesale. |
| `sec-quote` | `blockquote` の数値と語尾を変更 | Tight partial markers, not a whole-block swap. |
| `sec-hlevel` | 見出しレベルの昇格（`h3`→`h2`、テキスト同一） | The heading renders as `<h2>` carrying `data-diff-attr="tagName"`; no text-level markers anywhere in the section. |
| `sec-swap` | 小見出しブロックの前後入れ替え | Shown as delete+insert of the moved block. |
| `sec-legacy-permission` / `sec-integration` | 節そのものの増減（目次項目とセット） | The removed section stays as a whole `del` block, the new one as a whole `ins` block, and the nav gains/loses exactly one item each. |

The table of contents (`nav.toc`) additionally covers link churn: one item removed, one added, one
renamed. Every `nav li` must keep the **same computed `display`** — one item alone rendering `inline`
was a real reported bug — and every surviving item's `href="#..."` must still resolve.

## Invariants checked across the whole document

- Every `<table>` is rectangular: all rows in a table have the same cell count.
- No orphan bin (`#__diff_removed__`) is created and nothing is dumped at `body` level.
- The pasted `<style>` survives, so the diff is shown in the document's own design.
- No diff marker renders with `text-decoration: line-through`.
- No unexpected page errors while rendering.

## Files

```
all-cases-before.html   all-cases-after.html    the pair under test
generate.py             emits both files from one source (guarantees identical CSS)
evidence/
  all-cases-1-before.png   reference render of the before file
  all-cases-2-after.png    reference render of the after file
  all-cases-diff.png       the tool's HTML View output for the pair
  section-cols.png         close-up: a column added mid-table and a column removed mid-table
  section-cards.png        close-up: card added / removed / moved-and-edited / class-only change
  case2-reported-scenarios.png
                           the originally reported document, rendered after the fixes
```

Reference renders are captured so a rendering problem can be attributed: if a table looks ragged in
`all-cases-diff.png` but is uniform in both reference renders, the fault is in the diff, not the
fixture. Both reference renders are confirmed free of horizontal overflow with every table uniform
(before: 4/4/5/5/5/6 columns, after: 5/5/4/4/5/6).
