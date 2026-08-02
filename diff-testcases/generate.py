# diff-testcases を 1 セットに統合するジェネレータ。
#
# before / after を同じソースから吐くので <style> のバイト一致が構造的に保証される。
# 各テストケースは 1 つの <section> で、id を持ち、その節の中だけで完結した
# 変更パターンを表現する。判定ハーネスは id 単位でアサーションを書く。
import io, os

OUT = os.path.dirname(os.path.abspath(__file__))

CSS = """
:root{
  --bg:#f7f7f5; --fg:#22252a; --muted:#6b7280; --line:#d8d8d3;
  --accent:#1f6f5c; --accent-weak:#e6f0ec; --warn:#b45309; --bad:#b91c1c; --ok:#166534;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--fg);
  font:15px/1.75 "Hiragino Kaku Gothic ProN","Yu Gothic","Noto Sans JP",sans-serif;
}
.page{max-width:1080px;margin:0 auto;padding:0 0 4rem}
.hero{background:var(--accent);color:#fff;padding:2rem 2.5rem}
.hero h1{margin:0 0 .5rem;font-size:1.6rem;letter-spacing:.01em}
.hero .meta{font-size:.85rem;opacity:.9;display:flex;gap:1.5rem;flex-wrap:wrap}
.layout{display:flex;gap:2rem;padding:2rem 2.5rem 0;align-items:flex-start}
nav.toc{flex:0 0 220px;position:sticky;top:1rem;background:#fff;border:1px solid var(--line);border-radius:6px;padding:1rem}
nav.toc .toc-title{font-size:.8rem;color:var(--muted);letter-spacing:.08em;margin-bottom:.6rem}
nav.toc ul{list-style:none;margin:0;padding:0}
nav.toc li{margin:0 0 .35rem}
nav.toc a{color:var(--fg);text-decoration:none;font-size:.88rem;display:block;padding:.25rem .4rem;border-radius:4px}
nav.toc a:hover{background:var(--accent-weak)}
main{flex:1 1 auto;min-width:0}
section{background:#fff;border:1px solid var(--line);border-radius:6px;padding:1.4rem 1.6rem;margin:0 0 1.5rem}
section h2{margin:0 0 .2rem;font-size:1.12rem;color:var(--accent)}
section h3{margin:1.2rem 0 .4rem;font-size:.98rem}
section .lead{margin:.2rem 0 1rem;color:var(--muted);font-size:.86rem}
p{margin:0 0 .9rem}
table{border-collapse:collapse;width:100%;font-size:.88rem;margin:.4rem 0 .2rem}
th,td{border:1px solid var(--line);padding:.5rem .7rem;text-align:left;vertical-align:top}
thead th{background:var(--accent-weak);font-weight:600;white-space:nowrap}
tbody tr:nth-child(even){background:#fbfbfa}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.badge{display:inline-block;padding:.1rem .55rem;border-radius:999px;font-size:.76rem;font-weight:600}
.badge.ok{background:#dcfce7;color:var(--ok)}
.badge.warn{background:#fef3c7;color:var(--warn)}
.badge.bad{background:#fee2e2;color:var(--bad)}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:.9rem;margin:.6rem 0 .2rem}
.card{border:1px solid var(--line);border-radius:6px;padding:.9rem 1rem;background:#fff}
.card .head{display:flex;justify-content:space-between;align-items:center;gap:.6rem;margin-bottom:.4rem}
.card h4{margin:0;font-size:.95rem}
.card .desc{margin:0 0 .5rem;font-size:.86rem;color:#3f4550}
.card .foot{display:flex;justify-content:space-between;font-size:.78rem;color:var(--muted)}
.card.done{background:#f4f8f6;border-color:var(--accent)}
.card.done h4::after{content:"完了";margin-left:.5rem;font-size:.7rem;color:var(--accent)}
ul.tree{margin:.4rem 0;padding-left:1.2rem}
ul.tree ul,ul.tree ol{margin:.25rem 0}
ol.steps{margin:.4rem 0;padding-left:1.3rem}
ol.steps li{margin:0 0 .7rem}
ol.steps h3{margin:0 0 .2rem;font-size:.92rem}
ol.steps p{margin:0;font-size:.86rem;color:#3f4550}
dl.glossary{margin:.4rem 0}
dl.glossary dt{font-weight:600;margin-top:.7rem;font-size:.9rem}
dl.glossary dd{margin:.15rem 0 0;font-size:.86rem;color:#3f4550}
pre{background:#1e2228;color:#e6e6e6;border-radius:6px;padding:.9rem 1rem;overflow-x:auto;font-size:.82rem;line-height:1.6}
code{font-family:"SFMono-Regular",Menlo,Consolas,monospace}
p code{background:#eceae5;padding:.05rem .35rem;border-radius:3px;font-size:.85em}
blockquote{margin:.6rem 0;padding:.6rem 1rem;border-left:3px solid var(--accent);background:var(--accent-weak);font-size:.9rem}
blockquote .attrib{display:block;margin-top:.4rem;font-size:.8rem;color:var(--muted)}
.highlight{background:#fef08a;padding:0 .15rem}
footer{padding:1.2rem 2.5rem;color:var(--muted);font-size:.82rem}
"""


# ---------- 部品 ----------
def table(tid, header, rows, numeric=()):
    th = ''.join('<th>%s</th>' % c for c in header)
    out = ['<table id="%s">' % tid, '<thead><tr>%s</tr></thead>' % th, '<tbody>']
    for r in rows:
        tds = []
        for i, c in enumerate(r):
            cls = ' class="num"' if i in numeric else ''
            tds.append('<td%s>%s</td>' % (cls, c))
        out.append('<tr>%s</tr>' % ''.join(tds))
    out += ['</tbody>', '</table>']
    return '\n'.join('        ' + l for l in out)


def badge(kind, text):
    return '<span class="badge %s">%s</span>' % (kind, text)


def card(title, badge_kind, badge_text, desc, owner, date, cls='card'):
    return '\n'.join('        ' + l for l in [
        '<div class="%s">' % cls,
        '  <div class="head"><h4>%s</h4>%s</div>' % (title, badge(badge_kind, badge_text)),
        '  <p class="desc">%s</p>' % desc,
        '  <div class="foot"><span>%s</span><span>%s</span></div>' % (owner, date),
        '</div>',
    ])


def section(sid, title, lead, body):
    return '\n'.join([
        '      <section id="%s">' % sid,
        '        <h2>%s</h2>' % title,
        '        <p class="lead">%s</p>' % lead,
        body,
        '      </section>',
    ])


# ---------- 各テストケース ----------
# それぞれ (before_body, after_body) を返す。

def sec_col_add_tail():
    hdr_b = ['資産番号', '品目', '設置場所', '数量']
    hdr_a = ['資産番号', '品目', '設置場所', '数量', '備考']
    rows_b = [
        ['AST-0101', 'ノートPC（ThinkPad X1）', '3F開発室', '12'],
        ['AST-0102', '24型モニター', '3F開発室', '18'],
        ['AST-0103', 'レーザープリンター', '3F事務エリア', '2'],
        ['AST-0104', '会議室用ディスプレイ', '4F大会議室', '3'],
    ]
    notes = ['更新対象', '', '保守契約あり', '']
    rows_a = [r + [n] for r, n in zip(rows_b, notes)]
    b = table('t-col-add-tail', hdr_b, rows_b, numeric={3})
    a = table('t-col-add-tail', hdr_a, rows_a, numeric={3})
    return b, a


def sec_col_add_mid():
    hdr_b = ['資産番号', '品目', '設置場所', '数量']
    hdr_a = ['資産番号', '品目', '設置場所', '管理担当', '数量']
    rows_b = [
        ['AST-0201', 'デスクトップPC', '2F営業部', '9'],
        ['AST-0202', '複合機（コピー機）', '2F受付', '1'],
        ['AST-0203', 'UPS装置', '1Fサーバー室', '2'],
        ['AST-0204', 'シュレッダー', '2F事務エリア', '3'],
    ]
    owners = ['情報システム課', '総務課', '情報システム課', '総務課']
    rows_a = [r[:3] + [o, r[3]] for r, o in zip(rows_b, owners)]
    b = table('t-col-add-mid', hdr_b, rows_b, numeric={3})
    a = table('t-col-add-mid', hdr_a, rows_a, numeric={4})
    return b, a


def sec_col_del_mid():
    hdr_b = ['資産番号', '品目', '取得年度', '設置場所', '数量']
    hdr_a = ['資産番号', '品目', '設置場所', '数量']
    rows_b = [
        ['AST-0301', 'サーバーラック', '2021年度', '1Fサーバー室', '2'],
        ['AST-0302', 'ネットワークスイッチ', '2022年度', '1Fサーバー室', '6'],
        ['AST-0303', '無線アクセスポイント', '2023年度', '各フロア', '14'],
        ['AST-0304', 'テープバックアップ装置', '2020年度', '1Fサーバー室', '1'],
    ]
    rows_a = [[r[0], r[1], r[3], r[4]] for r in rows_b]
    b = table('t-col-del-mid', hdr_b, rows_b, numeric={4})
    a = table('t-col-del-mid', hdr_a, rows_a, numeric={3})
    return b, a


def sec_col_del_tail():
    hdr_b = ['資産番号', '品目', '設置場所', '数量', '旧管理番号']
    hdr_a = ['資産番号', '品目', '設置場所', '数量']
    rows_b = [
        ['AST-0401', 'プロジェクター', '4F大会議室', '1', 'OLD-77-A'],
        ['AST-0402', 'ホワイトボード', '4F大会議室', '4', 'OLD-77-B'],
        ['AST-0403', '書庫キャビネット', '2F事務エリア', '8', 'OLD-52-C'],
        ['AST-0404', '応接テーブル', '5F応接室', '2', 'OLD-31-D'],
    ]
    rows_a = [r[:4] for r in rows_b]
    b = table('t-col-del-tail', hdr_b, rows_b, numeric={3})
    a = table('t-col-del-tail', hdr_a, rows_a, numeric={3})
    return b, a


def sec_row_churn():
    hdr = ['プラン', '月額', '年額', '上限ユーザー', 'サポート']
    rows_b = [
        ['Lite', '$290', '$2,800', '5ユーザー', 'メールのみ'],
        ['Standard', '$780', '$8,000', '20ユーザー', 'メール・チャット'],
        ['Classic' + badge('warn', '受付終了'), '$450', '$4,500', '10ユーザー', 'メールのみ'],
        ['Business', '$1,980', '$20,000', '無制限', 'チャット・電話'],
    ]
    rows_a = [
        ['Lite', '$350', '$3,600', '5ユーザー', 'メールのみ'],
        ['Standard', '$780', '$8,400', '25ユーザー', 'メール・チャット'],
        ['Pro Plus' + badge('ok', '新設'), '$1,280', '$13,000', '35ユーザー', 'チャット・電話'],
        ['Business', '$2,180', '$22,000', '無制限', 'チャット・電話'],
    ]
    b = table('t-row-churn', hdr, rows_b, numeric={1, 2})
    a = table('t-row-churn', hdr, rows_a, numeric={1, 2})
    return b, a


def sec_lookalike():
    hdr = ['ログID', '時刻', '利用者', '操作', '対象', '結果']
    base = [
        ['LOG-0801-090112', '09:01:12', 'yamada.t', 'ログイン', '-', badge('ok', '成功')],
        ['LOG-0801-091003', '09:10:03', 'suzuki.m', 'ログイン', '-', badge('ok', '成功')],
        ['LOG-0801-094530', '09:45:30', 'sato.k', 'ログイン', '-', badge('ok', '成功')],
        ['LOG-0801-101245', '10:12:45', 'tanaka.r', '設定変更', '権限設定', badge('ok', '成功')],
        ['LOG-0801-103311', '10:33:11', 'ito.h', 'ログイン', '-', badge('ok', '成功')],
        ['LOG-0801-110850', '11:08:50', 'yamada.t', 'ファイル出力', '月次レポート', badge('ok', '成功')],
        ['LOG-0801-114122', '11:41:22', 'tanaka.r', 'ログイン', '-', badge('bad', '失敗')],
        ['LOG-0801-114140', '11:41:40', 'tanaka.r', 'ログイン', '-', badge('ok', '成功')],
    ]
    rows_b = [list(r) for r in base]
    rows_a = [list(r) for r in base]
    del rows_a[2]                                  # sato.k のログイン行を削除
    rows_a[2][5] = badge('bad', '失敗')            # tanaka.r の設定変更行の結果を変更（削除後は index 2）
    b = table('t-lookalike', hdr, rows_b)
    a = table('t-lookalike', hdr, rows_a)
    return b, a


def sec_cards():
    b_cards = [
        card('認証基盤の刷新', 'ok', '順調', 'SAML連携の実装が完了し、結合テストに入っている。', '担当: 情報システム課', '更新 2026-07-28'),
        card('決済APIの連携', 'warn', '注意', '外部ベンダーの仕様変更対応で1週間の遅延が見込まれる。', '担当: 決済チーム', '更新 2026-07-27'),
        card('通知基盤の移行', 'bad', '停滞', '送信遅延の原因調査が終わらず、移行判断を保留している。', '担当: 基盤チーム', '更新 2026-07-20'),
        card('監視体制の強化', 'ok', '順調', 'アラート閾値の見直しが完了し、夜間当番の運用を開始した。', '担当: 運用課', '更新 2026-07-29'),
    ]
    a_cards = [
        card('認証基盤の刷新', 'ok', '順調', 'SAML連携の実装が完了し、結合テストに入っている。応答時間も改善した。', '担当: 情報システム課', '更新 2026-08-01'),
        card('監視体制の強化', 'ok', '順調', 'アラート閾値の見直しが完了し、夜間当番の運用を開始した。', '担当: 運用課', '更新 2026-07-29'),
        card('決済APIの連携', 'ok', '順調', '外部ベンダーの仕様変更対応が完了し、遅延は解消した。', '担当: 決済チーム', '更新 2026-08-01'),
        card('データ基盤のPoC', 'ok', '新規', '分析基盤の候補製品を3つに絞り、評価環境の構築を開始した。', '担当: データチーム', '更新 2026-08-01'),
    ]
    wrap = lambda cs: '        <div class="grid">\n' + '\n'.join(cs) + '\n        </div>'
    return wrap(b_cards), wrap(a_cards)


def sec_card_attr():
    # テキストは完全同一。class だけが変わる（属性のみの変更）
    common = dict(title='棚卸データの移行', badge_kind='ok', badge_text='順調',
                  desc='旧システムからの棚卸データ移行スクリプトを実行し、件数の突合まで終えた。',
                  owner='担当: 情報システム課', date='更新 2026-07-31')
    b = card(cls='card', **common)
    a = card(cls='card done', **common)
    wrap = lambda c: '        <div class="grid">\n' + c + '\n        </div>'
    return wrap(b), wrap(a)


def sec_list_nest():
    b = """        <ul class="tree">
          <li>要件定義
            <ul>
              <li>現行業務のヒアリング</li>
              <li>要求一覧の作成</li>
              <li>優先度の確認
                <ul>
                  <li>顧客レビュー</li>
                  <li>社内レビュー</li>
                </ul>
              </li>
            </ul>
          </li>
          <li>設計
            <ul>
              <li>画面設計</li>
              <li>データベース設計</li>
              <li>外部インターフェース設計</li>
            </ul>
          </li>
          <li>実装
            <ul>
              <li>フロントエンド実装</li>
              <li>バックエンド実装</li>
              <li>単体テスト</li>
            </ul>
          </li>
          <li>リリース
            <ul>
              <li>リリースノート作成</li>
              <li>受入テスト</li>
              <li>本番反映</li>
            </ul>
          </li>
        </ul>"""
    a = """        <ul class="tree">
          <li>要件定義
            <ul>
              <li>現行業務のヒアリング</li>
              <li>要求一覧の作成</li>
              <li>優先度の確認</li>
              <li>顧客レビュー</li>
            </ul>
          </li>
          <li>設計
            <ul>
              <li>画面設計</li>
              <li>データベース設計
                <ul>
                  <li>外部インターフェース設計</li>
                </ul>
              </li>
            </ul>
          </li>
          <li>実装
            <ol>
              <li>フロントエンド実装</li>
              <li>バックエンド実装</li>
              <li>単体テスト</li>
            </ol>
          </li>
          <li>リリース
            <ul>
              <li>受入テスト</li>
              <li>リリースノート作成</li>
              <li>本番反映</li>
            </ul>
          </li>
        </ul>"""
    return b, a


def sec_steps():
    step = lambda h, p: '          <li>\n            <h3>%s</h3>\n            <p>%s</p>\n          </li>' % (h, p)
    s_alert = step('監視アラートの確認', '監視システムの通知内容と発生時刻を確認し、インシデントチケットを起票する。')
    s_call = step('障害対応チームの招集', '一次対応者は障害対応チームをチャットで招集し、対応体制を立ち上げる。')
    s_scope = step('影響範囲の特定', '影響を受けるサービスと利用者の範囲を特定し、重大度を判定する。')
    s_report = step('関係者への一次報告', '重大度に応じて、あらかじめ定めた関係者へ一次報告を行う。')
    s_fix_b = step('暫定対処の実施', '影響を最小化するための暫定対処（切り戻し、縮退運転等）を実施する。')
    s_fix_a = step('暫定対処の実施', '影響を最小化するための暫定対処（切り戻し、縮退運転、負荷分散設定の変更等）を実施する。対処内容と実施時刻はインシデントチケットに逐次記録すること。')
    s_done = step('復旧確認', 'サービスが正常に復旧したことを監視とヘルスチェックの両面で確認する。')
    b = '        <ol class="steps">\n' + '\n'.join([s_alert, s_call, s_scope, s_report, s_fix_b, s_done]) + '\n        </ol>'
    a = '        <ol class="steps">\n' + '\n'.join([s_alert, s_scope, s_report, s_call, s_fix_a, s_done]) + '\n        </ol>'
    return b, a


def sec_glossary():
    term = lambda t, d: '          <dt>%s</dt>\n          <dd>%s</dd>' % (t, d)
    sla = term('SLA（サービスレベル合意）', '提供者と利用者の間で合意した、可用性や応答時間の水準を定めた契約上の指標。')
    slo = term('SLO（サービスレベル目標）', 'SLAより厳しい水準で内部的に設定する目標値。SLA違反の予兆を早期に検知するために用いる。')
    rto = term('RTO（目標復旧時間）', '障害発生から復旧までに許容される時間の上限。')
    inc = term('インシデント', '意図しないサービス品質の低下、またはその恐れがある事象。')
    esc_b = term('エスカレーション', 'インシデントの重大度や対応の遅れに応じて、対応権限や報告先をより上位の体制に引き上げる行為。')
    esc_a = term('エスカレーション', 'インシデントの重大度や対応の遅れに応じて、対応権限や報告先をより上位の体制に引き上げる行為。一次対応者の判断のみに委ねず、あらかじめ定めた基準に沿って機械的に発動する。')
    onc = term('オンコール', '勤務時間外であっても、障害発生時に一次対応を行うために待機する体制。')
    pm = term('ポストモーテム', '復旧後に実施する振り返り。個人の責任追及ではなく再発防止を目的とする。')
    b = '        <dl class="glossary">\n' + '\n'.join([sla, rto, inc, esc_b, onc, pm]) + '\n        </dl>'
    a = '        <dl class="glossary">\n' + '\n'.join([sla, slo, rto, inc, esc_a, pm]) + '\n        </dl>'
    return b, a


def sec_prose():
    p = lambda s: '        <p>%s</p>' % s
    b = '\n'.join([
        p('本プロジェクトは、社内で個別に管理されていた資産情報を単一の台帳へ統合することを目的として、2026年2月に開始した。対象は本社ビルおよび2拠点の什器・OA機器であり、部門ごとに異なっていた管理粒度をそろえる作業から着手した。'),
        p('体制は情報システム課3名と総務課2名の計5名で、週次の進捗確認を継続してきた。外部ベンダーへの委託は行わず、既存の社内ツールの組み合わせで完結させる方針とした。'),
        p('うまくいった点として、初期段階で棚卸の粒度を合意できたことが大きい。粒度が定まっていたため、拠点ごとの入力作業が並行して進められ、想定より2週間早く一次データがそろった。'),
        p('一方で課題も残った。取得年度の情報が拠点によって欠落しており、遡って調査する手間が発生した。結果として、データ整備に要した工数は当初見積もりの38%増となった。'),
        p('定量的な成果としては、台帳の重複登録が412件から0件になり、月次の棚卸作業時間が約30%削減された。今後は減価償却の管理との連携を検討する。'),
        p('次フェーズの本番切り替えは2026年9月30日を予定している。切り替え後1か月は旧台帳を参照可能な状態で残し、差異が出た場合に追跡できるようにする。'),
    ])
    a = '\n'.join([
        p('本プロジェクトは、社内で個別に管理されていた資産情報を単一の台帳へ統合することを目的として、2026年2月に開始した。対象は本社ビルおよび2拠点の什器・OA機器であり、部門ごとに異なっていた管理粒度をそろえる作業から着手した。'),
        p('体制は情報システム課3名と総務課2名の計5名で、週次の進捗確認を継続してきた。外部ベンダーへの委託は行わず、既存の社内ツールの組み合わせで完結させる方針とした。'),
        p('うまくいった点として、初期段階で棚卸の粒度を合意できたことが大きい。粒度が定まっていたため、拠点ごとの入力作業が並行して進められ、想定より2週間早く一次データがそろった。'),
        p('一方で懸念も残った。取得年度の情報が拠点によって欠落しており、遡って調査する手間が発生した。結果として、データ整備に要した工数は当初見積もりの42%増となった。'),
        p('定量的な成果としては、台帳の重複登録が412件から0件になり、月次の棚卸作業時間が約30%削減された。今後は減価償却の管理との連携を検討する。'),
        p('次フェーズの本番切り替えは2026年10月15日を予定している。切り替え後1か月は旧台帳を参照可能な状態で残し、差異が出た場合に追跡できるようにする。'),
    ])
    return b, a


def sec_inline():
    # 可視テキストは before/after で完全に同一。マークアップと属性だけが変わる。
    b = '\n'.join([
        '        <p>棚卸台帳の締め日を <em>毎月末日</em> から毎月25日へ変更しました。',
        '        対象は本社および全拠点です。詳細は <a href="/docs/2026-07/asset-notes">運用メモ</a> を参照してください。</p>',
        '        <p>変更後は <span>締め日の翌営業日</span> に自動集計が走ります。集計結果に差異があった場合は情報システム課へ連絡してください。</p>',
    ])
    a = '\n'.join([
        '        <p>棚卸台帳の締め日を 毎月末日 から<strong>毎月25日</strong>へ変更しました。',
        '        対象は本社および全拠点です。詳細は <a href="/docs/2026-08/asset-notes">運用メモ</a> を参照してください。</p>',
        '        <p>変更後は <span class="highlight">締め日の翌営業日</span> に自動集計が走ります。集計結果に差異があった場合は情報システム課へ連絡してください。</p>',
    ])
    return b, a


def sec_code():
    head = '        <p>集計ジョブの起動スクリプトは <code>asset-batch</code> です。</p>\n        <pre><code>'
    tail = '</code></pre>'
    b_lines = [
        '#!/usr/bin/env bash',
        'set -euo pipefail',
        '',
        'TARGET_MONTH="${1:-$(date +%Y-%m)}"',
        'ENDPOINT="https://asset.internal/api/v1/aggregate"',
        '',
        'echo "aggregating ${TARGET_MONTH}"',
        'curl -sSf -X POST "${ENDPOINT}" \\',
        '  --header "Content-Type: application/json" \\',
        '  --data "{\\"month\\":\\"${TARGET_MONTH}\\"}"',
        '',
        'rm -f /tmp/asset-aggregate.lock',
        'echo "done"',
    ]
    a_lines = [
        '#!/usr/bin/env bash',
        'set -euo pipefail',
        '',
        'TARGET_MONTH="${1:-$(date +%Y-%m)}"',
        'ENDPOINT="https://asset.internal/api/v2/aggregate"',
        'RETRY=3',
        '',
        'echo "aggregating ${TARGET_MONTH}"',
        'curl -sSf --retry "${RETRY}" -X POST "${ENDPOINT}" \\',
        '  --header "Content-Type: application/json" \\',
        '  --data "{\\"month\\":\\"${TARGET_MONTH}\\"}"',
        '',
        'echo "done"',
    ]
    esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return head + '\n'.join(esc(l) for l in b_lines) + tail, head + '\n'.join(esc(l) for l in a_lines) + tail


def sec_quote():
    b = '\n'.join([
        '        <blockquote>',
        '          「私たちは、障害の発生を完全にゼロにすることを目指すのではなく、障害を30分以内に検知し、',
        '          顧客影響を最小化することを最優先とする。」',
        '          <span class="attrib">運用ポリシー 第1章 より</span>',
        '        </blockquote>',
    ])
    a = '\n'.join([
        '        <blockquote>',
        '          「私たちは、障害の発生を完全にゼロにすることを目指すのではなく、障害を15分以内に検知し、',
        '          顧客影響を最小化したうえで迅速に復旧することを最優先とする。」',
        '          <span class="attrib">運用ポリシー 第1章 より</span>',
        '        </blockquote>',
    ])
    return b, a


def sec_hlevel():
    # テキストは同一で見出しレベルだけが変わる
    b = '\n'.join([
        '        <h3>データの流れ</h3>',
        '        <p>各拠点の入力フォームから収集した棚卸データは、夜間バッチで台帳データベースへ取り込まれる。</p>',
        '        <h3>構成要素</h3>',
        '        <p>台帳データベース、集計ジョブ、参照用の社内ポータルの3つで構成される。</p>',
    ])
    a = '\n'.join([
        '        <h2>データの流れ</h2>',
        '        <p>各拠点の入力フォームから収集した棚卸データは、夜間バッチで台帳データベースへ取り込まれる。</p>',
        '        <h3>構成要素</h3>',
        '        <p>台帳データベース、集計ジョブ、参照用の社内ポータルの3つで構成される。</p>',
    ])
    return b, a


def sec_swap():
    risk = '\n'.join([
        '        <h3>想定されるリスク</h3>',
        '        <p>拠点ごとの入力遅延により、月次の集計が締め日に間に合わない可能性がある。締め日の3営業日前にリマインドを自動送信して対応する。</p>',
    ])
    plan = '\n'.join([
        '        <h3>今後の予定</h3>',
        '        <p>9月に本番切り替え、10月に旧台帳の参照停止、11月に減価償却管理との連携検討を予定している。</p>',
    ])
    return risk + '\n' + plan, plan + '\n' + risk


# 削除される節 / 追加される節（ナビ項目の増減とセットで使う）
LEGACY_SECTION = section('sec-legacy-permission', '権限管理（旧）',
                         '台帳の閲覧・編集権限の設定方針。',
                         '        <p>台帳の管理者は、利用者の権限を「閲覧のみ」「編集可」「管理者」の3段階で設定できる。異動・退職時は速やかに権限を見直すこと。</p>')
NEW_SECTION = section('sec-integration', '外部連携',
                      '社内の他システムとの連携方針。',
                      '        <p>資産台帳は、社内チャットおよび経理システムとの連携に対応する。連携設定は管理者権限を持つ利用者のみが行える。</p>')


def sec_direction():
    # どちら向きに diff を取っているかを、出力そのものから判別できるようにする。
    # 正しい向き（左=before / 右=after）なら「BEFORE（旧）」が赤、「AFTER（新）」が緑になる。
    # 逆に見えている場合は、エディタの左右に入れたファイルが入れ替わっている。
    b = '\n'.join([
        '        <p>この文書は <strong>BEFORE（旧・左ペインに入れる方）</strong> です。</p>',
        '        <p>版数 v1.2 / 2026-07-30 時点</p>',
    ])
    a = '\n'.join([
        '        <p>この文書は <strong>AFTER（新・右ペインに入れる方）</strong> です。</p>',
        '        <p>版数 v1.3 / 2026-08-01 時点</p>',
    ])
    return b, a


CASES = [
    ('sec-direction', 'diff の向き確認', 'BEFORE が赤、AFTER が緑になっていれば左右の入れ方が正しい。', sec_direction),
    ('sec-col-add-tail', '表：末尾に列を追加', '最後尾に「備考」列を追加。既存列の値は変えない。', sec_col_add_tail),
    ('sec-col-add-mid', '表：途中に列を追加', '「設置場所」と「数量」の間に「管理担当」列を挿入。', sec_col_add_mid),
    ('sec-col-del-mid', '表：途中の列を削除', '「取得年度」列を削除。前後の列は変えない。', sec_col_del_mid),
    ('sec-col-del-tail', '表：末尾の列を削除', '「旧管理番号」列を削除。', sec_col_del_tail),
    ('sec-row-churn', '表：行の増減と値の変更', '行を1本削除、1本追加し、金額を複数箇所変更。', sec_row_churn),
    ('sec-lookalike', '表：似た行が並ぶ中での1行削除', '同じ形の行が5本並ぶ中から1本を削除し、別の行のセルを1つ変更。', sec_lookalike),
    ('sec-cards', 'カード：追加・削除・並べ替え', '同じclassのカードを1枚削除、1枚追加、2枚入れ替え、1枚の本文を微修正。', sec_cards),
    ('sec-card-attr', 'カード：classだけの変更', 'テキストは完全に同一で、classだけが card から card done に変わる。', sec_card_attr),
    ('sec-list-nest', '入れ子リストの組み替え', '階層の昇格・降格、ul→ol、並べ替え、項目の削除。', sec_list_nest),
    ('sec-steps', '手順の並べ替えと本文書き換え', '2番目のステップを4番目へ移動し、1ステップの説明を書き換える。', sec_steps),
    ('sec-glossary', '用語集：用語の増減と定義の書き換え', 'dt/dd を1組追加、1組削除し、既存の定義を1つ書き換える。', sec_glossary),
    ('sec-prose', '長文：ごく小さな修正のみ', '6段落のうち3箇所だけを修正。過剰にマークしないことの確認。', sec_prose),
    ('sec-inline', 'インライン記法・属性のみの変更', '可視テキストは完全に同一。strong追加、em除去、href変更、class追加のみ。', sec_inline),
    ('sec-code', 'コードブロックの編集', '1行変更、1行追加、1行削除。インデントが崩れないことの確認。', sec_code),
    ('sec-quote', '引用文の部分修正', 'blockquote 内の数値と語尾を変更。', sec_quote),
    ('sec-hlevel', '見出しレベルの昇格', 'テキストは同一で h3 が h2 になる。', sec_hlevel),
    ('sec-swap', '小見出しの入れ替え', '2つの小見出しブロックの前後を入れ替える。', sec_swap),
]

NAV_BEFORE = [
    ('sec-col-add-tail', '表：列の追加'), ('sec-col-del-mid', '表：列の削除'),
    ('sec-row-churn', '表：行の増減'), ('sec-cards', 'カード'),
    ('sec-list-nest', 'リスト'), ('sec-steps', '手順'),
    ('sec-glossary', '用語集'), ('sec-prose', '振り返り'),
    ('sec-code', 'コード'), ('sec-legacy-permission', '権限管理'),
]
NAV_AFTER = [
    ('sec-col-add-tail', '表：列の追加'), ('sec-col-del-mid', '表：列の削除'),
    ('sec-row-churn', '表：行の増減'), ('sec-cards', 'カード'),
    ('sec-list-nest', 'リスト'), ('sec-steps', '手順'),
    ('sec-glossary', '用語集・用語の定義'), ('sec-prose', '振り返り'),
    ('sec-code', 'コード'), ('sec-integration', '外部連携'),
]


def build(which):
    idx = 0 if which == 'before' else 1
    nav_items = NAV_BEFORE if which == 'before' else NAV_AFTER
    nav = '\n'.join('          <li><a href="#%s">%s</a></li>' % (h, t) for h, t in nav_items)

    parts = []
    for sid, title, lead, fn in CASES:
        parts.append(section(sid, title, lead, fn()[idx]))
    # ナビの増減とセットになる節
    parts.append(LEGACY_SECTION if which == 'before' else NEW_SECTION)

    title = '資産台帳統合プロジェクト 進捗報告'
    date = '2026-07-30' if which == 'before' else '2026-08-01'
    rev = 'v1.2' if which == 'before' else 'v1.3'

    doc = []
    doc.append('<!DOCTYPE html>')
    doc.append('<html lang="ja">')
    doc.append('<head>')
    doc.append('<meta charset="utf-8">')
    doc.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    doc.append('<title>%s</title>' % title)
    doc.append('<sty' + 'le>')
    doc.append(CSS.strip())
    doc.append('</sty' + 'le>')
    doc.append('</he' + 'ad>')
    doc.append('<bo' + 'dy>')
    doc.append('<div class="page">')
    doc.append('  <header class="hero">')
    doc.append('    <h1>%s</h1>' % title)
    doc.append('    <div class="meta"><span>文書番号: PJ-2026-118</span><span>版数: %s</span><span>最終更新: %s</span><span>作成: 情報システム課</span></div>' % (rev, date))
    doc.append('  </header>')
    doc.append('  <div class="layout">')
    doc.append('    <nav class="toc">')
    doc.append('      <div class="toc-title">目次</div>')
    doc.append('      <ul>')
    doc.append(nav)
    doc.append('      </ul>')
    doc.append('    </nav>')
    doc.append('    <main>')
    doc.extend(parts)
    doc.append('    </main>')
    doc.append('  </div>')
    doc.append('  <footer>社内利用限定 / 問い合わせ: asset-admin@example.internal</footer>')
    doc.append('</div>')
    doc.append('</bo' + 'dy>')
    doc.append('</html>')
    return '\n'.join(doc) + '\n'


if __name__ == '__main__':
    for which in ('before', 'after'):
        path = os.path.join(OUT, 'all-cases-%s.html' % which)
        io.open(path, 'w', encoding='utf-8').write(build(which))
        print('wrote', path, len(build(which)), 'bytes')
