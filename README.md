# Nutanix Engineering Blog Posts

A home for drafting, reviewing, and archiving engineering blog posts published internally at Nutanix.

Each post lives in version control alongside its images, diagrams, and code samples. That way drafts can be reviewed like code, edits are tracked, and published pieces stay easy to find and update later.

## Repository Structure

```text
.
├── posts/
│   └── YYYY-MM-DD-short-slug/
│       ├── index.md        # The post itself
│       ├── assets/         # Images, diagrams, screenshots
│       └── code/           # Optional runnable snippets referenced in the post
├── templates/
│   └── post.md             # Starting template for new posts
└── README.md
```

- **One folder per post.** Name it `YYYY-MM-DD-short-slug`, using the target publish date (or the date you started, while it's still a draft).
- **Keep assets next to the post.** Reference them with relative paths, such as `![Architecture](assets/architecture.png)`.

## Writing a New Post

1. Create a branch: `git checkout -b post/short-slug`
2. Create the post folder from the template:
   ```bash
   mkdir -p posts/YYYY-MM-DD-short-slug/assets
   cp templates/post.md posts/YYYY-MM-DD-short-slug/index.md
   ```
3. Fill in the front matter and write the post in Markdown.
4. Open a pull request for review.
5. Once it's approved and published internally, update `status` to `published`, add the `published_url`, and merge.

## Front Matter

Every post starts with a YAML front matter block:

```yaml
---
title: "A Clear, Specific Title"
author: "Your Name"
date: YYYY-MM-DD
status: draft          # draft | in-review | published
tags: [distributed-systems, performance]
summary: "One or two sentences describing what the reader will learn."
published_url: ""      # Internal link once published
---
```

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
| _TBD_ | _First post coming soon_ | draft |
