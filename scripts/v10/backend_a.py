from helpers10 import R, Q, T, SUBJ, C
S = []
# ---------------------------------------------------------------- b-python
sid = "b-python"
S.append(SUBJ(sid, "Python and TypeScript for AI Engineers",
 "Almost every agent, connector and eval harness is Python or TypeScript. Typed, async, validated code is the difference between a demo and a service.",
 "AI engineers live in two languages. Python owns models, data and evals. TypeScript owns product front-ends, edge functions and many agent SDKs. You don't need every corner of either, but you do need the same production habits in both: type hints, schema validation at every boundary, async I/O for slow network calls, packaging that reproduces, and tests.\n\nThe common failure isn't syntax. It's untyped dictionaries flowing from an LLM into business logic, blocking calls inside an event loop, and 'works on my laptop' environments.",
 "Build a typed FastAPI service with a Pydantic request/response model that calls an LLM asynchronously, plus a small TypeScript client generated from its OpenAPI schema.",
 [T(sid, "py", "Production Python",
   "Production Python for AI work means four habits. First, type hints everywhere, checked by mypy or pyright, so refactors are safe. Second, Pydantic models at every boundary (HTTP input, LLM output, tool arguments), so bad data fails loudly and early. Third, asyncio for network-bound work: an agent mostly waits on model and API calls, so concurrency matters more than raw speed. Fourth, reproducible environments with a lockfile (uv, Poetry or pip-tools) and pinned model SDK versions, because SDKs change quickly.",
   [("Type hints and mypy", "Annotate functions and run a type checker in CI; it catches None-handling and wrong-argument bugs before production."),
    ("Pydantic validation", "Parse, don't trust: turn raw JSON from users, tools and LLMs into validated models with clear errors."),
    ("asyncio and concurrency", "Use async clients and asyncio.gather for parallel model and API calls; never block the event loop with sync I/O."),
    ("Packaging and environments", "Lock dependencies, pin SDK versions and build the same container locally and in CI.")]),
  T(sid, "ts", "TypeScript for AI products",
   "TypeScript matters because the product surface (web apps, browser extensions, edge functions, many MCP servers and agent SDKs) is written in it. Its value is static types over JavaScript's flexibility: you describe the shape of an API response once and the compiler checks every use. Pair it with a runtime validator such as Zod, because TypeScript types vanish at runtime and LLM output is untrusted. Learn promises and async/await, streaming with fetch and ReadableStream, and how to generate types from an OpenAPI or JSON schema so client and server never drift.",
   [("Static types vs runtime validation", "Types check your code at compile time; a runtime schema (Zod) checks the data you actually receive."),
    ("async/await and streaming", "Stream tokens to the UI with fetch and ReadableStream or server-sent events instead of waiting for the full answer."),
    ("Generated clients", "Generate TypeScript types from the server's OpenAPI document so contract changes break the build, not production."),
    ("Node, Deno, Bun and edge runtimes", "Know which runtime your code runs on; edge runtimes restrict APIs such as the filesystem and long-running work.")])],
 [Q("An LLM returns JSON for a tool call. What is the safest first step in Python?", ["Validate it into a Pydantic model and handle validation errors", "Pass the dict straight to the function", "Use eval() to parse it", "Assume the schema is followed because you asked nicely"], 0, "Model output is untrusted input; validate before use and feed errors back."),
  Q("Why use asyncio in an agent service?", ["Most time is spent waiting on network calls, so concurrency raises throughput", "It makes CPU-bound math faster", "It removes the need for timeouts", "It is required by Pydantic"], 0, "Agents are I/O-bound; async lets one process overlap many waits."),
  Q("TypeScript types protect you from bad API data at runtime.", ["False: types are erased; you need runtime validation such as Zod", "True: the compiler checks responses", "True, but only in strict mode", "False, because TypeScript has no types"], 0, "Static types disappear after compilation; validate untrusted data at runtime.")],
 [R("The Python Tutorial (official)", "https://docs.python.org/3/tutorial/", "docs", "intro", "The official tutorial, aimed at programmers new to Python. Covers data structures, modules, errors, classes and the standard library tour in an afternoon."),
  R("TypeScript Handbook", "https://www.typescriptlang.org/docs/handbook/intro.html", "docs", "intro", "The official handbook: everyday types, narrowing, generics, object types and modules. Read 'The Basics' and 'Everyday Types' first."),
  R("Pydantic documentation", "https://docs.pydantic.dev/latest/", "docs", "reference", "Models, fields, validators, JSON Schema generation, strict mode and serialization. The validation layer used by FastAPI and most LLM SDKs."),
  R("FastAPI documentation", "https://fastapi.tiangolo.com/", "docs", "intermediate", "Typed Python web APIs with automatic validation and OpenAPI docs. Its tutorial covers path/query parameters, request bodies, dependencies and async."),
  R("mypy documentation", "https://mypy.readthedocs.io/en/stable/", "docs", "reference", "The type-hints cheat sheet, how to adopt mypy in an existing codebase, protocols and structural subtyping."),
  R("Dropbox: Our journey to type checking 4 million lines of Python", "https://dropbox.tech/application/our-journey-to-type-checking-4-million-lines-of-python", "case", "intermediate", "Jukka Lehtosalo's 2019 account of how Dropbox adopted mypy incrementally, including the performance work and the case for types as verified documentation.")],
 dict(intuition="Think of types and schemas as the contracts between the pieces of an AI system. A model, a tool, a database and a UI all speak in JSON, and JSON lies easily: a missing field, a string where a number should be, a null nobody expected. Typed Python and TypeScript, plus runtime validation at each boundary, turn those silent lies into loud, early, fixable errors.",
  how=["Define the data shapes once (Pydantic models in Python, Zod schemas or generated types in TypeScript).", "Validate every boundary: HTTP input, LLM output, tool arguments and third-party API responses.", "Make network-bound work async and give every call a timeout.", "Run a type checker and tests in CI on every change.", "Lock dependencies and pin model SDK versions so builds reproduce."],
  example="An agent asks a model for {\"order_id\": \"A-17\", \"refund_usd\": 20}. One day the model returns refund_usd as \"twenty\". Without validation, the string reaches the payment code and crashes, or worse, is coerced. With a Pydantic model (order_id: str, refund_usd: float with gt=0, le=500), validation fails, the error text goes back to the model, and the retry returns 20.0. The cap at 500 also blocks an injected request for 5,000.",
  lang="python",
  code='''import asyncio, json
from dataclasses import dataclass
# Stdlib version of "validate at the boundary" (Pydantic does this with less code).
@dataclass(frozen=True)
class Refund:
    order_id: str
    refund_usd: float
    @classmethod
    def parse(cls, raw: str) -> "Refund":
        d = json.loads(raw)
        if not isinstance(d.get("order_id"), str) or not d["order_id"].startswith("A-"):
            raise ValueError("order_id must look like 'A-123'")
        amt = d.get("refund_usd")
        if not isinstance(amt, (int, float)) or not 0 < amt <= 500:
            raise ValueError("refund_usd must be a number in (0, 500]")
        return cls(d["order_id"], float(amt))
async def fake_llm(prompt: str, attempt: int) -> str:
    await asyncio.sleep(0.01)                      # network wait
    return '{"order_id": "A-17", "refund_usd": "twenty"}' if attempt == 0 else '{"order_id": "A-17", "refund_usd": 20}'
async def get_refund(prompt: str) -> Refund:
    err = ""
    for attempt in range(3):
        raw = await asyncio.wait_for(fake_llm(prompt + err, attempt), timeout=5)
        try: return Refund.parse(raw)
        except ValueError as e: err = f"\\nPrevious output invalid: {e}"
    raise RuntimeError("model never produced valid output")
print(asyncio.run(get_refund("Refund order A-17")))''',
  mistakes=["Passing raw dicts from the model straight into business logic.", "Calling a synchronous HTTP client inside an async handler, which freezes every other request.", "Trusting TypeScript types for runtime data instead of validating it.", "Unpinned SDK versions that change behaviour between deploys."],
  enterprise="A support team's FastAPI service calls three tools per request. Moving the calls from sequential requests to asyncio.gather, with a 10-second timeout each, cuts p95 latency from about 9 s to 4 s. Adding Pydantic models for tool outputs turns a weekly production crash into a logged validation error.",
  takeaways=["Validate every boundary; LLM output is untrusted input.", "Agents are I/O-bound: async plus timeouts beats faster code.", "Types plus a checker in CI make large codebases refactorable.", "Generate clients from schemas so front end and back end never drift."],
  diagram='flowchart LR\n  U["User / UI (TypeScript)"] -->|"typed request"| API["FastAPI (Pydantic in)"]\n  API -->|"async + timeout"| LLM["LLM"]\n  LLM -->|"raw JSON"| V{"Validate (Pydantic)"}\n  V -->|"ok"| BL["Business logic"]\n  V -->|"error text"| LLM\n  BL --> OUT["Typed response (OpenAPI)"]\n  OUT --> U',
  diagramAlt="A typed request flows from a TypeScript UI to a FastAPI service, which calls an LLM asynchronously. The model's raw JSON is validated; failures go back to the model, and valid data reaches business logic and returns as a typed response."),
 case=C("Dropbox", "Our journey to type checking 4 million lines of Python (Dropbox Tech, 2019)", "https://dropbox.tech/application/our-journey-to-type-checking-4-million-lines-of-python",
   "Dropbox, a heavy Python user, adopted static type checking with mypy and grew coverage to 4 million lines of annotated code. The post explains why: type annotations act as verified documentation, and a type checker finds subtle bugs such as forgetting to handle None. It also describes the performance work needed to keep mypy fast at that scale.",
   "Adopt types incrementally and invest in tooling speed. At scale, being able to understand code becomes the main constraint on productivity.")))
# ---------------------------------------------------------------- b-dsa
sid = "b-dsa"
S.append(SUBJ(sid, "Data Structures and Algorithms That Matter in Practice",
 "You won't hand-roll red-black trees, but choosing a dict over a list scan, a heap over a sort, or a linear regex over a backtracking one decides whether a system holds up.",
 "Practical DSA for AI engineers is about recognizing complexity in everyday code: hash maps for lookups, sets for dedup, heaps for top-k, queues for BFS and work scheduling, sorting plus binary search, and graphs for dependencies and lineage. Big-O matters when n is a million chunks, a hundred thousand tickets, or an attacker-controlled string.\n\nLearn the standard-library tools first: dict, set, collections.deque, heapq and bisect in Python. Know the cost of each operation, and treat any nested loop over large inputs as a review flag.",
 "Profile a slow dedup-and-rank step in a RAG pipeline, replace list scans with sets and a full sort with heapq.nlargest, and report the before/after timings.",
 [T(sid, "core", "Core structures and their costs",
   "Most performance bugs come from the wrong container. A Python list membership test scans every element (O(n)); a set or dict lookup is O(1) on average. Appending to a list is cheap, but inserting at the front is O(n); collections.deque fixes that for queues. When you need the best k of n items, a heap gives O(n log k) instead of sorting everything. When data is sorted, bisect finds positions in O(log n). Write down the operation you do most often, then pick the structure that makes it cheap.",
   [("Hash maps and sets", "Use them for membership, counting and joins in memory; average O(1) lookups."),
    ("Queues and deques", "Use deque for FIFO work queues and BFS; popleft is O(1), list.pop(0) is O(n)."),
    ("Heaps for top-k", "heapq.nlargest(k, items) keeps only k candidates, ideal for reranking or scheduling."),
    ("Sorting and binary search", "Sort once (O(n log n)), then answer many range or position queries with bisect in O(log n).")]),
  T(sid, "graph", "Graphs, recursion and complexity traps",
   "Graphs model a lot of AI systems: agent plans as task DAGs, data lineage, service dependencies and permission hierarchies. Topological sort orders a DAG of tasks, BFS finds shortest hops, and cycle detection catches circular dependencies. Complexity traps hide in innocent code: a nested loop comparing every pair of 100,000 chunks is 10 billion comparisons, recursion without memoization can explode exponentially, and some regular expressions backtrack exponentially on hostile input. Recognize the pattern, estimate n, and measure before and after.",
   [("Topological sort", "Order tasks so every dependency runs first; use it for pipelines and multi-step agent plans."),
    ("BFS and DFS", "Traverse dependency or lineage graphs; BFS gives the shortest path in hops."),
    ("Memoization", "Cache results of pure recursive calls (functools.lru_cache) to avoid recomputing subproblems."),
    ("Regex backtracking", "Nested quantifiers like (a+)+ can take exponential time; prefer linear-time engines such as RE2 for untrusted input.")])],
 [Q("You dedupe 1M chunk hashes with `if h not in seen_list`. What is the fix?", ["Use a set, turning O(n²) total work into about O(n)", "Sort the list after every insert", "Use a deque", "Increase the server's RAM"], 0, "List membership is O(n); set membership is O(1) on average."),
  Q("Best way to get the top 10 of 5 million scored candidates?", ["heapq.nlargest(10, ...)", "Sort all 5 million and slice", "Bubble sort", "Scan the list 10 times"], 0, "A heap of size k costs O(n log k) and little memory."),
  Q("Why can a single regular expression take down a service?", ["Backtracking engines can take exponential time on some inputs", "Regex always uses the GPU", "Regex disables caching", "Regex is O(1) but uses too much memory"], 0, "Catastrophic backtracking is an algorithmic-complexity bug; Cloudflare's 2019 outage is the classic example.")],
 [R("Python wiki: TimeComplexity", "https://wiki.python.org/moin/TimeComplexity", "reference", "reference", "Archived python.org page listing the big-O cost of operations on list, deque, set and dict in CPython. Keep it open when choosing containers."),
  R("heapq: heap queue algorithm (Python docs)", "https://docs.python.org/3/library/heapq.html", "docs", "intro", "The standard-library priority queue: heappush/heappop, nlargest/nsmallest and merge, with notes on stability and priority-queue implementation."),
  R("USF Data Structure Visualizations", "https://www.cs.usfca.edu/~galles/visualization/Algorithms.html", "interactive", "intro", "Animated visualizations of stacks, queues, hash tables, heaps, trees, sorting and graph algorithms. Step through each operation to build intuition."),
  R("Coding Interview University", "https://github.com/jwasham/coding-interview-university", "course", "intermediate", "A complete self-study computer science plan (complexity, data structures, sorting, graphs, recursion) with curated videos. Use it as a checklist, not a mandate."),
  R("Cloudflare: Details of the outage on July 2, 2019", "https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/", "case", "intermediate", "Cloudflare's post-mortem: one WAF rule's regex backtracked enormously, exhausting CPU worldwide for 27 minutes. It includes a readable explanation of regex backtracking.")],
 dict(intuition="Data structures are about making the operation you do most often cheap. If you mostly ask 'have I seen this?', you want a set. If you mostly ask 'what's the best item right now?', you want a heap. If you mostly ask 'what must happen first?', you want a graph and a topological sort. Algorithms only feel academic until n gets big, or until an attacker picks n for you.",
  how=["Name the dominant operation (lookup, top-k, ordering, traversal).", "Pick the container that makes it cheap (dict/set, heap, deque, sorted list plus bisect, graph).", "Estimate n in production, not in your test fixture.", "Measure with timeit or a profiler before and after.", "Guard untrusted input with linear-time algorithms and size limits."],
  example="A RAG pipeline dedupes 200,000 chunks by checking `if h not in seen` where seen is a list. That is about 200,000²/2 = 20 billion comparisons. At roughly 50 million per second in CPython, that takes around 400 s. Switching to a set makes it 200,000 hash lookups, well under a second. Replacing `sorted(scores)[-20:]` with heapq.nlargest(20, scores) avoids sorting everything on each query.",
  lang="python",
  code='''import heapq, timeit, random
from collections import deque, defaultdict
rng = random.Random(0)
hashes = [rng.randrange(50_000) for _ in range(20_000)]
def dedupe_list(xs):
    seen, out = [], []
    for h in xs:
        if h not in seen: seen.append(h); out.append(h)
    return out
def dedupe_set(xs):
    seen, out = set(), []
    for h in xs:
        if h not in seen: seen.add(h); out.append(h)
    return out
assert dedupe_list(hashes) == dedupe_set(hashes)
t_list = timeit.timeit(lambda: dedupe_list(hashes), number=1)
t_set = timeit.timeit(lambda: dedupe_set(hashes), number=1)
print(f"list {t_list:.3f}s vs set {t_set:.4f}s (~{t_list / t_set:.0f}x)")
scores = [(rng.random(), f"chunk{i}") for i in range(100_000)]
print("top-3:", [c for _, c in heapq.nlargest(3, scores)])
# Topological sort (Kahn's algorithm) for an agent's task plan
deps = {"fetch": [], "parse": ["fetch"], "embed": ["parse"], "index": ["embed"], "report": ["parse", "index"]}
indeg = {k: len(v) for k, v in deps.items()}; users = defaultdict(list)
for k, vs in deps.items():
    for v in vs: users[v].append(k)
q, order = deque(k for k, d in indeg.items() if d == 0), []
while q:
    n = q.popleft(); order.append(n)
    for m in users[n]:
        indeg[m] -= 1
        if indeg[m] == 0: q.append(m)
assert len(order) == len(deps), "cycle detected"
print("plan:", order)''',
  mistakes=["Membership checks on lists inside loops.", "Sorting everything to take the top few items.", "Recursion without memoization on overlapping subproblems.", "Running backtracking regexes on untrusted, unbounded input."],
  enterprise="A ticket-routing service slows to 40 s per batch as volume grows. A profile shows a nested loop matching every ticket against every rule. Indexing rules by keyword in a dict and capping input length brings the batch to under 1 s, and switching the rule engine to RE2 removes a backtracking risk found in review.",
  takeaways=["Choose the structure that makes the dominant operation cheap.", "Know the big-O of dict, set, list, deque and heap operations.", "Graphs and topological sort model plans, pipelines and lineage.", "Algorithmic complexity is a security property when attackers choose the input."],
  diagram='flowchart TD\n  Q{"Dominant operation?"} -->|"seen it?"| H["dict / set: O(1)"]\n  Q -->|"best k?"| HP["heap: O(n log k)"]\n  Q -->|"FIFO work"| D["deque: O(1) ends"]\n  Q -->|"range / position"| B["sorted list + bisect: O(log n)"]\n  Q -->|"what first?"| G["graph + topological sort"]',
  diagramAlt="A decision tree that maps the dominant operation to a data structure: membership to dict or set, best-k to a heap, FIFO work to a deque, range queries to a sorted list with bisect, and ordering dependencies to a graph with topological sort.",
  widget=None),
 case=C("Cloudflare", "Details of the Cloudflare outage on July 2, 2019", "https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/",
   "Cloudflare deployed a new WAF managed rule containing a regular expression that backtracked enormously. It exhausted CPU on every core handling HTTP/HTTPS traffic across its network, bringing down core proxying, CDN and WAF functionality for 27 minutes. The post-mortem explains regex backtracking in detail and the process gaps that slowed the response.",
   "Algorithmic complexity is an availability risk. Use linear-time matching for untrusted input, and stage global rule rollouts.")))
# ---------------------------------------------------------------- b-cli
sid = "b-cli"
S.append(SUBJ(sid, "Git, Linux and the Command Line",
 "FDEs and AI engineers debug on customer boxes, GPU nodes and CI runners. The shell and Git are the universal tools there.",
 "You will SSH into a VM inside a customer's VPC, read logs on a GPU node, bisect a regression and rescue a broken branch, often with no GUI. Fluency means: navigating and inspecting a Linux system (processes, ports, disk, permissions, systemd, environment variables), composing pipelines with grep, awk, jq and xargs, writing safe bash scripts, and using Git beyond add/commit/push (branches, rebase vs merge, bisect, reflog, tags, signed commits).\n\nSafety habits matter as much as speed: know which host you're on, prefer dry runs, and never run destructive commands you haven't read twice.",
 "Write a safe bash script (set -euo pipefail, dry-run flag, host check) that collects diagnostics from a Linux VM, and use git bisect to find the commit that broke a test in a sample repo.",
 [T(sid, "linux", "Linux and shell fluency",
   "Linux skills for AI work are diagnostic. Which process holds the port (ss -ltnp)? Why is the disk full (df -h, du -sh)? Is the service running (systemctl status, journalctl -u)? Which environment variables did the container get? Pipelines turn logs into answers: grep for errors, jq to slice JSON logs, sort | uniq -c for counts. For scripts, start with set -euo pipefail, quote variables, and add a --dry-run mode. Permissions, users and file ownership explain a large share of 'works locally, fails on the server' bugs.",
   [("Process, port and disk triage", "ps, top, ss -ltnp, df -h, du -sh and free -h answer most 'why is it slow or broken' questions."),
    ("systemd and logs", "systemctl status and journalctl -u <service> show whether a service is up and why it died."),
    ("Pipelines with grep, jq and awk", "Compose small tools: jq for JSON logs, sort | uniq -c for counts, xargs for batch actions."),
    ("Safe bash scripting", "Use set -euo pipefail, quote variables, check the hostname and support --dry-run before destructive steps.")]),
  T(sid, "git", "Git beyond the basics",
   "Git is your undo button and your audit log. Learn the model first: commits are snapshots, branches are movable pointers, and HEAD is where you are. Then the rescue tools: git reflog recovers 'lost' commits, git bisect binary-searches history for the commit that broke something, and git revert undoes a pushed change safely, unlike rewriting shared history. Agree on a team workflow (trunk-based with short-lived branches is common), protect main with required reviews and CI, and never commit secrets: once pushed, assume they are leaked and rotate them.",
   [("The commit graph", "Commits are snapshots, branches are pointers; draw the graph when a merge or rebase confuses you."),
    ("bisect and reflog", "git bisect finds a bad commit in log2(n) steps; git reflog recovers commits after a bad reset."),
    ("Merge, rebase and revert", "Rebase only private branches; use revert to undo commits that others already have."),
    ("Secrets and hygiene", "Use .gitignore, pre-commit secret scanning and rotation; deleting a pushed secret does not un-leak it.")])],
 [Q("A test started failing somewhere in the last 200 commits. Fastest systematic approach?", ["git bisect: about 8 test runs", "Read all 200 diffs", "Revert the last commit and hope", "Re-clone the repo"], 0, "Binary search over 200 commits needs about log2(200) ≈ 8 steps."),
  Q("What does `set -euo pipefail` do in a bash script?", ["Exit on errors, unset variables and failures inside pipelines", "Speed up the script", "Run it as root", "Disable logging"], 0, "It turns silent failures into immediate exits."),
  Q("You accidentally pushed an API key. What must you do?", ["Rotate the key, then remove it from history", "Delete the file in a new commit and move on", "Make the repo private and keep the key", "Force-push and keep the key"], 0, "Assume anything pushed is compromised; rotation is the real fix.")],
 [R("Pro Git (official book)", "https://git-scm.com/book/en/v2", "book", "intermediate", "The free, community-updated Pro Git book. Chapters 2–3 (basics, branching) and 7 (tools, including reset, rerere and bisect) cover what you need daily."),
  R("The Missing Semester of Your CS Education (MIT)", "https://missing.csail.mit.edu/", "course", "intro", "MIT's course on the tools nobody teaches: shell, scripting, editors, data wrangling, command-line environment, version control and debugging."),
  R("Learn Git Branching", "https://learngitbranching.js.org/", "interactive", "intro", "An interactive visual sandbox where you run Git commands and watch the commit graph change. The fastest way to understand rebase and cherry-pick."),
  R("GNU Bash Reference Manual", "https://www.gnu.org/software/bash/manual/bash.html", "reference", "reference", "The official Bash 5.3 manual: expansions, quoting, redirections, conditionals and the set builtin options used in safe scripts."),
  R("GitLab: Postmortem of database outage of January 31 (2017)", "https://about.gitlab.com/blog/2017/02/10/postmortem-of-database-outage-of-january-31/", "case", "intermediate", "A candid post-mortem: a deletion meant for the secondary ran on the primary, about 300 GB was removed, and several backup methods turned out not to work.")],
 dict(intuition="The command line is a workshop where small, sharp tools snap together. Git is a time machine with a full logbook. Together they let you inspect any system, automate any chore and undo almost any mistake, provided you know which machine you're standing on and you keep the logbook honest.",
  how=["Orient: whoami, hostname, pwd and environment before acting.", "Inspect: processes, ports, disk, services and logs.", "Compose: pipe small tools together to answer one question at a time.", "Script safely: strict mode, quoting, dry-run and host checks.", "Version everything: small commits, protected main, bisect and revert for recovery."],
  example="A model server on a customer VM returns 502s. Running ss -ltnp shows nothing listening on :8000. journalctl -u model-server shows 'CUDA out of memory' at startup. Running nvidia-smi shows a stale process holding 70 GB, which you stop. Back in the repo, git bisect over the last 64 commits takes 6 runs and finds a commit that doubled max_model_len. You revert it with git revert and push.",
  lang="bash",
  code='''#!/usr/bin/env bash
# Collect diagnostics safely from a Linux host. Usage: ./diag.sh [--dry-run] expected-hostname
set -euo pipefail
DRY=0; [[ "${1:-}" == "--dry-run" ]] && { DRY=1; shift; }
EXPECTED="${1:?usage: diag.sh [--dry-run] expected-hostname}"
[[ "$(hostname)" == "$EXPECTED" ]] || { echo "refusing: on $(hostname), expected $EXPECTED" >&2; exit 1; }
run() { if (( DRY )); then echo "[dry-run] $*"; else "$@"; fi; }
OUT="diag-$(date +%Y%m%d-%H%M%S)"; run mkdir -p "$OUT"
run sh -c "df -h > '$OUT/disk.txt'"
run sh -c "ss -ltnp > '$OUT/ports.txt' 2>/dev/null || true"
run sh -c "journalctl -u model-server --since '1 hour ago' --no-pager > '$OUT/service.log' 2>/dev/null || true"
run sh -c "grep -c -i error '$OUT/service.log' || true"
echo "done: $OUT"
# Find the commit that broke the tests in about log2(N) steps:
#   git bisect start HEAD v1.4.0 && git bisect run pytest -q tests/test_api.py && git bisect reset''',
  mistakes=["Running destructive commands without checking which host you are on.", "Scripts without strict mode that keep going after a failure.", "Rewriting shared history with force-push instead of reverting.", "Committing .env files and API keys."],
  enterprise="An FDE team standardizes a diagnostics script and a 'host banner' prompt that shows the environment name in red for production. Combined with protected branches and required CI, incidents caused by commands run on the wrong host drop to zero over two quarters.",
  takeaways=["Orient before you act: hostname, user and environment.", "Strict-mode bash with dry-run is the minimum for automation.", "bisect, reflog and revert are your recovery tools.", "Treat any pushed secret as leaked and rotate it."],
  diagram='flowchart LR\n  O["Orient: hostname, whoami"] --> I["Inspect: ps, ss, df, journalctl"]\n  I --> P["Pipe: grep | jq | sort | uniq -c"]\n  P --> F["Fix with a safe script (dry-run first)"]\n  F --> G["Commit + PR + CI"]\n  G -->|"regression?"| B["git bisect"]\n  B --> RV["git revert"]',
  diagramAlt="Flow from orienting on a host, inspecting processes, ports, disk and logs, piping tools to find the cause, fixing it with a dry-run-first script, then committing through a pull request with CI, and using git bisect and git revert when a regression appears."),
 case=C("GitLab", "Postmortem of database outage of January 31 (GitLab, 2017)", "https://about.gitlab.com/blog/2017/02/10/postmortem-of-database-outage-of-january-31/",
   "While fighting replication problems, a GitLab engineer ran a data-removal process meant for the secondary database on the primary (db1). By the time they stopped it a second or two later, about 300 GB of data had been removed. Finding and using backups then failed. The restore relied on a manual snapshot taken about 6 hours earlier, which was copied to staging.",
   "Make it obvious which host you're on, and test restores, not just backups. A safe environment is one where mistakes are quick to recover from.")))
# ---------------------------------------------------------------- b-debug
sid = "b-debug"
S.append(SUBJ(sid, "Debugging Systematically",
 "AI systems fail in layered ways (network, auth, data, prompt, model). A disciplined debugging loop finds the layer quickly instead of guessing.",
 "Debugging is the scientific method applied to software. Reproduce the failure. Shrink it to the smallest case. Form a hypothesis. Change one thing. Observe. With LLM systems, there are more layers to check: is it the network, the auth token, the retrieved context, the prompt template, the model version, the parser, or the tool?\n\nTools help (debuggers such as pdb and DevTools, structured logs, traces, the USE method for resources), but the habit matters more: read the actual error, check assumptions, and write down what you have ruled out.",
 "Take a failing agent trace, reproduce it deterministically by pinning the model, seed and inputs, bisect the layers (retrieval, prompt, model, parser), and write a one-page incident note with the root cause and a regression test.",
 [T(sid, "loop", "The debugging loop",
   "A reliable loop: reproduce, minimize, hypothesize, test, fix, and prevent. Reproducing an LLM bug means capturing the exact inputs: prompt, retrieved chunks, tool outputs, model name and version, temperature and seed. Minimizing means deleting context until the bug disappears, which shows you the trigger. Hypotheses should be falsifiable ('the date parser fails on ISO week formats'). Change one variable at a time. After the fix, add a regression test or eval case so the bug can't silently return. Keep notes; they become the post-mortem.",
   [("Reproduce deterministically", "Capture inputs, versions and settings; set temperature to 0 or pin a seed when the API allows it."),
    ("Minimize the case", "Remove context, tools and steps until the failure disappears; the last removal is the clue."),
    ("One change at a time", "Change a single variable per experiment so each result is interpretable."),
    ("Prevent recurrence", "Turn every fixed bug into a unit test or eval case.")]),
  T(sid, "tools", "Tools and layered diagnosis",
   "Pick the tool for the layer. For code, use an interactive debugger (pdb or breakpoint() in Python, Chrome DevTools for TypeScript) to inspect state at the failing line. For services, use structured logs and distributed traces to see which hop failed and how long each took. For resources, use Brendan Gregg's USE method: for every resource, check utilization, saturation and errors. For LLM behaviour, diff the prompt that worked against the one that failed, and replay traces against a pinned model. Work outside-in: network and auth first, then data, then prompt and model.",
   [("Interactive debuggers", "breakpoint() drops into pdb; DevTools breakpoints and watch expressions do the same in the browser."),
    ("Logs and traces", "Structured logs with request IDs and spans show where time and errors occur."),
    ("USE method", "Utilization, saturation and errors for CPU, memory, disk, network and GPU locate resource bottlenecks."),
    ("Prompt and trace diffs", "Compare a good and a bad trace side by side; the difference is usually in retrieved context or the template.")])],
 [Q("An agent gives a wrong answer 1 time in 20. First step?", ["Capture full traces of failures and reproduce one deterministically", "Switch to a bigger model", "Rewrite the system prompt from scratch", "Add more retries"], 0, "You can't fix what you can't reproduce; traces give you the exact inputs."),
  Q("What does the USE method check for each resource?", ["Utilization, saturation and errors", "Users, sessions and endpoints", "Uptime, speed and encryption", "Updates, security and exports"], 0, "Brendan Gregg's USE method is a checklist for resource bottlenecks."),
  Q("After fixing a parsing bug, what prevents it from returning?", ["A regression test or eval case built from the failing input", "A comment in the code", "A Slack message", "Restarting the service"], 0, "Bugs that aren't tested come back.")],
 [R("Julia Evans: A debugging manifesto", "https://jvns.ca/blog/2022/12/08/a-debugging-manifesto/", "blog", "intro", "A short list of debugging attitudes from Julia Evans' zine: inspect, don't guess; trust nothing; the bug is happening for a logical reason; it's probably your code."),
  R("pdb: The Python Debugger (Python docs)", "https://docs.python.org/3/library/pdb.html", "docs", "reference", "Breakpoints (including conditional ones), stepping, stack inspection and post-mortem debugging. breakpoint() enters pdb from any line."),
  R("Brendan Gregg: The USE Method", "https://www.brendangregg.com/usemethod.html", "article", "intermediate", "A checklist approach to performance: for every resource, check utilization, saturation and errors. Includes per-OS metric lists you can apply to GPU nodes."),
  R("Chrome DevTools: Debug JavaScript", "https://developer.chrome.com/docs/devtools/javascript", "docs", "intro", "A step-by-step tutorial on breakpoints, stepping and watch expressions in DevTools, for debugging TypeScript and JavaScript front ends.")],
 dict(intuition="Debugging is detective work with a strict rule: no accusations without evidence. A bug feels mysterious only because one of your assumptions is wrong. Reproduce the crime, narrow down the suspects (network, auth, data, prompt, model, parser), and test one alibi at a time until a single explanation is left.",
  how=["Reproduce: capture exact inputs, versions and settings.", "Minimize: strip the case down until the bug disappears.", "Locate the layer: network → auth → data → prompt → model → parser → tool.", "Hypothesize and test one change at a time.", "Fix, add a regression test or eval, and write a short note."],
  example="A contract-QA agent cites the wrong clause about 5% of the time. Traces show every failure involves PDFs with two-column layouts. Minimizing to one page reproduces it: the parser interleaves the columns, so chunks mix clauses. The model and prompt were fine. Switching the parser to a layout-aware mode and adding 10 two-column pages to the eval set fixes it, and the eval now guards against regressions.",
  lang="python",
  code='''# Minimize a failing input automatically (a tiny delta-debugging loop), then keep it as a regression test.
def buggy_parse(lines):
    # Bug: a line starting with "|" (a table row) is treated as a heading.
    return [l for l in lines if not l.startswith("|")]
def fails(lines):
    return len(buggy_parse(lines)) != len(lines)     # oracle: no line should be dropped
def minimize(case):
    changed = True
    while changed:
        changed = False
        for i in range(len(case)):
            smaller = case[:i] + case[i+1:]
            if smaller and fails(smaller):
                case, changed = smaller, True
                break
    return case
doc = ["# Terms", "Payment within 30 days.", "| fee | 2% |", "Termination with notice.", "## Annex"]
assert fails(doc)
minimal = minimize(doc)
print("minimal failing input:", minimal)
assert minimal == ["| fee | 2% |"]
# This minimal case becomes the regression test: assert not fails(["| fee | 2% |"]) after the fix.''',
  mistakes=["Changing several things at once, then not knowing which one helped.", "Blaming the model before checking retrieval, auth and parsing.", "Debugging without traces or captured inputs.", "Fixing the bug without adding a test, so it comes back."],
  enterprise="A bank's document assistant sees accuracy drop after a vendor update. The team replays 200 stored traces against the old and new model versions with identical retrieval and finds the drop is entirely in table-heavy questions. They pin the previous model for that route while they tune the prompt, and add 40 table questions to the eval gate.",
  takeaways=["Reproduce before you fix; capture full inputs and versions.", "Work outside-in through the layers.", "Change one variable per experiment.", "Every fixed bug becomes a test or eval case."],
  diagram='flowchart LR\n  R["Reproduce"] --> M["Minimize"]\n  M --> L{"Which layer?"}\n  L --> N["Network / auth"]\n  L --> D["Data / retrieval"]\n  L --> P["Prompt / model"]\n  L --> X["Parser / tool"]\n  N --> H["Hypothesis → one change"]\n  D --> H\n  P --> H\n  X --> H\n  H --> F["Fix + regression test"]',
  diagramAlt="The debugging loop: reproduce, minimize, then decide which layer fails (network and auth, data and retrieval, prompt and model, or parser and tool), form a hypothesis tested with one change, and finish with a fix plus a regression test."),
 case=None))
# ---------------------------------------------------------------- b-apis
sid = "b-apis"
S.append(SUBJ(sid, "REST vs GraphQL vs gRPC",
 "Agents and integrations consume APIs all day. Picking and using the right API style affects latency, token cost and how much glue code you write.",
 "Three styles dominate. REST models resources with HTTP methods and status codes: it's universal, cacheable and the default for public and partner APIs. GraphQL exposes a typed schema where the client asks for exactly the fields it needs in one round trip, which suits UIs and agents that need shaped data from many related objects. gRPC uses Protocol Buffers over HTTP/2 for fast, strongly typed, streaming service-to-service calls.\n\nFor AI work, the choice shows up as round trips, payload size (tokens!), schema discoverability for tool generation, and streaming support.",
 "Expose the same 'customer with last 5 orders' data as a REST endpoint, a GraphQL query and a gRPC method, then compare round trips, payload bytes and the tokens each response would cost an agent.",
 [T(sid, "styles", "Three styles and when to use each",
   "REST is resource-oriented: GET /customers/42, POST /orders, with HTTP semantics (safe and idempotent methods, status codes, caching headers). It's the lingua franca of SaaS integrations. GraphQL puts one endpoint in front of a typed graph; clients write queries naming the fields they want, which avoids over-fetching and chains of requests, but it moves complexity to the server (query cost limits, N+1 resolution, caching). gRPC defines services in .proto files and generates clients; it's efficient and supports bidirectional streaming, which is why it's common inside platforms and inference servers.",
   [("REST and HTTP semantics", "GET is safe, PUT and DELETE are idempotent, POST is neither; status codes and caching headers carry meaning."),
    ("GraphQL queries and schema", "Clients select fields from a typed schema in one request; introspection documents the API."),
    ("gRPC and Protocol Buffers", "Contract-first .proto definitions, generated clients, HTTP/2 and streaming for internal services."),
    ("Choosing", "Public or partner APIs: REST. Rich UI or agent data needs: GraphQL. Internal high-throughput or streaming: gRPC.")]),
  T(sid, "agents", "APIs as agent tools",
   "When an agent calls an API, every byte of the response becomes tokens. A REST endpoint returning a 40 KB customer object for a question that needs two fields wastes context and money. GraphQL's field selection, or a thin wrapper tool that projects only the needed fields, fixes that. Schemas matter too: OpenAPI documents and GraphQL introspection can be turned into tool definitions automatically, but the result is usually too broad. Curate a few task-shaped tools, add pagination and filters, and return compact, well-labelled results with clear errors.",
   [("Token cost of payloads", "Project responses to the fields the task needs; large JSON blobs crowd out reasoning context."),
    ("Schema-to-tool generation", "OpenAPI and GraphQL schemas can generate tools, but curate them into a small, task-shaped set."),
    ("Pagination and filtering", "Give tools limit, cursor and filter parameters so agents don't pull entire collections."),
    ("Errors agents can act on", "Return structured errors (for example RFC 9457 problem details) that say what to fix.")])],
 [Q("A UI needs a customer, their last 5 orders and each order's items. REST needs 7 calls. Which style reduces round trips by design?", ["GraphQL", "SOAP", "FTP", "gRPC unary calls"], 0, "GraphQL lets one query select nested related data."),
  Q("Which HTTP method is idempotent by definition?", ["PUT", "POST", "PATCH (always)", "CONNECT"], 0, "PUT and DELETE are idempotent; POST is not."),
  Q("Why does response size matter more when an agent is the client?", ["Every byte becomes tokens that cost money and context", "Agents can't parse JSON", "Large responses are always cached", "It doesn't matter"], 0, "Tool outputs are fed back into the context window.")],
 [R("GraphQL: Learn", "https://graphql.org/learn/", "docs", "intro", "The official GraphQL lessons: queries, mutations, schemas and types, validation, execution and best practices, including how GraphQL enables versionless APIs."),
  R("Introduction to gRPC", "https://grpc.io/docs/what-is-grpc/introduction/", "docs", "intro", "gRPC's overview of Protocol Buffers as the IDL and message format, service definitions and generated clients across languages."),
  R("MDN: HTTP request methods", "https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods", "reference", "reference", "Each HTTP method's semantics, plus the safe, idempotent and cacheable properties that REST APIs and retry logic rely on."),
  R("Fielding's dissertation, Chapter 5: REST", "https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm", "paper", "advanced", "The original definition of the REST architectural style and its constraints (client-server, stateless, cacheable, uniform interface, layered system)."),
  R("GitHub: The GitHub GraphQL API (2016)", "https://github.blog/news-insights/the-library/the-github-graphql-api/", "case", "intermediate", "Why GitHub added GraphQL: the REST API drove over 60% of database-tier requests, partly because hypermedia navigation forces repeated round trips.")],
 dict(intuition="REST is a library with a shelf per resource: you fetch whole books one at a time. GraphQL is a librarian you hand a precise list to, and you get exactly those pages in one trip. gRPC is a pneumatic tube between two departments that agreed on the form in advance: fast and typed, but internal.",
  how=["List the consumers: public partners, UIs, agents or internal services.", "Match the style: REST for broad compatibility, GraphQL for shaped data, gRPC for internal speed and streaming.", "Define the contract first (OpenAPI, GraphQL schema or .proto).", "For agent tools, project responses to the needed fields and add pagination.", "Return structured errors and document limits."],
  example="An agent answers 'when did customer 42's last 5 orders ship?'. With REST it calls GET /customers/42 (8 KB), then 5 × GET /orders/{id} (6 KB each): 6 calls, 38 KB, about 9,500 tokens. A GraphQL query for customer(id:42){orders(last:5){id shippedAt}} is 1 call and about 300 bytes, roughly 75 tokens. At $3 per million input tokens and 100,000 questions a month, that's about $2,850 vs $23.",
  lang="python",
  code='''import json
# Compare the payload an agent must read for one question: REST chain vs a GraphQL-style field selection.
customer = {"id": 42, "name": "Acme", "address": {"street": "1 Main", "city": "Detroit"}, "notes": "x" * 2000,
            "orders": [{"id": f"O-{i}", "shippedAt": f"2026-10-0{i}", "items": [{"sku": "S1", "desc": "y" * 900}] * 5} for i in range(1, 6)]}
rest_calls = [json.dumps({k: v for k, v in customer.items() if k != "orders"})] + [json.dumps(o) for o in customer["orders"]]
def select(obj, fields):
    """Tiny GraphQL-like projection: fields is a dict of name -> sub-selection (or None)."""
    if isinstance(obj, list): return [select(o, fields) for o in obj]
    return {k: (select(obj[k], sub) if sub else obj[k]) for k, sub in fields.items()}
gql = json.dumps(select(customer, {"id": None, "orders": {"id": None, "shippedAt": None}}))
rest_bytes = sum(len(c) for c in rest_calls)
tok = lambda b: b // 4                     # rough: ~4 bytes per token
print(f"REST: {len(rest_calls)} calls, {rest_bytes} bytes, ~{tok(rest_bytes)} tokens")
print(f"GraphQL-style: 1 call, {len(gql)} bytes, ~{tok(len(gql))} tokens")
print(gql)''',
  mistakes=["Exposing a raw REST API as an agent tool and letting it pull huge objects.", "Adopting GraphQL without query cost limits or depth limits.", "Using gRPC for public browser-facing APIs without a gateway.", "Ignoring HTTP semantics (using POST for everything), which breaks retries and caching."],
  enterprise="A CRM vendor's agent integration pulls full account objects through REST and hits context limits on large accounts. Wrapping the API in three task-shaped tools backed by GraphQL field selection cuts tool-output tokens by about 85% and removes the context-overflow errors.",
  takeaways=["REST for broad compatibility, GraphQL for shaped data, gRPC for internal speed.", "Respect HTTP semantics; retries and caches depend on them.", "For agents, response size is cost and context.", "Contract-first schemas enable generated clients and tools."],
  diagram='flowchart LR\n  C["Client"] -->|"GET /customers/42"| R1["REST"]\n  C -->|"GET /orders/1..5 (5 calls)"| R1\n  C -->|"one query, chosen fields"| G["GraphQL"]\n  S1["Service A"] <-->|"protobuf over HTTP/2, streaming"| GR["gRPC"]\n  GR <--> S2["Service B"]',
  diagramAlt="A client makes six REST calls to get a customer and five orders, or a single GraphQL query that selects only the needed fields. Two internal services exchange Protocol Buffer messages over HTTP/2 with gRPC streaming."),
 case=C("GitHub", "The GitHub GraphQL API (GitHub Blog, 2016)", "https://github.blog/news-insights/the-library/the-github-graphql-api/",
   "GitHub announced a GraphQL API alongside its widely copied REST API. One motivation was scalability: the REST API was responsible for over 60% of the requests made to its database tier, partly because hypermedia navigation requires clients to make repeated requests to collect what they need. GitHub implemented the schema with the graphql-ruby gem and used Shopify's graphql-batch to fetch related records efficiently.",
   "When clients need connected data, letting them ask for exactly what they need in one request can cut round trips and backend load. You then have to handle batching and query cost.")))
# ---------------------------------------------------------------- b-postgres
sid = "b-postgres"
S.append(SUBJ(sid, "PostgreSQL for AI Engineers: Indexing, Transactions and pgvector",
 "Postgres is the default system of record behind most AI products, and with pgvector it is often the vector store too. Indexes and transactions decide correctness and latency.",
 "Postgres stores users, conversations, tool results, audit logs, feature flags and, with the pgvector extension, embeddings. Three skills matter. Modeling: normalized tables with constraints, plus JSONB where flexibility genuinely helps. Indexing: B-tree for equality and range, GIN for JSONB and full-text, and HNSW or IVFFlat for vectors, always verified with EXPLAIN ANALYZE. Transactions: atomic multi-step writes, isolation levels, row locks and idempotent upserts with ON CONFLICT.\n\nMost 'the database is slow' problems are a missing index, an N+1 query pattern or a long-running transaction holding locks.",
 "Design a schema for conversations, messages and document chunks with embeddings in Postgres. Add B-tree, GIN and HNSW indexes, prove each one with EXPLAIN ANALYZE, and implement an idempotent ingestion upsert inside a transaction.",
 [T(sid, "idx", "Modeling and indexing",
   "Model the core entities relationally, with primary keys, foreign keys, NOT NULL and CHECK constraints, so the database itself rejects bad data. Use JSONB for genuinely variable attributes such as tool outputs, not as a way to skip modeling. Indexes trade write cost and disk for read speed. A B-tree on (tenant_id, created_at) serves 'latest messages for a tenant'. A GIN index serves JSONB containment and full-text search. pgvector adds HNSW and IVFFlat indexes for approximate nearest-neighbour search. Always confirm with EXPLAIN ANALYZE that the planner actually uses the index you added.",
   [("Constraints as guardrails", "Foreign keys, NOT NULL, UNIQUE and CHECK constraints stop bad data at the source."),
    ("B-tree and composite indexes", "Order composite index columns by how queries filter: equality columns first, then range or sort columns."),
    ("GIN, JSONB and full-text", "GIN indexes accelerate JSONB containment (@>) and tsvector full-text search."),
    ("pgvector HNSW and filters", "HNSW gives fast approximate search; combine it with WHERE filters such as tenant_id and check recall.")]),
  T(sid, "tx", "Transactions, isolation and locks",
   "A transaction makes several writes succeed or fail together: insert the message, update the conversation's last_message_at and record the token usage, or none of them. Postgres defaults to READ COMMITTED isolation. REPEATABLE READ and SERIALIZABLE give stronger guarantees but may abort transactions, which your code must retry. Use INSERT ... ON CONFLICT DO UPDATE for idempotent upserts, SELECT ... FOR UPDATE SKIP LOCKED to build safe job queues, and keep transactions short: an idle transaction holds locks and blocks vacuum. Connection pooling (PgBouncer) protects the database from many short-lived app connections.",
   [("Atomicity", "Group related writes in one transaction so a crash can't leave half-updated state."),
    ("Isolation levels", "READ COMMITTED by default; SERIALIZABLE prevents anomalies but requires retrying serialization failures."),
    ("Upserts and SKIP LOCKED", "ON CONFLICT makes ingestion idempotent; FOR UPDATE SKIP LOCKED lets many workers claim jobs safely."),
    ("Pooling and long transactions", "Pool connections and keep transactions short to avoid lock pile-ups and bloat.")])],
 [Q("A query filters `WHERE tenant_id = $1 ORDER BY created_at DESC LIMIT 20`. Best index?", ["Composite B-tree on (tenant_id, created_at)", "Separate index on created_at only", "GIN on tenant_id", "No index; add more RAM"], 0, "Equality column first, then the sort column, lets Postgres read just 20 rows."),
  Q("How do you make re-ingesting the same document safe to run twice?", ["INSERT ... ON CONFLICT (doc_id, chunk_no) DO UPDATE", "DELETE all rows first without a transaction", "Rely on the application to remember", "Use SERIALIZABLE on every read"], 0, "An upsert on a natural key makes the operation idempotent."),
  Q("You added an index but the query is still slow. What do you check?", ["EXPLAIN ANALYZE to see whether the planner uses it", "Restart Postgres", "Add the same index again", "Switch to MongoDB"], 0, "The plan shows whether the index is used and where time goes.")],
 [R("PostgreSQL docs: Chapter 11, Indexes", "https://www.postgresql.org/docs/current/indexes.html", "docs", "reference", "Official chapter on index types (B-tree, hash, GiST, SP-GiST, GIN, BRIN), multicolumn, partial and expression indexes, and index-only scans."),
  R("PostgreSQL docs: 13.2 Transaction Isolation", "https://www.postgresql.org/docs/current/transaction-iso.html", "docs", "advanced", "Exactly which anomalies each isolation level allows in Postgres, and why SERIALIZABLE transactions can fail and must be retried."),
  R("Use The Index, Luke", "https://use-the-index-luke.com/", "book", "intermediate", "Markus Winand's free developer-focused guide to SQL indexing: how B-trees work, composite index column order, and why some queries can't use an index."),
  R("pgvector", "https://github.com/pgvector/pgvector", "repo", "intermediate", "Vector types, distance operators, HNSW and IVFFlat indexes, and how filtering interacts with approximate search in Postgres."),
  R("Notion: Herding elephants, lessons learned from sharding Postgres (2021)", "https://www.notion.com/blog/sharding-postgres-at-notion", "case", "advanced", "How Notion split its Postgres monolith into 480 logical shards on 32 physical databases, with double-writes, an audit log and a short maintenance window.")],
 dict(intuition="Postgres is a careful accountant. Constraints are the rules it refuses to break, indexes are the tabs in its ledger that let it find a page without reading the whole book, and transactions are its promise that a set of entries is either fully written or never happened.",
  how=["Model entities with keys and constraints; use JSONB only for genuinely variable data.", "Write the important queries first, then design indexes for them.", "Verify every index with EXPLAIN ANALYZE on realistic data.", "Wrap multi-step writes in short transactions; use upserts for idempotency.", "Pool connections and monitor slow queries, locks and bloat."],
  example="A chat app's 'load conversation' query takes 1.8 s for big tenants: Postgres scans 3M messages and sorts them. Adding CREATE INDEX ON messages (tenant_id, conversation_id, created_at DESC) changes the plan to an index scan returning 50 rows in 4 ms. For RAG, an HNSW index on embedding with WHERE tenant_id = $1 returns the top 10 in about 15 ms instead of a 900 ms exact scan.",
  lang="python",
  code='''import sqlite3, time
# Same ideas in SQLite (stdlib) so it runs anywhere: composite index, query plan, idempotent upsert in a transaction.
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE messages(id INTEGER PRIMARY KEY, tenant_id INT NOT NULL, conv_id INT NOT NULL,
                      created_at INT NOT NULL, body TEXT NOT NULL);
CREATE TABLE chunks(doc_id TEXT, chunk_no INT, text TEXT, PRIMARY KEY(doc_id, chunk_no));
""")
db.executemany("INSERT INTO messages(tenant_id, conv_id, created_at, body) VALUES (?,?,?,?)",
               ((t % 50, t % 900, t, "hi") for t in range(200_000)))
q = "SELECT body FROM messages WHERE tenant_id=7 AND conv_id=7 ORDER BY created_at DESC LIMIT 20"
def timed():
    t = time.perf_counter(); db.execute(q).fetchall(); return (time.perf_counter() - t) * 1000
before = timed()
db.execute("CREATE INDEX ix_msg ON messages(tenant_id, conv_id, created_at DESC)")
after = timed()
print("plan:", db.execute("EXPLAIN QUERY PLAN " + q).fetchall()[0][-1])
print(f"before {before:.1f} ms, after {after:.2f} ms")
def ingest(doc_id, chunks):
    with db:                                   # one transaction: all chunks or none
        db.executemany("INSERT INTO chunks VALUES (?,?,?) ON CONFLICT(doc_id, chunk_no) DO UPDATE SET text=excluded.text",
                       [(doc_id, i, c) for i, c in enumerate(chunks)])
ingest("policy", ["a", "b"]); ingest("policy", ["a", "b2"])   # re-run is safe
print(db.execute("SELECT * FROM chunks").fetchall())
# Postgres + pgvector equivalent:  CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);''',
  mistakes=["Adding indexes without checking EXPLAIN ANALYZE.", "Storing everything in one JSONB column to avoid modeling.", "Long-running or idle-in-transaction sessions holding locks.", "Vector search without tenant filters, which leaks data across customers."],
  enterprise="A SaaS team keeps embeddings in Postgres with pgvector rather than adding a separate vector database. With an HNSW index, a tenant_id filter and nightly recall checks against exact search, they keep p95 retrieval under 30 ms for 40M chunks, and get transactions, backups and row-level security from the database they already run.",
  takeaways=["Constraints make the database a guardrail, not just storage.", "Design indexes for real queries and prove them with EXPLAIN ANALYZE.", "Short transactions plus upserts give correctness and idempotency.", "pgvector is often enough; filter by tenant and measure recall."],
  diagram='flowchart LR\n  APP["App / agent"] --> POOL["PgBouncer pool"]\n  POOL --> PG[("PostgreSQL")]\n  PG --> BT["B-tree: tenant_id, created_at"]\n  PG --> GIN["GIN: JSONB / full-text"]\n  PG --> HNSW["HNSW: pgvector embeddings"]\n  APP -->|"BEGIN ... upsert ... COMMIT"| POOL',
  diagramAlt="An app connects through a PgBouncer pool to PostgreSQL, which uses a B-tree index for tenant and time filters, a GIN index for JSONB and full-text search, and an HNSW index for pgvector embeddings. Writes are grouped into transactions with upserts."),
 case=C("Notion", "Herding elephants: Lessons learned from sharding Postgres at Notion (2021)", "https://www.notion.com/blog/sharding-postgres-at-notion",
   "Notion sharded its monolithic Postgres database into 480 logical shards, each a Postgres schema, spread evenly across 32 physical databases (15 per database), partitioned so related data stays together. The migration used double-writes with an audit log and a catch-up script. The final cutover took Notion down for five minutes of scheduled maintenance.",
   "Choose partition keys that keep related data and transactions on one host, and plan migrations around double-writes and verification.")))
