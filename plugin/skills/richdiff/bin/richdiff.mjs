#!/usr/bin/env node
// richdiff — md / html などの文書の変更を、ブラウザ (live-web-diff-tool) で見せる CLI。
//
// 依存パッケージはゼロ。node_modules は作らない。使う API も
// node:http / node:fs / node:path / node:os / node:crypto (randomUUID) /
// node:child_process / node:url くらいまでにとどめている（Node 18 でも動く古い形の API）。
// 新しい構文・新しい API には手を出さない、というのがこのファイルの制約。

import * as fs from 'node:fs';
import * as path from 'node:path';
import * as os from 'node:os';
import * as http from 'node:http';
import { randomUUID } from 'node:crypto';
import { spawn, execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// --version の出力はここが元。plugin.json の version と手で揃える
// （claude plugin tag が両者の一致を検証してくれる）。
const VERSION = '1.6.0';

// Node の下限。18 を下回ったら動かさない。
// 18 と 20 はサポート切れなので --help / README では 22 以上を勧めるが、
// 実装が古い API しか使っていない以上、下限自体を上げる必要はない。
const MIN_NODE_MAJOR = 18;
const RECOMMENDED_NODE_MAJOR = 22;

const HELP_TEXT = `richdiff v${VERSION} — md / html の変更をブラウザで見せる

使い方:
  richdiff --proposed <path>=<新内容ファイル> [--proposed ...]
  richdiff --git [<path>...]
  richdiff --git --rev <ref> [<path>...]
  richdiff --pair <変更前ファイル> <変更後ファイル>
  richdiff --manifest <manifest.json>

オプション:
  --view auto|text|markdown|html   表示方法（既定 auto。拡張子から判定）
  --port <n>                       ポート番号（既定は毎回空きポートを探す）
  --no-open                        ブラウザを開かず URL だけ出す
  --server-timeout <秒>            無操作でサーバが終了するまでの秒数（既定 1800）
  --version                        バージョンを表示
  --help                           このヘルプを表示

必要なもの: Node.js ${MIN_NODE_MAJOR} 以上（Node ${RECOMMENDED_NODE_MAJOR} 以上を推奨。
18 と 20 はサポートが切れているため）。依存パッケージはありません。

例:
  richdiff --git
  richdiff --git src/foo.md src/bar.html
  richdiff --pair before.md after.md
  richdiff --proposed docs/spec.md=/tmp/spec.new.md --no-open
`;

// ---- Node バージョン判定 -----------------------------------------------
// テストではわざと古い Node を用意する代わりに、この関数を直接呼んで確かめてよい。
export function checkNodeVersion(versionString) {
  const m = /^v(\d+)\./.exec(versionString || '');
  const major = m ? parseInt(m[1], 10) : 0;
  if (!m || major < MIN_NODE_MAJOR) {
    return {
      ok: false,
      message:
        `richdiff の実行には Node.js ${MIN_NODE_MAJOR} 以上が必要です` +
        `（現在: ${versionString || '不明'}）。Node ${RECOMMENDED_NODE_MAJOR} 以上を推奨します。`,
    };
  }
  return { ok: true };
}

// ---- view / lang の判定 --------------------------------------------------
// text 表示のとき Monaco へ渡す言語 id。わからないものは plaintext に落とす。
const EXT_TO_LANG = {
  '.json': 'json',
  '.yaml': 'yaml',
  '.yml': 'yaml',
  '.js': 'javascript',
  '.mjs': 'javascript',
  '.cjs': 'javascript',
  '.jsx': 'javascript',
  '.ts': 'typescript',
  '.tsx': 'typescript',
  '.py': 'python',
  '.css': 'css',
  '.scss': 'scss',
  '.less': 'less',
  '.xml': 'xml',
  '.sh': 'shell',
  '.bash': 'shell',
  '.go': 'go',
  '.rs': 'rust',
  '.java': 'java',
  '.c': 'c',
  '.h': 'c',
  '.cpp': 'cpp',
  '.cc': 'cpp',
  '.hpp': 'cpp',
  '.cs': 'csharp',
  '.php': 'php',
  '.rb': 'ruby',
  '.sql': 'sql',
  '.toml': 'toml',
  '.ini': 'ini',
  '.txt': 'plaintext',
};

export function inferLangFromExt(ext) {
  return EXT_TO_LANG[ext.toLowerCase()] || 'plaintext';
}

// ラベル（＝ファイルの見せかけ上のパス）の拡張子から、素の view / lang を決める。
// --view で強制されるのは view だけで、lang は常にこの表から決まる
// （text 表示に切り替わっても、Monaco のハイライトは元の言語のままにしたいため）。
export function naturalViewAndLang(label) {
  const ext = path.extname(label).toLowerCase();
  if (ext === '.md' || ext === '.markdown') return { view: 'markdown', lang: 'markdown' };
  if (ext === '.html' || ext === '.htm') return { view: 'html', lang: 'html' };
  return { view: 'text', lang: inferLangFromExt(ext) };
}

export function resolveFile(entry, forcedView) {
  const { view, lang } = naturalViewAndLang(entry.label);
  return {
    label: entry.label,
    before: entry.before,
    after: entry.after,
    view: forcedView && forcedView !== 'auto' ? forcedView : view,
    lang,
  };
}

// ---- 引数パース ----------------------------------------------------------
export function parseArgs(argv) {
  const opts = {
    mode: null,
    proposedPairs: [],
    gitPaths: [],
    gitRev: 'HEAD',
    gitRevExplicit: false,
    pairArgs: [],
    manifestFile: null,
    view: 'auto',
    port: null,
    noOpen: false,
    serverTimeoutSec: 1800,
    help: false,
    version: false,
    // 親から切り離してサーバだけを動かすための内部モード。利用者は指定しない。
    internalServe: false,
    payloadFile: null,
    token: null,
  };

  let i = 0;
  while (i < argv.length) {
    const a = argv[i];
    if (a === '--help' || a === '-h') {
      opts.help = true;
      i += 1;
    } else if (a === '--version' || a === '-v') {
      opts.version = true;
      i += 1;
    } else if (a === '--proposed') {
      const v = argv[i + 1];
      if (v === undefined) throw new Error('--proposed には <path>=<新内容ファイル> が必要です');
      const eq = v.indexOf('=');
      if (eq < 0) throw new Error(`--proposed の指定が不正です（<path>=<新内容ファイル> の形で）: ${v}`);
      opts.proposedPairs.push({ path: v.slice(0, eq), newFile: v.slice(eq + 1) });
      opts.mode = 'proposed';
      i += 2;
    } else if (a === '--git') {
      opts.mode = 'git';
      i += 1;
    } else if (a === '--rev') {
      const v = argv[i + 1];
      if (v === undefined) throw new Error('--rev には ref が必要です');
      opts.gitRev = v;
      opts.gitRevExplicit = true;
      i += 2;
    } else if (a === '--pair') {
      const before = argv[i + 1];
      const after = argv[i + 2];
      if (before === undefined || after === undefined) {
        throw new Error('--pair には <変更前> <変更後> の 2 つが必要です');
      }
      opts.pairArgs = [before, after];
      opts.mode = 'pair';
      i += 3;
    } else if (a === '--manifest') {
      const v = argv[i + 1];
      if (v === undefined) throw new Error('--manifest には json ファイルが必要です');
      opts.manifestFile = v;
      opts.mode = 'manifest';
      i += 2;
    } else if (a === '--view') {
      const v = argv[i + 1];
      if (!['auto', 'text', 'markdown', 'html'].includes(v)) {
        throw new Error(`--view は auto|text|markdown|html のいずれかです: ${v}`);
      }
      opts.view = v;
      i += 2;
    } else if (a === '--port') {
      const v = argv[i + 1];
      const n = parseInt(v, 10);
      if (!v || Number.isNaN(n) || n <= 0) throw new Error(`--port の値が不正です: ${v}`);
      opts.port = n;
      i += 2;
    } else if (a === '--no-open') {
      opts.noOpen = true;
      i += 1;
    } else if (a === '--server-timeout') {
      const v = argv[i + 1];
      const n = parseInt(v, 10);
      if (!v || Number.isNaN(n) || n <= 0) throw new Error(`--server-timeout の値が不正です: ${v}`);
      opts.serverTimeoutSec = n;
      i += 2;
    } else if (a === '--__internal-serve') {
      opts.internalServe = true;
      i += 1;
    } else if (a === '--payload-file') {
      opts.payloadFile = argv[i + 1];
      i += 2;
    } else if (a === '--token') {
      opts.token = argv[i + 1];
      i += 2;
    } else if (opts.mode === 'git' && !a.startsWith('-')) {
      opts.gitPaths.push(a);
      i += 1;
    } else {
      throw new Error(`不明な引数です: ${a}`);
    }
  }
  return opts;
}

// ---- 各モードから files を作る -------------------------------------------

function readFileOrEmpty(p) {
  try {
    return fs.readFileSync(p, 'utf8');
  } catch {
    return '';
  }
}

function buildFromProposed(opts) {
  return opts.proposedPairs.map(({ path: targetPath, newFile }) => {
    // 対象ファイルへの書き込みは一切しない。読むだけ。
    //
    // 見つからない場合は「これから作るファイル」とみなして変更前を空にする。
    // ただし黙って空にしてはいけない。パスを打ち間違えただけ、あるいは相対パスの
    // 基準となるカレントディレクトリが想定と違っただけのときに、「ファイル全体が
    // 新規追加された」という事実と異なる差分がそのまま表示されてしまうため。
    let before = '';
    if (fs.existsSync(targetPath)) {
      before = fs.readFileSync(targetPath, 'utf8');
    } else {
      process.stderr.write(
        `注意: ${targetPath} が見つかりません。新規作成とみなし、変更前を空として表示します。\n` +
        `      相対パスは実行時のカレントディレクトリ（${process.cwd()}）から解決されます。\n`
      );
    }
    const after = fs.readFileSync(newFile, 'utf8');
    return { label: targetPath, before, after };
  });
}

function buildFromPair(opts) {
  const [beforePath, afterPath] = opts.pairArgs;
  const before = fs.readFileSync(beforePath, 'utf8');
  const after = fs.readFileSync(afterPath, 'utf8');
  return [{ label: afterPath, before, after }];
}

function buildFromManifest(opts) {
  const raw = fs.readFileSync(opts.manifestFile, 'utf8');
  const list = JSON.parse(raw);
  if (!Array.isArray(list)) throw new Error('--manifest の JSON はファイルの配列である必要があります');
  return list.map((entry) => {
    const before = entry.beforeFile ? fs.readFileSync(entry.beforeFile, 'utf8') : '';
    const after = fs.readFileSync(entry.afterFile, 'utf8');
    return { label: entry.label, before, after };
  });
}

// git のサブコマンドは、ここでは「失敗したら空扱い／未コミット扱いにする」という
// 想定済みの分岐でしか使わない。失敗時の stderr（git 自身が出す不安げな文言）を
// そのまま利用者の画面に漏らさないよう、標準エラーは捨てる。
const GIT_STDIO = ['ignore', 'pipe', 'ignore'];

function gitShowOrEmpty(rev, targetPath) {
  try {
    return execFileSync('git', ['show', `${rev}:${targetPath}`], {
      encoding: 'utf8',
      stdio: GIT_STDIO,
    });
  } catch {
    // 新規ファイルなど、その版に存在しないものは before を空文字にする
    return '';
  }
}

function gitHasUncommittedChange(rev, targetPath) {
  // 追跡外（新規）ファイルは常に「未コミットの変更」扱い
  try {
    const tracked = execFileSync('git', ['ls-files', '--error-unmatch', '--', targetPath], {
      encoding: 'utf8',
      stdio: GIT_STDIO,
    });
    if (!tracked.trim()) return true;
  } catch {
    return true;
  }
  try {
    execFileSync('git', ['diff', '--quiet', rev, '--', targetPath], { stdio: GIT_STDIO });
    return false; // 差分なし
  } catch {
    return true; // diff --quiet は差分があると非 0 で終わる
  }
}

function listChangedPaths(rev) {
  const changed = execFileSync('git', ['diff', '--name-only', rev, '--'], { encoding: 'utf8' })
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);
  const untracked = execFileSync('git', ['ls-files', '--others', '--exclude-standard'], {
    encoding: 'utf8',
  })
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean);
  return Array.from(new Set([...changed, ...untracked]));
}

function buildFromGit(opts) {
  const rev = opts.gitRev;
  const targets = opts.gitPaths.length > 0 ? opts.gitPaths : listChangedPaths(rev);

  // --rev を省略した（＝ HEAD 比較の）とき、対象ファイルに未コミットの変更が
  // あるなら、「作業前からの変更も混ざっているかもしれない」と一度だけ知らせる。
  // 誰がいつ入れた変更かはここでは区別できないので、可能性の指摘にとどめる。
  if (!opts.gitRevExplicit) {
    const anyUncommitted = targets.some((p) => gitHasUncommittedChange(rev, p));
    if (anyUncommitted) {
      process.stderr.write(
        '警告: 対象ファイルには未コミットの変更があります。作業前からの変更も差分に含まれている可能性があります。\n'
      );
    }
  }

  return targets.map((targetPath) => {
    const before = gitShowOrEmpty(rev, targetPath);
    const after = readFileOrEmpty(targetPath);
    return { label: targetPath, before, after };
  });
}

export function buildFiles(opts) {
  let raw;
  if (opts.mode === 'proposed') raw = buildFromProposed(opts);
  else if (opts.mode === 'pair') raw = buildFromPair(opts);
  else if (opts.mode === 'manifest') raw = buildFromManifest(opts);
  else if (opts.mode === 'git') raw = buildFromGit(opts);
  else throw new Error('モードを 1 つ指定してください（--proposed / --git / --pair / --manifest）');

  return raw.map((entry) => resolveFile(entry, opts.view));
}

// ---- 空きポート -----------------------------------------------------------
function pickPort(explicitPort) {
  if (explicitPort) return Promise.resolve(explicitPort);
  return new Promise((resolve, reject) => {
    const probe = http.createServer();
    probe.on('error', reject);
    probe.listen(0, '127.0.0.1', () => {
      const { port } = probe.address();
      probe.close(() => resolve(port));
    });
  });
}

// ---- サーバが待ち受けを始めるのを待つ ---------------------------------------
// 切り離した子プロセスは spawn した直後にはまだ bind していない。ここを待たずに
// URL を出してブラウザを開くと、接続を拒否されて空のタブになる（実測で 1 回目が
// ECONNREFUSED、400ms 後に 200）。待ち受けが始まったことを確かめてから先へ進む。
// トークンを付けずに叩けば 403 が返るので、中身を取らずに生死だけ確かめられる。
function waitForServer(port, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  return new Promise((resolve) => {
    const attempt = () => {
      const req = http.get({ host: '127.0.0.1', port: port, path: '/payload.json' }, (res) => {
        res.resume();
        resolve(true);
      });
      req.on('error', () => {
        if (Date.now() >= deadline) { resolve(false); return; }
        setTimeout(attempt, 60);
      });
      req.setTimeout(1000, () => req.destroy());
    };
    attempt();
  });
}

// ---- ブラウザを開く --------------------------------------------------------
function openBrowser(url) {
  // 既定ブラウザで開く。失敗しても異常終了にはしない（URL は常に標準出力に出ているので、
  // それを人が拾えばよい）。
  try {
    let child;
    if (process.platform === 'darwin') {
      child = spawn('open', [url], { stdio: 'ignore', detached: true });
    } else if (process.platform === 'win32') {
      child = spawn('cmd', ['/c', 'start', '""', url], { stdio: 'ignore', detached: true, shell: false });
    } else {
      child = spawn('xdg-open', [url], { stdio: 'ignore', detached: true });
    }
    child.on('error', () => {});
    child.unref();
  } catch {
    // 開けなくても致命的ではない
  }
}

// ---- サーバ本体（切り離された子プロセスで動く側） --------------------------
function runServer(opts) {
  const selfPath = fileURLToPath(import.meta.url);
  const webIndexPath = path.join(path.dirname(selfPath), '..', 'web', 'index.html');

  let payloadJson;
  try {
    payloadJson = fs.readFileSync(opts.payloadFile, 'utf8');
  } catch {
    payloadJson = JSON.stringify({ files: [] });
  }
  // 読み終わったら一時ファイルは不要なので消す
  try {
    fs.unlinkSync(opts.payloadFile);
  } catch {
    // 消せなくても致命的ではない
  }

  let idleTimer = null;
  const armIdleTimer = () => {
    if (idleTimer) clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      server.close(() => process.exit(0));
    }, opts.serverTimeoutSec * 1000);
  };

  const server = http.createServer((req, res) => {
    armIdleTimer();
    let u;
    try {
      u = new URL(req.url, 'http://127.0.0.1');
    } catch {
      res.writeHead(400);
      res.end('Bad Request');
      return;
    }

    if (u.pathname === '/') {
      fs.readFile(webIndexPath, (err, data) => {
        if (err) {
          res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
          res.end('index.html を読み込めませんでした');
          return;
        }
        res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(data);
      });
      return;
    }

    if (u.pathname === '/payload.json') {
      const t = u.searchParams.get('token');
      if (t !== opts.token) {
        res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
        res.end('403 Forbidden');
        return;
      }
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      res.end(payloadJson);
      return;
    }

    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Not Found');
  });

  // 127.0.0.1 だけに bind する。0.0.0.0 にすると同じ Wi-Fi の他人からも
  // 仕様書の中身が読めてしまうため。
  server.listen(opts.port, '127.0.0.1', () => {
    armIdleTimer();
  });
}

// ---- 通常モード（サーバを立てて即終了する側） -------------------------------
async function main(argv) {
  const opts = parseArgs(argv);

  if (opts.internalServe) {
    runServer(opts);
    return; // このプロセスは終了せず、サーバとして生き続ける
  }

  if (opts.help) {
    process.stdout.write(HELP_TEXT);
    return;
  }
  if (opts.version) {
    process.stdout.write(`${VERSION}\n`);
    return;
  }

  const nodeCheck = checkNodeVersion(process.version);
  if (!nodeCheck.ok) {
    process.stderr.write(`${nodeCheck.message}\n`);
    process.exitCode = 1;
    return;
  }

  const files = buildFiles(opts);
  if (files.length === 0) {
    process.stderr.write('差分の対象ファイルがありません。\n');
    process.exitCode = 1;
    return;
  }

  const token = randomUUID();
  const port = await pickPort(opts.port);

  const payloadPath = path.join(os.tmpdir(), `richdiff-payload-${token}.json`);
  // 一時ディレクトリは他の利用者からも見える。サーバが読んだ直後に消しているとはいえ、
  // その一瞬のあいだ文書の中身が置かれるので、自分だけが読める権限で書く。
  fs.writeFileSync(payloadPath, JSON.stringify({ files }), { encoding: 'utf8', mode: 0o600 });

  const selfPath = fileURLToPath(import.meta.url);
  const child = spawn(
    process.execPath,
    [
      selfPath,
      '--__internal-serve',
      '--port',
      String(port),
      '--token',
      token,
      '--payload-file',
      payloadPath,
      '--server-timeout',
      String(opts.serverTimeoutSec),
    ],
    { detached: true, stdio: 'ignore' }
  );
  // CLI 本体はサーバを抱えたまま待たない。切り離して即終了する。
  // ここで待つと呼び出し側のターミナルが止まってしまう。
  child.unref();

  // ただし「待ち受けが始まったこと」だけは確かめる。ここを飛ばすと、開いた
  // ブラウザのほうが先に着いて接続を拒否され、空のタブが出る。
  if (!(await waitForServer(port, 8000))) {
    process.stderr.write('サーバの待ち受けを確認できませんでした。時間をおいて試してください。\n');
    process.exitCode = 1;
    return;
  }

  const url = `http://127.0.0.1:${port}/?token=${token}`;
  if (!opts.noOpen) {
    openBrowser(url);
  }

  const first = files[0].label;
  const countText = files.length > 1 ? `（${files.length} 件: ${first} ほか${files.length - 1}件）` : `（1 件: ${first}）`;
  const prefix = opts.noOpen ? 'URL' : '差分をブラウザで開きました';
  process.stdout.write(`${prefix}: ${url}  ${countText}\n`);
}

// このファイルを直接実行したときだけ main を動かす。import されただけなら
// 何も実行しない（テストから checkNodeVersion 等を直接呼べるようにするため）。
const isMainModule = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMainModule) {
  main(process.argv.slice(2)).catch((err) => {
    process.stderr.write(`エラー: ${err && err.message ? err.message : err}\n`);
    process.exitCode = 1;
  });
}
