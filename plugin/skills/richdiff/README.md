# richdiff

md / html の文書の変更内容を、タグを含まない見た目のままブラウザで表示する CLI、
および各エージェントから呼び出すための設定一式である。

差分エンジンには live-web-diff-tool を用いる（本ディレクトリの `web/index.html` が
その複製にあたる）。

## 何を解決するか

- **記法に埋もれずに読める。** md や html の差分をそのまま読むと、タグや記号と本文が
  混ざり、どこが変わったのかを追いにくい。richdiff はレンダリングした見た目のまま、
  変更箇所だけを色で示す。
- **文書全体を俯瞰できる。** エージェントとのやり取りの中では、変更は編集した箇所の
  断片としてしか提示されない。修正を何度か重ねた未コミットのファイルについて、
  「積み上がった結果、いま全体としてどうなっているか」を確かめる手段がない。
  richdiff は文書全体を一度に提示するため、変更をまとめて確認できる。

主たる対象は文書であり、コードの差分は git で読めるため狙いとしていない。ただし
md / html 以外の拡張子を与えた場合も、テキスト表示として開く。

## 動作要件

- Node.js **22 以上を推奨**する。実装は Node 18 で動作する API のみを使用しているが、
  18 および 20 はサポートが終了しているため、要求バージョンは 22 とする。
  18 未満の環境では、起動時に 1 行のエラーメッセージを出力して終了する
  （スタックトレースは出力しない）。
- 追加の npm パッケージは不要である。`node_modules` は生成しない。

## インストール（Claude Code）

環境を問わず、**ターミナルから次の 2 コマンド**で導入する。

```
claude plugin marketplace add iret-m-kitagawa/live-web-diff-tool
claude plugin install richdiff@live-web-diff-tool --scope user
```

1 行目でカタログを登録し、2 行目でインストールする。本リポジトリは公開されているため、
認証および事前の配布物を必要としない。

### どこまで影響するか

`--scope` で影響範囲を指定する。省略した場合は `user` となる。

| 指定 | 影響範囲 | 設定の保存先 |
|---|---|---|
| `--scope user` | そのユーザーの全プロジェクト | `~/.claude/plugins/` |
| `--scope project` | そのリポジトリを利用する全員 | `<repo>/.claude/settings.json` |
| `--scope local` | そのユーザーの、そのリポジトリのみ | `<repo>/.claude/settings.local.json` |

richdiff は特定のリポジトリに依存しないため、**通常は `user` を指定する。**
これにより、どのプロジェクトで作業していても利用できる。

カタログの登録も、既定ではユーザー単位である。

### インストール後

シェルから導入した場合、**実行中のセッションには反映されない。**

ターミナルの CLI では `/reload-plugins` で反映できる。一方、**VS Code / Cursor の
拡張ではこのコマンドが存在しない。** 代わりに案内される `/reload-skills` は、
プラグイン由来のスキルを拾わない（実行しても `no changes` となる）。

拡張を使っている場合は、**ウィンドウを再読み込みする**（コマンドパレットの
Developer: Reload Window）。アプリケーション自体を終了する必要はなく、
会話も引き継がれる。

反映されたかどうかは、スキルの一覧に `richdiff:richdiff` が現れるかで判断できる。
プラグイン由来のスキルは `プラグイン名:スキル名` の形で並ぶ。

有効になったのち、利用者が「diff を見せて」等の依頼を行った際に `richdiff` スキルが使用される。

### セッション内から導入する場合

ターミナルで `claude` を対話的に起動している場合に限り、`/plugin` で対話パネルを開き、
インストール内容やコンテキスト消費量を確認しながら導入することもできる。

ただし **VS Code / Cursor の拡張の中では `/plugin` は使用できない**
（`/plugin isn't available in this environment.` と表示される）。環境によって手順を
変えたくない場合は、前述のシェル版を用いること。

### 管理

| コマンド | 内容 |
|---|---|
| `claude plugin list` | インストール済みプラグインの一覧 |
| `claude plugin update richdiff@live-web-diff-tool` | 最新版に更新（適用には再起動が必要） |
| `claude plugin disable richdiff@live-web-diff-tool` | 一時的に無効化（アンインストールはしない） |
| `claude plugin uninstall richdiff@live-web-diff-tool` | アンインストール |
| `claude plugin marketplace update live-web-diff-tool` | カタログを最新化 |

更新は、リポジトリへの push 後に `claude plugin update` を実行する。再インストールは不要である。

**本マーケットプレイスの自動更新は、既定で無効である。** 自動更新が既定で有効なのは
公式のマーケットプレイスのみであり、それ以外は各利用者が明示的に有効化する必要がある。
有効化は `/plugin` の **Marketplaces** タブからのみ行えるため、`/plugin` を開けない
環境では、上記の `claude plugin update` による手動更新となる。

## Cursor のエージェントを使用する場合

Cursor には Claude Code のようなプラグイン機構がない。そのため、**ファイルの取得と
配置を手動で行う必要がある。** 手順は以下のとおりである。

### 1. リポジトリを取得する

任意の場所に clone する。

```
git clone https://github.com/iret-m-kitagawa/live-web-diff-tool.git ~/tools/live-web-diff-tool
```

### 2. ルールファイルを設置する

`plugin/skills/richdiff/cursor-rule.mdc` を、適用したい範囲に応じて次のいずれかの方法で設置する。

| 適用範囲 | 方法 |
|---|---|
| そのリポジトリのみ | 対象リポジトリの `.cursor/rules/richdiff.mdc` として複製する |
| その Cursor 環境の全プロジェクト | Settings の **Customize → Rules** に本文を貼り付ける。ユーザールールをファイルとして配置する方法は用意されていない |
| チーム全体 | ダッシュボードの Team Rules に登録する（Team / Enterprise プランが前提） |

### 3. コマンドのパスを書き換える

設置したルールの中の `<展開先>` を、手順 1 で clone した実際のパスに置き換える。

```
<展開先>/bin/richdiff.mjs
  ↓
~/tools/live-web-diff-tool/plugin/skills/richdiff/bin/richdiff.mjs
```

Claude Code では `${CLAUDE_SKILL_DIR}` がインストール先を解決するが、Cursor には
これに相当する仕組みがない。**絶対パスを記述する必要がある。**

### 4. 使えることを確認する

Cursor のエージェントに対し、変更のある文書について「diff を見せて」と依頼する。
ブラウザが開けば設置は完了である。

### 更新するとき

手順 1 で clone したディレクトリで `git pull` を実行する。`cursor-rule.mdc` の内容が
変わった場合は、手順 2 と 3 をやり直す。

### 適用のされ方

`.mdc` の frontmatter の組み合わせによって、ルールが読み込まれる条件が決まる。

| frontmatter | 適用条件 |
|---|---|
| `alwaysApply: true` | 常に適用 |
| `description` あり・`globs` なし | 内容に応じてエージェントが判断 |
| `globs` あり | 該当するファイルが文脈に含まれたとき |
| いずれも無し | `@` による明示指定時のみ |

`cursor-rule.mdc` は `description` のみを指定している。差分の提示を求められた場合にのみ
読み込ませたいためであり、常時適用は意図していない。

参照: [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules)

## CLI を直接使用する場合

エージェントを介さず、コマンドとして実行することもできる。

```
node <展開先>/bin/richdiff.mjs --help
```

`<展開先>` は `skills/richdiff` の配置先を指す（例: `~/.claude/skills/richdiff`）。
主な呼び出し方は以下のとおりである。

```
node <展開先>/bin/richdiff.mjs --git
node <展開先>/bin/richdiff.mjs --pair before.md after.md
node <展開先>/bin/richdiff.mjs --proposed docs/spec.md=/tmp/spec.new.md --no-open
```

## バージョンの確認

```
node <展開先>/bin/richdiff.mjs --version
```

`plugin.json` の `version` と `bin/richdiff.mjs` の `VERSION` 定数は、
別々に保持している。リリース時は次のコマンドで整合を確認する。

```
claude plugin validate plugin                 # plugin.json の検証
claude plugin validate .                      # marketplace.json の検証
claude plugin tag plugin                      # 版数の一致を確認して git タグを作成
```

また、リポジトリ直下の `index.html` と `web/index.html` の複製は
`node plugin/build.mjs` で更新する。
