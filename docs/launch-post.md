# Draft: Launching the Sapient Edge AI Deep Learning Atlas (v3)

*Status: draft only. Do not publish until approved.*

---

Most "AI roadmaps" are a list of topic names and a 90-day promise. The jobs that matter (architecting AI platforms, serving models under SLOs, running GPU fleets, building agents you can trust with real permissions) need a deeper map.

Today we're open-sourcing the **AI Deep Learning Atlas**. It has five role tracks from foundations to frontier (Architect, Engineer, Inference, Infrastructure, Agentic), plus a Shared Core.

### What's inside

- **91 subjects, 198 topics, 990 subtopics.** Every subject *and every topic* has its own original explainer, so it's not a link dump.
- **41 concept cards** with diagrams and worked examples, with the math checked. They cover ring all-reduce, MIG vs time-slicing, cold-start math, cost per million tokens, KV-aware routing, prompt-injection defense, MoE routing, HNSW, GraphRAG, A2A, distillation, RoPE and more.
- **The infra content most roadmaps skip**: NCCL/RDMA debugging, GPU Operator, DRA, Kueue, Xid/ECC triage, NCCL hangs, unit economics, power and cooling, weight exfiltration and MCP permissions.
- **283 quiz questions**, a lab per subject, and **6 capstones** covering architecture, infra, deploy, security, observability, scaling and cost.
- **5 learning paths** with no deadlines (Cloud/DevOps → AI Infra, SWE → AI Engineer, Architect for clients, and more).
- A **104-term glossary**, XP, ranks and streaks.
- **130 resource links**, all checked in October 2026.
- **Works fully offline.** It's one static page with the diagrams bundled.

### How to use it

1. Pick a learning path, or start with the Shared Core.
2. Tick subtopics as you go, and follow "what to learn next."
3. Open a concept card whenever a term keeps coming up.
4. Finish with your track's capstone. It doubles as a portfolio piece.

### Why we built it

Sapient Edge helps enterprises ship AI systems that survive production. We wanted a teaching artifact we'd be proud to hand to a client or a new hire. A lot of compute went into building it, so it should help as many people as possible.

Repo + live site: *[add GitHub URL after publish]*

— Sapient Edge
