# 3 つ目のテストセット（エッジケース）のジェネレータ。
#
# セット1（資産台帳・明るい/flex/左ナビ）とセット2（バックエンド設計書・暗い/grid/上部ナビ）
# でカバーできていない HTML の書き方と差分パターンを集めたもの。
# 体裁もさらに変えて、白背景・セリフ寄り・段組みを使う印刷物風にしてある。
#
# before / after を同じソースから吐くので <style> のバイト一致は構造的に保証される。
import io, os, base64

OUT = os.path.dirname(os.path.abspath(__file__))

CSS = """
:root{
  --ink:#1b1b1b; --sub:#6a6a6a; --rule:#d6d2c8; --paper:#faf8f4; --accent:#7a3b2e;
  --tint:#f2ede4; --ok:#2f6b3a; --warn:#8a6d1f; --bad:#8c2f28;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--paper); color:var(--ink);
  font:15px/1.85 "Hiragino Mincho ProN","Yu Mincho","Noto Serif JP",serif;
}
.sheet{max-width:940px; margin:0 auto; padding:2.4rem 2.6rem 4rem; background:#fff;
  border-left:1px solid var(--rule); border-right:1px solid var(--rule); min-height:100vh}
.dochead{border-bottom:3px double var(--rule); padding-bottom:1rem; margin-bottom:1.2rem}
.dochead h1{margin:0 0 .3rem; font-size:1.35rem; letter-spacing:.04em}
.docmeta{font-size:.8rem; color:var(--sub); display:flex; gap:1.4rem; flex-wrap:wrap;
  font-family:"Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif}
nav.idx{border:1px solid var(--rule); background:var(--tint); padding:.8rem 1rem; margin:0 0 1.6rem;
  font-family:"Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; font-size:.82rem}
nav.idx b{display:block; margin-bottom:.4rem; color:var(--accent); font-size:.78rem; letter-spacing:.1em}
nav.idx ol{margin:0; padding-left:1.3rem; columns:2; column-gap:1.6rem}
nav.idx li{margin:.1rem 0}
nav.idx a{color:var(--ink); text-decoration:none}
nav.idx a:hover{text-decoration:underline}
section{margin:0 0 2rem}
section > h2{font-size:1.02rem; margin:0 0 .2rem; padding-left:.55rem;
  border-left:4px solid var(--accent); letter-spacing:.03em}
.lead{margin:.15rem 0 .9rem .8rem; color:var(--sub); font-size:.8rem;
  font-family:"Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif}
p{margin:0 0 .8rem}
.cols{column-count:2; column-gap:2rem; font-size:.9rem}
.cols p{margin:0 0 .7rem}
table{border-collapse:collapse; width:100%; font-size:.84rem; margin:.4rem 0 .6rem;
  font-family:"Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif}
th,td{border:1px solid var(--rule); padding:.4rem .6rem; text-align:left; vertical-align:top}
thead th{background:var(--tint)}
tfoot td,tfoot th{background:#f7f5f0; font-weight:600}
table table{margin:.2rem 0; font-size:.94em}
col.narrow{width:6rem}
form{border:1px solid var(--rule); padding:.9rem 1.1rem; background:#fdfcfa;
  font-family:"Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; font-size:.85rem}
fieldset{border:1px solid var(--rule); margin:0 0 .8rem; padding:.6rem .8rem}
legend{padding:0 .4rem; font-size:.8rem; color:var(--accent)}
label{display:inline-block; min-width:8rem}
input,select,textarea{font:inherit; padding:.15rem .35rem; border:1px solid var(--rule); background:#fff}
textarea{width:100%; height:3.4rem}
.card{border:1px solid var(--rule); padding:.7rem .9rem; margin:.5rem 0; background:#fdfcfa;
  font-family:"Hiragino Kaku Gothic ProN","Yu Gothic",sans-serif; font-size:.86rem}
.card h3{margin:0 0 .25rem; font-size:.92rem}
.card p{margin:0; color:#3d3d3d}
figure{margin:.5rem 0}
figure img{border:1px solid var(--rule); background:#fff}
figcaption{font-size:.78rem; color:var(--sub); margin-top:.25rem}
.grid-table{display:table; width:100%; border:1px solid var(--rule); font-size:.84rem}
.grid-row{display:table-row}
.grid-cell{display:table-cell; border:1px solid var(--rule); padding:.35rem .6rem}
.pass{display:contents}
.aside{float:right; width:38%; margin:0 0 .6rem 1rem; padding:.55rem .8rem;
  border:1px solid var(--rule); background:var(--tint); font-size:.8rem}
.rtl{direction:rtl; text-align:right; border:1px solid var(--rule); padding:.5rem .8rem; background:#fdfcfa}
ins{background:#e8f3e8; text-decoration:none; border-bottom:1px solid var(--ok)}
del{background:#f7e9e8; text-decoration:line-through}
mark{background:#fdf3c8; padding:0 .15rem}
kbd{font-family:Menlo,Consolas,monospace; font-size:.85em; border:1px solid var(--rule);
  border-bottom-width:2px; border-radius:3px; padding:0 .3rem; background:#fbfaf7}
code{font-family:Menlo,Consolas,monospace; font-size:.88em; background:var(--tint); padding:0 .25rem}
address{font-style:normal; font-size:.85rem; border-left:3px solid var(--rule); padding-left:.7rem}
hgroup h3{margin:0; font-size:.98rem}
hgroup p{margin:.1rem 0 0; color:var(--sub); font-size:.82rem}
.deep{border-left:1px dotted var(--rule); padding-left:.6rem; margin:.15rem 0}
ul{margin:.3rem 0; padding-left:1.3rem}
li{margin:.1rem 0}
footer{margin-top:2rem; padding-top:.8rem; border-top:1px solid var(--rule);
  font-size:.78rem; color:var(--sub)}
"""


def img_data_uri(fill, label):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="120" height="48">'
           '<rect width="120" height="48" fill="%s"/>'
           '<text x="60" y="30" font-size="13" text-anchor="middle" fill="#fff">%s</text>'
           '</svg>') % (fill, label)
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode('utf-8')).decode('ascii')


IMG_A = img_data_uri('#7a3b2e', 'FLOW-A')
IMG_B = img_data_uri('#2f6b3a', 'FLOW-B')


def section(sid, title, lead, body):
    return '\n'.join([
        '    <section id="%s">' % sid,
        '      <h2>%s</h2>' % title,
        '      <p class="lead">%s</p>' % lead,
        body,
        '    </section>',
    ])


def table(tid, header, rows, foot=None, colgroup=None, bodies=None):
    lines = ['<table id="%s">' % tid]
    if colgroup:
        lines.append('  <colgroup>%s</colgroup>' % ''.join(colgroup))
    lines.append('  <thead><tr>%s</tr></thead>' % ''.join('<th>%s</th>' % c for c in header))
    if bodies:
        for grp in bodies:
            lines.append('  <tbody>')
            for r in grp:
                lines.append('    <tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r))
            lines.append('  </tbody>')
    else:
        lines.append('  <tbody>')
        for r in rows:
            lines.append('    <tr>%s</tr>' % ''.join('<td>%s</td>' % c for c in r))
        lines.append('  </tbody>')
    if foot:
        lines.append('  <tfoot><tr>%s</tr></tfoot>' % ''.join('<td>%s</td>' % c for c in foot))
    lines.append('</table>')
    return '\n'.join('      ' + l for l in lines)


# ---------- 各テストケース ----------

def sec_direction():
    b = ('      <p>この文書は <strong>BEFORE（旧・左ペインに入れる方）</strong> です。</p>\n'
         '      <p class="lead">第 3 版 / 2026-07-28 起案</p>')
    a = ('      <p>この文書は <strong>AFTER（新・右ペインに入れる方）</strong> です。</p>\n'
         '      <p class="lead">第 4 版 / 2026-08-03 確定</p>')
    return b, a


def sec_form():
    def f(deadline, route, note, urgent_checked, legend):
        return '\n'.join('      ' + l for l in [
            '<form>',
            '  <fieldset>',
            '    <legend>%s</legend>' % legend,
            '    <p><label for="f-deadline">申請期限</label>',
            '      <input id="f-deadline" name="deadline" value="%s"></p>' % deadline,
            '    <p><label for="f-route">承認経路</label>',
            '      <select id="f-route" name="route">',
            '        <option value="direct"%s>直属上長のみ</option>' % (' selected' if route == 'direct' else ''),
            '        <option value="dept"%s>部門長まで</option>' % (' selected' if route == 'dept' else ''),
            '        <option value="exec"%s>役員まで</option>' % (' selected' if route == 'exec' else ''),
            '      </select></p>',
            '    <p><label for="f-urgent">緊急扱い</label>',
            '      <input id="f-urgent" type="checkbox"%s> 24 時間以内に処理する</p>' % (' checked' if urgent_checked else ''),
            '  </fieldset>',
            '  <p><label for="f-note">備考欄の初期値</label></p>',
            '  <textarea id="f-note" name="note">%s</textarea>' % note,
            '</form>',
        ])
    b = f('毎月 20 日', 'direct', '添付が必要な場合はファイル名に申請番号を含めること。', False, '既定値（旧）')
    a = f('毎月 25 日', 'dept', '添付が必要な場合はファイル名に申請番号と部門コードを含めること。', True, '既定値（新）')
    return b, a


def sec_table_parts():
    hdr = ['区分', '申請種別', '件数']
    grp1 = [['定型', '経費精算', '128'], ['定型', '勤怠修正', '96']]
    grp2_b = [['非定型', '設備購入', '14'], ['非定型', '外部委託', '7']]
    grp2_a = [['非定型', '設備購入', '14'], ['非定型', '外部委託', '9'], ['非定型', '協業契約', '3']]
    cg = ['<col class="narrow">', '<col>', '<col class="narrow">']
    b = table('t-parts', hdr, None, foot=['合計', '—', '245'], colgroup=cg, bodies=[grp1, grp2_b])
    a = table('t-parts', hdr, None, foot=['合計', '—', '250'], colgroup=cg, bodies=[grp1, grp2_a])
    return b, a


def sec_table_nested():
    def inner(rows):
        return ('<table><tr><th>段階</th><th>担当</th></tr>'
                + ''.join('<tr><td>%s</td><td>%s</td></tr>' % r for r in rows) + '</table>')
    b_inner = inner([('一次', '課長'), ('二次', '部長')])
    a_inner = inner([('一次', '課長'), ('二次', '本部長'), ('三次', '役員')])
    hdr = ['申請種別', '承認の内訳', '所要日数']
    rows_b = [['設備購入', b_inner, '5 営業日'], ['外部委託', '課長のみ', '2 営業日']]
    rows_a = [['設備購入', a_inner, '5 営業日'], ['外部委託', '課長のみ', '2 営業日']]
    return table('t-nested', hdr, rows_b), table('t-nested', hdr, rows_a)


def sec_col_reorder():
    hdr_b = ['申請番号', '区分', '担当', '状態', '期限']
    hdr_a = ['申請番号', '担当', '区分', '状態', '期限']
    rows_b = [
        ['REQ-1001', '経費', '田中', '承認済', '2026-08-10'],
        ['REQ-1002', '勤怠', '鈴木', '差戻し', '2026-08-12'],
        ['REQ-1003', '設備', '佐藤', '審査中', '2026-08-18'],
        ['REQ-1004', '委託', '高橋', '承認済', '2026-08-20'],
    ]
    rows_a = [[r[0], r[2], r[1], r[3], r[4]] for r in rows_b]
    return table('t-reorder', hdr_b, rows_b), table('t-reorder', hdr_a, rows_a)


def sec_col_rename():
    hdr_b = ['申請番号', '担当', '起票日', '状態']
    hdr_a = ['申請番号', '申請担当者', '起票日', '状態']
    rows = [
        ['REQ-2001', '山田', '2026-07-01', '承認済'],
        ['REQ-2002', '伊藤', '2026-07-04', '承認済'],
        ['REQ-2003', '渡辺', '2026-07-11', '審査中'],
        ['REQ-2004', '中村', '2026-07-19', '差戻し'],
    ]
    return table('t-rename', hdr_b, rows), table('t-rename', hdr_a, rows)


def sec_dup_blocks():
    card = ('<div class="card">\n'
            '        <h3>共通チェック項目</h3>\n'
            '        <p>申請番号・起票日・添付の有無を確認し、不足があれば差し戻す。</p>\n'
            '      </div>')
    b = '\n'.join('      ' + card for _ in range(3))
    a = '\n'.join('      ' + card for _ in range(2))
    return b, a


def sec_dup_text():
    p = '      <p>本項目は、申請の内容にかかわらず、すべての経路で同じ手順を適用する。</p>'
    p_mid = ('      <p>本項目は、申請の内容にかかわらず、すべての経路で'
             '同じ手順を適用する。ただし緊急扱いの場合は二次承認を省略できる。</p>')
    return '\n'.join([p, p, p]), '\n'.join([p, p_mid, p])


def sec_inline_semantics():
    b = '\n'.join('      ' + l for l in [
        '<p>受付開始は <time datetime="2026-08-01">2026年8月1日</time> とする。',
        '  <ruby>申請<rt>しんせい</rt></ruby>は所定の様式で行う。</p>',
        '<p>手数料は本体価格の 3<sup>rd</sup> 区分に従い、係数 k<sub>1</sub> を用いて算出する。',
        '  <mark>差戻しの件数</mark>は月次で集計する。</p>',
        '<p>画面上では <kbd>Ctrl</kbd> + <kbd>S</kbd> で下書き保存できる。</p>',
    ])
    a = '\n'.join('      ' + l for l in [
        '<p>受付開始は <time datetime="2026-09-01">2026年9月1日</time> とする。',
        '  <ruby>申請<rt>しんちょく</rt></ruby>は所定の様式で行う。</p>',
        '<p>手数料は本体価格の 4<sup>th</sup> 区分に従い、係数 k<sub>2</sub> を用いて算出する。',
        '  差戻しの件数は<mark>月次</mark>で集計する。</p>',
        '<p>画面上では <kbd>Ctrl</kbd> + <kbd>S</kbd> で下書き保存できる。</p>',
    ])
    return b, a


def sec_emoji():
    b = '\n'.join('      ' + l for l in [
        '<p>進捗の記号は 👍🏽 が承認、👎🏽 が差戻し、🇯🇵 が国内案件を表す。</p>',
        '<p>担当グループのアイコンは 👨‍👩‍👧 を用い、期限超過には ⏰ を添える。</p>',
        '<p>絵文字を含む行の途中の語だけを差し替える: 対象は 🎯 経費精算 とする。</p>',
    ])
    a = '\n'.join('      ' + l for l in [
        '<p>進捗の記号は 👍🏽 が承認、🚫 が差戻し、🇯🇵 が国内案件を表す。</p>',
        '<p>担当グループのアイコンは 👨‍👩‍👧 を用い、期限超過には 🔥 を添える。</p>',
        '<p>絵文字を含む行の途中の語だけを差し替える: 対象は 🎯 勤怠修正 とする。</p>',
    ])
    return b, a


def sec_style_attr():
    def t(style2):
        rows = [
            ['<td>REQ-3001</td>', '<td>経費精算</td>', '<td>承認済</td>'],
            ['<td>REQ-3002</td>', '<td>設備購入</td>', '<td%s>保留</td>' % style2],
            ['<td>REQ-3003</td>', '<td>外部委託</td>', '<td>承認済</td>'],
        ]
        lines = ['<table id="t-style">',
                 '  <thead><tr><th>申請番号</th><th>種別</th><th>状態</th></tr></thead>',
                 '  <tbody>']
        for r in rows:
            lines.append('    <tr>%s</tr>' % ''.join(r))
        lines += ['  </tbody>', '</table>']
        return '\n'.join('      ' + l for l in lines)
    return t(''), t(' style="background:#fdf3c8"')


def sec_img():
    def fig(src1, alt1, alt2):
        return '\n'.join('      ' + l for l in [
            '<figure>',
            '  <img src="%s" alt="%s" width="120" height="48">' % (src1, alt1),
            '  <figcaption>標準経路の図</figcaption>',
            '</figure>',
            '<figure>',
            '  <img src="%s" alt="%s" width="120" height="48">' % (IMG_B, alt2),
            '  <figcaption>例外経路の図</figcaption>',
            '</figure>',
        ])
    return (fig(IMG_A, '標準経路 A', '例外経路の概略'),
            fig(IMG_B, '標準経路 A', '例外経路の概略（役員承認を含む）'))


def sec_hidden():
    note = ('<p class="lead" %s>この注記は改訂中のため一時的に伏せている。'
            '内容が確定するまで参照しないこと。</p>')
    b = '      ' + (note % 'hidden')
    a = '      ' + (note % '')
    return b, a


def sec_comment():
    b = '\n'.join('      ' + l for l in [
        '<!-- TODO: 承認フローの最終形は未確定。第 4 版で差し替える。 -->',
        '<p>本節は承認フローの概要を示す。詳細は別紙に定める。</p>',
    ])
    a = '\n'.join('      ' + l for l in [
        '<!-- DONE: 承認フローは 2026-08-03 の会議で確定した。 -->',
        '<p>本節は承認フローの概要を示す。詳細は別紙に定める。</p>',
    ])
    return b, a


def sec_authors_insdel():
    b = '\n'.join('      ' + l for l in [
        '<p>第 2 版からの変更点: 承認者は <del>課長</del><ins>部長</ins> とする。',
        '  申請期限は <del>15 日</del><ins>20 日</ins> に変更した。</p>',
    ])
    a = '\n'.join('      ' + l for l in [
        '<p>第 2 版からの変更点: 承認者は <del>課長</del><ins>部長</ins> とする。',
        '  申請期限は <del>15 日</del><ins>25 日</ins> に変更した。',
        '  経路は <ins>部門長を経由する</ins>。</p>',
    ])
    return b, a


def sec_move_across():
    def block(notes, limits):
        return '\n'.join('      ' + l for l in
                         ['<h3>注意事項</h3>', '<ul>']
                         + ['  <li>%s</li>' % x for x in notes]
                         + ['</ul>', '<h3>制限事項</h3>', '<ul>']
                         + ['  <li>%s</li>' % x for x in limits]
                         + ['</ul>'])
    moved = '代理申請は同一部門内に限る'
    b = block(['添付は 10MB まで', moved, '取消は起票当日のみ'],
              ['同時申請は 5 件まで', '過去分の遡及申請は不可'])
    a = block(['添付は 10MB まで', '取消は起票当日のみ'],
              ['同時申請は 5 件まで', moved, '過去分の遡及申請は不可'])
    return b, a


def sec_replace_all():
    b = '\n'.join('      ' + l for l in [
        '<p>旧システムでは、申請は紙の様式に記入し、押印のうえ総務課へ提出していた。',
        '  受理後は台帳に転記し、月末にまとめて集計していた。</p>',
        '<table id="t-replace"><thead><tr><th>様式番号</th><th>名称</th></tr></thead>',
        '  <tbody><tr><td>様式1号</td><td>経費精算書</td></tr>',
        '  <tr><td>様式2号</td><td>勤怠修正届</td></tr></tbody></table>',
    ])
    a = '\n'.join('      ' + l for l in [
        '<p>新システムは API 経由での連携を前提とする。クライアントは OAuth 2.0 の',
        '  クライアントクレデンシャルで認証し、JSON でリクエストを送信する。</p>',
        '<table id="t-replace"><thead><tr><th>エンドポイント</th><th>メソッド</th></tr></thead>',
        '  <tbody><tr><td>/v1/requests</td><td>POST</td></tr>',
        '  <tr><td>/v1/requests/{id}/approve</td><td>PUT</td></tr></tbody></table>',
    ])
    return b, a


def sec_deep():
    def nest(leaf, extra=None):
        inner = ['<ul>', '  <li>%s</li>' % leaf]
        if extra:
            inner.append('  <li>%s</li>' % extra)
        inner.append('</ul>')
        s = '\n'.join(inner)
        for _ in range(6):
            s = '<div class="deep">\n' + '\n'.join('  ' + l for l in s.split('\n')) + '\n</div>'
        return '\n'.join('      ' + l for l in s.split('\n'))
    return nest('最下層の判定基準は起票日とする'), nest('最下層の判定基準は受理日とする', '受理日が休日の場合は翌営業日')


def sec_rtl():
    b = '\n'.join('      ' + l for l in [
        '<div class="rtl" dir="rtl" lang="ar">',
        '  <p>مدة الموافقة القصوى هي 5 أيام عمل.</p>',
        '</div>',
        '<p>申請 ID は <bdi>REQ-4001-AR</bdi> の形式で採番する。</p>',
    ])
    a = '\n'.join('      ' + l for l in [
        '<div class="rtl" dir="rtl" lang="ar">',
        '  <p>مدة الموافقة القصوى هي 3 أيام عمل.</p>',
        '</div>',
        '<p>申請 ID は <bdi>REQ-4002-AR</bdi> の形式で採番する。</p>',
    ])
    return b, a


def sec_css_layout():
    def build(cell, passthru, aside, col1):
        return '\n'.join('      ' + l for l in [
            '<div class="grid-table">',
            '  <div class="grid-row"><div class="grid-cell">経路</div><div class="grid-cell">%s</div></div>' % cell,
            '  <div class="grid-row"><div class="grid-cell">例外</div><div class="grid-cell">役員承認</div></div>',
            '</div>',
            '<div class="pass"><p>%s</p></div>' % passthru,
            '<div class="aside">%s</div>' % aside,
            '<div class="cols">',
            '  <p>%s</p>' % col1,
            '  <p>集計は月末締めとし、翌月 5 営業日以内に確定させる。差戻し分は当月に計上する。</p>',
            '  <p>保存期間は 7 年とし、期間経過後は年度単位で削除する。</p>',
            '</div>',
        ])
    b = build('課長 → 部長', 'display:contents のラッパを挟んだ段落。旧文面。',
              '補足: 旧経路では部長決裁で完了する。',
              '段組みの本文。申請の受付は平日 9 時から 17 時までとする。')
    a = build('課長 → 本部長', 'display:contents のラッパを挟んだ段落。新文面。',
              '補足: 新経路では本部長決裁まで必要になる。',
              '段組みの本文。申請の受付は平日 9 時から 18 時までとする。')
    return b, a


def sec_misc_containers():
    b = '\n'.join('      ' + l for l in [
        '<hgroup>',
        '  <h3>問い合わせ窓口</h3>',
        '  <p>平日 9:00〜17:00（年末年始を除く）</p>',
        '</hgroup>',
        '<address>',
        '  社内申請サポート窓口<br>',
        '  内線 4120 / workflow-support@example.internal',
        '</address>',
    ])
    a = '\n'.join('      ' + l for l in [
        '<hgroup>',
        '  <h3>問い合わせ窓口</h3>',
        '  <p>平日 9:00〜18:00（年末年始を除く）</p>',
        '</hgroup>',
        '<address>',
        '  社内申請サポート窓口<br>',
        '  内線 4130 / workflow-support@example.internal',
        '</address>',
    ])
    return b, a


LEGACY = section('sec-legacy-approval', '紙様式による承認（廃止）',
                 'BEFORE にだけある節。移行完了後に削除する。',
                 '      <p>紙の様式に押印して総務課へ提出する運用。移行完了をもって廃止する。</p>')
NEWSEC = section('sec-delegation', '代理承認',
                 'AFTER にだけある節。第 4 版で追加した。',
                 '      <p>承認者が不在の場合、あらかじめ登録した代理者が承認できる。'
                 '代理承認の記録は監査ログに残す。</p>')


CASES = [
    ('sec-direction', 'diff の向き確認', 'BEFORE が赤、AFTER が緑になっていれば左右の入れ方が正しい。', sec_direction),
    ('sec-form', 'フォームの既定値', 'テキストではなく value / selected / checked / textarea の中身が違う。', sec_form),
    ('sec-table-parts', '表：colgroup・複数 tbody・tfoot', 'BEFORE は非定型が2行、AFTER は3行。tfoot の合計も違う。colgroup は同じ。', sec_table_parts),
    ('sec-table-nested', '表：セルの中の入れ子表', '外側の表は同じ。内側の表が BEFORE は2行、AFTER は3行で、担当も1つ違う。', sec_table_nested),
    ('sec-col-reorder', '表：列の入れ替え（増減なし）', 'BEFORE は「区分・担当」の順、AFTER は「担当・区分」の順。列数は5のまま。', sec_col_reorder),
    ('sec-col-rename', '表：列名だけの変更', 'BEFORE の「担当」が AFTER では「申請担当者」。データセルは1つも違わない。', sec_col_rename),
    ('sec-dup-blocks', '同一ブロックが並ぶ', '完全に同じカードが BEFORE は3枚、AFTER は2枚。', sec_dup_blocks),
    ('sec-dup-text', '同一の段落が繰り返される', '同じ段落が3つ。BEFORE と AFTER で違うのは真ん中の1つだけ。', sec_dup_text),
    ('sec-inline-semantics', 'インライン要素（time・ruby・sup・sub・mark・kbd）', 'time の datetime と表示、ruby の読み、sup/sub、mark の範囲が違う。kbd は同じ。', sec_inline_semantics),
    ('sec-emoji', '絵文字（肌色修飾・国旗・ZWJ 連結）', '絵文字を含む行で、絵文字1つと語1つが違う。他の絵文字は同じ。', sec_emoji),
    ('sec-style-attr', 'インライン style 属性だけの変更', 'テキストは完全に同一。あるセルの style 属性の有無だけが違う。', sec_style_attr),
    ('sec-img', 'data: URI の画像（src と alt）', '1枚目は src が違い、2枚目は alt だけが違う。', sec_img),
    ('sec-hidden', 'hidden 属性の付け外し', 'テキストは完全に同一。BEFORE は hidden 付き、AFTER は無し。', sec_hidden),
    ('sec-comment', 'HTML コメントの変更', '本文は完全に同一。コメントの文言だけが違う。', sec_comment),
    ('sec-authors-insdel', '文書が元から持つ ins / del', '執筆者が書いた ins/del を含む段落。AFTER では数値が1つと文が1つ違う。', sec_authors_insdel),
    ('sec-move-across', '項目が別のリストへ移る', '「代理申請は同一部門内に限る」が BEFORE では注意事項、AFTER では制限事項にある。', sec_move_across),
    ('sec-replace-all', '節の中身を丸ごと差し替え', '見出し以外は本文も表も BEFORE と AFTER で全く別物。', sec_replace_all),
    ('sec-deep', '6 階層の入れ子', '最下層の語が1つ違い、AFTER には最下層に項目が1つ多い。', sec_deep),
    ('sec-rtl', 'dir="rtl" と bdi', 'アラビア語の数値が1つと、bdi 内の ID が違う。', sec_rtl),
    ('sec-css-layout', 'CSS 由来のレイアウト', 'display:table / display:contents / float / column-count の各ブロックで文言が1箇所ずつ違う。', sec_css_layout),
    ('sec-misc-containers', 'hgroup と address', 'hgroup の副題の時刻と、address の内線番号が違う。', sec_misc_containers),
]

NAV_BEFORE = [
    ('sec-form', 'フォーム'), ('sec-table-parts', '表の部品'), ('sec-col-reorder', '列の入れ替え'),
    ('sec-dup-blocks', '同一ブロック'), ('sec-emoji', '絵文字'), ('sec-img', '画像'),
    ('sec-move-across', '項目の移動'), ('sec-deep', '入れ子'), ('sec-rtl', 'RTL'),
    ('sec-legacy-approval', '紙様式による承認'),
]
NAV_AFTER = [
    ('sec-form', 'フォーム'), ('sec-table-parts', '表の部品'), ('sec-col-reorder', '列の入れ替え'),
    ('sec-dup-blocks', '同一ブロック'), ('sec-emoji', '絵文字と記号'), ('sec-img', '画像'),
    ('sec-move-across', '項目の移動'), ('sec-deep', '入れ子'), ('sec-rtl', 'RTL'),
    ('sec-delegation', '代理承認'),
]


def build(which):
    idx = 0 if which == 'before' else 1
    nav_items = NAV_BEFORE if which == 'before' else NAV_AFTER
    nav = '\n'.join('        <li><a href="#%s">%s</a></li>' % (h, t) for h, t in nav_items)

    parts = [section(sid, title, lead, fn()[idx]) for sid, title, lead, fn in CASES]
    parts.append(LEGACY if which == 'before' else NEWSEC)

    rev = '第 3 版' if which == 'before' else '第 4 版'
    date = '2026-07-28' if which == 'before' else '2026-08-03'
    state = '起案' if which == 'before' else '確定'

    doc = []
    doc.append('<!DOCTYPE html>')
    doc.append('<html lang="ja">')
    doc.append('<head>')
    doc.append('<meta charset="utf-8">')
    doc.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    doc.append('<title>社内申請ワークフロー 移行仕様書</title>')
    doc.append('<sty' + 'le>')
    doc.append(CSS.strip())
    doc.append('</sty' + 'le>')
    doc.append('</he' + 'ad>')
    doc.append('<bo' + 'dy>')
    doc.append('  <div class="sheet">')
    doc.append('    <div class="dochead">')
    doc.append('      <h1>社内申請ワークフロー 移行仕様書</h1>')
    doc.append('      <div class="docmeta"><span>文書番号 WF-2026-007</span><span>%s</span>'
               '<span>%s</span><span>%s</span></div>' % (rev, date, state))
    doc.append('    </div>')
    doc.append('    <nav class="idx">')
    doc.append('      <b>目次</b>')
    doc.append('      <ol>')
    doc.append(nav)
    doc.append('      </ol>')
    doc.append('    </nav>')
    doc.extend(parts)
    doc.append('    <footer>社内限定 / 総務課 業務システム担当</footer>')
    doc.append('  </div>')
    doc.append('</bo' + 'dy>')
    doc.append('</html>')
    return '\n'.join(doc) + '\n'


if __name__ == '__main__':
    for which in ('before', 'after'):
        path = os.path.join(OUT, 'edge-cases-%s.html' % which)
        io.open(path, 'w', encoding='utf-8').write(build(which))
        print('wrote', path, len(build(which)), 'bytes')
