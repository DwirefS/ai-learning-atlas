def C(id,title,hints,summary,body,mermaid,example):
    return dict(id=id,title=title,trackHints=hints,summary=summary,body=body,mermaid=mermaid,example=example)
CONCEPTS=[
C("voice-latency","Voice Agent Latency Pipeline",["engineer","agentic"],
"Where the milliseconds go between a caller finishing a sentence and hearing the agent reply, and how streaming hides them.",
"""Voice-to-voice latency is measured from the end of user speech to the first audible agent audio. People perceive pauses above roughly a second as awkward, so production targets are usually around 500-800 ms.

In a cascaded pipeline the hops are: end-of-turn detection (VAD plus a semantic turn model deciding the user is done), final STT transcript, LLM time to first token, TTS time to first audio byte, and network and jitter buffers in both directions.

The key trick is streaming overlap. STT streams partial transcripts so the final arrives quickly; the LLM streams tokens; TTS starts speaking as soon as the first sentence is complete, while the rest is still being generated. The user hears the first sentence while the agent is still thinking about the third.

Tool calls break the flow. If a calendar lookup takes 1.5 s, speak a short filler ('Let me check that for you') and then the result. Barge-in must cancel TTS and generation within about 200 ms.

Speech-to-speech models remove the STT and TTS hops but keep turn detection and network.""",
"""flowchart LR
  U[User stops speaking] --> EOT[End-of-turn detect]
  EOT --> STT[Final transcript]
  STT --> LLM[LLM first token]
  LLM --> S1[First sentence complete]
  S1 --> TTS[TTS first audio]
  TTS --> N[Network to caller]
  LLM -.tool call.-> F[Speak filler]
  B[Barge-in] -.cancel.-> TTS""",
"Budget: end-of-turn 200 ms + final transcript 100 ms + LLM first token 300 ms + first sentence (about 8 tokens at 50 tokens/s) 160 ms + TTS first audio 120 ms + network 80 ms = 960 ms. Switching to a faster turn model (100 ms) and a smaller LLM (180 ms first token) gives 100 + 100 + 180 + 160 + 120 + 80 = 740 ms, inside an 800 ms target."),
C("docrag-pipeline","Document and Multimodal RAG Pipeline",["engineer","data"],
"Two roads from PDF to answer, parse-then-embed and embed-the-page, and how hybrid systems combine them.",
"""Road 1, parse-then-embed: a layout parser splits each page into regions; tables become Markdown or HTML with headers; charts and images get VLM captions and, where possible, extracted data series; text is chunked with page and bounding-box references and embedded as single vectors.

Road 2, embed-the-page: each page image goes through a ColPali-style model that outputs one vector per patch. Queries are embedded per token and scored by late interaction: for each query token take the best-matching patch similarity and sum. No OCR, strong on visual layouts, but much bigger indexes.

Hybrid: run both retrievers, fuse with reciprocal rank fusion, rerank, then send the top pages (as images) plus their extracted text to a VLM that answers with page-level citations.

Evaluate per question type (prose, table, chart, image), track index size and cost per query, and keep image counts and resolution under control.""",
"""flowchart TB
  PDF[PDF pages] --> LP[Layout parse]
  LP --> TB[Tables as Markdown]
  LP --> CH[Charts and figures to VLM captions]
  LP --> TX[Text chunks]
  TB --> E1[Text embeddings]
  CH --> E1
  TX --> E1
  PDF --> IMG[Page images]
  IMG --> CP[ColPali patch vectors]
  Q[Query] --> E1
  Q --> CP
  E1 --> RRF[Rank fusion + rerank]
  CP --> RRF
  RRF --> VLM[VLM answer with page citations]""",
"Index size: 10,000 pages × 1,030 patch vectors × 128 dimensions × 2 bytes (fp16) ≈ 2.64 GB for the visual index. Binarizing to 1 bit per dimension gives 10,000 × 1,030 × 16 bytes ≈ 165 MB, 16x smaller. A text index of 10,000 pages × 3 chunks × 1,024 dims × 4 bytes ≈ 123 MB."),
C("model-router","Model Router: Cheap vs Smart",["engineer","inference","trust"],
"Send each request to the cheapest model that will get it right, escalate when needed, and prove the savings with evals.",
"""Most traffic is easy, so routing can cut cost substantially without hurting quality. Routing strategies:

Rules: route by task type, input length, tenant tier or tool needs (for example, all classification goes to a small model).
Classifier routers: a small model or embedding classifier predicts difficulty or which model will succeed, trained on eval data where both models were scored.
Cascades: try the cheap model first, check its output with a verifier (schema validity, confidence, a judge, or tests), and escalate to the strong model only on failure.

Measure on a golden set: quality of the routed system versus always-strong, cost per request, latency, and the escalation rate. Watch for drift; the share of hard requests changes over time.

Implement in the LLM gateway so every app benefits, with logging of which route each request took and why.""",
"""flowchart LR
  R[Request] --> RT{Router: rules or classifier}
  RT -->|easy| S[Small model]
  RT -->|hard| L[Large model]
  S --> V{Verifier: schema, judge, tests}
  V -->|pass| OUT[Response]
  V -->|fail| L
  L --> OUT
  OUT --> LOG[(Route, cost, quality logs)]""",
"1M requests per month at 1,500 tokens each. Always-large at $5 per 1M tokens: 1.5B tokens × $5/M = $7,500. Cascade: everything hits small ($0.30/M) = $450, and 20% escalate to large = 300M tokens × $5/M = $1,500, total $1,950, a 74% saving. It's only worth it if routed quality on the golden set stays within your threshold.")]
