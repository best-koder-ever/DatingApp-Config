#!/usr/bin/env node
/**
 * stitch-photo-fetch.js — Download rendered screenshots from a Stitch project.
 *
 * Uses the local stitch-mcp proxy (which handles OAuth/token refresh) as a
 * stdio MCP client, then pulls each screen's screenshot via get_screen.
 * Output is a full rendered UI screen (Stitch renders designs, not raw
 * portraits) — for bot profile photos you'd typically crop the portrait
 * region, or use a screen designed to BE the profile photo.
 *
 * Usage:
 *   STITCH_API_KEY=<key> CLOUDSDK_CONFIG=~/.stitch-mcp/config \
 *     node scripts/stitch-photo-fetch.js --project <projectId> \
 *       [--out Personas/photos/pilot] [--prefix elsa] [--max 5]
 */
const { spawn, execSync } = require('child_process');
const readline = require('readline');
const path = require('path');

const args = process.argv.slice(2);
const get = (flag, dflt) => { const i = args.indexOf(flag); return i >= 0 ? args[i + 1] : dflt; };
const PROJECT = get('--project', '');
const OUT = get('--out', 'Personas/photos/pilot');
const PREFIX = get('--prefix', 'stitch');
const MAX = parseInt(get('--max', '10'), 10) || 10;

if (!PROJECT) { console.error('Usage: --project <id> [--out dir] [--prefix name] [--max N]'); process.exit(1); }

const child = spawn('stitch-mcp', ['proxy'], { env: process.env });
child.stderr.on('data', d => process.stderr.write(d));
const rl = readline.createInterface({ input: child.stdout });
let id = 0; const pending = {};
rl.on('line', line => { line = line.trim(); if (!line) return; try { const m = JSON.parse(line); if (m.id && pending[m.id]) { pending[m.id](m); delete pending[m.id]; } } catch (e) {} });
function call(method, params) {
  return new Promise((res, rej) => {
    const mid = ++id; pending[mid] = res;
    child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: mid, method, params }) + '\n');
    setTimeout(() => { if (pending[mid]) { delete pending[mid]; rej(new Error('timeout ' + method)); } }, 120000);
  });
}
function textOf(r) { return (r.result && r.result.content || []).filter(c => c.type === 'text').map(c => c.text).join('\n'); }
const sleep = ms => new Promise(r => setTimeout(r, ms));
function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) || 'screen'; }

(async () => {
  const fs = require('fs');
  fs.mkdirSync(OUT, { recursive: true });
  await call('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'stitch-photo-fetch', version: '1.0' } });
  await call('notifications/initialized', {});

  let j = null;
  for (let i = 0; i < 4 && !j; i++) {
    try { j = JSON.parse(textOf(await call('tools/call', { name: 'get_project', arguments: { name: 'projects/' + PROJECT } }))); }
    catch (e) { console.log(`get_project attempt ${i} failed, retrying...`); await sleep(4000); }
  }
  if (!j) { console.error('❌ get_project unavailable for', PROJECT); child.kill(); process.exit(1); }
  const proj = j.project || j;
  const instances = proj.screenInstances || [];
  console.log(`Project "${proj.title || PROJECT}" — ${instances.length} screen instances`);

  let n = 0;
  for (const inst of instances) {
    const screenName = inst.sourceScreen || inst.name;
    if (!screenName) continue;
    try {
      const scr = JSON.parse(textOf(await call('tools/call', { name: 'get_screen', arguments: { name: screenName } })));
      const s = scr.screen || scr;
      const shot = s.screenshot || s.thumbnailScreenshot || {};
      const file = path.join(OUT, `${PREFIX}_${String(n + 1).padStart(2, '0')}_${slug(s.title || 'screen')}.png`);
      if (shot.downloadUrl) {
        execSync(`curl -sSL "${shot.downloadUrl}" -o "${file}"`);
        console.log(`  ✅ ${file}  (${s.width}x${s.height})`);
        n++;
      } else {
        console.log(`  ⚠️  no screenshot for ${screenName}`);
      }
    } catch (e) { console.log(`  ⚠️  ${screenName}: ${e.message.slice(0, 80)}`); }
    if (n >= MAX) break;
    await sleep(1500);
  }
  console.log(`Done — ${n} screenshots in ${OUT}`);
  child.kill(); process.exit(0);
})().catch(e => { console.error('FAIL', e.message); child.kill(); process.exit(1); });
