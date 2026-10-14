from helpers10 import R, Q, T, SUBJ, C
S = []
# ---------------------------------------------------------------- b-webhooks
sid = "b-webhooks"
S.append(SUBJ(sid, "Webhooks and Event-Driven Integration",
 "Agents need to react when something happens in a customer's systems (a ticket is created, a payment fails, a document changes). Webhooks and events are how SaaS tells you.",
 "Polling an API every minute is slow and wasteful. With webhooks, the source system sends an HTTP POST to your endpoint when an event occurs. Event-driven integration generalizes this: events flow through a bus or queue (Kafka, EventBridge, Pub/Sub) to any number of consumers, such as an indexing job, an agent and an audit log.\n\nWebhooks look simple and fail in predictable ways. Signatures go unverified, retries create duplicates, events arrive out of order, slow handlers time out, and missed events are never replayed. A production receiver verifies, acknowledges fast, queues the work, dedupes by event ID and reconciles periodically.",
 "Build a webhook receiver for a ticketing system: verify HMAC signatures with a timestamp, return 2xx within a second, enqueue events, dedupe by event ID, trigger an agent triage job, and reconcile missed events nightly via the source API.",
 [T(sid, "recv", "Receiving webhooks safely",
   "Treat the webhook endpoint as public and hostile. Verify the signature: most providers sign the raw request body with HMAC-SHA256 using a shared secret, and include a timestamp to stop replays. Compare signatures in constant time and reject old timestamps. Respond 2xx quickly, typically within a few seconds, because providers retry on timeouts and errors, which multiplies load. Do the real work asynchronously from a queue. Store the event ID and skip duplicates, since delivery is at-least-once. Subscribe only to the events you need, and use HTTPS.",
   [("Signature verification", "Recompute the HMAC over the raw body and compare in constant time; reject unsigned requests."),
    ("Timestamps and replay protection", "Include the timestamp in the signed content and reject deliveries older than a few minutes."),
    ("Acknowledge fast, process later", "Return 2xx immediately and push the event to a queue for workers."),
    ("Idempotency by event ID", "Store processed event IDs; providers retry, so duplicates are normal.")]),
  T(sid, "eda", "Event-driven architecture",
   "Events are facts about the past ('ticket.created', 'invoice.paid'). Publishing them to a bus lets new consumers subscribe without changing the producer, which is how you add an agent to an existing workflow without touching the core system. Use a consistent envelope (CloudEvents: id, source, type, time, data) and version event schemas. Expect out-of-order delivery: include sequence numbers or timestamps and fetch the current state from the source API when order matters. Because events can be missed, run periodic reconciliation jobs that compare your state with the source of truth.",
   [("Events vs commands", "Events state what happened; commands ask for something to happen. Consumers decide how to react to events."),
    ("CloudEvents envelope", "A standard event format (id, source, type, time, data) makes routing and tooling reusable."),
    ("Ordering and 'thin' events", "When order matters, treat the event as a hint and re-read current state from the API."),
    ("Reconciliation", "Scheduled jobs compare local state with the source system to repair missed or failed events.")])],
 [Q("A webhook handler calls an LLM synchronously and takes 25 s. The provider times out at 10 s. What happens?", ["The provider retries, multiplying load and duplicate work", "Nothing; providers wait forever", "The LLM call speeds up", "The event is guaranteed to process exactly once"], 0, "Acknowledge fast and process asynchronously."),
  Q("How do you check a webhook really came from the provider?", ["Verify the HMAC signature over the raw body, with a timestamp", "Check the User-Agent header", "Trust the source IP alone", "Look for a 'from' field in the JSON"], 0, "Signatures with timestamps defend against forgery and replay."),
  Q("Why run a nightly reconciliation job if you have webhooks?", ["Webhooks can be missed or fail; reconciliation repairs drift", "Webhooks only work at night", "Providers require it legally", "To delete old events"], 0, "Delivery isn't guaranteed; compare with the source of truth.")],
 [R("Stripe: Receive Stripe events in your webhook endpoint", "https://docs.stripe.com/webhooks", "docs", "intermediate", "Stripe's guide to webhook endpoints: verifying signatures, handling duplicate events, responding quickly with 2xx, retries and best practices."),
  R("GitHub Docs: Best practices for using webhooks", "https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks", "docs", "intro", "Subscribe to the minimum events, use a webhook secret, respond within 10 seconds, process asynchronously, and use the delivery ID to avoid duplicates."),
  R("GitHub Docs: Validating webhook deliveries", "https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries", "docs", "reference", "How to verify X-Hub-Signature-256 HMAC signatures in several languages, using constant-time comparison."),
  R("Standard Webhooks", "https://www.standardwebhooks.com/", "spec", "intermediate", "An open specification and libraries for sending and verifying webhooks consistently (signature headers, timestamps, IDs), created because every provider does it differently."),
  R("CloudEvents", "https://cloudevents.io/", "spec", "reference", "The CNCF specification for describing event data in a common way, so producers, routers and consumers can share tooling across sources.")],
 dict(intuition="Polling is calling the restaurant every five minutes to ask if your table is ready. A webhook is the restaurant texting you. But anyone can send you a text, the restaurant may text twice, and sometimes the text never arrives. So check it's really them, ignore duplicates, and look at the board now and then.",
  how=["Register an HTTPS endpoint and subscribe only to the needed events.", "Verify signature and timestamp on the raw body.", "Respond 2xx immediately and enqueue the event.", "Process from the queue idempotently, keyed by event ID.", "Reconcile with the source API on a schedule; alert on signature failures and backlog."],
  example="A ServiceNow instance fires incident.created about 2,000 times a day. The receiver verifies the HMAC, stores the event ID and enqueues it in about 40 ms. A triage agent reads the incident through the API with a scoped token, proposes a category and assignee, and writes back a work note. Over a week, 1.6% of deliveries are retries and are skipped as duplicates. The nightly reconciliation finds 3 incidents whose webhooks never arrived and triages them.",
  lang="python",
  code='''import hashlib, hmac, json, time
# A webhook receiver core: verify HMAC + timestamp, dedupe by event id, enqueue, and acknowledge fast.
SECRET = b"whsec_demo"
SEEN, QUEUE = set(), []
def sign(body: bytes, ts: int) -> str:
    return hmac.new(SECRET, f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
def receive(headers: dict, body: bytes, now=None, tolerance_s=300):
    now = now or int(time.time())
    ts, sig = int(headers.get("X-Timestamp", 0)), headers.get("X-Signature", "")
    if abs(now - ts) > tolerance_s: return 400, "stale timestamp"
    if not hmac.compare_digest(sign(body, ts), sig): return 401, "bad signature"
    event = json.loads(body)
    if event["id"] in SEEN: return 200, "duplicate ignored"
    SEEN.add(event["id"]); QUEUE.append(event)          # real system: durable queue, then workers
    return 200, "queued"
body = json.dumps({"id": "evt_1", "type": "incident.created", "data": {"number": "INC0012"}}).encode()
ts = int(time.time())
good = {"X-Timestamp": str(ts), "X-Signature": sign(body, ts)}
print(receive(good, body))                              # (200, 'queued')
print(receive(good, body))                              # provider retry -> (200, 'duplicate ignored')
print(receive({"X-Timestamp": str(ts), "X-Signature": "forged"}, body))
print(receive(good, body, now=ts + 3600))              # replay an hour later -> rejected
print("queued events:", [e["id"] for e in QUEUE])''',
  mistakes=["Skipping signature verification, or verifying a re-serialized body instead of the raw bytes.", "Doing slow work (LLM calls) before responding.", "Assuming exactly-once, in-order delivery.", "No reconciliation, so missed events are lost forever."],
  enterprise="A field-service company adds an AI dispatcher to its existing work-order system without changing it: the system already publishes work_order.created to EventBridge. The dispatcher subscribes, drafts a technician assignment and posts it back through the API for human approval. Rolling back is as simple as removing the subscription.",
  takeaways=["Verify signatures and timestamps on the raw body.", "Acknowledge fast; do real work from a queue.", "Dedupe by event ID; expect retries and disorder.", "Reconcile against the source of truth on a schedule."],
  diagram='flowchart LR\n  SRC["SaaS (ServiceNow / Stripe / GitHub)"] -->|"POST event + HMAC"| RX["Webhook receiver"]\n  RX -->|"verify, dedupe, 2xx in < 1 s"| BUS[["Queue / event bus"]]\n  BUS --> AG["Triage agent"]\n  BUS --> IX["Indexer"]\n  BUS --> AU["Audit log"]\n  AG -->|"read state + write back (scoped token)"| SRC\n  REC["Nightly reconciliation"] -->|"compare via API"| SRC',
  diagramAlt="A SaaS system posts a signed event to a webhook receiver, which verifies, dedupes and acknowledges within a second, then publishes to a queue or event bus. A triage agent, an indexer and an audit log consume events; the agent reads state and writes back with a scoped token, and a nightly reconciliation job compares state with the source API."),
 case=None))
# ---------------------------------------------------------------- b-apidesign
sid = "b-apidesign"
S.append(SUBJ(sid, "API Design and Versioning",
 "The APIs you build for customers, agents and MCP servers outlive any model. Good design and careful versioning let you change internals without breaking integrations.",
 "A well-designed API is predictable: consistent resource names, standard methods, clear errors, pagination, filtering and documented limits. Contract-first design (write the OpenAPI document, review it, then implement) catches problems while they're cheap to fix.\n\nVersioning is the promise you make about change. Additive changes (new optional fields, new endpoints) are safe. Removing or renaming fields, changing types or changing semantics are breaking. Strategies include URL versions (/v1), header or date-based versions with per-account pinning (Stripe), and deprecation windows with clear communication. Agents raise the stakes because their tool definitions are generated from your schema.",
 "Write an OpenAPI 3 spec for a 'tickets' API with cursor pagination, filtering, RFC 9457 error responses and an Idempotency-Key header. Then add a breaking change behind a dated version and a compatibility layer.",
 [T(sid, "design", "Designing predictable APIs",
   "Follow a style guide (Google's AIP-based API design guide or the Microsoft REST API guidelines) so every endpoint feels the same. Use nouns for resources and standard methods for actions, with plural collections, stable IDs and consistent casing. Paginate every list with cursors rather than offsets for large or changing data, and cap page sizes. Return machine-readable errors, such as RFC 9457 problem details with type, title, status and detail, so clients and agents can react. Document rate limits and auth in the OpenAPI spec, and generate SDKs and tool definitions from it.",
   [("Resource-oriented naming", "Collections and resources (/tickets, /tickets/{id}) with standard methods; custom actions only when needed."),
    ("Cursor pagination and filters", "Opaque cursors are stable under inserts; cap page size and support filters agents can use."),
    ("Problem details errors", "RFC 9457 JSON errors with a type URI and a human-readable detail."),
    ("Contract-first with OpenAPI", "Review the spec before coding; generate docs, clients, mocks and tests from it.")]),
  T(sid, "version", "Versioning and evolution",
   "Decide what counts as breaking and write it down. Usually, adding optional request fields, response fields or endpoints is fine; removing, renaming or retyping anything is breaking, and so is changing defaults or semantics. Clients must ignore unknown fields. To ship breaking changes, use a new version: a URL major version for rare big redesigns, or dated versions where each account is pinned to the version it started with and upgrades explicitly, with the server translating between versions. Announce deprecations with dates, send Deprecation and Sunset headers, and measure who still calls old versions.",
   [("Breaking vs additive changes", "Additions are safe if clients ignore unknown fields; removals, renames and type changes are breaking."),
    ("URL major versions", "/v1 to /v2 for rare, large redesigns; expensive for everyone to migrate."),
    ("Dated versions with pinning", "Pin each account to a version, translate responses for old versions, and let customers upgrade deliberately."),
    ("Deprecation process", "Publish timelines, send Deprecation and Sunset headers, track usage, and contact remaining callers.")])],
 [Q("Which change is breaking for existing clients?", ["Renaming the field `status` to `state`", "Adding a new optional response field", "Adding a new endpoint", "Adding an optional query parameter"], 0, "Renames and removals break clients that read the old field."),
  Q("Why prefer cursor pagination over offset pagination for a busy ticket list?", ["Cursors stay stable when new rows are inserted", "Offsets are not allowed in HTTP", "Cursors return more rows", "Offsets require GraphQL"], 0, "Offsets skip or duplicate rows as data changes underneath."),
  Q("How does Stripe keep old integrations working while the API evolves?", ["Accounts are pinned to the version current at their first request", "It never changes the API", "It forces everyone to /v2 each year", "It breaks clients and sends emails"], 0, "Per-account version pinning plus server-side translation.")],
 [R("Google Cloud API Design Guide", "https://cloud.google.com/apis/design", "guide", "intermediate", "Google's guidelines for consistent APIs, aligned with the AIPs: resource-oriented design, standard methods, naming, errors, versioning and compatibility."),
  R("Microsoft REST API Guidelines", "https://github.com/microsoft/api-guidelines", "guide", "intermediate", "Microsoft's public REST API guidelines (with Azure- and Graph-specific variants) on URLs, errors, pagination, long-running operations and versioning."),
  R("OpenAPI Specification", "https://spec.openapis.org/oas/latest.html", "spec", "reference", "The OpenAPI Specification (v3.2.x) for describing HTTP APIs in a language-agnostic way. The source for docs, SDKs, mocks and agent tool definitions."),
  R("RFC 9457: Problem Details for HTTP APIs", "https://www.rfc-editor.org/rfc/rfc9457", "spec", "reference", "Defines the application/problem+json format (type, title, status, detail, instance) for machine-readable HTTP API errors, replacing RFC 7807."),
  R("Stripe: APIs as infrastructure, future-proofing Stripe with versioning", "https://stripe.com/blog/api-versioning", "case", "advanced", "How Stripe has kept compatibility with every API version since 2011: per-account version pinning, version change modules and incremental upgrades.")],
 dict(intuition="An API is a promise to strangers. Good design makes the promise easy to understand (same patterns everywhere, clear errors). Versioning makes it possible to keep the promise while you keep changing the building behind the front desk: old visitors still get the counter they know, and new visitors get the new one.",
  how=["Pick a style guide and write the OpenAPI contract first.", "Use resources, standard methods, cursor pagination, filters and problem-details errors.", "Classify every change as additive or breaking before merging.", "Ship breaking changes behind a new version, with translation for pinned clients.", "Deprecate with dates and headers, and track remaining usage."],
  example="Your tickets API returns priority as a string ('high'). A new model needs a numeric priority from 1 to 5. Changing the type in place would break 140 integrations and every agent tool generated from v2025-06-01. Instead, release version 2026-10-01 with priority_level as an integer. Accounts pinned to the old version keep receiving strings, translated server-side. Usage metrics show 92% of traffic upgraded within 4 months.",
  lang="python",
  code='''import json
# Dated API versions with per-account pinning and server-side translation (Stripe-style), plus problem-details errors.
VERSIONS = ["2025-06-01", "2026-10-01"]
ACCOUNT_VERSION = {"acct_old": "2025-06-01", "acct_new": "2026-10-01"}
PRIORITY_TO_LEVEL = {"low": 1, "normal": 3, "high": 5}
def internal_ticket(tid):            # latest internal representation
    return {"id": tid, "title": "VPN down", "priority_level": 5}
DOWNGRADES = {                       # one function per version change, applied newest -> oldest
    "2026-10-01": lambda t: {**{k: v for k, v in t.items() if k != "priority_level"},
                             "priority": {v: k for k, v in PRIORITY_TO_LEVEL.items()}[t["priority_level"]]},
}
def render(ticket, version):
    for v in reversed(VERSIONS):
        if v <= version: break
        ticket = DOWNGRADES[v](ticket)
    return ticket
def get_ticket(account, tid, header_version=None):
    version = header_version or ACCOUNT_VERSION.get(account, VERSIONS[-1])
    if version not in VERSIONS:
        return 400, {"type": "https://api.example.com/problems/unknown-version", "title": "Unknown API version",
                     "status": 400, "detail": f"Use one of {VERSIONS}"}
    return 200, render(internal_ticket(tid), version)
print(get_ticket("acct_old", "T-1"))      # pinned: gets 'priority': 'high'
print(get_ticket("acct_new", "T-1"))      # latest: gets 'priority_level': 5
print(json.dumps(get_ticket("acct_old", "T-1", "2024-01-01")[1]))''',
  mistakes=["Changing field types or names in place.", "Offset pagination on large, changing collections.", "Free-text error messages that clients must parse.", "No deprecation telemetry, so you never know who would break."],
  enterprise="A logistics platform publishes its shipment API through an MCP server for customer agents. Because tool schemas are generated from OpenAPI, a renamed field once broke every customer's agent overnight. The team now runs a schema-diff check in CI that blocks breaking changes unless they come with a new dated version.",
  takeaways=["Contract-first with OpenAPI; follow one style guide.", "Cursor pagination, filters and RFC 9457 errors make APIs agent-friendly.", "Additive changes are safe; breaking changes need a version.", "Pin and translate versions; deprecate with dates and telemetry."],
  diagram='flowchart LR\n  REQ["Request (account, optional version header)"] --> PIN{"Version?"}\n  PIN -->|"pinned 2025-06-01"| INT["Internal latest model"]\n  PIN -->|"2026-10-01"| INT\n  INT --> TR["Apply version-change transforms back to requested version"]\n  TR --> RES["Response in the client\'s version"]\n  PIN -->|"unknown"| ERR["400 problem+json"]',
  diagramAlt="A request carries an account and an optional version header. The server resolves the pinned or requested version, builds the latest internal model, applies version-change transforms back to the requested version, and returns the response, or a 400 problem-details error for an unknown version."),
 case=C("Stripe", "APIs as infrastructure: future-proofing Stripe with versioning (Stripe blog)", "https://stripe.com/blog/api-versioning",
   "Stripe says it has maintained compatibility with every version of its API since the company started in 2011. The first time a user makes an API request, their account is automatically pinned to the most recent version, and every later call uses that version implicitly unless they upgrade. This guarantees users don't accidentally receive breaking changes, while Stripe avoids painful major URL versions.",
   "Treat API compatibility as infrastructure. Pinning, server-side translation and incremental upgrades let you evolve quickly without breaking integrations.")))
# ---------------------------------------------------------------- b-resilience
sid = "b-resilience"
S.append(SUBJ(sid, "Rate Limiting, Retries, Timeouts and Idempotency",
 "Model APIs throttle, networks drop and agents retry. Without timeouts, backoff and idempotency, a small blip becomes a retry storm or a double charge.",
 "Four tools make distributed calls safe. Timeouts bound how long you wait, so one slow dependency can't exhaust your threads. Retries with exponential backoff and jitter recover from transient failures without synchronized stampedes, and should only be used for retryable errors (429, 503, timeouts). Idempotency keys make it safe to repeat a non-idempotent operation such as 'create refund', because the server returns the original result for a repeated key. Rate limiters (token bucket, sliding window) protect your service and keep you inside provider quotas; load shedding reserves capacity for critical traffic.\n\nCircuit breakers stop calling a failing dependency for a while.",
 "Wrap an LLM and a payments call in a client with per-call timeouts, a deadline budget, retries with full jitter limited to retryable errors, idempotency keys and a circuit breaker. Then put a token-bucket limiter in front of your own API and load-test it.",
 [T(sid, "client", "Client side: timeouts, retries, backoff and breakers",
   "Every network call needs a timeout, and a request as a whole needs a deadline budget shared by all its calls. Retry only errors that may succeed later (timeouts, 429, 502–504), never validation errors. Use exponential backoff with jitter. Full jitter, a random sleep between 0 and base × 2^attempt, spreads retries out so clients don't stampede together. Cap attempts and respect Retry-After headers. Retries multiply load at every layer, so retry at one layer only. A circuit breaker opens after repeated failures, fails fast for a cool-down period, and then half-opens to probe recovery.",
   [("Timeouts and deadlines", "Per-call timeouts plus an overall deadline propagated to downstream calls."),
    ("Retry only retryable errors", "429, 503 and timeouts are retryable; 400 and 401 are not. Honour Retry-After."),
    ("Exponential backoff with jitter", "Randomized, growing delays prevent synchronized retry storms."),
    ("Circuit breakers", "Fail fast while a dependency is down; probe with half-open requests before resuming.")]),
  T(sid, "server", "Server side: idempotency, rate limits and load shedding",
   "If a client retries POST /refunds after a timeout, did the first refund happen? Idempotency keys answer that. The client sends a unique Idempotency-Key, and the server stores the key with the result, so a repeat returns the saved response instead of acting twice. Agents need this badly, because they retry and sometimes repeat tool calls. Rate limiting protects your service: token buckets allow short bursts while enforcing an average rate, per user, tenant or API key. Load shedders go further by dropping low-priority traffic when the system is saturated, so critical requests such as payments keep working.",
   [("Idempotency keys", "Store key → result for a retention window; repeated keys replay the stored response."),
    ("Token bucket rate limiting", "Tokens refill at rate r up to capacity b, allowing bursts up to b and an average of r."),
    ("Per-tenant and per-model quotas", "Limit by API key, tenant and model to keep one customer or agent from starving others."),
    ("Load shedding and prioritization", "Reserve capacity for critical endpoints and shed non-critical traffic under stress.")])],
 [Q("A refund POST timed out. The client retries. What prevents a double refund?", ["An Idempotency-Key the server remembers with the result", "A longer timeout", "Retrying faster", "Switching to GET"], 0, "The server returns the original result for a repeated key."),
  Q("Why add jitter to exponential backoff?", ["To stop many clients retrying at the same moment", "To make retries faster", "To satisfy HTTP/2", "To avoid needing timeouts"], 0, "Synchronized retries create thundering herds; randomness spreads them."),
  Q("Which error should NOT be retried automatically?", ["400 Bad Request (validation error)", "503 Service Unavailable", "429 Too Many Requests", "A connection timeout"], 0, "The same invalid request will fail again; fix it instead.")],
 [R("AWS Builders' Library: Timeouts, retries, and backoff with jitter", "https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/", "article", "intermediate", "Marc Brooker on how Amazon sets timeouts, why retries are 'selfish', retrying at a single layer, and using backoff with jitter to avoid overload."),
  R("AWS Architecture Blog: Exponential Backoff and Jitter", "https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/", "article", "intermediate", "Simulations comparing no jitter, full jitter, equal jitter and decorrelated jitter, showing why randomized backoff cuts total work and completion time."),
  R("Stripe: Designing robust and predictable APIs with idempotency", "https://stripe.com/blog/idempotency", "case", "intermediate", "Why ambiguous failures make retries dangerous, how Stripe's Idempotency-Key header makes POSTs safe to retry, and exponential backoff on the client."),
  R("Stripe: Scaling your API with rate limiters", "https://stripe.com/blog/rate-limiters", "article", "advanced", "Stripe's four limiter types (request rate, concurrent requests, fleet usage and worker utilization load shedders), token buckets in Redis, and reserving capacity for critical requests."),
  R("Martin Fowler: Circuit Breaker", "https://martinfowler.com/bliki/CircuitBreaker.html", "article", "intro", "The circuit breaker pattern explained with state transitions (closed, open, half-open) and why remote calls that hang need it.")],
 dict(intuition="Calling another service is like phoning a busy office. Hang up if nobody answers in time (timeout). Call back later, and not all at once with everyone else (backoff with jitter). Quote your reference number so they don't process your order twice (idempotency key). If the office is clearly closed, stop calling for a while (circuit breaker). And if you run the office, hand out numbered tickets so the queue stays manageable (rate limiting).",
  how=["Set per-call timeouts and an end-to-end deadline.", "Classify errors as retryable or not; retry with capped exponential backoff, full jitter and Retry-After.", "Send idempotency keys on every mutating call, including agent tool calls.", "Add a circuit breaker per dependency.", "Rate-limit and shed load on your own API by tenant and priority."],
  example="An agent platform makes 50,000 LLM calls an hour against a 1,000-requests-per-minute quota. At peak, a burst of 2,000 requests triggers 429s. Without jitter, all clients retry exactly 1 s later and trip the limit again three times in a row. With full jitter over a doubling window and a client-side token bucket at 950 per minute, retries spread out, the 429 rate drops from 18% to under 1%, and p95 latency falls.",
  lang="python",
  code='''import random, time
# Retries with full jitter (retryable errors only) + idempotency keys + a token-bucket limiter + a tiny circuit breaker.
class Retryable(Exception): pass
class Fatal(Exception): pass
def call_with_retries(fn, *, attempts=5, base=0.02, cap=0.5, deadline_s=2.0, rng=random.Random(7)):
    start = time.monotonic()
    for i in range(attempts):
        try: return fn()
        except Fatal: raise                                    # never retry e.g. 400s
        except Retryable:
            sleep = rng.uniform(0, min(cap, base * 2 ** i))   # full jitter
            if i == attempts - 1 or time.monotonic() - start + sleep > deadline_s: raise
            time.sleep(sleep)
class TokenBucket:
    def __init__(self, rate, capacity): self.rate, self.cap, self.tokens, self.t = rate, capacity, capacity, time.monotonic()
    def allow(self):
        now = time.monotonic(); self.tokens = min(self.cap, self.tokens + (now - self.t) * self.rate); self.t = now
        if self.tokens >= 1: self.tokens -= 1; return True
        return False
class Breaker:
    def __init__(self, threshold=3, cooldown=0.2): self.fail, self.th, self.cd, self.opened = 0, threshold, cooldown, None
    def __call__(self, fn):
        if self.opened and time.monotonic() - self.opened < self.cd: raise Retryable("circuit open")
        try: r = fn(); self.fail, self.opened = 0, None; return r
        except Retryable: self.fail += 1; self.opened = time.monotonic() if self.fail >= self.th else None; raise
IDEMP = {}
def create_refund(key, amount):                                # server side
    if key in IDEMP: return IDEMP[key]
    IDEMP[key] = {"refund_id": f"re_{len(IDEMP) + 1}", "amount": amount}; return IDEMP[key]
flaky = iter([Retryable("503"), Retryable("timeout"), None])
def attempt():
    e = next(flaky)
    if e: raise e
    return create_refund("idem-123", 20)
print(call_with_retries(attempt)); print(create_refund("idem-123", 20))   # same refund, not a second one
tb = TokenBucket(rate=5, capacity=10); print("burst allowed:", sum(tb.allow() for _ in range(25)), "of 25")
br = Breaker()
def down(): raise Retryable("503")
for _ in range(4):
    try: br(down)
    except Retryable as e: last = str(e)
print("breaker:", last)''',
  mistakes=["No timeouts, so one hung dependency exhausts every worker.", "Retrying non-retryable errors, or retrying at every layer.", "Fixed retry delays without jitter, which cause synchronized stampedes.", "Mutating tool calls without idempotency keys, which leads to double actions when agents retry."],
  enterprise="A payments-adjacent agent issues refunds through a tool. After an incident where a model API timeout caused the agent to retry and issue two refunds, the team adds idempotency keys derived from (conversation_id, tool_call_id) and a per-tenant token bucket. Duplicate refunds drop to zero, and a noisy tenant can no longer starve the others.",
  takeaways=["Every call gets a timeout; every request gets a deadline.", "Retry only retryable errors, with capped exponential backoff and jitter.", "Idempotency keys make retries of mutations safe, which agents need.", "Rate-limit, shed load and use circuit breakers to contain failure."],
  diagram='flowchart LR\n  A["Agent / client"] -->|"timeout + deadline"| CB{"Circuit breaker"}\n  CB -->|"closed"| RL["Token bucket (client quota)"]\n  RL --> API["Service / model API"]\n  API -->|"429 / 503"| BO["Backoff with full jitter"]\n  BO --> CB\n  API -->|"POST + Idempotency-Key"| ST[("Key → result store")]\n  CB -->|"open: fail fast"| FB["Fallback / error"]',
  diagramAlt="An agent calls a service with a timeout and deadline through a circuit breaker and a client-side token bucket. 429 and 503 responses trigger backoff with full jitter before retrying. Mutating POSTs carry an idempotency key stored with the result, and an open breaker fails fast to a fallback."),
 case=C("Stripe", "Designing robust and predictable APIs with idempotency (Stripe blog)", "https://stripe.com/blog/idempotency",
   "Stripe explains that after a network failure the client often can't tell whether an operation such as a charge succeeded, so a blind retry is dangerous. Stripe lets clients send a unique value in an Idempotency-Key header on mutating (POST) requests, which guarantees the operation's side effects happen only once however many times it's retried. It also recommends clients retry with exponential backoff.",
   "Ambiguous failures are normal in distributed systems. Make mutations idempotent so the safe client behaviour, retrying, is also the simple one.")))
