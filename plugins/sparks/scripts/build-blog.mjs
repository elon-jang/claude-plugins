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
  },
});

const SOURCE_DIR = values.source;
const OUTPUT_DIR = values.output;
const MANIFEST_PATH = values.manifest;
const selectedFiles = values.files ? values.files.split(',').map(f => f.trim()) : null;
const buildAll = values.all || false;

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
  --bg: #faf9f7;
  --bg-secondary: #f5f4f1;
  --text: #1c1917;
  --text-secondary: #57534e;
  --text-tertiary: #a8a29e;
  --accent: #292524;
  --accent-hover: #1c1917;
  --border: #e7e5e4;
  --border-light: #f0efed;
  --code-bg: #f5f4f1;
  --tag-bg: #f0efed;
  --tag-text: #57534e;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
  --shadow-hover: 0 4px 12px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
  --radius: 12px;
  --search-bg: #ffffff;
  --search-focus: #78716c;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #111110;
    --bg-secondary: #1c1b1a;
    --text: #f2f0ed;
    --text-secondary: #a8a29e;
    --text-tertiary: #6b6562;
    --accent: #e7e5e4;
    --accent-hover: #f2f0ed;
    --border: #2c2b2a;
    --border-light: #242322;
    --code-bg: #1c1b1a;
    --tag-bg: #242322;
    --tag-text: #a8a29e;
    --shadow: 0 1px 3px rgba(0,0,0,0.2);
    --shadow-hover: 0 4px 12px rgba(0,0,0,0.3);
    --search-bg: #1c1b1a;
    --search-focus: #78716c;
  }
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.85;
  word-break: keep-all;
  -webkit-font-smoothing: antialiased;
}

.container {
  max-width: 660px;
  margin: 0 auto;
  padding: 2rem 1.5rem 5rem;
}

/* Header */
.site-header {
  text-align: center;
  padding: 4rem 0 3rem;
  margin-bottom: 2.5rem;
  border-bottom: 1px solid var(--border);
}
.site-header h1 {
  font-size: 1.35rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  color: var(--text);
}
.site-header p {
  color: var(--text-tertiary);
  margin-top: 0.5rem;
  font-size: 0.85rem;
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
  width: 15px;
  height: 15px;
}
.search-input {
  width: 100%;
  padding: 0.65rem 1rem 0.65rem 2.4rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--search-bg);
  color: var(--text);
  font-size: 0.875rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
}
.search-input::placeholder {
  color: var(--text-tertiary);
}
.search-input:focus {
  border-color: var(--search-focus);
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
  font-size: 0.78rem;
  margin-bottom: 1.5rem;
  padding: 0 0.25rem;
}
.stats-count { font-variant-numeric: tabular-nums; }

/* Index */
.month-group { margin-bottom: 2rem; }
.month-label {
  font-size: 0.72rem;
  font-weight: 500;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
  padding: 0 0.25rem;
}
.post-item {
  display: flex;
  align-items: baseline;
  gap: 1.2rem;
  padding: 0.6rem 0.75rem;
  margin: 0 -0.25rem;
  border-radius: 6px;
  transition: background 0.12s;
  cursor: pointer;
  text-decoration: none;
}
.post-item:hover {
  background: var(--bg-secondary);
}
.post-date {
  font-size: 0.75rem;
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
.post-item:hover .post-title { color: var(--text); opacity: 0.75; }

/* Post page */
.post-header {
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}
.post-header h1 {
  font-size: 1.65rem;
  font-weight: 700;
  line-height: 1.45;
  letter-spacing: -0.02em;
}
.post-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  color: var(--text-tertiary);
  font-size: 0.82rem;
}
.post-tags { display: inline-flex; gap: 0.3rem; flex-wrap: wrap; }
.tag {
  font-size: 0.68rem;
  padding: 0.15rem 0.5rem;
  background: var(--tag-bg);
  color: var(--tag-text);
  border-radius: 4px;
  font-weight: 400;
  letter-spacing: 0.02em;
}
.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  margin-bottom: 2rem;
  color: var(--text-tertiary);
  text-decoration: none;
  font-size: 0.82rem;
  transition: color 0.15s;
  letter-spacing: 0.01em;
}
.back-link:hover { color: var(--text-secondary); }

/* Content */
.post-content { font-size: 1rem; }
.post-content h1 { font-size: 1.45rem; margin: 2.5rem 0 0.9rem; font-weight: 700; letter-spacing: -0.01em; }
.post-content h2 {
  font-size: 1.1rem;
  margin: 2.8rem 0 0.8rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--text);
}
.post-content h3 { font-size: 1rem; margin: 1.8rem 0 0.5rem; font-weight: 600; }
.post-content p { margin-bottom: 1.1rem; }
.post-content ul, .post-content ol { margin: 0.5rem 0 1.2rem 1.4rem; }
.post-content li { margin-bottom: 0.35rem; }
.post-content blockquote {
  border-left: 2px solid var(--border);
  padding: 0.1rem 1.1rem;
  margin: 1.5rem 0;
  color: var(--text-secondary);
  font-style: italic;
}
.post-content a {
  color: var(--text);
  text-decoration: underline;
  text-decoration-color: var(--border);
  text-underline-offset: 3px;
  transition: text-decoration-color 0.15s;
}
.post-content a:hover { text-decoration-color: var(--text-secondary); }
.post-content img { max-width: 100%; border-radius: 6px; margin: 1.5rem 0; }
.post-content hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 2.5rem 0;
}
.post-content strong { font-weight: 600; }
.post-content em { font-style: italic; color: var(--text-secondary); }

/* Code */
.post-content code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.83em;
  background: var(--code-bg);
  padding: 0.15em 0.4em;
  border-radius: 4px;
  color: var(--text);
}
.post-content pre {
  background: var(--code-bg);
  border-radius: 6px;
  padding: 1.2rem;
  overflow-x: auto;
  margin: 1.2rem 0;
  border: 1px solid var(--border);
}
.post-content pre code {
  background: none;
  padding: 0;
  font-size: 0.84rem;
  line-height: 1.65;
}

/* Table */
.post-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.2rem 0;
  font-size: 0.9rem;
}
.post-content th, .post-content td {
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--border);
  text-align: left;
}
.post-content th { background: var(--bg-secondary); font-weight: 500; color: var(--text-secondary); font-size: 0.82rem; }

/* Footer */
.site-footer {
  text-align: center;
  padding: 2rem 0;
  margin-top: 4rem;
  border-top: 1px solid var(--border-light);
  color: var(--text-tertiary);
  font-size: 0.72rem;
  letter-spacing: 0.04em;
}

@media (max-width: 600px) {
  .container { padding: 1rem 1rem 3rem; }
  .site-header { padding: 2.5rem 0 2rem; }
  .site-header h1 { font-size: 1.2rem; }
  .post-item { flex-direction: column; gap: 0.1rem; padding: 0.55rem 0.75rem; }
  .post-date { font-size: 0.7rem; }
  .post-header h1 { font-size: 1.35rem; }
  .post-content h2 { font-size: 1.05rem; margin: 2rem 0 0.7rem; }
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
  // Auto-detect section titles: standalone short lines (2–35 chars) surrounded by blank lines
  // that don't start with markdown special chars and don't end with sentence punctuation.
  // Handles essay-style posts where section headings are written as plain text.
  content = content.replace(
    /\n{2,}([^#>*\-`\d\n][^\n]{0,32}[^\n.!?。,:])\n{2,}/g,
    '\n\n## $1\n\n'
  );
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
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css" media="(prefers-color-scheme: light)">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark-dimmed.min.css" media="(prefers-color-scheme: dark)">
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
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>hljs.highlightAll();</script>
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
  const allPosts = manifest.map(e => parsePost(e.file, { access: e.access }));
  saveManifest(manifest);

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
