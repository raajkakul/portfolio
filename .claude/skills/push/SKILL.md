---
name: push
description: Ship the current uncommitted changes in this portfolio repo to the live site — stages everything, writes a commit message from the actual diff, commits, and pushes to the GitHub Pages deploy branch. Trigger this whenever Raj types "/push" in this repo, or says things like "push this," "ship it," "deploy the changes," or "publish what I just did" while working in the portfolio folder. Since invoking this IS the explicit go-ahead, don't pause to re-confirm the push itself — just do it and report the result.
---

# Push portfolio changes live

A one-command shortcut for the commit-and-deploy step Raj does constantly while
iterating on this site: stage whatever changed, write a real commit message (not a
placeholder), commit, and push to the branch GitHub Pages actually deploys from. The
point of this skill is to remove friction from that loop — don't add a confirmation
step back in just because pushing is normally a "pause and check" kind of action.
Typing `/push` (or asking for it in plain language) already *is* that check.

## 1. See what actually changed

```
git status --porcelain
```

If this is empty and there's nothing staged either, there's nothing to ship — say so
plainly and stop. Don't invent a commit for a clean working tree.

## 2. Stage everything

```
git add -A
```

This repo's `.gitignore` already excludes `CLAUDE.md` and `.thumbnail` from tracking, so
`-A` is safe here — it won't accidentally publish the internal working notes. Don't
narrow this to specific files by default; the whole point of this command is to grab
whatever Raj just changed without him having to enumerate it.

## 3. Write the commit message from the real diff

Read `git diff --staged` (and `--stat` for a quick overview if the diff is large) and
describe what actually changed — don't write a generic "update files" message. Look at
`git log --oneline -10` first to match this repo's existing tone: short, imperative,
factual one-liners (e.g. "Update bio, employment status/dates, and contact section
labels", "Replace placeholder project data with real content from case
documentation"). A short body paragraph is fine for substantial changes, but most
commits here are a single line.

Do not add `Co-Authored-By`, an email address, or any author metadata to the message —
this repo's git identity is already configured (name "Raj") and past guidance for this
project has been explicit that commit trailers like that shouldn't appear.

Commit with a heredoc so multi-line messages don't get mangled:

```bash
git commit -m "$(cat <<'EOF'
<message here>
EOF
)"
```

## 4. Push to wherever this repo actually deploys from

Don't hardcode a branch mapping here — repos change. Check this directory's own
`CLAUDE.md` for a documented deploy convention (look for a line describing how GitHub
Pages deploys and what to push). As of this skill being written, that file says GitHub
Pages deploys from `main` while local work happens on `master`, so the push is:

```
git push origin master:main
```

If `CLAUDE.md` is ever missing or says something different, follow what it says instead
of this default — it's the source of truth, this skill is just a shortcut for the
common case.

## 5. Report the result

Tell Raj the new commit hash and that it's pushed. GitHub Pages typically takes a
minute or two to rebuild, so it's fine to mention that rather than trying to verify the
live site immediately.

## If something goes wrong

- **Push rejected (non-fast-forward / remote has diverged)** — do not force-push.
  Report the exact git error and ask how Raj wants to proceed; this usually means
  something else pushed to `main` directly, which is worth surfacing rather than
  papering over.
- **Merge conflict markers in the working tree** — stop and flag it; don't try to
  auto-resolve conflicts as part of a "quick push."
- **Nothing to commit but Raj clearly expected something to ship** — double check
  you're actually in the portfolio repo and not a different working directory; this
  skill only operates on `C:\Users\rajka\Documents\claude\portofolio`.
