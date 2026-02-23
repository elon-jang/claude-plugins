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
    files: { type: 'string', short: 'f' },
    all: { type: 'boolean', default: false },
  },
});

const SOURCE_DIR = values.source;
const OUTPUT_DIR = values.output;
const selectedFiles = values.files ? values.files.split(',').map(f => f.trim()) : null;
const buildAll = values.all || false;

if (!SOURCE_DIR || !OUTPUT_DIR) {
  console.error('Usage: node build-blog.mjs --source <blog-dir> --output <build-dir> [--files f1.md,f2.md | --all]');
  process.exit(1);
}

// --- Marked config (GFM) ---
marked.setOptions({ gfm: true, breaks: true });

// --- Helpers ---
function readAllPosts() {
  const files = fs.readdirSync(SOURCE_DIR).filter(f => f.endsWith('.md'));
  return files.map(filename => {
    const raw = fs.readFileSync(path.join(SOURCE_DIR, filename), 'utf-8');
    const dateMatch = filename.match(/^(\d{4}-\d{2}-\d{2})/);
    let data = {}, content = raw;
    try {
      const parsed = matter(raw);
      data = parsed.data;
      content = parsed.content;
    } catch {
      // Malformed frontmatter (e.g. unquoted colons) - strip it manually
      const fmMatch = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
      if (fmMatch) {
        content = fmMatch[2];
        // Extract what we can with regex
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
      date: String(data.date || (dateMatch ? dateMatch[1] : '')).substring(0, 10),
      tags: data.tags || [],
      content,
    };
  }).sort((a, b) => b.date.localeCompare(a.date));
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const d = new Date(dateStr + 'T00:00:00');
  return d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
}

function escapeHtml(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// --- CSS ---
const CSS = `/* Sparks Blog */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg: #ffffff;
  --bg-secondary: #f8f9fa;
  --text: #1a1a2e;
  --text-secondary: #555;
  --accent: #4361ee;
  --accent-light: #eef0ff;
  --border: #e0e0e0;
  --code-bg: #f5f5f5;
  --tag-bg: #e8ecff;
  --tag-text: #3a50c2;
  --shadow: rgba(0,0,0,0.06);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0d1117;
    --bg-secondary: #161b22;
    --text: #e6edf3;
    --text-secondary: #8b949e;
    --accent: #6d8cff;
    --accent-light: #1c2541;
    --border: #30363d;
    --code-bg: #1c2333;
    --tag-bg: #1c2541;
    --tag-text: #8da6ff;
    --shadow: rgba(0,0,0,0.3);
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
  max-width: 720px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem;
}

/* Header */
.site-header {
  text-align: center;
  padding: 3rem 0 2rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2.5rem;
}
.site-header h1 {
  font-size: 1.8rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.site-header p {
  color: var(--text-secondary);
  margin-top: 0.4rem;
  font-size: 0.95rem;
}

/* Index */
.month-group { margin-bottom: 2rem; }
.month-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.8rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border);
}
.post-item {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  padding: 0.6rem 0;
}
.post-date {
  font-size: 0.82rem;
  color: var(--text-secondary);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.post-title a {
  color: var(--text);
  text-decoration: none;
  font-weight: 400;
  transition: color 0.15s;
}
.post-title a:hover { color: var(--accent); }
.post-tags { display: inline-flex; gap: 0.3rem; margin-left: 0.5rem; }
.tag {
  font-size: 0.7rem;
  padding: 0.1rem 0.5rem;
  background: var(--tag-bg);
  color: var(--tag-text);
  border-radius: 99px;
  font-weight: 500;
}

/* Post */
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
.back-link {
  display: inline-block;
  margin-bottom: 1.5rem;
  color: var(--accent);
  text-decoration: none;
  font-size: 0.9rem;
}
.back-link:hover { text-decoration: underline; }

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
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.8rem;
}

/* Stats */
.stats {
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

@media (max-width: 600px) {
  .container { padding: 1rem 1rem 3rem; }
  .site-header { padding: 2rem 0 1.5rem; }
  .site-header h1 { font-size: 1.4rem; }
  .post-item { flex-direction: column; gap: 0.2rem; }
  .post-header h1 { font-size: 1.3rem; }
}
`;

// --- Templates ---
function postHtml(post) {
  const html = marked(post.content);
  const tagsHtml = post.tags.length
    ? `<div class="post-tags">${post.tags.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('')}</div>`
    : '';

  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${escapeHtml(post.title)}</title>
<link rel="stylesheet" href="../../style.css">
</head>
<body>
<div class="container">
  <a href="../../" class="back-link">&larr; 목록으로</a>
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

function indexHtml(posts) {
  // Group by month
  const groups = new Map();
  for (const post of posts) {
    const month = post.date ? post.date.substring(0, 7) : 'unknown';
    if (!groups.has(month)) groups.set(month, []);
    groups.get(month).push(post);
  }

  let postsHtml = '';
  for (const [month, monthPosts] of groups) {
    const d = new Date(month + '-01T00:00:00');
    const label = d.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' });
    postsHtml += `<div class="month-group">
  <div class="month-label">${label}</div>`;
    for (const post of monthPosts) {
      const tagsHtml = post.tags.slice(0, 3).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('');
      postsHtml += `
  <div class="post-item">
    <span class="post-date">${post.date}</span>
    <span class="post-title"><a href="posts/${encodeURIComponent(post.slug)}/index.html">${escapeHtml(post.title)}</a></span>
    <span class="post-tags">${tagsHtml}</span>
  </div>`;
    }
    postsHtml += `\n</div>\n`;
  }

  return `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sparks Blog</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div class="container">
  <header class="site-header">
    <h1>Sparks Blog</h1>
    <p>Knowledge & Insights</p>
  </header>
  <div class="stats">${posts.length}개의 글</div>
  ${postsHtml}
  <footer class="site-footer">Built with Sparks</footer>
</div>
</body>
</html>`;
}

// --- Build ---
function build() {
  const allPosts = readAllPosts();
  const postsToBuild = buildAll || !selectedFiles
    ? allPosts
    : allPosts.filter(p => selectedFiles.includes(p.filename));

  // Create output dirs
  fs.mkdirSync(path.join(OUTPUT_DIR, 'posts'), { recursive: true });

  // Write style.css
  fs.writeFileSync(path.join(OUTPUT_DIR, 'style.css'), CSS);

  // Build individual posts
  let built = 0;
  for (const post of postsToBuild) {
    const postDir = path.join(OUTPUT_DIR, 'posts', post.slug);
    fs.mkdirSync(postDir, { recursive: true });
    fs.writeFileSync(path.join(postDir, 'index.html'), postHtml(post));
    built++;
  }

  // Always rebuild index from ALL posts
  fs.writeFileSync(path.join(OUTPUT_DIR, 'index.html'), indexHtml(allPosts));

  console.log(`Built ${built} post(s), index updated (${allPosts.length} total)`);
}

build();
