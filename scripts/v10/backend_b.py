from helpers10 import R, Q, T, SUBJ, C
S = []
# ---------------------------------------------------------------- b-docstore
sid = "b-docstore"
S.append(SUBJ(sid, "MongoDB and Document Stores",
 "Many customer systems, and many agent memory and logging stores, are document databases. Knowing when documents beat tables, and how to model them, avoids painful migrations.",
 "Document databases such as MongoDB store JSON-like documents with flexible schemas, rich nested structures and horizontal scaling. They shine when an entity is naturally read and written as a whole (a product with variants, a conversation with its messages, an agent run with its steps), and when the shape varies between records.\n\nThe central skill is modeling for access patterns: embed what you read together, reference what grows without bound or is shared. Know the trade-offs too: single-document writes are atomic, multi-document transactions exist but cost more, and schema validation is opt-in. MongoDB Atlas also offers vector search, so documents and embeddings can live together.",
 "Model agent runs (steps, tool calls, costs) in a document store: embed bounded step arrays, reference large artifacts, add JSON Schema validation and a compound index, then compare with the equivalent Postgres JSONB design.",
 [T(sid, "model", "Modeling for access patterns",
   "Start from the queries, not the entities. If the app always loads a conversation with its last 50 messages, embedding recent messages in the conversation document gives one read. If a channel's messages grow forever, embedding them will eventually exceed document size limits (16 MB in MongoDB) and slow every update, so reference them in a separate collection, bucketed by time. Duplicate small, rarely changing fields (such as a user's display name) to avoid joins, and accept that updates then touch several documents. Turn on schema validation for fields your code depends on.",
   [("Embed vs reference", "Embed data read together and bounded in size; reference data that is shared or grows without bound."),
    ("Bucketing unbounded data", "Group time-series or chat data into buckets (per day or per N items) to cap document size."),
    ("Schema validation", "Use $jsonSchema validators so required fields and types are enforced by the database."),
    ("Compound indexes", "Index fields in the order queries filter and sort, as in relational databases.")]),
  T(sid, "tradeoffs", "Consistency, transactions and choosing a store",
   "In MongoDB a single-document write is atomic, which is why good document models put data that must change together into one document. Multi-document ACID transactions exist but add latency and coordination, so frequent use is a signal the data might be relational. Read and write concerns control durability and consistency across a replica set. Choose a document store for variable, hierarchical, document-shaped data with clear access patterns. Choose Postgres when you need many-to-many relationships, ad-hoc joins and strong constraints. Postgres JSONB is a middle ground for occasional flexibility.",
   [("Single-document atomicity", "Design documents so one logical change is one document write."),
    ("Multi-document transactions", "Available, but costlier; frequent need suggests a relational model."),
    ("Read and write concerns", "writeConcern majority and readConcern majority trade latency for durability and consistency."),
    ("Document store vs Postgres", "Variable, nested, access-pattern-driven data favours documents; relationships and constraints favour Postgres.")])],
 [Q("A chat channel's messages grow forever. How should they be stored in a document database?", ["Separate collection, bucketed by channel and time", "One array inside the channel document", "One document per byte", "A single global document"], 0, "Unbounded arrays hit size limits and slow updates; bucket them."),
  Q("Which write is atomic in MongoDB without an explicit transaction?", ["Any write to a single document, including nested fields", "Writes across two collections", "A bulk insert of 1,000 documents", "Nothing is ever atomic"], 0, "Single-document operations are atomic, so model data that changes together into one document."),
  Q("Strong signal you should use a relational database instead?", ["Many ad-hoc joins and many-to-many relationships with strict constraints", "Each record has a different shape", "You read whole documents at once", "You need horizontal scaling"], 0, "Relational strengths are joins, relationships and constraints.")],
 [R("MongoDB: Data Modeling", "https://www.mongodb.com/docs/manual/data-modeling/", "docs", "intro", "MongoDB's data modeling guide: flexible schema design, embedding vs referencing, and designing schemas around application use cases."),
  R("MongoDB: Transactions", "https://www.mongodb.com/docs/manual/core/transactions/", "docs", "reference", "Explains that single-document operations are atomic, when multi-document transactions are needed, and their production considerations."),
  R("MongoDB Vector Search overview", "https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/", "docs", "intermediate", "How to create vector indexes in MongoDB and run semantic and hybrid search, keeping embeddings next to operational documents."),
  R("Discord: How Discord stores billions of messages", "https://discord.com/blog/how-discord-stores-billions-of-messages", "case", "intermediate", "Discord's account of starting on a single MongoDB replica set, hitting RAM and latency limits at 100 million messages, and moving to Cassandra with time buckets.")],
 dict(intuition="A document store is a filing cabinet of folders. Each folder holds everything about one thing, so you grab it in one motion. That is great when you always want the whole folder, and awkward when you constantly need to cross-reference pages between folders. A relational database is the opposite: neat index cards joined on demand.",
  how=["List the read and write access patterns and their frequencies.", "Embed data that is read together and bounded; reference data that is shared or unbounded.", "Add schema validation for fields code depends on.", "Create compound indexes for the main queries.", "Keep logical changes inside one document; use transactions sparingly."],
  example="Agent runs average 12 steps, at most 200, at about 1 KB per step, so a run document stays under 200 KB. Embedding the steps lets the trace viewer load a run in one read. Large tool outputs (PDF extracts of up to 5 MB) go to object storage, with a reference in the step. An index on {tenant_id: 1, started_at: -1} serves the 'recent runs' list. The design avoids the 16 MB document limit with plenty of headroom.",
  lang="python",
  code='''import json
# Model agent runs as documents: embed bounded steps, reference big artifacts, validate, and index access patterns.
MAX_STEPS, MAX_DOC_BYTES = 200, 16 * 1024 * 1024        # MongoDB's 16 MB document limit
SCHEMA = {"required": {"tenant_id": str, "run_id": str, "started_at": str, "steps": list}}
def validate(doc):
    for field, typ in SCHEMA["required"].items():
        if not isinstance(doc.get(field), typ): raise ValueError(f"{field} missing or not {typ.__name__}")
    if len(doc["steps"]) > MAX_STEPS: raise ValueError("too many steps: move to a bucketed collection")
    if len(json.dumps(doc).encode()) > MAX_DOC_BYTES: raise ValueError("document too large")
    return doc
def add_step(doc, tool, args, output):
    step = {"tool": tool, "args": args}
    if len(output) > 4096:                                # big artifact: reference, don't embed
        step["output_ref"] = f"s3://runs/{doc['run_id']}/{len(doc['steps'])}.txt"
    else:
        step["output"] = output
    doc["steps"].append(step); return validate(doc)
run = validate({"tenant_id": "t1", "run_id": "r-9", "started_at": "2026-10-14T10:00Z", "steps": []})
add_step(run, "search", {"q": "refund policy"}, "Refunds within 30 days.")
add_step(run, "read_pdf", {"id": "contract.pdf"}, "x" * 50_000)
print(json.dumps(run, indent=1))
# In MongoDB: db.runs.createIndex({tenant_id: 1, started_at: -1}); validator: {$jsonSchema: {...}}''',
  mistakes=["Embedding unbounded arrays such as all messages in a channel.", "Using a document store but needing joins everywhere.", "No schema validation, so every reader must handle every possible shape.", "Assuming multi-document writes are atomic without a transaction."],
  enterprise="A retailer's product catalog has 40 categories with different attributes. Modeling products as documents with category-specific fields, plus validation for the shared core (sku, price, status), replaces a 200-column sparse table and lets an agent fetch a complete product in one read.",
  takeaways=["Model for access patterns: embed together-read data, reference unbounded data.", "Single-document writes are atomic; design around that.", "Validate schemas in the database, even if they're flexible.", "Choose documents for nested, variable data and Postgres for relationships."],
  diagram='flowchart TD\n  A{"Read together and bounded?"} -->|"yes"| E["Embed in parent document"]\n  A -->|"no"| B{"Shared or unbounded?"}\n  B -->|"unbounded"| BK["Separate collection, bucketed by time"]\n  B -->|"shared"| RF["Reference by id"]\n  E --> V["$jsonSchema validation + compound index"]\n  BK --> V\n  RF --> V',
  diagramAlt="A decision flow for document modeling: embed data that is read together and bounded; otherwise put unbounded data in a separate time-bucketed collection or reference shared data by id. All paths end with schema validation and compound indexes."),
 case=C("Discord", "How Discord Stores Billions of Messages (Discord Engineering, 2017)", "https://discord.com/blog/how-discord-stores-billions-of-messages",
   "Discord's first version, built in under two months in early 2015, stored everything in a single MongoDB replica set, deliberately planned for easy migration. Around November 2015 it reached 100 million stored messages. The data and index no longer fit in RAM and latencies became unpredictable. Discord moved messages to Cassandra, bucketing each channel's messages by time (about 10 days per bucket) to keep partitions under about 100 MB.",
   "Start with what lets you iterate quickly, but plan the migration path. Model unbounded, growing data with buckets from the start.")))
# ---------------------------------------------------------------- b-auth
sid = "b-auth"
S.append(SUBJ(sid, "Authentication and Authorization: OAuth2, OIDC, SAML SSO, RBAC and ABAC",
 "Every enterprise deployment starts with 'it must use our SSO' and ends with 'the agent may only see what this user may see'. Identity is the first gate in every security review.",
 "Authentication answers who you are; authorization answers what you may do. In enterprises, authentication is delegated to an identity provider (Entra ID, Okta, Ping) via SAML 2.0 or OpenID Connect, so users sign in once. OAuth 2.0 issues scoped access tokens so an app or agent can call APIs on a user's behalf without seeing their password. Authorization models range from RBAC (roles grant permissions) to ABAC (policies over attributes of the user, resource and context) to relationship-based models (Zanzibar, OpenFGA).\n\nFor agents, the key rule is to act with the user's identity and the narrowest scopes, never with a shared superuser key.",
 "Add OIDC login (authorization code flow with PKCE) to a small web app, map IdP groups to roles, enforce an ABAC rule on documents, and show an agent tool call using a down-scoped, short-lived token.",
 [T(sid, "authn", "Authentication: SSO with SAML and OIDC",
   "Single sign-on lets employees use their corporate identity for your app. SAML 2.0 is XML-based and still dominant in enterprise SaaS: the identity provider (IdP) sends a signed assertion to your service provider (SP) after login. OpenID Connect is a JSON/JWT identity layer on top of OAuth 2.0 and is preferred for new apps and mobile. Either way, verify signatures, audience, issuer and expiry; reject unsigned or replayed assertions; and support IdP-initiated and SP-initiated flows as customers require. SCIM provisioning keeps user accounts and group memberships in sync, including deprovisioning when someone leaves.",
   [("SAML 2.0", "XML assertions signed by the IdP; validate signature, audience, recipient and NotOnOrAfter, and guard against XML signature wrapping."),
    ("OpenID Connect", "ID tokens (JWT) from an OAuth 2.0 authorization code flow with PKCE; verify iss, aud, exp and nonce."),
    ("SCIM provisioning", "The IdP creates, updates and deactivates users and groups in your app automatically."),
    ("MFA and session policy", "Leave MFA and conditional access to the IdP; keep app sessions short and revocable.")]),
  T(sid, "authz", "Authorization: OAuth scopes, RBAC, ABAC and agents",
   "OAuth 2.0 lets a client obtain an access token with specific scopes, for example read:tickets, from an authorization server. Tokens should be short-lived, audience-restricted and refreshable. RBAC maps users to roles and roles to permissions: simple and auditable, but it explodes when access depends on context. ABAC evaluates policies over attributes, such as 'region = EU and clearance ≥ confidential and request during working hours', which suits data-dependent rules. For agents, use delegated tokens (on-behalf-of or token exchange per RFC 8693) so every tool call carries the user's permissions, and enforce authorization at the API or retrieval layer, never in the prompt.",
   [("OAuth 2.0 scopes and tokens", "Short-lived, audience-bound access tokens with minimal scopes; refresh tokens stored securely."),
    ("RBAC", "Users get roles, roles get permissions; map IdP groups to roles and review them regularly."),
    ("ABAC", "Policies over user, resource and context attributes handle rules that roles can't express cleanly."),
    ("Delegated access for agents", "Agents call tools with the user's down-scoped token; authorization is enforced by the system, not by the prompt.")])],
 [Q("An enterprise says 'use our Okta SSO'. Which protocols do you typically implement?", ["SAML 2.0 and/or OpenID Connect", "FTP and SMTP", "Basic auth with shared passwords", "OAuth 1.0a only"], 0, "Enterprise SSO is almost always SAML or OIDC, often with SCIM for provisioning."),
  Q("Where must 'the agent can only see documents this user can see' be enforced?", ["In the retrieval and API layer, using the user's identity", "In the system prompt", "In the UI only", "By asking the model to be careful"], 0, "Prompts are not security boundaries; enforce authorization in code and data access."),
  Q("A rule depends on user region, document classification and time of day. Which model fits best?", ["ABAC", "Plain RBAC with one role per combination", "No authorization", "Shared API key"], 0, "Attribute-based policies express context-dependent rules without role explosion.")],
 [R("OAuth 2.0 (oauth.net)", "https://oauth.net/2/", "reference", "intro", "The community hub for OAuth 2.0: grant types, PKCE, token types and links to every relevant RFC and extension. Good orientation before reading specs."),
  R("OpenID Foundation: How OpenID Connect Works", "https://openid.net/developers/how-connect-works/", "docs", "intro", "Explains OIDC as an identity layer on OAuth 2.0 (RFC 6749/6750): ID tokens, the UserInfo endpoint and how authentication by an authorization server is verified."),
  R("OWASP SAML Security Cheat Sheet", "https://cheatsheetseries.owasp.org/cheatsheets/SAML_Security_Cheat_Sheet.html", "reference", "advanced", "Concrete SAML hardening: validate signatures and the protocol, defend against XML signature wrapping, and IdP and SP considerations for SSO."),
  R("RFC 9700: Best Current Practice for OAuth 2.0 Security", "https://datatracker.ietf.org/doc/html/rfc9700", "spec", "advanced", "The IETF's current OAuth security guidance: PKCE everywhere, no implicit grant, sender-constrained and audience-restricted tokens, and refresh token protection."),
  R("NIST: Attribute Based Access Control", "https://csrc.nist.gov/projects/attribute-based-access-control", "reference", "intermediate", "NIST's ABAC project page and guidance (SP 800-162), explaining ABAC's place among access control models and its policy and attribute components.")],
 dict(intuition="Authentication is showing your badge at the front door; the company's security desk (the IdP) issues the badge. Authorization is which rooms the badge opens. OAuth is a valet key: it lets an app or agent drive your car to one place without handing over your house keys. Agents should always carry the user's valet key, never a master key.",
  how=["Delegate login to the customer's IdP via SAML or OIDC; verify every assertion or token.", "Provision and deprovision users with SCIM.", "Map IdP groups to roles (RBAC); add ABAC policies where context matters.", "Issue short-lived, scoped, audience-bound tokens.", "Give agents delegated tokens and enforce authorization in APIs and retrieval."],
  example="An HR assistant serves 8,000 employees. Login uses OIDC with Entra ID, and the 'HR-Partners' group maps to the hr_partner role. An ABAC rule allows reading a salary record only if user.role = hr_partner and user.region = record.region. When an HR partner in the EU asks the agent about salaries, the search tool runs with her token, filters by region and returns only EU records. A US partner asking the same question gets zero EU rows, without relying on the prompt at all.",
  lang="python",
  code='''import base64, hashlib, hmac, json, time
# 1) Verify an HS256 JWT-style token (real OIDC uses RS256 + the IdP's JWKS; the checks are the same).
SECRET = b"demo-only-secret"
b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=")
def sign(claims):
    h, p = b64(json.dumps({"alg": "HS256"}).encode()), b64(json.dumps(claims).encode())
    return b".".join([h, p, b64(hmac.new(SECRET, h + b"." + p, hashlib.sha256).digest())]).decode()
def verify(token, aud, iss):
    h, p, s = token.encode().split(b".")
    if not hmac.compare_digest(b64(hmac.new(SECRET, h + b"." + p, hashlib.sha256).digest()), s): raise PermissionError("bad signature")
    c = json.loads(base64.urlsafe_b64decode(p + b"=" * (-len(p) % 4)))
    if c["aud"] != aud or c["iss"] != iss or c["exp"] < time.time(): raise PermissionError("bad aud/iss/exp")
    return c
# 2) RBAC from IdP groups + an ABAC rule, enforced in the tool, not the prompt.
ROLE_OF_GROUP = {"HR-Partners": "hr_partner", "Employees": "employee"}
RECORDS = [{"id": 1, "region": "EU", "salary": 81000}, {"id": 2, "region": "US", "salary": 95000}]
def search_salaries(token):
    u = verify(token, aud="hr-assistant", iss="https://idp.example.com")
    roles = {ROLE_OF_GROUP[g] for g in u["groups"] if g in ROLE_OF_GROUP}
    return [r for r in RECORDS if "hr_partner" in roles and r["region"] == u["region"]]
t_eu = sign({"sub": "ana", "groups": ["HR-Partners"], "region": "EU", "aud": "hr-assistant", "iss": "https://idp.example.com", "exp": time.time() + 300})
t_emp = sign({"sub": "bo", "groups": ["Employees"], "region": "US", "aud": "hr-assistant", "iss": "https://idp.example.com", "exp": time.time() + 300})
print("ana:", search_salaries(t_eu)); print("bo:", search_salaries(t_emp))''',
  mistakes=["Agents using a shared service account with admin rights.", "Putting access rules in the system prompt instead of in code.", "Skipping signature, audience or expiry checks on tokens or SAML assertions.", "No SCIM deprovisioning, so people who leave keep access."],
  enterprise="A legal-tech vendor wins a deal only after adding SAML SSO, SCIM deprovisioning and document-level ABAC. In the security review, the customer's CISO tests that a contractor account removed in Okta loses access within minutes and that the agent cannot retrieve matters outside the contractor's practice group.",
  takeaways=["Delegate authentication to the customer's IdP via SAML or OIDC.", "Verify signature, issuer, audience and expiry every time.", "RBAC for coarse access, ABAC or ReBAC for context and data-level rules.", "Agents act with the user's down-scoped token; enforce authorization outside the prompt."],
  diagram='sequenceDiagram\n  participant U as User\n  participant App as App / Agent\n  participant IdP as IdP (Okta / Entra)\n  participant API as Tool API\n  U->>App: Open app\n  App->>IdP: OIDC auth request (PKCE)\n  IdP-->>App: ID token + access token (scoped)\n  App->>API: Tool call with user token\n  API->>API: Verify token, RBAC + ABAC check\n  API-->>App: Only permitted data',
  diagramAlt="Sequence diagram: the user opens the app, the app redirects to the IdP with an OIDC request using PKCE, the IdP returns an ID token and a scoped access token, and the app or agent calls a tool API with the user's token. The API verifies the token and applies RBAC and ABAC checks, then returns only permitted data."),
 case=None))
# ---------------------------------------------------------------- b-async
sid = "b-async"
S.append(SUBJ(sid, "Caching, Queues and Background Jobs",
 "LLM calls are slow and expensive, and ingestion and agent runs take minutes. Caches and queues keep the product responsive and the bill predictable.",
 "Three patterns carry most AI back ends. Caching stores results you'll need again: exact-match response caches, embedding caches keyed by content hash, and provider prompt caching for long shared prefixes. Queues decouple producers from consumers so a spike of uploads or agent tasks doesn't overload workers or the model API. Background jobs run slow work (ingestion, long agent runs, report generation) outside the request, with status the user can poll or be notified about.\n\nThe hard parts are invalidation, retries without duplicates, dead-letter handling and visibility into backlog.",
 "Move document ingestion out of the upload request into a queue with workers. Cache embeddings by content hash, add retries with a dead-letter queue, and expose job status to the UI.",
 [T(sid, "cache", "Caching for AI workloads",
   "Cache at the layer where work is repeated. Embedding the same chunk twice is pure waste, so key embeddings by a hash of the text and model name. Exact-match response caches (key = hash of model, prompt and parameters) help for repeated queries such as FAQ bots. Provider prompt caching discounts long, stable prefixes such as system prompts and tool definitions. Every cache needs a TTL or an invalidation rule tied to the source data: when a policy document changes, cached answers built from it must expire. Redis is the usual store; measure hit rate, latency saved and cost saved.",
   [("Cache keys", "Include everything that changes the result: model, version, prompt, parameters and tenant."),
    ("Embedding cache by content hash", "Never re-embed identical text; key by sha256(text) plus the embedding model."),
    ("TTL and invalidation", "Expire on time and on source change; stale answers are a correctness bug."),
    ("Measuring value", "Track hit rate, p95 latency and dollars saved per cache.")]),
  T(sid, "queues", "Queues, workers and background jobs",
   "A queue (Redis, SQS, RabbitMQ, Kafka) holds work items; workers pull and process them at a controlled rate. This absorbs spikes, enforces concurrency limits towards rate-limited model APIs, and lets you scale workers independently. Delivery is usually at-least-once, so handlers must be idempotent. Failed messages are retried with backoff and, after N attempts, moved to a dead-letter queue for inspection. Long-running jobs need status records (queued, running, succeeded, failed) and progress reporting. Watch queue depth and age of the oldest message as primary health signals.",
   [("At-least-once delivery", "Expect duplicates; make handlers idempotent with keys or upserts."),
    ("Concurrency and rate control", "Size the worker pool to stay inside model API rate limits."),
    ("Retries and dead-letter queues", "Retry with backoff, then park poison messages in a DLQ with the error."),
    ("Job status and observability", "Persist job state, show progress, and alert on queue depth and oldest-message age.")])],
 [Q("Users upload 500-page PDFs and the upload request times out. Fix?", ["Enqueue ingestion as a background job and return a job ID", "Raise the HTTP timeout to 30 minutes", "Ask users to upload smaller files", "Embed synchronously but faster"], 0, "Slow work belongs in background workers with status polling or notifications."),
  Q("Your queue delivers at least once. What must handlers be?", ["Idempotent", "Single-threaded", "Written in Go", "Stateless and without logs"], 0, "Duplicates will happen; processing twice must not cause double effects."),
  Q("What should an embedding cache key include?", ["Hash of the text and the embedding model and version", "Only the document title", "The current time", "The user's IP address"], 0, "Same text with a different model gives different vectors.")],
 [R("Redis documentation: Develop with Redis", "https://redis.io/docs/latest/develop/", "docs", "reference", "Redis data types, commands, client libraries and patterns for caching, queues (lists, streams) and rate limiting, with an interactive command tutorial."),
  R("Celery: Introduction", "https://docs.celeryq.dev/en/stable/getting-started/introduction.html", "docs", "intro", "What a task queue is, how Celery distributes tasks to workers via a broker such as Redis or RabbitMQ, and its retry and scheduling features."),
  R("Amazon SQS: dead-letter queues", "https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html", "docs", "reference", "How SQS moves messages that repeatedly fail into a dead-letter queue (maxReceiveCount, retention, redrive) so they can be debugged without blocking the queue."),
  R("Anthropic prompt caching docs", "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching", "docs", "intermediate", "Cache stable prompt prefixes with cache_control to reduce cost and latency. Covers TTLs, minimum cacheable length and cache write vs read pricing."),
  R("Slack: Scaling Slack's Job Queue", "https://slack.engineering/scaling-slacks-job-queue/", "case", "advanced", "How Slack put Kafka in front of its Redis-based job queue after an outage, while handling over 1.4 billion jobs on peak days at up to 33,000 per second.")],
 dict(intuition="A cache is a sticky note with yesterday's answer: fast, but you must throw it away when the facts change. A queue is a ticket dispenser at a busy counter: customers take a number, workers serve them at a steady pace, and nobody gets turned away just because ten people arrived at once.",
  how=["Find repeated work (same embeddings, same prompts, same prefixes) and cache it with correct keys and TTLs.", "Move anything slower than a couple of seconds into background jobs.", "Put a queue between producers and workers and size workers to downstream rate limits.", "Make handlers idempotent; retry with backoff and dead-letter poison messages.", "Expose job status and monitor queue depth, age and DLQ size."],
  example="A knowledge base re-indexes nightly: 1.2M chunks, of which 96% are unchanged. Embedding everything costs 1.2M × 500 tokens = 600M tokens, about $12 at $0.02/M, and takes 3 hours. A content-hash cache embeds only the 48,000 changed chunks (24M tokens, about $0.48) in 8 minutes. Ingestion jobs run through a queue with 16 workers, capped at the embedding API's 3,000 requests per minute.",
  lang="python",
  code='''import hashlib, queue, threading, random
# Embedding cache by content hash + a worker pool with retries and a dead-letter queue.
CACHE, DLQ, calls = {}, [], {"n": 0}
lock = threading.Lock()
def embed_api(text):                       # stub for a paid, rate-limited API that sometimes fails
    with lock: calls["n"] += 1
    if random.random() < 0.1: raise TimeoutError("transient")
    return [len(text) % 7, len(text) % 11]
def embed_cached(text, model="emb-v3"):
    key = hashlib.sha256(f"{model}|{text}".encode()).hexdigest()
    with lock:
        if key in CACHE: return CACHE[key]
    vec = embed_api(text)
    with lock: CACHE[key] = vec
    return vec
jobs = queue.Queue()
def worker():
    while True:
        item = jobs.get()
        if item is None: break
        text, attempt = item
        try: embed_cached(text)
        except TimeoutError as e:
            if attempt < 3: jobs.put((text, attempt + 1))    # retry (a real system adds backoff)
            else: DLQ.append((text, str(e)))
        finally: jobs.task_done()
random.seed(1)
chunks = [f"chunk {i % 300}" for i in range(1000)]          # lots of repeats
for c in chunks: jobs.put((c, 0))
ts = [threading.Thread(target=worker) for _ in range(8)]
for t in ts: t.start()
jobs.join()
for _ in ts: jobs.put(None)
for t in ts: t.join()
print(f"{len(chunks)} chunks, {len(CACHE)} unique embedded, {calls['n']} API calls, DLQ={len(DLQ)}")''',
  mistakes=["Cache keys that omit the model version or tenant.", "No invalidation, so answers outlive the policy that produced them.", "Non-idempotent handlers on an at-least-once queue.", "Infinite retries with no dead-letter queue, which blocks the queue."],
  enterprise="An insurer's claims assistant generates a summary for every new claim document. Running the summaries as queued background jobs, capped at the provider's rate limit, keeps the claims UI responsive at month-end peaks. A dead-letter queue surfaces the 0.3% of documents that fail OCR for manual handling instead of silently dropping them.",
  takeaways=["Cache repeated work with complete keys and real invalidation.", "Slow work goes to background jobs with visible status.", "Queues absorb spikes and enforce rate limits.", "At-least-once delivery requires idempotent handlers and a DLQ."],
  diagram='flowchart LR\n  UP["Upload API"] -->|"enqueue job id"| Q[["Queue"]]\n  Q --> W1["Worker"]\n  Q --> W2["Worker"]\n  W1 --> C{"Embedding cache hit?"}\n  W2 --> C\n  C -->|"no"| EMB["Embedding API (rate-limited)"]\n  C -->|"yes"| IDX[("Index")]\n  EMB --> IDX\n  W1 -->|"after N failures"| DLQ[["Dead-letter queue"]]\n  UP -->|"job status"| UI["UI polls / webhook"]',
  diagramAlt="The upload API enqueues a job and returns its ID. Workers pull from the queue, check an embedding cache, call the rate-limited embedding API only on a miss, write to the index, and move repeatedly failing messages to a dead-letter queue. The UI polls job status."),
 case=C("Slack", "Scaling Slack's Job Queue (Slack Engineering, 2017)", "https://slack.engineering/scaling-slacks-job-queue/",
   "Slack's job queue handles business logic too slow for a web request: every message post, push notification, URL unfurl, reminder and billing calculation. On its busiest days it processes over 1.4 billion jobs, at a peak of 33,000 per second. After database contention slowed job execution and Redis reached its memory limit, causing a significant outage, Slack put Kafka in front of Redis as a durable buffer.",
   "Queues need a durable buffer and back-pressure. When consumers slow down, the queue's own storage must not become the next failure point.")))
