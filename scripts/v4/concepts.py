def C(id,title,hints,summary,body,mermaid,example):
    return dict(id=id,title=title,trackHints=hints,summary=summary,body=body,mermaid=mermaid,example=example)
CONCEPTS=[
C("agent-data-arch","Agent–Data Integration Reference Architecture",["data","agentic","architect"],
"How enterprise data reaches agents safely: sources → lakehouse and indexes → semantic layer and catalog → MCP tools → agent, with identity and policy on every hop.",
"""'Integrate the data sources and the agents do the rest' is the right ambition. This is the architecture that makes it safe.

Sources (OLTP databases, SaaS apps, documents, tickets, events) flow two ways. Structured changes stream through CDC into lakehouse tables (bronze → silver → gold) governed by data contracts. Unstructured content goes through a parse → chunk → enrich → embed pipeline into a search index that stores ACLs with every chunk.

On top sit three access layers. A semantic layer defines metrics so agents ask for 'net revenue by region' instead of writing free SQL. A catalog holds descriptions, owners, classifications, health and lineage, so agents can discover data and check whether it is trustworthy right now. Action APIs wrap systems of record.

All three are exposed to agents as MCP tools and resources: retrieve, query_metric, find_dataset, and task-shaped write tools. Every call carries the end user's identity (OAuth on-behalf-of), passes a policy engine (allow / deny / require approval) and emits a trace span and an audit event.

The agent harness never holds database credentials and never sees raw tables. It sees a small, documented menu of tools, which is better for accuracy and for security.

Common mistakes: one god-mode SQL tool; vector-only designs that cannot count; lineage that stops before the agent, so nobody can say which source fed an answer.""",
"""flowchart LR
  subgraph Sources
    DB[(OLTP DBs)]
    SaaS[SaaS apps]
    Docs[Documents]
  end
  DB -->|CDC| LH[(Lakehouse gold tables)]
  SaaS -->|connectors| LH
  Docs -->|parse chunk embed| IDX[(Search index with ACLs)]
  LH --> SEM[Semantic layer]
  LH --> CAT[Catalog and lineage]
  IDX --> CAT
  SEM --> MCP[MCP tools]
  IDX --> MCP
  CAT --> MCP
  MCP --> POL{Policy engine}
  POL --> AG[Agent harness]
  U[User identity] -.on behalf of.-> MCP
  AG --> TR[Traces and audit log]""",
"A user asks 'Which of my top-10 accounts have open P1 tickets, and what does their contract say about SLA credits?' The agent makes 3 tool calls: query_metric(top accounts by ARR, owner = me) ≈ 300 ms, search_tickets(accounts, P1, open) ≈ 200 ms, retrieve(contract SLA clause, those accounts) ≈ 400 ms. Tool time is 0.9 s, plus two model turns of about 1.5 s each, for roughly 3.9 s total, and every call ran with the user's own permissions."),
C("permission-aware-rag","Permission-Aware RAG: Pre-filter vs Post-filter",["data","engineer","trust"],
"Retrieval must enforce the same access rules as opening the file. Pre-filtering inside the index is the safe default; post-filtering leaks and starves.",
"""Every chunk is stored with the principals allowed to read it (user and group IDs) and its sensitivity label. At query time the system resolves the caller's identity and group memberships from the identity provider (cached briefly so revocations land fast).

Pre-filter: the permission predicate is applied inside the vector or search engine before ranking. Only authorized chunks compete for top-k, so the user gets the best results they are allowed to see.

Post-filter: the engine ranks everything, returns top-k, then the app drops forbidden chunks. Two problems. Starvation: if the user may see a small share of the corpus, most of top-k is discarded and the answer has no evidence. Leakage: counts, timing, snippets in logs, or a bug in the filter expose forbidden content.

For complex, fast-changing permissions (sharing links, nested groups, per-record rules), combine a coarse metadata pre-filter (tenant, department) with a fine-grained ReBAC check (OpenFGA or SpiceDB, Zanzibar-style) on the candidate set.

Remember the other leak paths: semantic caches keyed only on query text, agent memories and summaries that mix scopes, fine-tuned models that memorized restricted data, and traces readable by more people than the source documents.""",
"""flowchart TB
  Q[User query + identity] --> ID[Resolve groups from IdP]
  ID --> PF{Pre-filter: allowed principals}
  PF --> ANN[ANN search over authorized chunks]
  ANN --> RR[Rerank top-k]
  RR --> FG{Fine-grained ReBAC check}
  FG --> LLM[Generate answer with citations]
  X[Post-filter after top-k] -.starves and leaks.-> LLM""",
"A user may read 2% of a 1M-chunk corpus. Post-filtering a top-50 result: the chance that none of the 50 is authorized is 0.98^50 ≈ 0.364, so about 36% of queries return zero evidence, and on average only 50 × 0.02 = 1 authorized chunk survives. Pre-filtering returns 50 authorized chunks every time."),
C("cdc-freshness","CDC Freshness Budget for Agent Context",["data","trust"],
"How long from a database commit until the agent can see it, and how to budget each hop.",
"""Freshness is the time from a change committed in the source system to that change being visible to the agent: in a table it queries, or in an index it retrieves from. It is an SLO you can budget hop by hop.

Typical path: the commit lands in the WAL; Debezium reads it and publishes to Kafka; a stream processor transforms it, upserts into a lakehouse table and, for text, re-chunks and re-embeds; the search index refreshes so the new vectors become searchable.

Each hop has a latency distribution. Embedding and index refresh usually dominate, because embeddings are batched for throughput and indexes refresh on intervals. Trade-offs: smaller batches are fresher but cost more per token; shorter refresh intervals load the cluster.

Deletes and ACL changes need the same, or a tighter, budget than inserts, because a stale vector for a revoked document is a data leak. Hash chunk text so unchanged content is never re-embedded.

Monitor consumer lag and end-to-end freshness with synthetic canary records: write a marker row every minute and measure when it becomes retrievable.""",
"""flowchart LR
  C[Commit in source DB] --> W[WAL]
  W --> D[Debezium]
  D --> K[Kafka topic]
  K --> F[Stream processor]
  F --> T[(Lakehouse upsert)]
  F --> E[Embed batch]
  E --> I[(Index refresh)]
  I --> A[Agent retrieval]""",
"p95 budget: WAL→Debezium 1 s + Kafka 0.5 s + processing 1 s + embedding batch window 5 s + embed call 1.5 s + index refresh 1 s = 10 s. Embedding plus refresh is 7.5 of the 10 s (75%), so that is where to tune. Halving the batch window to 2.5 s gives a 7.5 s p95."),
C("unstructured-pipeline","Unstructured Data Pipeline: Parse → Chunk → Enrich → Embed",["data","engineer"],
"The stages that turn messy documents into cited, permissioned, deduplicated evidence, and what each costs.",
"""Stage 1, fetch: connectors pull content plus metadata and ACLs, incrementally, using change feeds or modified-since cursors.
Stage 2, parse: route by document class. Born-digital HTML needs simple extraction; PDFs need layout analysis; scans need OCR; complex tables and charts may need a vision-language model. Output structured elements (title, heading, paragraph, table, figure) with page numbers.
Stage 3, normalize: clean boilerplate, detect language, and remove exact and near-duplicates (MinHash).
Stage 4, enrich: attach source, section path, dates, owner, ACLs, PII tags and domain metadata used for filtering.
Stage 5, chunk: split on structure, keep tables whole, prepend context headers.
Stage 6, embed and index: batch on GPUs or via API, write to the index with source key and version.

Make every stage idempotent and versioned so you can re-run one stage when a better parser or embedding model appears. Re-index blue/green behind an alias, evaluated on a golden set before switching.""",
"""flowchart LR
  F[Fetch + ACLs] --> P[Parse by class]
  P --> N[Normalize + dedup]
  N --> EN[Enrich metadata + PII]
  EN --> CH[Structure-aware chunk]
  CH --> EM[Embed batch]
  EM --> IX[(Index v2)]
  IX --> AL{Alias switch after evals}""",
"Corpus of 1M pages, about 2 chunks per page at 400 tokens each = 800M tokens. At $0.02 per 1M tokens, the full embed costs 800 × $0.02 = $16. If 5% of pages change per day and content hashing skips the rest, daily re-embedding is 40M tokens = $0.80. Parsing, not embedding, is usually the bigger bill."),
C("agentops-loop","The Agent Ops Control Loop",["trust","agentic","infra"],
"Observe → evaluate → decide → act: how operations keeps a fleet of agents within SLOs, budgets and policy.",
"""Agent Ops runs a continuous control loop around every production agent.

Observe: traces (OpenTelemetry GenAI spans) capture every model call, tool call, token count, cost and outcome; queues report depth and age; gateways report error rates and spend.
Evaluate: online evals score a sample of runs; SLIs are computed (task success, p95 time to complete, cost per task, escalation rate, policy-violation rate); error budgets burn or recover.
Decide: alerts and automated rules compare against SLOs and budgets. Is this a provider blip (retry), a regression (roll back), a runaway (cap), or an attack (kill switch)?
Act: levers include retries and failover in the gateway, step/token caps, budget circuit breakers, scoped kill switches (tool, agent, tenant, global autonomy), degrade modes (read-only or approval-required), and atomic rollback of prompt, model alias, tools and policy.

Then learn: failures become eval cases, runbooks are updated, and new alerts are added. The loop should be faster than the agent: a runaway agent can spend in minutes what a human notices in hours.""",
"""flowchart LR
  O[Observe: traces, queues, spend] --> E[Evaluate: online evals, SLIs]
  E --> D{Decide vs SLOs and budgets}
  D -->|blip| R[Retry or failover]
  D -->|regression| RB[Rollback manifest]
  D -->|runaway| CAP[Step and budget caps]
  D -->|attack| KS[Kill switch]
  R --> O
  RB --> L[Learn: new evals, runbooks]
  CAP --> L
  KS --> L
  L --> O""",
"A task averages 12 steps, each with 6,000 input tokens at $3/M and 400 output tokens at $15/M: per step 0.018 + 0.006 = $0.024, so $0.288 per task. A loop bug that runs 200 steps costs $4.80 per task. At 1,000 tasks/hour that is $4,800/hour versus a normal $288/hour. A 30-step cap limits the worst case to $0.72 per task."),
C("eval-pipeline","Eval Pipeline: Offline Gates and Online Monitoring",["trust","engineer"],
"From error analysis to golden sets, calibrated judges, CI gates and production sampling, with the statistics to trust the numbers.",
"""1. Error analysis: read real traces, label failures, cluster into failure modes.
2. Golden set: versioned cases covering common paths, edge cases and every past incident, plus a held-out slice.
3. Graders: deterministic checks first (schemas, values, tool calls, end states); calibrated LLM judges for subjective criteria; humans for calibration and spot checks.
4. Offline gate: CI runs the suite on every change to prompts, models, tools or retrieval; results are compared with the production baseline using confidence intervals; significant regressions block the merge.
5. Canary and online evals: a small share of live traffic is scored asynchronously; SLOs and drift by cohort are monitored.
6. Feedback: low scores and user corrections go to review queues; confirmed failures are promoted into the golden set.

Statistics matter. A 200-case suite measures an 80% pass rate with a standard error of about 2.8 points, so a 2-point drop is noise. Judges are imperfect classifiers; correct the observed pass rate with their measured true-positive and true-negative rates.""",
"""flowchart LR
  EA[Error analysis] --> GS[Golden set v_n]
  GS --> GR[Graders: code, judge, human]
  GR --> CI{CI gate vs baseline}
  CI -->|pass| CAN[Canary + online evals]
  CI -->|fail| FIX[Fix and retry]
  CAN --> MON[SLO and drift monitors]
  MON --> RQ[Review queue]
  RQ --> GS""",
"Judge calibration: TPR 0.90, TNR 0.80. The judge says 75% pass. The true pass rate p solves 0.75 = 0.90p + 0.20(1 − p), so p = (0.75 − 0.20) / 0.70 ≈ 0.786, about 79%. Sample size: with n = 200 and p = 0.8, SE = √(0.8 × 0.2 / 200) ≈ 0.028, so the 95% interval is about ±5.5 points."),
C("policy-gate","Policy-as-Code Gates Across the Agent Lifecycle",["trust","architect"],
"The model proposes, the policy engine disposes: the same rules enforced in CI, at admission, at every tool call and on data access.",
"""Policies written in Rego (OPA) or Cedar live in Git with unit tests and are evaluated by an engine outside the model.

Gate 1, CI: Conftest checks each agent manifest. Are the declared tools allowed for its risk tier? Is the model alias on the approved list? Is an eval report less than 30 days old attached? Is a human-oversight config present for high-risk actions?
Gate 2, admission: Gatekeeper or Kyverno admits only signed images and approved configurations to the cluster.
Gate 3, runtime tool calls: middleware sends {agent, user, tenant, tool, arguments, risk signals} to the engine and gets allow, deny, or require-approval. Approvals become durable workflow signals.
Gate 4, data access: field-level filtering by classification and the user's entitlements.

Every decision is logged with input, result, reason and policy version. That is audit evidence and incident data at once. Roll out new deny rules in dry-run first, and watch deny rates for both attacks and broken rules.""",
"""flowchart LR
  M[Agent manifest PR] --> G1{CI: Conftest}
  G1 --> G2{Admission: Gatekeeper}
  G2 --> RT[Agent running]
  RT -->|tool call| G3{Runtime authorizer OPA or Cedar}
  G3 -->|allow| T[Tool executes]
  G3 -->|require approval| H[Human approval signal]
  G3 -->|deny| X[Blocked + reason]
  T --> G4{Data field filter}
  G3 --> LOG[(Decision log)]""",
"Refund policy: agents may refund up to $100 alone, up to $500 with approval, and never above $500. A call refund_order(amount = 320, tenant = acme) by the support agent returns require-approval. Engine latency is typically about 1 ms per decision, so 10 tool calls per run add about 10 ms, which is negligible next to roughly 1.5 s per model turn."),
C("audit-trail","AI Audit Trail: From Run to Evidence",["trust"],
"What an accountable agent records, how it stays tamper-evident, and how it becomes evidence for auditors.",
"""An audit event is a structured, immutable record answering: who asked, who or what acted on whose behalf, which versions were live (agent, model, prompt, tools, policy), which sources were used, what tools were called and with what result, which policies decided what, who approved, and what changed in the world.

Write events to write-once storage (object lock) with hash chaining: each batch includes the hash of the previous batch, so any edit breaks the chain. Hold delete rights outside the engineering team. Minimize personal data by storing references and tokenized fields, and apply retention schedules by regulation and contract.

Link every audit event to its trace through run_id. Traces are rich, short-lived and for engineers; audit events are lean, long-lived and for accountability.

Evidence is the audit trail organized by control: run reconstruction on demand, versions deployed with their eval results, human-oversight statistics, incidents and corrective actions. Express it in machine-readable form (for example OSCAL) where possible.""",
"""flowchart TB
  RUN[Agent run run_id] --> EV[Audit events: actor, versions, sources, tools, decisions, approvals]
  EV --> HC[Hash chain batches]
  HC --> WORM[(WORM storage, object lock)]
  RUN --> TR[(Traces, short retention)]
  WORM --> REP[Evidence reports by control]
  REP --> AUD[Auditor or regulator]""",
"200,000 runs per day × 4 KB of audit events per run = 800 MB per day, so about 292 GB per year (800 MB × 365). Keeping it for 6 years is about 1.75 TB, which is cheap in archive storage. The expensive part is the query layer for run reconstruction, not storage."),
C("controls-crosswalk","Controls Crosswalk: EU AI Act × NIST AI RMF × ISO/IEC 42001",["trust","architect"],
"Write each control once, map it to every obligation it satisfies, implement it as a gate, and collect evidence automatically.",
"""Frameworks overlap heavily. Instead of three compliance programs, keep one control library.

A control is a testable statement in your own words, for example 'Every production agent has a passing eval report less than 30 days old' or 'All tool calls by high-risk agents are logged with policy decisions and retained six years'. Each control records its owner, its implementation (policy, CI gate, process), its test and its evidence source.

The crosswalk maps controls to obligations: EU AI Act articles (risk management, Art. 9; data governance, Art. 10; technical documentation, Art. 11; record-keeping, Art. 12; transparency to deployers, Art. 13; human oversight, Art. 14; accuracy, robustness and cybersecurity, Art. 15), NIST AI RMF functions and subcategories (Govern, Map, Measure, Manage), and ISO/IEC 42001 clauses and Annex A controls.

Remember the amended EU timeline: Annex III high-risk obligations apply from 2 December 2027 and Annex I from 2 August 2028, while prohibitions, AI literacy, GPAI and Article 50 transparency already apply. This is education, not legal advice; confirm with counsel.""",
"""flowchart LR
  subgraph Obligations
    EU[EU AI Act Art 9-15, 50]
    NI[NIST AI RMF Govern Map Measure Manage]
    ISO[ISO 42001 clauses + Annex A]
  end
  EU --> CL[Control library]
  NI --> CL
  ISO --> CL
  CL --> IMP[Implementation: policy, gate, process]
  IMP --> EVD[(Automated evidence)]
  EVD --> DASH[Compliance status per agent]""",
"Control C-07, 'eval report less than 30 days old before deploy', maps to EU AI Act Art. 9 and Art. 15, NIST AI RMF Measure, and ISO 42001 performance evaluation. That is one CI gate for four obligations. Fifteen such controls, each covering about 3 obligations, give roughly 45 mappings from 15 implementations."),
C("fde-lifecycle","FDE Engagement Lifecycle",["architect","engineer"],
"Discover → scope → prototype → harden → pilot → hand over → feed back: how forward deployed engineers take agents from idea to production.",
"""Discover: shadow the workflow and quantify volume, time and cost. Find where data access, value and risk tolerance line up.
Scope: one narrow use case, a baseline metric and target, required data and system access, security reviewers, and explicit non-goals.
Prototype (days): real-shaped data, simplest agent that could work, demo to the people who do the work.
Harden (weeks): customer-derived eval set, least-privilege connectors and MCP servers, tracing, guardrails, human approval for risky actions, security and privacy review.
Pilot: a small user group, feedback capture, an outcome dashboard, and fixes driven by error analysis.
Hand over: IaC, runbooks, dashboards, eval suite, trained owners and champions.
Feed back: reusable connectors and patterns to the FDE practice, feature requests to the product.

The critical path is almost always access and approvals, not prompting, so start security conversations in week one.""",
"""flowchart LR
  D[Discover] --> S[Scope + metric]
  S --> P[Prototype days]
  P --> H[Harden weeks: evals, IAM, security review]
  H --> PI[Pilot + feedback]
  PI --> HO[Handover: runbooks, owners]
  HO --> FB[Field feedback to product]
  PI -.error analysis.-> H""",
"Support deflection case: 40,000 tickets/month, 30% resolved by the agent = 12,000 tickets × $6 human cost saved = $72,000/month. Costs: 40,000 conversations × $0.30 model and tool cost = $12,000, plus $15,000 platform and operations = $27,000. Net value is $45,000/month, which is the number the CFO asks for.")]
