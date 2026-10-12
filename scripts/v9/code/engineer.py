CODE = {}
CODE["e-prompt"] = ("python", '''# Assemble context with an explicit token budget: instructions > schema > examples > history.
def ntok(s): return len(s) // 4 + 1          # rough estimate; use the model's tokenizer in production
def build_prompt(parts, budget):
    out, used = [], 0
    for name, text, required in parts:          # parts are in priority order
        t = ntok(text)
        if used + t > budget:
            if required: raise ValueError(f"required part '{name}' does not fit")
            continue
        out.append(f"## {name}\\n{text}"); used += t
    return "\\n\\n".join(out), used
parts = [("Instructions", "Answer using only the schema columns.", True),
         ("Schema", "columns: service.name, duration_ms, http.status_code", True),
         ("Examples", "Q: slow requests -> HEATMAP(duration_ms)" * 20, False),
         ("History", "previous query: COUNT WHERE status>=500", False)]
prompt, used = build_prompt(parts, budget=120)
print(used, "tokens\\n", prompt)
''')
CODE["e-tok"] = ("python", '''from collections import Counter
# Byte-pair encoding: repeatedly merge the most frequent adjacent pair.
words = Counter({"l o w": 5, "l o w e r": 2, "n e w e s t": 6, "w i d e s t": 3})
def merge_once(words):
    pairs = Counter()
    for w, f in words.items():
        s = w.split()
        for a, b in zip(s, s[1:]): pairs[a, b] += f
    (a, b), _ = pairs.most_common(1)[0]
    new = Counter({w.replace(f"{a} {b}", a + b): f for w, f in words.items()})
    return (a, b), new
for _ in range(4):
    pair, words = merge_once(words)
    print("merge", pair, "->", list(words))
''')
CODE["e-tools"] = ("python", '''import json
# Validate a model's tool call against a JSON-schema-like spec before executing it.
TOOLS = {"get_order": {"required": {"order_id": str}, "optional": {"include_items": bool}}}
def validate(call):
    spec = TOOLS.get(call.get("name"))
    if not spec: return f"unknown tool {call.get('name')!r}"
    args = call.get("arguments", {})
    for k, t in spec["required"].items():
        if not isinstance(args.get(k), t): return f"missing/invalid {k}"
    extra = set(args) - set(spec["required"]) - set(spec["optional"])
    return f"unexpected args {sorted(extra)}" if extra else None
raw = '{"name": "get_order", "arguments": {"order_id": "A-17", "verbose": true}}'
err = validate(json.loads(raw))
print("error fed back to the model:" if err else "ok", err)
''')
CODE["e-rag"] = ("python", '''import math, re
from collections import Counter
# Hybrid retrieval: BM25 + a toy "dense" score, fused with Reciprocal Rank Fusion.
docs = {"d1": "refund policy for bereavement fares", "d2": "baggage allowance and fees",
        "d3": "how to request a refund after travel", "d4": "loyalty points expiry"}
tok = lambda s: re.findall(r"\\w+", s.lower())
N, avgdl = len(docs), sum(len(tok(d)) for d in docs.values()) / len(docs)
df = Counter(t for d in docs.values() for t in set(tok(d)))
def bm25(q, d, k1=1.5, b=0.75):
    tf, dl = Counter(tok(d)), len(tok(d))
    return sum(math.log(1 + (N - df[t] + .5) / (df[t] + .5)) * tf[t]*(k1+1) / (tf[t] + k1*(1-b+b*dl/avgdl))
               for t in tok(q) if t in tf)
def dense(q, d): return len(set(tok(q)) & set(tok(d))) / math.sqrt(len(tok(d)))   # stand-in for embeddings
def rrf(rankings, k=60):
    s = Counter()
    for r in rankings:
        for i, d in enumerate(r): s[d] += 1 / (k + i + 1)
    return [d for d, _ in s.most_common()]
q = "refund bereavement"
r1 = sorted(docs, key=lambda d: -bm25(q, docs[d])); r2 = sorted(docs, key=lambda d: -dense(q, docs[d]))
print(rrf([r1, r2])[:2])
''')
CODE["e-cache"] = ("python", '''import math
# Semantic cache: return a stored answer when a new query is close enough in embedding space.
def embed(text):            # toy bag-of-letters embedding; use a real embedding model in practice
    v = [0]*26
    for ch in text.lower():
        if ch.isalpha(): v[ord(ch)-97] += 1
    n = math.sqrt(sum(x*x for x in v)) or 1
    return [x/n for x in v]
cache = []
def lookup(q, threshold=0.95):
    e = embed(q)
    best = max(cache, key=lambda it: sum(a*b for a, b in zip(e, it[0])), default=None)
    if best and sum(a*b for a, b in zip(e, best[0])) >= threshold: return best[1]
def store(q, answer): cache.append((embed(q), answer))
store("What is your refund policy?", "Refunds within 30 days.")
print(lookup("what's your refund policy"))     # hit
print(lookup("How do I reset my password?"))   # miss -> None
# Tune the threshold on real paraphrase pairs; false hits are worse than misses.
''')
CODE["e-eval"] = ("python", '''# Assertion-style evals (cheap, deterministic) run on every prompt change.
cases = [
  {"input": "list homes in Detroit under 300k", "output": "Found 3 listings in Detroit ...", "must": ["Detroit"], "must_not": ["Chicago"]},
  {"input": "email the client",                "output": "I sent the email to {client}",   "must": [],        "must_not": ["{", "}"]},
]
def check(c):
    fails = [f"missing {m!r}" for m in c["must"] if m not in c["output"]]
    fails += [f"contains {m!r}" for m in c["must_not"] if m in c["output"]]
    return fails
for c in cases:
    f = check(c); print("PASS" if not f else "FAIL", c["input"], f)
''')
CODE["e-vector"] = ("python", '''import random, math
# Why ANN indexes exist: exact search is O(N); IVF searches only the nearest clusters.
rng = random.Random(1); D = 8
vecs = [[rng.gauss(0, 1) for _ in range(D)] for _ in range(2000)]
dist = lambda a, b: sum((x-y)**2 for x, y in zip(a, b))
cents = rng.sample(vecs, 16)
for _ in range(5):                                   # a few k-means iterations
    buckets = [[] for _ in cents]
    for v in vecs: buckets[min(range(len(cents)), key=lambda i: dist(v, cents[i]))].append(v)
    cents = [[sum(c)/len(b) for c in zip(*b)] if b else cents[i] for i, b in enumerate(buckets)]
q = [rng.gauss(0, 1) for _ in range(D)]
exact = min(vecs, key=lambda v: dist(q, v))
probe = sorted(range(len(cents)), key=lambda i: dist(q, cents[i]))[:3]   # nprobe=3
cand = [v for i in probe for v in buckets[i]]
approx = min(cand, key=lambda v: dist(q, v))
print(f"scanned {len(cand)}/{len(vecs)} vectors; found exact NN: {approx == exact}")
''')
CODE["e-reasoning"] = ("python", '''import random
from collections import Counter
# Test-time compute in its simplest form: self-consistency (sample N, majority vote).
def noisy_solver(rng):                      # stand-in for a model that is right 60% of the time
    return "42" if rng.random() < 0.6 else rng.choice(["41", "43", "24"])
def accuracy(n_samples, trials=2000, rng=random.Random(0)):
    ok = 0
    for _ in range(trials):
        votes = Counter(noisy_solver(rng) for _ in range(n_samples))
        ok += votes.most_common(1)[0][0] == "42"
    return ok / trials
for n in (1, 5, 15):
    print(f"{n:>2} samples -> {accuracy(n):.2f}")    # more compute, higher accuracy, higher cost
''')
CODE["e-agents"] = ("python", '''# A bounded agent loop: plan -> act -> observe, with step and error caps. The "model" is scripted.
def fake_model(history):
    if not any(h[0] == "obs" for h in history): return ("tool", "search", "weather Detroit")
    return ("final", "It is 12°C in Detroit.")
TOOLS = {"search": lambda q: "Detroit: 12°C, cloudy"}
def run(task, max_steps=5):
    history = [("user", task)]
    for step in range(max_steps):
        kind, *rest = fake_model(history)
        if kind == "final": return rest[0], step
        name, arg = rest
        try: obs = TOOLS[name](arg)
        except Exception as e: obs = f"error: {e}"
        history.append(("obs", obs))
    raise RuntimeError("step budget exhausted")
print(run("What's the weather in Detroit?"))
''')
CODE["e-prod"] = ("python", '''import random, time
# Retry with exponential backoff + jitter, a timeout budget, and a fallback model.
class Transient(Exception): pass
def flaky(prompt, rng=random.Random(3)):
    if rng.random() < 0.6: raise Transient("429 rate limited")
    return "primary: ok"
def call_with_retries(fn, prompt, attempts=4, base=0.05, deadline_s=1.0):
    start = time.monotonic()
    for i in range(attempts):
        try: return fn(prompt)
        except Transient:
            sleep = base * 2**i * random.uniform(0.5, 1.5)
            if time.monotonic() - start + sleep > deadline_s: break
            time.sleep(sleep)
    return "fallback-model: ok"
print(call_with_retries(flaky, "hi"))
''')
CODE["e-ft"] = ("python", '''import json
# Prepare chat-format SFT data and hold out an eval split before any fine-tuning job.
examples = [("Classify: 'refund not received'", "billing"), ("Classify: 'app crashes on login'", "bug"),
            ("Classify: 'how do I export data'", "how-to"), ("Classify: 'charged twice'", "billing")]
rows = [{"messages": [{"role": "system", "content": "Label the ticket."},
                      {"role": "user", "content": q}, {"role": "assistant", "content": a}]} for q, a in examples]
train, held_out = rows[:-1], rows[-1:]
with open("/tmp/train.jsonl", "w") as f:
    for r in train: f.write(json.dumps(r) + "\\n")
print(len(train), "train rows;", len(held_out), "held out. First row:", json.dumps(train[0])[:90], "...")
''')
CODE["e-synth"] = ("python", '''import random
# Template-based synthetic data with dedup and a quality filter (an LLM would generate; a judge would filter).
rng = random.Random(5)
intents = {"billing": ["I was charged {n} times", "refund my {item}"], "bug": ["{item} crashes on start", "error {code} when saving"]}
fill = lambda t: t.format(n=rng.randint(2, 3), item=rng.choice(["app", "order", "plugin"]), code=rng.randint(400, 599))
data = {(fill(t), label) for label, ts in intents.items() for t in ts for _ in range(5)}
data = [d for d in data if len(d[0].split()) >= 3]           # trivial quality filter
print(len(data), "unique examples, e.g.", sorted(data)[:3])
''')
CODE["e-docrag"] = ("python", '''# Keep tables intact when chunking documents: one table = one chunk, with its caption as context.
doc = [("h", "Q3 results"), ("p", "Revenue grew in all regions."),
       ("table", "| region | revenue |\\n| EU | 10 |\\n| US | 14 |"), ("caption", "Table 1: Revenue by region ($M)"),
       ("p", "Costs were flat.")]
chunks, cur, heading = [], [], ""
for kind, text in doc:
    if kind == "h": heading = text; continue
    if kind == "table": chunks.append(f"[{heading}] TABLE\\n{text}"); continue
    if kind == "caption": chunks[-1] += f"\\n{text}"; continue
    chunks.append(f"[{heading}] {text}")
for c in chunks: print("---\\n" + c)
''')
CODE["e-vision"] = ("python", '''import json
# Validate VLM/OCR extraction output against a schema and cross-check totals before trusting it.
raw = '{"invoice_no": "INV-881", "lines": [{"desc": "GPU hours", "qty": 10, "unit": 2.5}], "total": 25.0}'
def validate_invoice(d):
    errs = []
    if not str(d.get("invoice_no", "")).startswith("INV-"): errs.append("invoice_no")
    calc = round(sum(l["qty"] * l["unit"] for l in d.get("lines", [])), 2)
    if abs(calc - d.get("total", -1)) > 0.01: errs.append(f"total mismatch {calc} != {d.get('total')}")
    return errs
errs = validate_invoice(json.loads(raw))
print("accept" if not errs else f"send to human review: {errs}")
''')
CODE["e-multi"] = ("python", '''# Cascade routing: try the cheap model; escalate when its confidence is low.
def small(q): return ("Paris", 0.97) if "capital of France" in q else ("not sure", 0.40)
def large(q): return ("A detailed answer", 0.90)
COST = {"small": 0.1, "large": 1.0}
def route(q, threshold=0.8):
    ans, conf = small(q)
    if conf >= threshold: return ans, COST["small"]
    return large(q)[0], COST["small"] + COST["large"]
for q in ["capital of France?", "explain our Q3 churn drivers"]:
    print(q, "->", route(q))
''')
CODE["e-datafly"] = ("python", '''from collections import Counter
# Turn production feedback into the next eval set and training candidates.
logs = [{"q": "cancel order", "thumb": "down", "reason": "wrong policy"},
        {"q": "cancel order", "thumb": "down", "reason": "wrong policy"},
        {"q": "track parcel", "thumb": "up"},
        {"q": "change address", "thumb": "down", "reason": "tool error"}]
fails = [l for l in logs if l["thumb"] == "down"]
print("top failure reasons:", Counter(l["reason"] for l in fails).most_common())
new_eval_cases = sorted({l["q"] for l in fails})
print("add to golden set (after human labeling):", new_eval_cases)
''')
CODE["e-edge"] = ("python", '''# Will a model fit on the device? weights + KV cache + runtime overhead vs available RAM.
def fits(params_b, bits, ctx, layers, kv_heads, head_dim, ram_gb, overhead_gb=0.5):
    weights = params_b * 1e9 * bits / 8 / 1e9
    kv = 2 * layers * kv_heads * head_dim * ctx * 2 / 1e9
    total = weights + kv + overhead_gb
    return round(total, 2), total <= ram_gb
print("3B @3.7 bits, 4k ctx:", fits(3, 3.7, 4096, 26, 8, 128, ram_gb=4))
print("8B @16 bits, 4k ctx:", fits(8, 16, 4096, 32, 8, 128, ram_gb=4))
''')
CODE["e-llmops"] = ("yaml", '''# CI gate for a prompt/model change (GitHub Actions + promptfoo-style eval)
name: llm-eval
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx promptfoo@latest eval -c evals/promptfooconfig.yaml --output results.json
      - run: python scripts/gate.py results.json --min-pass-rate 0.92   # fail the PR on regression
''')
CODE["e-voice"] = ("python", '''# Voice-agent latency budget: each stage adds up before the user hears anything.
budget_ms = {"endpointing (VAD silence)": 300, "STT final": 150, "LLM time-to-first-token": 350,
             "TTS first audio": 120, "network + jitter buffer": 100}
total = sum(budget_ms.values())
for k, v in budget_ms.items(): print(f"{k:<28}{v:>5} ms")
print(f"{'total':<28}{total:>5} ms  ->", "feels natural" if total <= 1000 else "feels slow")
# Streaming every stage and barge-in (stop TTS when the user speaks) matter more than any single model.
''')
CODE["e-post"] = ("python", '''import json
# Preference pairs for DPO-style post-training: prompt, chosen, rejected, plus provenance.
pairs = [{"prompt": "Summarize the refund policy.",
          "chosen": "Refunds are available within 30 days with a receipt.",
          "rejected": "Refunds are always available, no questions asked.",
          "labeler": "policy-team", "reason": "rejected is factually wrong"}]
for p in pairs:
    assert p["chosen"] != p["rejected"] and p["reason"]
print(json.dumps(pairs[0], indent=1))
''')
CODE["e-multimodal-app"] = ("python", '''import base64, json
# Build a multimodal chat message (OpenAI-style content parts) from local image bytes.
png_1x1 = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
msg = {"role": "user", "content": [
    {"type": "text", "text": "Describe any damage visible in this photo."},
    {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png_1x1).decode()}}]}
print(json.dumps(msg)[:140], "...")
# Downscale images before sending: image tokens scale with resolution and dominate cost.
''')
CODE["e-rlenv"] = ("python", '''import random
# A tiny RL environment with a verifiable reward, plus a reward-hacking check.
class MathEnv:
    def reset(self, rng=random.Random(0)):
        self.a, self.b = rng.randint(1, 50), rng.randint(1, 50)
        return f"What is {self.a}+{self.b}? Answer with a number."
    def step(self, answer: str):
        try: ok = int(answer.strip()) == self.a + self.b
        except ValueError: ok = False
        return (1.0 if ok else 0.0), True
env = MathEnv(); obs = env.reset(); print(obs)
print("correct:", env.step(str(env.a + env.b)), " hack attempt:", env.step("the answer is correct"))
''')
CODE["e-genmedia"] = ("python", '''import math, random
# The core of diffusion: the forward noising process x_t = sqrt(a_bar)*x0 + sqrt(1-a_bar)*eps.
T = 1000
betas = [1e-4 + (0.02 - 1e-4) * t / (T - 1) for t in range(T)]   # linear schedule (DDPM)
a_bar, p = [], 1.0
for b in betas: p *= (1 - b); a_bar.append(p)
x0, rng = 1.0, random.Random(0)
for t in (0, 250, 500, 999):
    eps = rng.gauss(0, 1)
    xt = math.sqrt(a_bar[t]) * x0 + math.sqrt(1 - a_bar[t]) * eps
    print(f"t={t:>4} signal={math.sqrt(a_bar[t]):.3f} x_t={xt:+.3f}")
# A model learns to predict eps from x_t; sampling runs this backwards.
''')
