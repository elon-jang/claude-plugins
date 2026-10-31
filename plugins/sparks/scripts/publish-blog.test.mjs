import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { assertPreserved, normalizeRoute, postRoutes, validateLinks, publish } from './publish-blog.mjs';

test('same count with a replaced post fails preservation', () => {
  assert.throws(() => assertPreserved(['/posts/old'], new Set(['/posts/new'])), /old/);
});

test('encoded Korean, trailing slash and index.html identify the same route', () => {
  assert.equal(normalizeRoute('/posts/%ED%95%9C%EA%B8%80/index.html'), normalizeRoute('/posts/한글/'));
  assert.deepEqual(postRoutes('<a href="posts/old/index.html">old</a><a href="/posts/new/">new</a>'), ['/posts/old', '/posts/new']);
});

test('asset and private page removal are blocked by inventory comparison', () => {
  assert.throws(() => assertPreserved(['/private/posts/old', '/image.png'], new Set(['/posts/new'])), /private/);
});

test('broken image stops verification', t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sparks-test-'));
  t.after(() => fs.rmSync(dir, { recursive: true }));
  fs.writeFileSync(path.join(dir, 'index.html'), '<img src="missing.png">');
  assert.throws(() => validateLinks(dir), /Broken local link/);
});

for (const all of [false, true]) {
  test(`partial source cannot silently shrink manifest (all=${all})`, t => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sparks-test-'));
    t.after(() => fs.rmSync(dir, { recursive: true }));
    fs.mkdirSync(path.join(dir, 'blog'));
    fs.writeFileSync(path.join(dir, 'blog/new.md'), '# New\n');
    const manifest = '[{"file":"old.md","access":"public"}]';
    fs.writeFileSync(path.join(dir, 'published.json'), manifest);
    const result = spawnSync(process.execPath, [fileURLToPath(new URL('./build-blog.mjs', import.meta.url)),
      '--source', path.join(dir, 'blog'), '--output', path.join(dir, 'out'),
      '--manifest', path.join(dir, 'published.json'), ...(all ? ['--all'] : ['--files', 'new.md'])], { encoding: 'utf8' });
    assert.notEqual(result.status, 0);
    assert.match(result.stderr, /Published source missing/);
    assert.equal(fs.readFileSync(path.join(dir, 'published.json'), 'utf8'), manifest);
  });
}

test('adding one post builds existing public and private posts and preserves access', t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sparks-test-'));
  t.after(() => fs.rmSync(dir, { recursive: true }));
  fs.mkdirSync(path.join(dir, 'blog'));
  for (const name of ['old', 'secret', 'new']) fs.writeFileSync(path.join(dir, `blog/${name}.md`), `# ${name}\n`);
  fs.writeFileSync(path.join(dir, 'published.json'), JSON.stringify([
    { file: 'old.md', access: 'public' }, { file: 'secret.md', access: 'private' },
  ]));
  const result = spawnSync(process.execPath, [fileURLToPath(new URL('./build-blog.mjs', import.meta.url)),
    '--source', path.join(dir, 'blog'), '--output', path.join(dir, 'out'),
    '--manifest', path.join(dir, 'published.json'), '--files', 'new.md'], { encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
  for (const p of ['posts/old/index.html', 'private/posts/secret/index.html', 'posts/new/index.html']) {
    assert.ok(fs.existsSync(path.join(dir, 'out', p)));
  }
  assert.equal(JSON.parse(fs.readFileSync(path.join(dir, 'published.json'))).length, 3);
});

for (const missing of [false, true]) {
  test(`CLI dry run checks live paths without updating manifest (missing=${missing})`, async t => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'sparks-test-'));
    const originalFetch = globalThis.fetch;
    t.after(() => { globalThis.fetch = originalFetch; fs.rmSync(dir, { recursive: true }); });
    fs.mkdirSync(path.join(dir, '.sparks'));
    fs.mkdirSync(path.join(dir, 'blog'));
    fs.writeFileSync(path.join(dir, '.sparks/config.json'), JSON.stringify({ publish: {
      projectName: 'test', branch: 'production', url: 'https://example.invalid',
    }}));
    const manifest = '[{"file":"old.md","access":"public"}]';
    fs.writeFileSync(path.join(dir, '.sparks/published.json'), manifest);
    for (const name of ['old', 'new']) fs.writeFileSync(path.join(dir, `blog/${name}.md`), `# ${name}\n`);
    globalThis.fetch = async url => new URL(url).pathname === '/sparks-inventory.json'
      ? new Response('', { status: 404 })
      : new Response(`<a href="posts/${missing ? 'absent' : 'old'}/index.html">post</a>`);
    const args = ['--repo', dir, '--files', 'new.md'];
    if (missing) await assert.rejects(publish(args), /Existing paths missing/);
    else assert.equal((await publish(args)).posts, 2);
    assert.equal(fs.readFileSync(path.join(dir, '.sparks/published.json'), 'utf8'), manifest);
    assert.ok(!fs.existsSync(path.join(dir, '.sparks/publish.lock')));
  });
}
