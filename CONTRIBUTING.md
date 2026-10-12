# Contributing

Thanks for helping improve the Atlas.

## Curriculum changes

1. Edit generators under `scripts/` or JSON under `data/`.
2. Every resource **must** include a working `url`.
3. Run link check:

```bash
python3 scripts/linkcheck.py
```

4. Keep explainers original (no pasted copyrighted chapters).
5. Prefer canonical sources: arXiv abs, official docs, GitHub, known courses.

## App changes

- Keep the site static (no build step required for readers).
- Mobile + dark theme should keep working.
- Test in headless Chrome when possible.

## PRs

- Small, focused PRs.
- Describe which track/level you touched.
- Do not commit secrets.
