#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { parseArgs } from 'util';
import matter from 'gray-matter';
import { marked } from 'marked';

// --- CLI Args ---
const { values } = parseArgs({
  options: {
    source: { type: 'string', short: 's' },
    output: { type: 'string', short: 'o' },
    manifest: { type: 'string', short: 'm' },
    files: { type: 'string', short: 'f' },
    all: { type: 'boolean', default: false },
    config: { type: 'string', short: 'c' },
    draft: { type: 'string', short: 'd' },
  },
});

const SOURCE_DIR = values.source;
const OUTPUT_DIR = values.output;
const MANIFEST_PATH = values.manifest;
const selectedFiles = values.files ? values.files.split(',').map(f => f.trim()) : null;
const buildAll = values.all || false;
const draftFile = values.draft || null;

if (!SOURCE_DIR || !OUTPUT_DIR || !MANIFEST_PATH) {
  console.error('Usage: node build-blog.mjs --source <blog-dir> --output <build-dir> --manifest <published.json> [--files f1.md,f2.md:private | --all] [--config <config.json>]');
  process.exit(1);
}

// --- Site config (from .sparks/config.json) ---
let siteConfig = { title: 'Blog', description: '' };
if (values.config && fs.existsSync(values.config)) {
  try {
    const cfg = JSON.parse(fs.readFileSync(values.config, 'utf-8'));
    if (cfg.publish?.title) siteConfig.title = cfg.publish.title;
    if (cfg.publish?.description) siteConfig.description = cfg.publish.description;
  } catch { /* ignore parse errors */ }
}

// --- Marked config (GFM) ---
marked.setOptions({ gfm: true, breaks: true });

// --- Helpers ---
function toDateStr(val, fallback) {
  if (!val) return fallback || '';
  if (val instanceof Date) {
    return val.toISOString().substring(0, 10);
  }
  const s = String(val);
  const m = s.match(/\d{4}-\d{2}-\d{2}/);
  return m ? m[0] : fallback || '';
}

function parsePost(filename, { access = 'public', baseDir } = {}) {
  const dir = baseDir || SOURCE_DIR;
  const raw = fs.readFileSync(path.join(dir, filename), 'utf-8');
  const dateMatch = filename.match(/^(\d{4}-\d{2}-\d{2})/);
  const dateFallback = dateMatch ? dateMatch[1] : '';
  let data = {}, content = raw;
  try {
    const parsed = matter(raw);
    data = parsed.data;
    content = parsed.content;
  } catch {
    const fmMatch = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    if (fmMatch) {
      content = fmMatch[2];
      const titleMatch = fmMatch[1].match(/^title:\s*"?(.+?)"?\s*$/m);
      const dateM = fmMatch[1].match(/^date:\s*"?(\d{4}-\d{2}-\d{2})"?\s*$/m);
      const tagsMatch = fmMatch[1].match(/^tags:\s*\[(.+)\]\s*$/m);
      if (titleMatch) data.title = titleMatch[1];
      if (dateM) data.date = dateM[1];
      if (tagsMatch) data.tags = tagsMatch[1].split(',').map(t => t.trim());
    }
  }
  return {
    filename,
    slug: filename.replace(/\.md$/, ''),
    title: data.title || filename.replace(/\.md$/, '').replace(/^\d{4}-\d{2}-\d{2}-/, '').replace(/-/g, ' '),
    date: toDateStr(data.date, dateFallback),
    tags: data.tags || [],
    access: access || 'public',
    content,
  };
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T00:00:00');
  if (isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// --- Manifest ---
// Format: [{ file: "name.md", access: "public"|"private" }, ...]
// Legacy format (string array) is auto-migrated to public
function loadManifest() {
  if (fs.existsSync(MANIFEST_PATH)) {
    const raw = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8'));
    if (!Array.isArray(raw)) return [];
    return raw.map(entry =>
      typeof entry === 'string' ? { file: entry, access: 'public' } : entry
    );
  }
  return [];
}

function saveManifest(entries) {
  const dir = path.dirname(MANIFEST_PATH);
  fs.mkdirSync(dir, { recursive: true });
  const unique = [...new Map(entries.map(e => [e.file, e])).values()]
    .sort((a, b) => a.file.localeCompare(b.file));
  fs.writeFileSync(MANIFEST_PATH, JSON.stringify(unique, null, 2) + '\n');
}

// --- CSS ---
const CSS = `/* Sparks Blog */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #fafafa;
  --bg-secondary: #ffffff;
  --text: #1a1a1a;
  --text-secondary: #6b7280;
  --text-tertiary: #9ca3af;
  --accent: #2563eb;
  --accent-hover: #1d4ed8;
  --border: #e5e7eb;
  --border-light: #f3f4f6;
  --code-bg: #f3f4f6;
  --tag-bg: #eff6ff;
  --tag-text: #2563eb;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-hover: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
  --radius: 12px;
  --search-bg: #ffffff;
  --search-focus: #2563eb;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f0f0f;
    --bg-secondary: #1a1a1a;
    --text: #f0f0f0;
    --text-secondary: #9ca3af;
    --text-tertiary: #6b7280;
    --accent: #60a5fa;
    --accent-hover: #93bbfd;
    --border: #2a2a2a;
    --border-light: #222222;
    --code-bg: #1e1e1e;
    --tag-bg: #1e293b;
    --tag-text: #60a5fa;
    --shadow: 0 1px 3px rgba(0,0,0,0.2);
    --shadow-hover: 0 4px 12px rgba(0,0,0,0.3);
    --search-bg: #1a1a1a;
    --search-focus: #60a5fa;
  }
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.8;
  word-break: keep-all;
  -webkit-font-smoothing: antialiased;
}

.container {
  max-width: 680px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

/* Header */
.site-header {
  text-align: center;
  padding: 3.5rem 0 2.5rem;
  margin-bottom: 2rem;
}
.site-header h1 {
  font-size: 1.6rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--text);
}
.site-header p {
  color: var(--text-tertiary);
  margin-top: 0.5rem;
  font-size: 0.88rem;
  font-weight: 300;
  letter-spacing: 0.02em;
}

/* Search */
.search-wrap {
  position: relative;
  margin-bottom: 2rem;
}
.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-tertiary);
  pointer-events: none;
  width: 16px;
  height: 16px;
}
.search-input {
  width: 100%;
  padding: 0.7rem 1rem 0.7rem 2.5rem;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--search-bg);
  color: var(--text);
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-input::placeholder {
  color: var(--text-tertiary);
}
.search-input:focus {
  border-color: var(--search-focus);
  box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
}
.search-clear {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  display: none;
  padding: 2px;
}
.search-clear:hover { color: var(--text-secondary); }
.search-empty {
  text-align: center;
  color: var(--text-tertiary);
  padding: 3rem 1rem;
  font-size: 0.9rem;
  display: none;
}

/* Stats bar */
.stats-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--text-tertiary);
  font-size: 0.8rem;
  margin-bottom: 1.5rem;
  padding: 0 0.25rem;
}
.stats-count { font-variant-numeric: tabular-nums; }

/* Index */
.month-group { margin-bottom: 1.5rem; }
.month-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.6rem;
  padding: 0 0.25rem;
}
.post-item {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  padding: 0.75rem 1rem;
  margin: 0 -0.25rem;
  border-radius: 10px;
  transition: background 0.15s;
  cursor: pointer;
  text-decoration: none;
}
.post-item:hover {
  background: var(--bg-secondary);
}
.post-date {
  font-size: 0.78rem;
  color: var(--text-tertiary);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  min-width: 4.5em;
  flex-shrink: 0;
}
.post-title {
  font-weight: 400;
  font-size: 0.95rem;
  color: var(--text);
  line-height: 1.5;
}
.post-item:hover .post-title { color: var(--accent); }

/* Post page */
.post-header { margin-bottom: 2rem; }
.post-header h1 {
  font-size: 1.6rem;
  font-weight: 700;
  line-height: 1.4;
  letter-spacing: -0.01em;
}
.post-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.8rem;
  color: var(--text-secondary);
  font-size: 0.85rem;
}
.post-tags { display: inline-flex; gap: 0.3rem; }
.tag {
  font-size: 0.7rem;
  padding: 0.15rem 0.55rem;
  background: var(--tag-bg);
  color: var(--tag-text);
  border-radius: 99px;
  font-weight: 500;
}
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  margin-bottom: 1.5rem;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.15s;
}
.back-link:hover { color: var(--accent); }

/* Content */
.post-content h1 { font-size: 1.5rem; margin: 2rem 0 1rem; font-weight: 700; }
.post-content h2 { font-size: 1.25rem; margin: 1.8rem 0 0.8rem; font-weight: 700; }
.post-content h3 { font-size: 1.1rem; margin: 1.5rem 0 0.6rem; font-weight: 500; }
.post-content p { margin-bottom: 1rem; }
.post-content ul, .post-content ol { margin: 0.5rem 0 1rem 1.5rem; }
.post-content li { margin-bottom: 0.3rem; }
.post-content blockquote {
  border-left: 3px solid var(--accent);
  padding: 0.5rem 1rem;
  margin: 1rem 0;
  background: var(--bg-secondary);
  border-radius: 0 6px 6px 0;
  color: var(--text-secondary);
}
.post-content a { color: var(--accent); text-decoration: none; }
.post-content a:hover { text-decoration: underline; }
.post-content img { max-width: 100%; border-radius: 8px; margin: 1rem 0; }
.post-content hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2rem 0;
}
.post-content strong { font-weight: 700; }
.post-content em { font-style: italic; }

/* Code */
.post-content code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  background: var(--code-bg);
  padding: 0.15em 0.4em;
  border-radius: 4px;
}
.post-content pre {
  background: var(--code-bg);
  border-radius: 8px;
  padding: 1.2rem;
  overflow-x: auto;
  margin: 1rem 0;
  border: 1px solid var(--border);
}
.post-content pre code {
  background: none;
  padding: 0;
  font-size: 0.85rem;
  line-height: 1.6;
}

/* Table */
.post-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
}
.post-content th, .post-content td {
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--border);
  text-align: left;
}
.post-content th { background: var(--bg-secondary); font-weight: 500; }

/* Footer */
.site-footer {
  text-align: center;
  padding: 2rem 0;
  margin-top: 3rem;
  border-top: 1px solid var(--border-light);
  color: var(--text-tertiary);
  font-size: 0.75rem;
  letter-spacing: 0.02em;
}

@media (max-width: 600px) {
  .container { padding: 1rem 1rem 3rem; }
  .site-header { padding: 2.5rem 0 1.5rem; }
  .site-header h1 { font-size: 1.3rem; }
  .post-item { flex-direction: column; gap: 0.15rem; padding: 0.6rem 0.75rem; }
  .post-date { font-size: 0.72rem; }
  .post-header h1 { font-size: 1.3rem; }
}
`;

// --- Templates ---
function postHtml(post) {
  // Remove leading h1 if it duplicates the frontmatter title
  let content = post.content.trimStart();
  const h1Match = content.match(/^#\s+(.+)\n*/);
  if (h1Match) {
    content = content.slice(h1Match[0].length);
  }
  // Pre-process bold markers before marked: **text** → <strong>text</strong>
  // (marked occasionally misses ** in certain positions; this ensures consistent rendering)
  content = content.replace(/\*\*(.+?)\*\*/gs, '<strong>$1</strong>');
  const html = marked(content);
  const tagsHtml = post.tags.length
    ? `<div class="post-tags">${post.tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}</div>`
    : '';
  const isPrivate = post.access === 'private';
  const cssPath = isPrivate ? '../../../style.css' : '../../style.css';
  const backPath = isPrivate ? '../../../private/' : '../../';

  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escapeHtml(post.title)}</title>
<link rel="stylesheet" href="${cssPath}">
</head>
<body>
<div class="container">
  <a href="${backPath}" class="back-link">&larr; 목록으로</a>
  <article>
    <div class="post-header">
      <h1>${escapeHtml(post.title)}</h1>
      <div class="post-meta">
        <time>${formatDate(post.date)}</time>
        ${tagsHtml}
      </div>
    </div>
    <div class="post-content">${html}</div>
  </article>
</div>
</body>
</html>`;
}

function shortDate(dateStr) {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length < 3) return dateStr;
  return `${parts[1]}.${parts[2]}`;
}

function indexHtml(posts, { isPrivate = false } = {}) {
  // Group by month
  const groups = new Map();
  for (const post of posts) {
    const month = post.date ? post.date.substring(0, 7) : 'unknown';
    if (!groups.has(month)) groups.set(month, []);
    groups.get(month).push(post);
  }

  const cssPath = isPrivate ? '../style.css' : 'style.css';
  const titleSuffix = isPrivate ? ' (Private)' : '';

  let postsHtml = '';
  for (const [month, monthPosts] of groups) {
    const d = new Date(month + '-01T00:00:00');
    const label = isNaN(d.getTime()) ? month : d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' });
    postsHtml += `<div class="month-group" data-month="${month}">
  <div class="month-label">${label}</div>`;
    for (const post of monthPosts) {
      const tagsData = post.tags.map(t => escapeHtml(t)).join(',');
      postsHtml += `
  <a class="post-item" href="posts/${encodeURIComponent(post.slug)}/index.html" data-title="${escapeHtml(post.title).toLowerCase()}" data-tags="${tagsData.toLowerCase()}">
    <span class="post-date">${shortDate(post.date)}</span>
    <span class="post-title">${escapeHtml(post.title)}</span>
  </a>`;
    }
    postsHtml += `\n</div>\n`;
  }

  // Search data for content search
  const searchData = JSON.stringify(posts.map(p => ({
    s: p.slug,
    t: p.title,
    g: p.tags,
  })));

  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escapeHtml(siteConfig.title + titleSuffix)}</title>
<link rel="stylesheet" href="${cssPath}">
</head>
<body>
<div class="container">
  <header class="site-header">
    <h1>${escapeHtml(siteConfig.title)}</h1>
    ${siteConfig.description ? `<p>${escapeHtml(siteConfig.description)}</p>` : ''}
  </header>
  <div class="search-wrap">
    <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
    <input type="text" class="search-input" placeholder="Search posts..." autocomplete="off" spellcheck="false">
    <button class="search-clear" aria-label="Clear">&times;</button>
  </div>
  <div class="search-empty">No posts found.</div>
  <div class="stats-bar">
    <span class="stats-count">${posts.length} posts</span>
  </div>
  <div id="posts-list">
  ${postsHtml}
  </div>
  <footer class="site-footer">Built with Sparks</footer>
</div>
<script>
(function(){
  const input = document.querySelector('.search-input');
  const clearBtn = document.querySelector('.search-clear');
  const emptyMsg = document.querySelector('.search-empty');
  const groups = document.querySelectorAll('.month-group');
  const items = document.querySelectorAll('.post-item');
  const statsCount = document.querySelector('.stats-count');
  const total = items.length;

  function doSearch() {
    const q = input.value.trim().toLowerCase();
    clearBtn.style.display = q ? 'block' : 'none';
    let shown = 0;
    groups.forEach(g => {
      const posts = g.querySelectorAll('.post-item');
      let groupVisible = 0;
      posts.forEach(p => {
        const title = p.dataset.title || '';
        const tags = p.dataset.tags || '';
        const match = !q || title.includes(q) || tags.includes(q);
        p.style.display = match ? '' : 'none';
        if (match) { groupVisible++; shown++; }
      });
      g.style.display = groupVisible ? '' : 'none';
    });
    emptyMsg.style.display = (q && shown === 0) ? 'block' : 'none';
    statsCount.textContent = q ? shown + ' / ' + total + ' posts' : total + ' posts';
  }

  input.addEventListener('input', doSearch);
  clearBtn.addEventListener('click', function() {
    input.value = '';
    doSearch();
    input.focus();
  });
  input.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') { input.value = ''; doSearch(); }
  });
  // Keyboard shortcut: / to focus search
  document.addEventListener('keydown', function(e) {
    if (e.key === '/' && document.activeElement !== input) {
      e.preventDefault();
      input.focus();
    }
  });
})();
</script>
</body>
</html>`;
}

// --- Build ---
function build() {
  if (!fs.existsSync(SOURCE_DIR)) {
    console.error(`Error: source directory not found: ${SOURCE_DIR}`);
    process.exit(1);
  }
  const allSourceFiles = fs.readdirSync(SOURCE_DIR).filter(f => f.endsWith('.md'));

  // 1. Load manifest and determine which files to add
  let manifest = loadManifest();
  if (buildAll) {
    // Preserve existing access settings, default new files to public
    const existing = new Map(manifest.map(e => [e.file, e.access]));
    manifest = allSourceFiles.map(f => ({ file: f, access: existing.get(f) || 'public' }));
  } else if (selectedFiles) {
    // --files format: "file1.md:private,file2.md" or "file1.md,file2.md"
    const newEntries = selectedFiles.map(f => {
      const [name, access] = f.split(':');
      return { file: name, access: access || 'public' };
    });
    // New entries override existing access for the same file
    const overrides = new Map(newEntries.map(e => [e.file, e.access]));
    manifest = manifest.filter(e => !overrides.has(e.file)).concat(newEntries);
  }
  // Remove files that no longer exist in source
  // Guard: empty source dir must not silently wipe the manifest
  if (allSourceFiles.length === 0 && manifest.length > 0) {
    console.error(`Error: source directory is empty but manifest has ${manifest.length} entries. Aborting to prevent data loss.`);
    process.exit(1);
  }
  manifest = manifest.filter(e => allSourceFiles.includes(e.file));

  // 2. Parse posts and split by access
  let allPosts = manifest.map(e => parsePost(e.file, { access: e.access }));

  // 3. If --draft, parse draft file and merge (without saving to manifest)
  if (draftFile) {
    const draftDir = path.dirname(draftFile);
    const draftFilename = path.basename(draftFile);
    const draftPost = parsePost(draftFilename, { baseDir: draftDir });
    allPosts.push(draftPost);
    console.log(`Draft included: ${draftPost.title}`);
  } else {
    // Only save manifest when not in draft mode
    saveManifest(manifest);
  }

  allPosts.sort((a, b) => b.date.localeCompare(a.date));
  const publicPosts = allPosts.filter(p => p.access !== 'private');
  const privatePosts = allPosts.filter(p => p.access === 'private');

  // 4. Create output dirs + shared CSS
  fs.mkdirSync(path.join(OUTPUT_DIR, 'posts'), { recursive: true });
  fs.writeFileSync(path.join(OUTPUT_DIR, 'style.css'), CSS);

  // 5. Build public posts
  for (const post of publicPosts) {
    const postDir = path.join(OUTPUT_DIR, 'posts', post.slug);
    fs.mkdirSync(postDir, { recursive: true });
    fs.writeFileSync(path.join(postDir, 'index.html'), postHtml(post));
  }
  fs.writeFileSync(path.join(OUTPUT_DIR, 'index.html'), indexHtml(publicPosts));

  // 6. Build private posts (under /private/)
  if (privatePosts.length > 0) {
    fs.mkdirSync(path.join(OUTPUT_DIR, 'private', 'posts'), { recursive: true });
    for (const post of privatePosts) {
      const postDir = path.join(OUTPUT_DIR, 'private', 'posts', post.slug);
      fs.mkdirSync(postDir, { recursive: true });
      fs.writeFileSync(path.join(postDir, 'index.html'), postHtml(post));
    }
    fs.writeFileSync(path.join(OUTPUT_DIR, 'private', 'index.html'), indexHtml(privatePosts, { isPrivate: true }));
  }

  console.log(`Published ${publicPosts.length} public + ${privatePosts.length} private post(s)`);
}

build();
