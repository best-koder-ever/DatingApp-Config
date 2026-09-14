#!/usr/bin/env node
const { spawn } = require('child_process');
const fs = require('fs');

const args = process.argv.slice(2);
const get = (flag, dflt) => {
  const i = args.indexOf(flag);
  return i >= 0 ? args[i + 1] : dflt;
};

const projectId = get('--project', '');
const batchesPath = get('--batches', '');
if (!projectId || !batchesPath) {
  console.error('Usage: stitch_generate_grids.js --project <id> --batches <batches.json>');
  process.exit(1);
}

const batches = JSON.parse(fs.readFileSync(batchesPath, 'utf8'));
const outPath = batchesPath.replace(/batches\.json$/, 'generated.json');
let generated = fs.existsSync(outPath) ? JSON.parse(fs.readFileSync(outPath, 'utf8')) : [];
const done = new Set(generated.map(x => x.index));

function textOf(r) {
  return (r.result && r.result.content || [])
    .filter(c => c.type === 'text')
    .map(c => c.text)
    .join('\n');
}

function extractScreens(response) {
  const text = textOf(response);
  try {
    const parsed = JSON.parse(text);
    const screens = [];
    for (const comp of parsed.outputComponents || []) {
      for (const screen of (((comp.design || {}).screens) || [])) screens.push(screen);
    }
    return screens;
  } catch {
    return [];
  }
}

async function run() {
  const { default: readline } = await import('readline');
  const child = spawn('stitch-mcp', ['proxy'], { env: process.env });
  child.stderr.on('data', d => process.stderr.write(d));

  const rl = readline.createInterface({ input: child.stdout });
  let id = 0;
  const pending = {};
  rl.on('line', line => {
    try {
      const msg = JSON.parse(line);
      if (msg.id && pending[msg.id]) {
        pending[msg.id](msg);
        delete pending[msg.id];
      }
    } catch {}
  });

  const call = (method, params, timeout = 60000) => new Promise((resolve, reject) => {
    const mid = ++id;
    pending[mid] = resolve;
    child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: mid, method, params }) + '\n');
    setTimeout(() => {
      if (pending[mid]) {
        delete pending[mid];
        reject(new Error(`timeout ${method}`));
      }
    }, timeout);
  });

  await call('initialize', {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'stitch-generate-bot-grids', version: '1.0' },
  });
  await call('notifications/initialized', {});

  try {
    for (const batch of batches) {
      if (done.has(batch.index)) {
        console.log(`skip batch ${batch.index}: already generated`);
        continue;
      }
      console.log(`generating batch ${batch.index} (${batch.personas.join(', ')})`);
      const response = await call('tools/call', {
        name: 'generate_screen_from_text',
        arguments: {
          projectId,
          prompt: batch.prompt,
          deviceType: 'AGNOSTIC',
          modelId: 'GEMINI_3_8_FLASH',
        },
      }, 360000);
      const screens = extractScreens(response);
      if (!screens.length) throw new Error(`batch ${batch.index} returned no screens`);
      const screen = screens[0];
      generated.push({
        index: batch.index,
        personas: batch.personas,
        screen: screen.name,
        title: screen.title,
        prompt: screen.prompt,
        width: Number(screen.width || 0),
        height: Number(screen.height || 0),
        downloadUrl: (screen.screenshot || {}).downloadUrl,
      });
      fs.writeFileSync(outPath, JSON.stringify(generated, null, 2));
      console.log(`generated batch ${batch.index}: ${screen.name}`);
    }
  } finally {
    child.kill();
  }
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
