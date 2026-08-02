# 2 つ目のテストセット（バックエンド設計書）のジェネレータ。
#
# 1 つ目（generate.py / 資産台帳）とは HTML の書き方を意図的に変えてある。
# 同じ差分パターンでも、体裁が違うだけで壊れる実装は珍しくないため、
# 「どんな HTML が来ても持つか」を確かめるのがこのセットの役目。
#
#   - 暗い配色（診断色がダーク背景の上で読めるか）
#   - grid レイアウト＋上部の横並びナビ（1 つ目は flex＋左サイドナビ）
#   - <article> と <hr> で区切る（1 つ目は section をカード化）
#   - <thead> の無い表 / th scope="row" の行見出し / colspan・rowspan のある表
#   - <details><summary> / インライン SVG / <figure><figcaption> / abbr[title]
#
# before / after を同じソースから吐くので <style> のバイト一致は構造的に保証される。
import io, os

OUT = os.path.dirname(os.path.abspath(__file__))

CSS = """
:root{
  --bg:#12151a; --panel:#191d24; --fg:#dde3ea; --dim:#8b95a3; --line:#2a313b;
  --key:#7fd1c1; --accent:#6ea8fe; --warn:#e8b339; --bad:#f0736a; --ok:#5fd48a;
  --mono:"SFMono-Regular",Menlo,Consolas,"Courier New",monospace;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--fg);
  font:14px/1.8 "Hiragino Kaku Gothic ProN","Yu Gothic","Noto Sans JP",sans-serif;
}
.topbar{
  position:sticky; top:0; z-index:5; background:#0d1015; border-bottom:1px solid var(--line);
  padding:.9rem 1.6rem; display:grid; grid-template-columns:1fr auto; align-items:center; gap:1rem;
}
.topbar .title{font-size:1.02rem; font-weight:700; letter-spacing:.02em}
.topbar .rev{font-family:var(--mono); font-size:.78rem; color:var(--dim)}
nav.sitenav{display:flex; flex-wrap:wrap; gap:.15rem; padding:.5rem 1.6rem; background:#0d1015; border-bottom:1px solid var(--line)}
nav.sitenav a{
  display:inline-block; padding:.28rem .7rem; border-radius:4px; text-decoration:none;
  color:var(--dim); font-size:.8rem; border:1px solid transparent;
}
nav.sitenav a:hover{color:var(--fg); border-color:var(--line)}
.wrap{display:grid; grid-template-columns:minmax(0,1fr); max-width:1000px; margin:0 auto; padding:1.6rem}
article{padding:.2rem 0 1.4rem}
hr{border:0; border-top:1px solid var(--line); margin:1.6rem 0}
h2{margin:0 0 .25rem; font-size:1.05rem; color:var(--key); letter-spacing:.01em}
h3{margin:1.4rem 0 .4rem; font-size:.94rem; color:var(--fg)}
h4{margin:1rem 0 .3rem; font-size:.88rem; color:var(--fg)}
.note{margin:.1rem 0 1rem; color:var(--dim); font-size:.82rem}
p{margin:0 0 .85rem}
table{border-collapse:collapse; width:100%; font-size:.82rem; margin:.5rem 0 .3rem; background:var(--panel)}
th,td{border:1px solid var(--line); padding:.45rem .65rem; text-align:left; vertical-align:top}
th{color:var(--key); font-weight:600; white-space:nowrap}
th[scope="row"]{color:var(--fg); font-family:var(--mono); font-weight:500; width:1%}
td.mono,th.mono{font-family:var(--mono); font-size:.94em}
caption{caption-side:top; text-align:left; color:var(--dim); font-size:.78rem; padding:0 0 .35rem}
.tag{display:inline-block; padding:.02rem .45rem; border-radius:3px; font-size:.72rem; font-family:var(--mono)}
.tag.get{background:#12362e; color:var(--ok)}
.tag.post{background:#153050; color:var(--accent)}
.tag.del{background:#3a1e1c; color:var(--bad)}
.tag.new{background:#3a3116; color:var(--warn)}
.svc{border-left:2px solid var(--line); padding:.1rem 0 .1rem .9rem; margin:.6rem 0}
.svc h3{margin:0 0 .2rem}
.svc p{margin:0 0 .3rem; font-size:.84rem; color:#b9c2cd}
.svc .meta{font-family:var(--mono); font-size:.75rem; color:var(--dim)}
.flag{padding:.5rem .8rem; border:1px dashed var(--line); border-radius:4px; font-size:.84rem}
.flag[data-state="on"]{border-style:solid; border-color:var(--ok)}
ol.seq{margin:.4rem 0; padding-left:1.4rem}
ol.seq li{margin:.15rem 0}
ol.seq ol{margin:.2rem 0}
ol.run{margin:.4rem 0; padding-left:1.4rem}
ol.run li{margin:0 0 .8rem}
ol.run h4{margin:0 0 .2rem}
ol.run p{margin:0; font-size:.83rem; color:#b9c2cd}
details{border:1px solid var(--line); border-radius:4px; padding:.4rem .7rem; margin:.4rem 0; background:var(--panel)}
summary{cursor:default; font-size:.86rem; color:var(--key)}
details p{margin:.35rem 0 .1rem; font-size:.82rem; color:#b9c2cd}
pre{background:#0d1015; border:1px solid var(--line); border-radius:4px; padding:.8rem .9rem; overflow-x:auto; font-size:.78rem; line-height:1.65}
code{font-family:var(--mono)}
p code,li code,td code{background:#0d1015; border:1px solid var(--line); border-radius:3px; padding:0 .3rem; font-size:.92em}
blockquote{margin:.6rem 0; padding:.5rem .9rem; border-left:3px solid var(--key); background:var(--panel); font-size:.86rem}
blockquote cite{display:block; margin-top:.35rem; font-size:.76rem; color:var(--dim); font-style:normal}
figure{margin:.6rem 0}
figcaption{color:var(--dim); font-size:.78rem; margin-top:.35rem}
abbr[title]{border-bottom:1px dotted var(--dim); text-decoration:none}
.mark{background:#3a3116; padding:0 .2rem}
footer{padding:1.2rem 1.6rem 2.4rem; color:var(--dim); font-size:.78rem; border-top:1px solid var(--line)}
"""


# ---------- 部品 ----------
def rows_html(rows, tag='td', indent='        '):
    out = []
    for r in rows:
        cells = []
        for c in r:
            if isinstance(c, tuple):
                cells.append('<%s %s>%s</%s>' % (c[1], c[2], c[0], c[1]))
            else:
                cells.append('<%s>%s</%s>' % (tag, c, tag))
        out.append('<tr>%s</tr>' % ''.join(cells))
    return '\n'.join(indent + l for l in out)


def plain_table(tid, caption, header, rows, indent='        '):
    """thead を持たない表。見出し行も tbody の中に直接置く。"""
    lines = ['<table id="%s">' % tid]
    if caption:
        lines.append('  <caption>%s</caption>' % caption)
    lines.append('  <tr>%s</tr>' % ''.join('<th>%s</th>' % c for c in header))
    for r in rows:
        lines.append('  <tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r))
    lines.append('</table>')
    return '\n'.join(indent + l for l in lines)


def rowhead_table(tid, caption, header, rows, indent='        '):
    """1 列目が th scope="row" の行見出しになっている表。"""
    lines = ['<table id="%s">' % tid]
    if caption:
        lines.append('  <caption>%s</caption>' % caption)
    lines.append('  <thead><tr>%s</tr></thead>' % ''.join('<th>%s</th>' % c for c in header))
    lines.append('  <tbody>')
    for r in rows:
        cells = ['<th scope="row">%s</th>' % r[0]] + ['<td>%s</td>' % c for c in r[1:]]
        lines.append('    <tr>%s</tr>' % ''.join(cells))
    lines.append('  </tbody>')
    lines.append('</table>')
    return '\n'.join(indent + l for l in lines)


def article(sid, title, note, body):
    return '\n'.join([
        '      <article id="%s">' % sid,
        '        <h2>%s</h2>' % title,
        '        <p class="note">%s</p>' % note,
        body,
        '      </article>',
        '      <hr>',
    ])


def tag(kind, text):
    return '<span class="tag %s">%s</span>' % (kind, text)


# ---------- 各テストケース ----------

def sec_direction():
    b = '\n'.join([
        '        <p>この文書は <strong>BEFORE（旧・左ペインに入れる方）</strong> です。</p>',
        '        <p class="note">リビジョン r14 / 2026-07-30 承認前</p>',
    ])
    a = '\n'.join([
        '        <p>この文書は <strong>AFTER（新・右ペインに入れる方）</strong> です。</p>',
        '        <p class="note">リビジョン r15 / 2026-08-02 承認済</p>',
    ])
    return b, a


def sec_endpoints():
    # thead の無い表。途中に「認証」列が増える。
    hdr_b = ['メソッド', 'パス', '概要', '応答']
    hdr_a = ['メソッド', 'パス', '概要', '認証', '応答']
    rows_b = [
        [tag('get', 'GET'), '<code>/v1/orders</code>', '注文一覧の取得', '<code>200 OK</code>'],
        [tag('get', 'GET'), '<code>/v1/orders/{id}</code>', '注文の単体取得', '<code>200 OK</code>'],
        [tag('post', 'POST'), '<code>/v1/orders</code>', '注文の作成', '<code>201 Created</code>'],
        [tag('post', 'POST'), '<code>/v1/orders/{id}/cancel</code>', '注文のキャンセル', '<code>202 Accepted</code>'],
    ]
    auth = ['必須', '必須', '必須', '必須（管理者）']
    rows_a = [r[:3] + [a] + r[3:] for r, a in zip(rows_b, auth)]
    return (plain_table('t-endpoints', '公開 API 一覧', hdr_b, rows_b),
            plain_table('t-endpoints', '公開 API 一覧', hdr_a, rows_a))


def sec_errors():
    # th scope="row" の行見出しを持つ表。末尾の「旧コード」列がなくなる。
    hdr_b = ['エラーコード', 'HTTP', '意味', 'リトライ', '旧コード']
    hdr_a = ['エラーコード', 'HTTP', '意味', 'リトライ']
    rows_b = [
        ['ORD-4001', '400', 'リクエスト本文の検証に失敗', '不可', 'E1001'],
        ['ORD-4041', '404', '指定した注文が存在しない', '不可', 'E1004'],
        ['ORD-4091', '409', '注文の状態が遷移条件を満たさない', '不可', 'E1009'],
        ['ORD-5031', '503', '在庫サービスが応答しない', '可（指数バックオフ）', 'E1503'],
    ]
    rows_a = [r[:4] for r in rows_b]
    return (rowhead_table('t-errors', 'エラーコード一覧', hdr_b, rows_b),
            rowhead_table('t-errors', 'エラーコード一覧', hdr_a, rows_a))


def sec_schema():
    # colspan を含む表。列対応が取れないので位置合わせにフォールバックする経路。
    def build(rows):
        lines = ['<table id="t-schema">',
                 '  <caption>orders テーブル定義</caption>',
                 '  <tr><th colspan="2">列</th><th colspan="3">制約</th></tr>',
                 '  <tr><th>名称</th><th>型</th><th>NULL</th><th>既定値</th><th>備考</th></tr>']
        for r in rows:
            lines.append('  <tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r))
        lines.append('</table>')
        return '\n'.join('        ' + l for l in lines)
    rows_b = [
        ['<code>id</code>', '<code>bigint</code>', '不可', '—', '主キー'],
        ['<code>customer_id</code>', '<code>bigint</code>', '不可', '—', '外部キー'],
        ['<code>status</code>', '<code>varchar(16)</code>', '不可', "<code>'pending'</code>", '状態遷移は本文参照'],
        ['<code>total_amount</code>', '<code>decimal(12,2)</code>', '不可', '<code>0</code>', '税込'],
        ['<code>memo</code>', '<code>text</code>', '可', '<code>NULL</code>', '運用メモ'],
    ]
    rows_a = [
        ['<code>id</code>', '<code>bigint</code>', '不可', '—', '主キー'],
        ['<code>customer_id</code>', '<code>bigint</code>', '不可', '—', '外部キー'],
        ['<code>status</code>', '<code>varchar(24)</code>', '不可', "<code>'pending'</code>", '状態遷移は本文参照'],
        ['<code>total_amount</code>', '<code>decimal(12,2)</code>', '不可', '<code>0</code>', '税込'],
        ['<code>canceled_at</code>', '<code>timestamptz</code>', '可', '<code>NULL</code>', 'キャンセル日時'],
    ]
    return build(rows_b), build(rows_a)


def sec_limits():
    # rowspan を含む表。ここも列対応が取れない経路。
    def build(vals):
        lines = ['<table id="t-limits">',
                 '  <caption>レート制限</caption>',
                 '  <tr><th>区分</th><th>対象</th><th>上限</th><th>単位</th></tr>',
                 '  <tr><th rowspan="2" scope="row">一般</th><td>参照系</td><td>%s</td><td>req/min</td></tr>' % vals[0],
                 '  <tr><td>更新系</td><td>%s</td><td>req/min</td></tr>' % vals[1],
                 '  <tr><th rowspan="2" scope="row">管理者</th><td>参照系</td><td>%s</td><td>req/min</td></tr>' % vals[2],
                 '  <tr><td>更新系</td><td>%s</td><td>req/min</td></tr>' % vals[3],
                 '</table>']
        return '\n'.join('        ' + l for l in lines)
    return build(['600', '120', '1,200', '300']), build(['900', '180', '1,200', '300'])


def sec_audit():
    # よく似た行が並ぶ中で 1 行が消え、別の行の 1 セルだけが変わる。
    hdr = ['イベントID', '発生時刻', '主体', '種別', '対象', '結果']
    base = [
        ['EVT-20260801-0001', '00:00:12', 'batch@system', 'JOB_START', 'nightly-recalc', tag('get', 'OK')],
        ['EVT-20260801-0002', '00:03:40', 'batch@system', 'JOB_END', 'nightly-recalc', tag('get', 'OK')],
        ['EVT-20260801-0003', '01:15:07', 'svc-inventory', 'SYNC', 'stock-delta', tag('get', 'OK')],
        ['EVT-20260801-0004', '02:00:00', 'batch@system', 'JOB_START', 'invoice-export', tag('get', 'OK')],
        ['EVT-20260801-0005', '02:04:55', 'batch@system', 'JOB_END', 'invoice-export', tag('get', 'OK')],
        ['EVT-20260801-0006', '03:12:31', 'svc-payment', 'CALLBACK', 'settle-batch', tag('get', 'OK')],
        ['EVT-20260801-0007', '04:00:00', 'batch@system', 'JOB_START', 'stale-cleanup', tag('get', 'OK')],
        ['EVT-20260801-0008', '04:00:31', 'batch@system', 'JOB_END', 'stale-cleanup', tag('get', 'OK')],
    ]
    rows_b = [list(r) for r in base]
    rows_a = [list(r) for r in base]
    del rows_a[5]                              # svc-payment の CALLBACK 行を削除
    rows_a[2][5] = tag('del', 'FAILED')        # svc-inventory の SYNC 行の結果を変更
    return (plain_table('t-audit', '夜間バッチ監査ログ（抜粋）', hdr, rows_b),
            plain_table('t-audit', '夜間バッチ監査ログ（抜粋）', hdr, rows_a))


def sec_services():
    # class 名を持たない <article> ではなく、.svc を持つ div。1 つ削除・1 つ追加・
    # 1 つは位置が動いたうえ本文も変わる。
    def svc(name, desc, meta):
        return '\n'.join('        ' + l for l in [
            '<div class="svc">',
            '  <h3>%s</h3>' % name,
            '  <p>%s</p>' % desc,
            '  <div class="meta">%s</div>' % meta,
            '</div>',
        ])
    b = '\n'.join([
        svc('inventory-service', '在庫の引当と解放を担当する。注文確定時に同期で呼び出す。', 'gRPC / SLO 99.9% / owner: 在庫チーム'),
        svc('payment-service', '決済の与信と確定を担当する。タイムアウトは 5 秒。', 'REST / SLO 99.95% / owner: 決済チーム'),
        svc('legacy-mailer', '注文確認メールを送る旧基盤。移行対象。', 'SMTP / SLO なし / owner: 基盤チーム'),
        svc('search-indexer', '注文の検索インデックスを非同期で更新する。', 'Kafka / SLO 99.5% / owner: 検索チーム'),
    ])
    a = '\n'.join([
        svc('inventory-service', '在庫の引当と解放を担当する。注文確定時に同期で呼び出す。', 'gRPC / SLO 99.9% / owner: 在庫チーム'),
        svc('search-indexer', '注文の検索インデックスを非同期で更新する。', 'Kafka / SLO 99.5% / owner: 検索チーム'),
        svc('payment-service', '決済の与信と確定を担当する。タイムアウトは 3 秒に短縮した。', 'REST / SLO 99.99% / owner: 決済チーム'),
        svc('notification-service', '注文確認とキャンセル通知をまとめて送る新基盤。', 'REST / SLO 99.9% / owner: 通知チーム'),
    ])
    return b, a


def sec_flag():
    # 表示テキストは完全に同一で、data-state 属性と class だけが変わる。
    body = ('<p>注文キャンセルの非同期化。有効化するとキャンセル要求を'
            'キューに積み、確定を後続のワーカーに委ねる。</p>')
    b = '        <div class="flag" data-state="off">\n          %s\n        </div>' % body
    a = '        <div class="flag" data-state="on">\n          %s\n        </div>' % body
    return b, a


def sec_sequence():
    b = """        <ol class="seq">
          <li>API ゲートウェイがトークンを検証する
            <ol>
              <li>署名の検証</li>
              <li>有効期限の確認</li>
              <li>スコープの確認</li>
            </ol>
          </li>
          <li>注文サービスがリクエストを受け取る</li>
          <li>在庫サービスに引当を依頼する
            <ol>
              <li>在庫数の確認</li>
              <li>引当レコードの作成</li>
            </ol>
          </li>
          <li>決済サービスに与信を依頼する</li>
          <li>注文レコードを確定して応答する</li>
        </ol>"""
    a = """        <ol class="seq">
          <li>API ゲートウェイがトークンを検証する
            <ol>
              <li>署名の検証</li>
              <li>スコープの確認</li>
              <li>有効期限の確認</li>
            </ol>
          </li>
          <li>注文サービスがリクエストを受け取る
            <ol>
              <li>冪等キーの重複確認</li>
            </ol>
          </li>
          <li>決済サービスに与信を依頼する</li>
          <li>在庫サービスに引当を依頼する
            <ol>
              <li>在庫数の確認</li>
              <li>引当レコードの作成</li>
            </ol>
          </li>
          <li>注文レコードを確定して応答する</li>
        </ol>"""
    return b, a


def sec_runbook():
    step = lambda h, p: '          <li>\n            <h4>%s</h4>\n            <p>%s</p>\n          </li>' % (h, p)
    s_detect = step('異常の検知', '在庫引当の失敗率が 5 分平均で 1% を超えるとアラートが発火する。')
    s_scope = step('影響範囲の確認', 'ダッシュボードで失敗している注文の件数と対象リージョンを確認する。')
    s_flag = step('フラグの切り戻し', '非同期キャンセルのフィーチャーフラグを無効化し、同期処理に戻す。')
    s_notify = step('関係者への連絡', '決済チームと在庫チームに状況を共有し、判断者を明確にする。')
    s_check_b = step('復旧確認', '失敗率が 5 分平均で 0.1% を下回ることを確認する。')
    s_check_a = step('復旧確認', '失敗率が 5 分平均で 0.1% を下回り、キューの滞留がゼロになることを確認する。'
                                '確認した時刻をインシデントチケットに記録すること。')
    b = '        <ol class="run">\n' + '\n'.join([s_detect, s_flag, s_scope, s_notify, s_check_b]) + '\n        </ol>'
    a = '        <ol class="run">\n' + '\n'.join([s_detect, s_scope, s_notify, s_flag, s_check_a]) + '\n        </ol>'
    return b, a


def sec_terms():
    d = lambda s, p: '        <details>\n          <summary>%s</summary>\n          <p>%s</p>\n        </details>' % (s, p)
    idem = d('冪等キー', 'クライアントが生成する一意な文字列。同じキーでの再送は同じ結果を返し、二重に注文が作られない。')
    saga = d('Saga', '複数サービスにまたがる更新を、補償トランザクションで巻き戻せるように分割する方式。')
    outbox = d('Outbox', 'DB の更新と同一トランザクションでイベント行を書き、別プロセスが配信する方式。')
    bulk_b = d('一括確定', '複数の注文をまとめて確定する社内向けの操作。')
    circuit = d('サーキットブレーカ', '連続失敗が閾値を超えた依存先への呼び出しを一定時間止める仕組み。')
    saga_a = d('Saga', '複数サービスにまたがる更新を、補償トランザクションで巻き戻せるように分割する方式。'
                       '本設計では注文・在庫・決済の 3 者にまたがる確定処理に適用する。')
    b = '\n'.join([idem, saga, outbox, bulk_b, circuit])
    a = '\n'.join([idem, saga_a, outbox, circuit, d('デッドレターキュー', '規定回数の再試行に失敗したメッセージを退避させる先。')])
    return b, a


def sec_overview():
    p = lambda s: '        <p>%s</p>' % s
    b = '\n'.join([
        p('本書は注文管理サービス（<code>order-service</code>）のバックエンド設計を定める。'
          '対象は注文の作成・参照・キャンセルであり、返品と再注文は次期スコープとする。'),
        p('注文の確定は在庫と決済の 2 つの外部サービスに依存する。いずれかが失敗した場合は'
          '補償処理で巻き戻し、注文レコードは作成しない方針とする。'),
        p('可用性目標は月間 99.9% とし、計画停止は含めない。'
          '応答時間は参照系で p95 200ms、更新系で p95 600ms を目標とする。'),
        p('データストアは PostgreSQL 16 を用いる。読み取り負荷が高い一覧取得のみ'
          'リードレプリカに振り分け、整合性が要る参照はプライマリに向ける。'),
        p('本設計は 2026 年 9 月のリリースを前提としている。'
          '移行期間中は旧バッチとの二重稼働を許容する。'),
    ])
    a = '\n'.join([
        p('本書は注文管理サービス（<code>order-service</code>）のバックエンド設計を定める。'
          '対象は注文の作成・参照・キャンセルであり、返品と再注文は次期スコープとする。'),
        p('注文の確定は在庫と決済の 2 つの外部サービスに依存する。いずれかが失敗した場合は'
          '補償処理で巻き戻し、注文レコードは作成しない方針とする。'),
        p('可用性目標は月間 99.95% とし、計画停止は含めない。'
          '応答時間は参照系で p95 200ms、更新系で p95 400ms を目標とする。'),
        p('データストアは PostgreSQL 16 を用いる。読み取り負荷が高い一覧取得のみ'
          'リードレプリカに振り分け、整合性が要る参照はプライマリに向ける。'),
        p('本設計は 2026 年 10 月のリリースを前提としている。'
          '移行期間中は旧バッチとの二重稼働を許容する。'),
    ])
    return b, a


def sec_inline():
    # 可視テキストは完全に同一。abbr の title、リンク先、強調の付け外しだけが違う。
    b = '\n'.join([
        '        <p>本サービスの <abbr title="Service Level Objective">SLO</abbr> は',
        '        月間 99.9% とする。詳細は <a href="/docs/r14/slo">SLO 定義</a> を参照。</p>',
        '        <p>障害時の一次対応は <em>オンコール担当</em> が行う。手順は運用手順の節にまとめている。</p>',
    ])
    a = '\n'.join([
        '        <p>本サービスの <abbr title="Service Level Objective（サービスレベル目標）">SLO</abbr> は',
        '        月間 99.9% とする。詳細は <a href="/docs/r15/slo">SLO 定義</a> を参照。</p>',
        '        <p>障害時の一次対応は <strong>オンコール担当</strong> が行う。手順は運用手順の節にまとめている。</p>',
    ])
    return b, a


def sec_payload():
    head = '        <pre><code>'
    tail = '</code></pre>'
    b_lines = [
        'POST /v1/orders HTTP/1.1',
        'Content-Type: application/json',
        'Idempotency-Key: 5f3c1a9e-2b77-4d0e-9a11-6c2f0b8d4e33',
        '',
        '{',
        '  "customer_id": 90210,',
        '  "items": [',
        '    { "sku": "SKU-1188", "quantity": 2 },',
        '    { "sku": "SKU-2043", "quantity": 1 }',
        '  ],',
        '  "coupon_code": "SUMMER2026",',
        '  "note": "gift wrapping"',
        '}',
    ]
    a_lines = [
        'POST /v1/orders HTTP/1.1',
        'Content-Type: application/json',
        'Idempotency-Key: 5f3c1a9e-2b77-4d0e-9a11-6c2f0b8d4e33',
        '',
        '{',
        '  "customer_id": 90210,',
        '  "items": [',
        '    { "sku": "SKU-1188", "quantity": 3 },',
        '    { "sku": "SKU-2043", "quantity": 1 }',
        '  ],',
        '  "coupon_code": "AUTUMN2026",',
        '  "callback_url": "https://hooks.example.internal/orders",',
        '}',
    ]
    esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return head + '\n'.join(esc(l) for l in b_lines) + tail, head + '\n'.join(esc(l) for l in a_lines) + tail


def sec_note():
    b = '\n'.join([
        '        <blockquote>',
        '          在庫の引当は注文確定の同期処理に含める。非同期にすると、在庫が無い注文を',
        '          受理してしまい、後続の補償処理が複雑になるためである。',
        '          <cite>設計方針 第3章 / 2026-07-30 レビュー</cite>',
        '        </blockquote>',
    ])
    a = '\n'.join([
        '        <blockquote>',
        '          在庫の引当は注文確定の同期処理に含める。非同期にすると、在庫が無い注文を',
        '          受理してしまい、後続の補償処理が複雑になるためである。キャンセルのみ',
        '          非同期化の対象とする。',
        '          <cite>設計方針 第3章 / 2026-08-02 レビュー</cite>',
        '        </blockquote>',
    ])
    return b, a


def sec_diagram():
    # インライン SVG。ラベルの文言と図形が変わる。
    def svg(label3, extra):
        parts = [
            '<figure>',
            '  <svg id="d-arch" viewBox="0 0 620 130" width="100%" height="130" role="img" aria-label="構成図">',
            '    <rect x="8" y="34" width="130" height="52" rx="6" fill="#191d24" stroke="#2a313b"></rect>',
            '    <text x="73" y="65" fill="#dde3ea" font-size="12" text-anchor="middle">API Gateway</text>',
            '    <rect x="178" y="34" width="130" height="52" rx="6" fill="#191d24" stroke="#2a313b"></rect>',
            '    <text x="243" y="65" fill="#dde3ea" font-size="12" text-anchor="middle">order-service</text>',
            '    <rect x="348" y="34" width="130" height="52" rx="6" fill="#191d24" stroke="#2a313b"></rect>',
            '    <text x="413" y="65" fill="#dde3ea" font-size="12" text-anchor="middle">%s</text>' % label3,
        ]
        parts += extra
        parts += [
            '    <line x1="138" y1="60" x2="178" y2="60" stroke="#8b95a3" stroke-width="1"></line>',
            '    <line x1="308" y1="60" x2="348" y2="60" stroke="#8b95a3" stroke-width="1"></line>',
            '  </svg>',
            '  <figcaption>注文確定の同期経路（r14 時点）</figcaption>',
            '</figure>',
        ]
        return '\n'.join('        ' + l for l in parts)
    b = svg('inventory-service', [])
    a = svg('inventory-service', [
        '    <rect x="518" y="34" width="94" height="52" rx="6" fill="#191d24" stroke="#5fd48a"></rect>',
        '    <text x="565" y="65" fill="#dde3ea" font-size="12" text-anchor="middle">outbox</text>',
    ]).replace('（r14 時点）', '（r15 時点）')
    return b, a


def sec_figure():
    # figure の中に表を置き、キャプションだけを書き換える。
    def build(cap, ttl):
        lines = ['<figure>',
                 '  <table id="t-slo">',
                 '    <tr><th>指標</th><th>目標</th><th>測定方法</th></tr>',
                 '    <tr><td>可用性</td><td>%s</td><td>合成監視の成功率（1 分間隔）</td></tr>' % ttl,
                 '    <tr><td>参照系 p95</td><td>200ms</td><td>ロードバランサのアクセスログ</td></tr>',
                 '    <tr><td>更新系 p95</td><td>600ms</td><td>ロードバランサのアクセスログ</td></tr>',
                 '  </table>',
                 '  <figcaption>%s</figcaption>' % cap,
                 '</figure>']
        return '\n'.join('        ' + l for l in lines)
    return (build('非機能要件の測定方法（承認前）', '99.9%'),
            build('非機能要件の測定方法（2026-08-02 承認済）', '99.95%'))


def sec_hlevel():
    b = '\n'.join([
        '        <h4>再試行方針</h4>',
        '        <p>依存先の 5xx と接続タイムアウトのみ再試行の対象とする。最大 3 回、指数バックオフとする。</p>',
        '        <h4>打ち切り条件</h4>',
        '        <p>合計待ち時間が 10 秒を超えた場合は再試行を打ち切り、呼び出し元に 503 を返す。</p>',
    ])
    a = '\n'.join([
        '        <h3>再試行方針</h3>',
        '        <p>依存先の 5xx と接続タイムアウトのみ再試行の対象とする。最大 3 回、指数バックオフとする。</p>',
        '        <h4>打ち切り条件</h4>',
        '        <p>合計待ち時間が 10 秒を超えた場合は再試行を打ち切り、呼び出し元に 503 を返す。</p>',
    ])
    return b, a


def sec_swap():
    scale = '\n'.join([
        '        <h3>スケーリング</h3>',
        '        <p>CPU 使用率 60% を目標に水平スケールする。最小 3 台、最大 20 台とする。</p>',
    ])
    deploy = '\n'.join([
        '        <h3>デプロイ</h3>',
        '        <p>Blue-Green 方式とし、切り替え後 30 分は旧系を待機させる。</p>',
    ])
    return scale + '\n' + deploy, deploy + '\n' + scale


LEGACY = article('sec-legacy-batch', '旧バッチ連携（廃止予定）',
                 '移行完了までの暫定仕様。',
                 '        <p>旧注文バッチは 1 日 1 回 CSV を出力し、共有ストレージ経由で連携している。'
                 '移行完了後に停止する。</p>')
NEWSEC = article('sec-webhook', 'Webhook 通知',
                 '注文状態の変化を外部へ通知する。',
                 '        <p>注文の確定とキャンセルを Webhook で通知する。署名は HMAC-SHA256 とし、'
                 '再送は最大 5 回、指数バックオフとする。</p>')


CASES = [
    ('sec-direction', 'diff の向き確認', 'BEFORE が赤、AFTER が緑になっていれば左右の入れ方が正しい。', sec_direction),
    ('sec-overview', '概要', '5 段落のうち BEFORE と AFTER で違うのは 4 箇所だけ。過剰にマークしないことの確認。', sec_overview),
    ('sec-endpoints', 'API エンドポイント一覧', 'thead の無い表。BEFORE は4列、AFTER は「概要」と「応答」の間に「認証」列が増えて5列。', sec_endpoints),
    ('sec-errors', 'エラーコード一覧', '1 列目が th scope="row" の表。BEFORE は5列、AFTER は末尾の「旧コード」列が無くなって4列。', sec_errors),
    ('sec-schema', 'テーブル定義', 'colspan を含む表。BEFORE にだけ memo 行、AFTER にだけ canceled_at 行。status の型も違う。', sec_schema),
    ('sec-limits', 'レート制限', 'rowspan を含む表。一般区分の 2 つの上限値だけが違う。', sec_limits),
    ('sec-audit', '監査ログ', 'BEFORE は8行、AFTER は svc-payment の CALLBACK 行が無くて7行。svc-inventory の結果も違う。', sec_audit),
    ('sec-services', '依存サービス', 'BEFORE にだけ legacy-mailer、AFTER にだけ notification-service。payment-service は位置も本文も違う。', sec_services),
    ('sec-flag', 'フィーチャーフラグ', 'テキストは完全に同一。data-state が BEFORE は off、AFTER は on。', sec_flag),
    ('sec-sequence', '処理シーケンス', '入れ子の ol。BEFORE と AFTER で順序と階層が違う。AFTER にだけ冪等キーの重複確認。', sec_sequence),
    ('sec-runbook', '運用手順', '「フラグの切り戻し」が BEFORE では2番目、AFTER では4番目。「復旧確認」の説明文も違う。', sec_runbook),
    ('sec-terms', '用語', 'details/summary。BEFORE にだけ「一括確定」、AFTER にだけ「デッドレターキュー」。Saga の説明文も違う。', sec_terms),
    ('sec-inline', 'インライン記法・属性のみ', '可視テキストは BEFORE と AFTER で完全に同一。abbr の title、リンク先、em/strong だけが違う。', sec_inline),
    ('sec-payload', 'リクエスト例', '1行が違い、AFTER にだけある行と BEFORE にだけある行が1本ずつ。インデントが崩れないことの確認。', sec_payload),
    ('sec-note', '設計上の注意', 'blockquote と cite。追記された一文と日付が違う。', sec_note),
    ('sec-diagram', '構成図', 'インライン SVG。AFTER にだけ outbox の箱があり、キャプションのリビジョンも違う。', sec_diagram),
    ('sec-figure', '非機能要件', 'figure の中の表。可用性の目標値とキャプションが違う。', sec_figure),
    ('sec-hlevel', '再試行', 'テキストは同一。「再試行方針」が BEFORE は h4、AFTER は h3。', sec_hlevel),
    ('sec-swap', 'デプロイとスケーリング', '2つの小見出しブロックの前後が BEFORE と AFTER で逆。', sec_swap),
]

NAV_BEFORE = [
    ('sec-overview', '概要'), ('sec-endpoints', 'API'), ('sec-errors', 'エラー'),
    ('sec-schema', 'スキーマ'), ('sec-services', '依存'), ('sec-sequence', 'シーケンス'),
    ('sec-runbook', '運用'), ('sec-terms', '用語'), ('sec-legacy-batch', '旧バッチ連携'),
]
NAV_AFTER = [
    ('sec-overview', '概要'), ('sec-endpoints', 'API'), ('sec-errors', 'エラーコード'),
    ('sec-schema', 'スキーマ'), ('sec-services', '依存'), ('sec-sequence', 'シーケンス'),
    ('sec-runbook', '運用'), ('sec-terms', '用語'), ('sec-webhook', 'Webhook'),
]


def build(which):
    idx = 0 if which == 'before' else 1
    nav_items = NAV_BEFORE if which == 'before' else NAV_AFTER
    nav = '\n'.join('      <a href="#%s">%s</a>' % (h, t) for h, t in nav_items)

    parts = [article(sid, title, note, fn()[idx]) for sid, title, note, fn in CASES]
    parts.append(LEGACY if which == 'before' else NEWSEC)

    rev = 'r14' if which == 'before' else 'r15'
    date = '2026-07-30' if which == 'before' else '2026-08-02'
    state = '承認前' if which == 'before' else '承認済'

    doc = []
    doc.append('<!DOCTYPE html>')
    doc.append('<html lang="ja">')
    doc.append('<head>')
    doc.append('<meta charset="utf-8">')
    doc.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    doc.append('<title>注文管理サービス バックエンド設計書</title>')
    doc.append('<sty' + 'le>')
    doc.append(CSS.strip())
    doc.append('</sty' + 'le>')
    doc.append('</he' + 'ad>')
    doc.append('<bo' + 'dy>')
    doc.append('<div class="topbar">')
    doc.append('  <div class="title">注文管理サービス <code>order-service</code> バックエンド設計書</div>')
    doc.append('  <div class="rev">DES-ORD-2026 / %s / %s / %s</div>' % (rev, date, state))
    doc.append('</div>')
    doc.append('<nav class="sitenav">')
    doc.append(nav)
    doc.append('</nav>')
    doc.append('<div class="wrap">')
    doc.append('  <main>')
    doc.extend(parts)
    doc.append('  </main>')
    doc.append('</div>')
    doc.append('<footer>社内限定 / 問い合わせ: order-platform@example.internal</footer>')
    doc.append('</bo' + 'dy>')
    doc.append('</html>')
    return '\n'.join(doc) + '\n'


if __name__ == '__main__':
    for which in ('before', 'after'):
        path = os.path.join(OUT, 'backend-design-%s.html' % which)
        io.open(path, 'w', encoding='utf-8').write(build(which))
        print('wrote', path, len(build(which)), 'bytes')
