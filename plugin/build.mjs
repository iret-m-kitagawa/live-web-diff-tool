#!/usr/bin/env node
// リポジトリ直下の index.html を、スキルの中の web/index.html へ複製する。
//
// スキルは自分のディレクトリの外を参照できない（プラグインとして入れると
// キャッシュへコピーされるため）。そのため差分エンジンの本体は複製して同梱する
// 必要があり、放っておくと本体と複製がずれる。それを防ぐためだけのスクリプト。
//
// 以前は配布用の zip も作っていたが、リポジトリを公開してマーケットプレイス経由で
// 配れるようになったため、zip の受け取り手がいなくなった。複製だけを残している。
//
// 依存パッケージは増やさない。開発者用のスクリプトだが、この方針は配布物と同じ。

import * as fs from 'node:fs';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url)); // <repo>/plugin
const repoRoot = path.resolve(here, '..');
const skillDir = path.join(here, 'skills', 'richdiff');

const src = path.join(repoRoot, 'index.html');
const dest = path.join(skillDir, 'web', 'index.html');

const before = fs.existsSync(dest) ? fs.readFileSync(dest, 'utf8') : null;
const now = fs.readFileSync(src, 'utf8');

if (before === now) {
  console.log('複製は最新です。変更はありません。');
} else {
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, now, 'utf8');
  console.log(`複製しました: ${path.relative(repoRoot, src)} -> ${path.relative(repoRoot, dest)}`);
}
