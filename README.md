# Sapient Edge — AI Deep Learning Atlas (v3)

**0→100 expert learning paths** for five AI roles, plus a Shared Core:

1. **AI Architect** · 2. **AI Engineer** · 3. **AI Inference Engineer** · 4. **AI Infrastructure** · 5. **Agentic AI**

It's an atlas, not a link dump. It has original explainers for every subject *and* every topic, 41 deep concept cards with diagrams and worked examples (the math is checked), quizzes, hands-on labs, capstone projects, career learning paths and a searchable glossary. It's built for working engineers moving into deep AI systems work. Current as of October 2026.

![Infra track](docs/screenshots/01-desktop-infra-track.png)

## At a glance (v3)

| | v2 | v3 |
|---|---|---|
| Subjects | 83 | **91** |
| Topics (each with its own explainer) | 171 (none) | **198 (all)** |
| Subtopics | 855 | **990** |
| Quiz questions (≥3 per subject, with explanations) | 84 | **283** |
| Unique resource URLs (link-checked) | 99 | **130** |
| Concept cards (diagram + worked example) | 27 | **41** |
| Capstone projects | – | **6** |
| Learning paths | – | **5** |
| Glossary terms | – | **104** |
| SVG illustrations | 6 | **39** |

## Use it

Open `index.html` in any modern browser. **It works fully offline:** Mermaid is bundled in `assets/vendor/`, and the page loads nothing from a CDN.

```bash
python3 -m http.server 8080   # optional; then open http://localhost:8080
```

Progress, XP, rank and streaks are saved in your browser (`localStorage`). Use **Export progress** to move them to another device.

## What's inside

- **Tracks → levels → subjects → topics → subtopics.** Every subject has *why it matters*, an original explainer, 3+ verified resources, a hands-on lab and a self-check quiz. Every topic has its own 60–150 word explainer.
- **Concept cards**, including new in v3: NCCL collectives & ring all-reduce · GPU sharing (MIG / time-slicing / MPS / DRA) · cold-start math · LLM gateway & KV-aware routing · cost per 1M tokens & capacity planning · prompt-injection defense in depth · MoE routing & capacity · HNSW / IVF / PQ · GraphRAG · A2A · computer-use agents · distillation · RoPE & long context · GPU failure triage (Xid, ECC, NCCL hangs).
- **AI infrastructure gap fill**: GPU interconnects & collective debugging, GPU sharing & batch scheduling (GPU Operator, MIG, time-slicing, DRA, Kueue, Volcano), GPU failure operations, AI-specific platform security (prompt injection, weight exfiltration, agent/tool/MCP permissions), unit economics & capacity/power planning, weight loading & cold start, LLM gateways & inference routing, P/D disaggregation frameworks, vector search internals.
- **Capstones** (one per track). Each one covers architecture, infra, deploy, security, observability, scaling and cost.
- **Learning paths**, with no fixed timelines: Cloud/DevOps → AI Infra · SWE → AI Engineer · Solutions Architect for clients · Perf engineer → Inference · AI Engineer → Agent builder.
- **Glossary**: A–Z, filtered by the search box.

| Path | Purpose |
|------|---------|
| `index.html` | App shell (curriculum + concepts embedded) |
| `assets/js/app.js` | UI logic |
| `assets/img/` | SVG illustrations (track heroes, level art) |
| `assets/vendor/mermaid.min.js` | Bundled Mermaid (offline diagrams) |
| `data/curriculum.json`, `data/concepts.json` | Full content (also per-track `data/_*.json`) |
| `scripts/build_v3.py` | Merges `scripts/v3/*` content into data and re-embeds `index.html` |
| `scripts/linkcheck.py` | HTTP-checks every resource URL → `docs/resources_linkcheck.csv` |
| `docs/` | Screenshots, link report, stats, launch drafts |

## Link check

All 130 resource URLs were checked on 2026-10-11, and 129 passed the automated check. The one exception is ISO/IEC 42001 (iso.org), which returns 403 to scripted clients. That page was confirmed live separately. See `docs/resources_linkcheck.csv`.

## GitHub Pages

The workflow `.github/workflows/pages.yml` publishes the repo root. After pushing, set Pages source to "GitHub Actions". No build step is needed.

## License

- **Code** (HTML/JS/CSS/scripts): [MIT](./LICENSE)
- **Content** (curriculum, explainers, diagrams): [CC BY 4.0](./LICENSE-CONTENT). Please credit **Sapient Edge**.
- Bundled Mermaid is MIT-licensed by its authors.

## Disclaimer

This is a learning atlas, not a certification. Prices, hardware figures and examples are illustrative, so re-check them before relying on them. Nothing here is legal advice on the EU AI Act or other compliance topics.
