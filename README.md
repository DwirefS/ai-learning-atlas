# Sapient Edge — AI Deep Learning Atlas (v5)

**0→100 expert learning paths for 13 enterprise agentic-AI roles**, organized as 7 tracks plus a Shared Core.

**Roles (new in v4).** The 8 core roles are AI Engineer · Forward Deployed Engineer · Agent Ops Engineer · AI Security Engineer · AI Infrastructure Engineer · Cloud Security Engineer (AI) · AI Governance Engineer · AI Evals Engineer. The other 5 are roles most lists miss: **AI-Ready Data Engineer** · ML / Post-training Engineer · AI Platform / LLMOps Engineer · AI Solutions Architect · AI Product Engineer / Manager.

**Tracks:** AI Architect · AI Engineer · AI Inference Engineer · AI Infrastructure · Agentic AI · **AI-Ready Data Engineering** (new) · **AgentOps, Evals, Security & Governance** (new).

Everything is centered on agentic AI and on the data engineering agents depend on. It's an atlas, not a link dump. Every subject and every topic has an original explainer. There are 51 concept cards with diagrams and worked examples (the math is checked), plus quizzes, hands-on labs, capstones, learning paths (including a **Universal Agentic Path** that covers all 13 roles in order) and a glossary. Current as of October 2026.

![Roles view](docs/screenshots/09-desktop-roles.png)

## At a glance

| | v3 | v5 |
|---|---|---|
| Role cards (mission, day-to-day, skills, tools, interview signals, capstone, mapped curriculum) | – | **13** |
| Tracks (+ Shared Core) | 5 | **7** |
| Subjects | 91 | **121** |
| Topics (each with its own explainer) | 198 | **288** |
| Subtopics | 990 | **1,440** |
| Quiz questions (≥3 per subject, with explanations) | 283 | **373** |
| Unique resource URLs (link-checked) | 130 | **228** |
| Concept cards (diagram + worked example) | 41 | **54** |
| Capstone projects | 6 | **8** |
| Project ladder builds (4 tiers) | – | **21** |
| Learning paths | 5 | **6** |
| Glossary terms | 104 | **136** |

### New in v6: coverage audit
We checked the atlas against 167 topics taken from about 45 job postings from 2026, course syllabi (DeepLearning.AI, CS336, CS224N, FSDL, Hugging Face), vendor docs (OpenAI, Anthropic, Google, Bedrock, Azure Foundry, Databricks, LangChain, LlamaIndex) and roadmap repos. Before: 114 covered, 31 thin, 22 missing. After: 167 covered. See `docs/coverage_audit.csv` (after) and `docs/coverage_audit_before.csv`. To re-run it: `python3 scripts/audit/audit.py`.
The audit added 8 subjects: NLP Foundations, Agentic Design Patterns, Agent Frameworks & Platforms, Reasoning Models & API Platform, RL Environments, Generative Media, Agent Attacks and Responsible AI. It also added 8 topics to existing subjects.

## New in v5

- **Project Ladder view: one AI skill = one project.** There are 21 hands-on builds in 4 tiers (Starter → Expert). Each has a goal, stack options, steps, stretch goals, checkable "done when" criteria, mapped roles and linked subjects. They cover semantic search over notes, your own MCP server to a database, function calling that books real calendar meetings, evals that catch prompt regressions, multimodal PDF RAG, a receipt reader, model routing, an observability dashboard, guardrails, a research/cold-email agent, a LoRA fine-tune in your voice, and a phone voice agent. The agentic, data and ops builds are CDC data product, durable workflows, kill switches, policy as code, audit trail, secure landing zone, trajectory evals, self-hosted inference and an end-to-end FDE engagement.
- **3 new subjects:** Multimodal and Document RAG (layout parsing, tables/charts, ColPali visual retrieval, multimodal embeddings), Vision and Document AI (OCR vs VLM extraction, validated JSON from receipts and invoices), and Real-Time Voice Agents (STT/TTS, speech-to-speech, VAD and turn-taking, barge-in, latency budget, SIP/Twilio).
- **3 new concept cards:** voice agent latency pipeline · document/multimodal RAG pipeline · model router (cheap vs smart).

### New in v4

- **Roles view.** Each of the 13 role cards maps to existing and new subjects. Shared subjects are linked, not duplicated, and a 🔗 count shows how many roles reuse each one.
- **AI-Ready Data Engineering track (11 subjects):** lakehouse and table formats, semantic layer and text-to-SQL, CDC and streaming freshness, unstructured pipelines, data contracts and circuit breakers, catalogs and lineage, connecting agents to enterprise data (APIs, MCP, OAuth on-behalf-of), permission-aware retrieval, AI-ready data products and mesh, agent memory and write-back data, and data ops for agent fleets.
- **AgentOps, Evals, Security & Governance track (12 subjects):** tracing and SLOs, eval engineering and golden sets, queues and durable execution, LLM-as-judge calibration and online evals, cloud security for AI (workload identity, private endpoints, KMS, CSPM/AI-SPM), threat modeling, red teaming and sandboxing, policy as code (OPA/Cedar), AI audit logging, the EU AI Act / NIST AI RMF / ISO 42001 controls crosswalk (updated for the Digital Omnibus, Reg. (EU) 2026/1744), trajectory evals and pass^k, kill switches, budgets and runbooks, and operating agent fleets 24/7.
- **Delivery and platform subjects:** forward deployed engineering (discovery to production), AI solutions architecture and sizing, AI product management for agents, and AI platform / LLMOps.
- **10 new concept cards:** agent–data integration reference architecture · permission-aware RAG · CDC freshness budget · unstructured pipeline · Agent Ops control loop · eval pipeline · policy-as-code gates · AI audit trail · controls crosswalk · FDE engagement lifecycle.

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
| `data/curriculum.json`, `data/concepts.json` | Full content (also per-track `data/_*.json` and `data/_roles.json`) |
| `scripts/build_v5.py` | Runs `build_v4.py` (which runs `build_v3.py`), then merges `scripts/v5/*` (voice/doc/vision subjects, concepts, Project Ladder) and re-embeds `index.html` |
| `scripts/linkcheck.py` | HTTP-checks every resource URL → `docs/resources_linkcheck.csv` |
| `docs/` | Screenshots, link report, stats, launch drafts |

## Link check

All 259 resource URLs were checked on 2026-10-11, and 254 passed the automated check. The 5 exceptions are known false negatives. ISO/IEC 42001 (iso.org) returns 403 to scripted clients. Three docs.vllm.ai pages returned 429 (rate limiting) but are live. The Stanford CS336 site timed out at 20 s but answers with a 301 when given a longer timeout. EUR-Lex returns a 202 bot challenge to scripts. See `docs/resources_linkcheck.csv`.

## GitHub Pages

The workflow `.github/workflows/pages.yml` publishes the repo root. After pushing, set Pages source to "GitHub Actions". No build step is needed.

## License

- **Code** (HTML/JS/CSS/scripts): [MIT](./LICENSE)
- **Content** (curriculum, explainers, diagrams): [CC BY 4.0](./LICENSE-CONTENT). Please credit **Sapient Edge**.
- Bundled Mermaid is MIT-licensed by its authors.

## Disclaimer

This is a learning atlas, not a certification. Prices, hardware figures and examples are illustrative, so re-check them before relying on them. Nothing here is legal advice on the EU AI Act or other compliance topics.
