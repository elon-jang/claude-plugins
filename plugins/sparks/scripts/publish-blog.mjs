#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { parseArgs } from 'node:util';
import { spawnSync } from 'node:child_process';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const readJson = p => JSON.parse(fs.readFileSync(p, 'utf8'));

export function normalizeRoute(value) {
  const url = new URL(value, 'https://blog.invalid/');
  return decodeURIComponent(url.pathname).normalize('NFC').replace(/index\.html$/, '').replace(/\/$/, '') || '/';
}

export function postRoutes(html) {
  return [...html.matchAll(/href=["']([^"']+)["']/g)]
    .map(m => m[1]).filter(p => /^(?:\/)?posts\//.test(p)).map(normalizeRoute);
}

export function assertPreserved(previous, next) {
  const missing = [...new Set(previous)].filter(p => !next.has(p));
  if (missing.length) throw new Error(`Existing paths missing (${missing.length}):\n${missing.join('\n')}`);
}

function filesUnder(root, dir = root) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const p = path.join(dir, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`Symlink not allowed in build: ${p}`);
    return entry.isDirectory() ? filesUnder(root, p) : [path.relative(root, p)];
  });
}

export function validateLinks(output) {
  const files = filesUnder(output);
  for (const file of files.filter(f => f.endsWith('.html'))) {
    const html = fs.readFileSync(path.join(output, file), 'utf8');
    for (const [, raw] of html.matchAll(/(?:href|src)=["']([^"']+)["']/g)) {
      if (/^(?:[a-z][a-z\d+.-]*:|\/\/|#)/i.test(raw)) continue;
      const resolved = new URL(raw.replaceAll('&amp;', '&'), `https://blog.invalid/${file}`);
      const rel = decodeURIComponent(resolved.pathname).slice(1);
      const target = path.resolve(output, rel);
      if (target !== path.resolve(output) && !target.startsWith(path.resolve(output) + path.sep)) throw new Error(`Invalid link: ${file}: ${raw}`);
      if (!fs.existsSync(target) || (fs.statSync(target).isDirectory() && !fs.existsSync(path.join(target, 'index.html')))) {
        throw new Error(`Broken local link: ${file}: ${raw}`);
      }
    }
  }
  return files;
}

function run(command, args, cwd) {
  const result = spawnSync(command, args, { cwd, stdio: 'inherit' });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`${command} failed (${result.status})`);
}

async function get(url) {
  const response = await fetch(url, { signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`Baseline fetch failed: ${url} (${response.status})`);
  return response.text();
}

export async function publish(args = process.argv.slice(2)) {
  const { values } = parseArgs({ args, options: {
    repo: { type: 'string' }, files: { type: 'string' }, all: { type: 'boolean' },
    deploy: { type: 'boolean' }, bootstrap: { type: 'boolean' },
  }});
  const configuredRepo = values.repo || readJson(path.join(os.homedir(), '.sparks/config.json')).defaultRepo;
  if (!configuredRepo) throw new Error('Specify --repo <knowledge repository>');
  const repo = fs.realpathSync(configuredRepo.replace(/^~(?=\/|$)/, os.homedir()));
  const state = path.join(repo, '.sparks');
  const configPath = path.join(state, 'config.json');
  const config = readJson(configPath);
  const { projectName, branch, url } = config.publish || {};
  if (!projectName || !branch || !url || new URL(url).protocol !== 'https:') {
    throw new Error('publish.projectName, branch and HTTPS url are required in repository config');
  }
  const manifestPath = path.join(state, 'published.json');
  const original = readJson(manifestPath);
  if (!Array.isArray(original)) throw new Error('Manifest must be an array');
  const source = path.join(repo, 'blog');
  const sourceFiles = fs.readdirSync(source).filter(f => f.endsWith('.md'));
  const entries = new Map();
  const add = entry => {
    const e = typeof entry === 'string' ? { file: entry, access: 'public' } : entry;
    if (!e || path.basename(e.file || '') !== e.file || !e.file.endsWith('.md') || !['public', 'private'].includes(e.access)) {
      throw new Error(`Invalid manifest entry: ${JSON.stringify(e)}`);
    }
    entries.set(e.file, e);
  };
  original.forEach(add);
  if (values.all) sourceFiles.forEach(file => { if (!entries.has(file)) add({ file, access: 'public' }); });
  if (values.files) values.files.split(',').forEach(s => {
    const [file, access] = s.trim().split(':');
    add({ file, access: access || entries.get(file)?.access || 'public' });
  });
  for (const file of entries.keys()) if (!sourceFiles.includes(file)) throw new Error(`Published source missing: ${file}`);

  const lock = path.join(state, 'publish.lock');
  const fd = fs.openSync(lock, 'wx');
  let stage;
  try {
    stage = fs.mkdtempSync(path.join(state, 'publish-'));
    const stagedManifest = path.join(stage, 'published.json');
    fs.writeFileSync(stagedManifest, JSON.stringify([...entries.values()], null, 2) + '\n');
    // The builder locates static assets next to its manifest.
    if (fs.existsSync(path.join(state, 'static'))) fs.cpSync(path.join(state, 'static'), path.join(stage, 'static'), { recursive: true });
    const output = path.join(stage, 'site');
    run(process.execPath, [path.join(scriptDir, 'build-blog.mjs'), '--source', source, '--output', output,
      '--manifest', stagedManifest, '--config', configPath], repo);
    const files = validateLinks(output);
    const routes = new Set(files.map(f => normalizeRoute('/' + f)));
    const baselineUrl = new URL(url);
    const indexUrl = new URL('/', baselineUrl);
    let baseline;
    try { baseline = await get(indexUrl); }
    catch (error) {
      if (!values.bootstrap || !values.deploy || original.length) throw error;
      console.log('Explicit bootstrap: no deployed baseline.');
    }
    if (baseline !== undefined) {
      const oldPosts = postRoutes(baseline);
      if (!oldPosts.length) throw new Error('No posts found in live index; cannot verify baseline');
      assertPreserved(oldPosts, routes);
      // New deployments expose every asset, including private and unlisted pages.
      const response = await fetch(new URL('/sparks-inventory.json', baselineUrl), { signal: AbortSignal.timeout(30000) });
      if (response.ok && response.headers.get('content-type')?.includes('application/json')) {
        const inventory = await response.json();
        if (inventory.version !== 1 || !Array.isArray(inventory.paths)) throw new Error('Invalid live inventory');
        assertPreserved(inventory.paths, routes);
      } else if (response.status === 404 || response.ok) {
        console.log('Legacy baseline: checking public index; no asset inventory available.');
      } else throw new Error(`Inventory fetch failed (${response.status})`);
      console.log(`Preserved ${oldPosts.length} existing public post paths.`);
    }
    fs.writeFileSync(path.join(output, 'sparks-inventory.json'), JSON.stringify({ version: 1, paths: [...routes].sort() }));
    console.log(`Validated ${entries.size} posts / ${files.length} files. Build: ${output}`);
    if (!values.deploy) return { output, posts: entries.size };
    // Recheck the baseline just before upload; shared CI must also serialize this project.
    if (baseline !== undefined && await get(indexUrl) !== baseline) throw new Error('Live index changed during build. Retry with latest repository.');
    run('wrangler', ['pages', 'deploy', output, '--project-name', projectName, '--branch', branch,
      '--commit-dirty=true', '--commit-message', 'deploy: Sparks full site'], repo);
    fs.renameSync(stagedManifest, manifestPath);
    console.log(`Deployment command succeeded: ${url}. Keep the build for review and recovery.`);
    return { output, posts: entries.size };
  } finally {
    fs.closeSync(fd);
    fs.unlinkSync(lock);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  publish().catch(error => { console.error(error.message); process.exitCode = 1; });
}
