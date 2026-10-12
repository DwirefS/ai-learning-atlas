# Sapient Edge — AI Learning Atlas (v8)

**A free, offline "Khan Academy for AI engineering", centered on agentic AI.** 129 full lessons, each with an intuition, a step-by-step walkthrough, a diagram, a worked example, common mistakes, an enterprise case, key takeaways, a quiz with explanations, and annotated resources. There are 11 interactive explainers. Mastery levels go Familiar → Proficient → Mastered.

**0→100 expert learning paths for 13 enterprise agentic-AI roles**, organized as 7 tracks plus a Shared Core.

**Roles (new in v4).** The 8 core roles are AI Engineer · Forward Deployed Engineer · Agent Ops Engineer · AI Security Engineer · AI Infrastructure Engineer · Cloud Security Engineer (AI) · AI Governance Engineer · AI Evals Engineer. The other 5 are roles most lists miss: **AI-Ready Data Engineer** · ML / Post-training Engineer · AI Platform / LLMOps Engineer · AI Solutions Architect · AI Product Engineer / Manager.

**Tracks:** AI Architect · AI Engineer · AI Inference Engineer · AI Infrastructure · Agentic AI · **AI-Ready Data Engineering** (new) · **AgentOps, Evals, Security & Governance** (new).

Everything is centered on agentic AI and on the data engineering agents depend on. It's an atlas, not a link dump. Every subject and every topic has an original explainer. There are 57 concept cards with diagrams and worked examples (the math is checked), plus quizzes, hands-on labs, capstones, learning paths (including a **Universal Agentic Path** that covers all 13 roles in order) and a glossary. Current as of October 2026.

![Home course map](docs/screenshots/16-desktop-home.png)

![A lesson](docs/screenshots/17-desktop-lesson.png)

## At a glance

| | v3 | v7 | v8 |
|---|---|---|---|
| Full lessons (intuition, how, diagram, example, mistakes, enterprise, takeaways, quiz, annotated resources) | – | – | **129** |
| Per-lesson diagrams (with alt text) | – | 0 | **129** |
| Interactive explainers (dependency-free JS/SVG) | – | – | **11** |
| Subtopic explanations | – | 0 | **782** |
| Annotated resources (why + level) | – | 0 | **275** |
| Words of teaching content (curriculum JSON) | – | 82,537 | **151,084** |
| Role cards (mission, day-to-day, skills, tools, interview signals, capstone, mapped curriculum) | – | **13** | 13 |
| Tracks (+ Shared Core) | 5 | **7** | 7 |
| Subjects | 91 | **129** | 129 |
| Topics (each with its own explainer) | 198 | **328** | 328 |
| Subtopics | 990 | **1,644** | 1,644 |
| Quiz questions (≥3 per subject, with explanations) | 283 | **412** | 412 |
| Unique resource URLs (link-checked) | 130 | **275** | 275 |
| Concept cards (diagram + worked example) | 41 | **57** | 57 |
| Capstone projects | 6 | **8** | 8 |
| Project ladder builds (4 tiers) | – | **28** | 28 |
| Learning paths | 5 | **7** | 7 |
| Glossary terms | 104 | **143** | 143 |

## What's new in v8: learn on-site

- **Every subject is now a full lesson.** Each has: 💡 Intuition → ⚙️ How it works → 🗺️ Diagram → 🧪 Interactive explainer (where relevant) → 🧮 Worked example or code → 📚 Topics (with subtopic explanations) → ⚠️ Common mistakes → 🏢 In the enterprise → ✅ Key takeaways → 📝 Quiz → 🔗 Annotated resources (why to read each one, plus its level) → lab and prev/next.
- **11 interactive explainers**, all dependency-free JS + SVG and keyboard accessible: softmax & temperature, tokenization, self-attention, KV cache memory, static vs continuous batching, quantization, RAG retrieval, agent loop, eval math (pass@k / pass^k / sample size), model routing, context budget. Find them all under **Explainers** (`#/playground`).
- **Learner UX:**
  - Home course map.
  - Mastery levels per lesson (Familiar / Proficient / Mastered, earned through quizzes), reading time and prev/next.
  - Deep-linkable routes (`#/lesson/<id>`, `#/track/<id>`, …).
  - Mobile reading typography; skip link, focus rings and diagram alt text.
  - XP, ranks and new badges.
- **Pedagogy:** see [`docs/pedagogy.md`](docs/pedagogy.md) for what we borrowed from Khan Academy, DeepLearning.AI, Hugging Face, fast.ai, Google MLCC and Microsoft Learn.
- **Quality bar enforced by the build:** `scripts/build_v8.py` fails if any lesson is missing a section. Lesson content lives in `scripts/v8/lessons/*.py`, and resource notes in `scripts/v8/resnotes.py`.
- **QA:** all 129 lessons load in headless Chrome on desktop (1440px) and mobile (390px). Every diagram renders, every explainer mounts, there are 0 console errors and no horizontal overflow.

![Lesson diagram and explainer](docs/screenshots/19-desktop-lesson-diagram-widget.png)

### New in v7: Suraj Sharma's 12 stages
This version goes deeper on the stages of Suraj Sharma's "6 months to become an AI Engineer in the Agentic Era" that the atlas covered only thinly:
- **8 new topics:** context engineering and token budgets, agentic RAG with self-correction, raw MCP over JSON-RPC, streaming UX, graceful-degradation fallback chains, the DPO feedback flywheel, ADRs and teardowns, and three-tier memory.
- **3 concept cards, with diagrams and worked math:** Context Token Budget Allocator, Agentic RAG Self-Correction Loop, and Fallback and Degradation Chain.
- **7 Project Ladder builds:** p-context, p-mcp-raw, p-agentic-rag, p-memory, p-streaming, p-flywheel and p-teardown.
- **An untimed path**, "Agentic AI Engineer (Suraj Sharma's 12 stages)", that maps each stage to a subject and a ladder project.
- **18 audit topics** attributed to the post, all now covered (185 of 185 audit items).

## New in v6: coverage audit
We checked the atlas against 167 topics taken from about 45 job postings from 2026, course syllabi (DeepLearning.AI, CS336, CS224N, FSDL, Hugging Face), vendor docs (OpenAI, Anthropic, Google, Bedrock, Azure Foundry, Databricks, LangChain, LlamaIndex) and roadmap repos. Before: 114 covered, 31 thin, 22 missing. After: 167 covered. See `docs/coverage_audit.csv` (after) and `docs/coverage_audit_before.csv`. To re-run it: `python3 scripts/audit/audit.py`.
The audit added 8 subjects: NLP Foundations, Agentic Design Patterns, Agent Frameworks & Platforms, Reasoning Models & API Platform, RL Environments, Generative Media, Agent Attacks and Responsible AI. It also added 8 topics to existing subjects.

## New in v5

- **Project Ladder view: one AI skill = one project.** There are 21 hands-on builds (28 as of v7) in 4 tiers (Starter → Expert). Each has a goal, stack options, steps, stretch goals, checkable "done when" criteria, mapped roles and linked subjects. They cover semantic search over notes, your own MCP server to a database, function calling that books real calendar meetings, evals that catch prompt regressions, multimodal PDF RAG, a receipt reader, model routing, an observability dashboard, guardrails, a research/cold-email agent, a LoRA fine-tune in your voice, and a phone voice agent. The agentic, data and ops builds are CDC data product, durable workflows, kill switches, policy as code, audit trail, secure landing zone, trajectory evals, self-hosted inference and an end-to-end FDE engagement.
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
| `assets/js/app.js` | UI logic (routes, lessons, mastery, XP/badges) |
| `assets/js/widgets.js` | 11 interactive explainers (no dependencies) |
| `scripts/build_v8.py` | Current build: runs the v7→v3 chain, merges `scripts/v8/lessons/*` and resource notes, validates the lesson bar, re-embeds `index.html` |
| `docs/pedagogy.md` | Lesson design and rationale |
| `assets/img/` | SVG illustrations (track heroes, level art) |
| `assets/vendor/mermaid.min.js` | Bundled Mermaid (offline diagrams) |
| `data/curriculum.json`, `data/concepts.json` | Full content (also per-track `data/_*.json` and `data/_roles.json`) |
| `scripts/build_v5.py` | Runs `build_v4.py` (which runs `build_v3.py`), then merges `scripts/v5/*` (voice/doc/vision subjects, concepts, Project Ladder) and re-embeds `index.html` |
| `scripts/linkcheck.py` | HTTP-checks every resource URL → `docs/resources_linkcheck.csv` |
| `docs/` | Screenshots, link report, stats, launch drafts |

## Link check

All 275 resource URLs were re-checked on 2026-10-12 for v8, and 272 passed the automated check. None of the 3 exceptions is a dead link:

- ISO/IEC 42001 (iso.org) returns 403 to scripted clients.
- docs.vllm.ai returned 429 (rate-limited after many requests to the same host).
- The Stanford CS336 site timed out at 20 s, but answers with a 301 when given a longer timeout. See `docs/resources_linkcheck.csv`.

## GitHub Pages

The workflow `.github/workflows/pages.yml` publishes the repo root. After pushing, set Pages source to "GitHub Actions". No build step is needed.

## License

- **Code** (HTML/JS/CSS/scripts): [MIT](./LICENSE)
- **Content** (curriculum, explainers, diagrams): [CC BY 4.0](./LICENSE-CONTENT). Please credit **Sapient Edge**.
- Bundled Mermaid is MIT-licensed by its authors.

## Disclaimer

This is a learning atlas, not a certification. Prices, hardware figures and examples are illustrative, so re-check them before relying on them. Nothing here is legal advice on the EU AI Act or other compliance topics.
