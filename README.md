# Nutanix Engineering Blog Posts

A home for drafting, reviewing, and archiving engineering blog posts published internally at Nutanix.

Each post lives in version control alongside its images, diagrams, and code samples. That way drafts can be reviewed like code, edits are tracked, and published pieces stay easy to find and update later.

## Repository Structure

```text
.
├── posts/
│   └── YYYY-MM-DD-short-slug/
│       ├── index.html      # The post itself: a single self-contained HTML page
│       ├── assets/         # Images, diagrams, screenshots, earlier drafts
│       └── code/           # Optional runnable snippets referenced in the post
└── README.md
```

- **One folder per post.** Name it `YYYY-MM-DD-short-slug`, using the target publish date (or the date you started, while it's still a draft).
- **Keep each post self-contained.** Put the CSS in a `<style>` block inside `index.html` and avoid external fonts, scripts, or CDNs, so the page renders the same anywhere, including offline.
- **Keep assets next to the post.** Reference them with relative paths, such as `<img src="assets/architecture.png" alt="Architecture">` or `<a href="code/example.py">`.

## Writing a New Post

1. Create a branch: `git checkout -b post/short-slug`
2. Create the post folder, starting from the most recent post's page:
   ```bash
   mkdir -p posts/YYYY-MM-DD-short-slug/assets
   cp posts/2026-09-28-nutanix-AI-inference/index.html posts/YYYY-MM-DD-short-slug/index.html
   ```
3. Update the metadata in `<head>`, replace the body content, and keep the table of contents in sync with the section IDs.
4. Preview it locally by opening `index.html` in a browser, or serve the repo with `python3 -m http.server` and browse to the post folder.
5. Push it for review.
6. Once it's approved and published internally, set `post:status` to `published`, fill in `post:published_url`, and update the Post Index below.

## Post Metadata

Every post declares its metadata in `<head>`, so it stays machine-readable without a build step:

```html
<title>A Clear, Specific Title</title>
<meta name="author" content="Your Name" />
<meta name="date" content="YYYY-MM-DD" />
<meta name="description" content="One or two sentences describing what the reader will learn." />
<meta name="keywords" content="distributed-systems, performance" />
<meta name="post:status" content="draft" />      <!-- draft | in-review | published -->
<meta name="post:published_url" content="" />   <!-- internal link once published -->
```

Keep the visible byline in the page header (author, date, read time, status) consistent with these values.

## Writing Guidelines

- **Lead with the why.** Open with the problem or question the post answers.
- **Know your audience.** Assume engineering peers who may not know your team's systems, and define acronyms and internal codenames on first use.
- **Show, don't just tell.** Use diagrams, code snippets, and real (sanitized) data where they help.
- **Keep it focused.** One main idea per post. If it keeps growing, split it into a series.
- **End with takeaways.** Summarize the key lessons or next steps.

## Confidentiality

These posts are for **internal audiences only**. Before committing, make sure you've removed:

- Customer names, data, or identifying details
- Credentials, tokens, internal hostnames, or IP addresses
- Anything not yet cleared for broader internal distribution

## Post Index

| Date | Title | Status |
| ---- | ----- | ------ |
| 2026-09-28 | [Inference Is an Infrastructure Problem: From GPT-2 on a Laptop to Nutanix Enterprise AI](posts/2026-09-28-nutanix-AI-inference/index.html) | draft |
