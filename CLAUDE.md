# portofolio — Project Context

Spy/classified-dossier themed static portfolio site for Raj Kakul.
Live: https://raajkakul.github.io/portfolio
Repo: https://github.com/raajkakul/portfolio
Stack: Plain HTML, CSS, vanilla JS — no build system, no framework, no dependencies.

---

## Commands

| Command | Purpose |
|---------|---------|
| `python3 -m http.server 8080` | Serve locally at http://localhost:8080 |
| `git push origin main` | Deploy (GitHub Pages auto-deploys from main) |

No build step. Edit files directly and push.

---

## Architecture

```
portofolio/
  index.html                # Main page — all sections: hero, projects, skills, education, experience, contact
  style.css                 # All styles — single file, no preprocessor
  project-squatswat.html    # Detail page for OPERATION: SQUAT-SWAT
  badges/                   # PNG badge assets (brass/bronze circular frame style)
  CLAUDE.md                 # This file
```

---

## Design System

Spy/classified-dossier aesthetic. Preserve these conventions in all changes:
- Colors: parchment/aged-paper backgrounds, red accents, dark text
- Fonts: monospace/typewriter style for "classified" feel
- Interactions: redacted-reveal hover effects on links and names
- Section labels use spy-themed names, not generic ones:
  - Projects → "ACTIVE CASE FILES"
  - Education → "ACADEMIC CREDENTIALS"
  - Experience → "OPERATIVE HISTORY"
  - Contact → "SECURE CHANNELS"
- Each project entry uses format: "OPERATION: \<CODENAME\>"

---

## Current State

*Claude updates this section at the end of every session.*

- **Last session**: 2026-06-25
- **Last worked on**: Memory system planning — no code changes yet
- **Next tasks**:
  1. Clone repo locally into this directory
  2. Add Education section ("ACADEMIC CREDENTIALS")
  3. Add Experience section ("OPERATIVE HISTORY")
  4. Add Contact section ("SECURE CHANNELS")
  5. Fix `project-squatswat.html` — replace all `[placeholder]` text
  6. Expand project grid and skills badges
- **Known blockers**: None

---

## Gotchas

- No build step — changes deploy immediately on `git push origin main`. Do not push broken HTML to main.
- `project-squatswat.html` still has `[placeholder]` text — must be replaced before any public push.
- Badge images are custom PNGs in `badges/` with a brass/bronze circular frame style. New badges without PNG assets need CSS-only circle badge fallbacks matching the existing design.
- Responsive breakpoint for single-column stacking: ≤850px. Match this for all new sections.

---

## Memory Files

Directory: `/home/rajkakul/.claude/projects/-mnt-c-users-rajka-Documents-claude-portofolio/memory/`

*(No memory files yet. Create here as significant design decisions are made.)*
