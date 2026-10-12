CODE = {}
CODE["i-life"] = ("python", '''# Decompose request latency: TTFT (queue + prefill) and TPOT (per output token).
def latency(prompt_tok, out_tok, queue_ms=40, prefill_tok_per_s=8000, decode_tok_per_s=60):
    ttft = queue_ms + prompt_tok / prefill_tok_per_s * 1000
    tpot = 1000 / decode_tok_per_s
    return ttft, tpot, ttft + tpot * (out_tok - 1)
for p, o in [(500, 200), (20_000, 200), (500, 1500)]:
    ttft, tpot, e2e = latency(p, o)
    print(f"prompt {p:>6} out {o:>5}: TTFT {ttft:6.0f} ms, TPOT {tpot:4.1f} ms, total {e2e/1000:5.1f} s")
''')
CODE["i-engines"] = ("bash", '''# Serve an open model with an OpenAI-compatible API (vLLM), then call it.
pip install vllm
vllm serve meta-llama/Llama-3.1-8B-Instruct --max-model-len 16384 --gpu-memory-utilization 0.90 &
curl -s localhost:8000/v1/chat/completions -H 'Content-Type: application/json' \\
  -d '{"model":"meta-llama/Llama-3.1-8B-Instruct","messages":[{"role":"user","content":"Hello"}],"max_tokens":32}'
# Requires a GPU. SGLang (python -m sglang.launch_server) and TGI expose similar endpoints.
''')
CODE["i-mem"] = ("python", '''# How many concurrent sequences fit on one GPU?  free = HBM*util - weights - activations
def max_seqs(hbm_gb, util, params_b, bytes_w, layers, kv_heads, head_dim, ctx, act_gb=2.0):
    weights = params_b * bytes_w
    kv_per_seq = 2 * layers * kv_heads * head_dim * ctx * 2 / 1e9
    free = hbm_gb * util - weights - act_gb
    return max(0, int(free // kv_per_seq)), round(kv_per_seq, 2)
print("80GB, 8B fp16, 8k ctx :", max_seqs(80, 0.9, 8, 2, 32, 8, 128, 8192))
print("80GB, 70B fp8, 8k ctx :", max_seqs(80, 0.9, 70, 1, 80, 8, 128, 8192))
''')
CODE["i-batch"] = ("python", '''import random
# Static vs continuous batching simulation (iterations needed to finish all requests).
rng = random.Random(0); lengths = [rng.choice([20, 50, 400]) for _ in range(64)]; B = 8
static = sum(max(lengths[i:i+B]) for i in range(0, len(lengths), B))   # batch waits for its longest
queue, active, steps = list(lengths), [], 0
while queue or active:
    while queue and len(active) < B: active.append(queue.pop(0))       # refill free slots every step
    active = [r - 1 for r in active if r > 1]; steps += 1
print(f"static: {static} steps, continuous: {steps} steps, speedup {static/steps:.1f}x")
''')
CODE["i-quant"] = ("python", '''import random
# Symmetric per-channel int8 quantization and its reconstruction error.
rng = random.Random(0)
W = [[rng.gauss(0, 0.02) for _ in range(64)] for _ in range(4)]
def quant_row(row, bits=8):
    qmax = 2**(bits-1) - 1; scale = max(abs(x) for x in row) / qmax
    q = [round(x / scale) for x in row]; return q, scale
for bits in (8, 4):
    err = 0
    for row in W:
        q, s = quant_row(row, bits); err += sum((x - qi*s)**2 for x, qi in zip(row, q))
    print(f"int{bits}: mean sq error {err/(4*64):.2e}, size {bits/16:.0%} of fp16")
''')
CODE["i-spec"] = ("python", '''# Expected tokens per target-model pass with speculative decoding (Leviathan et al.):
# E = (1 - a^(k+1)) / (1 - a), a = acceptance rate, k = draft length.
def expected_tokens(a, k): return (1 - a**(k + 1)) / (1 - a)
for a in (0.6, 0.8, 0.9):
    row = ", ".join(f"k={k}: {expected_tokens(a, k):.2f}" for k in (2, 4, 8))
    print(f"acceptance {a}: {row}")
# Gains shrink when the draft is slow or acceptance is low; measure on your traffic.
''')
CODE["i-struct"] = ("python", '''import re
# Constrained decoding in miniature: mask tokens that would break the allowed pattern.
vocab = ['{"', 'status', '":', '"ok"', '"error"', '}', 'hello', '42']
allowed = re.compile(r'^\\{"status":"(ok|error)"\\}$')
prefixes = {'', '{"', '{"status', '{"status":', '{"status":"ok"', '{"status":"error"'}
def valid_next(prefix):
    return [t for t in vocab if (prefix + t) in prefixes or allowed.match(prefix + t)]
out = ""
while not allowed.match(out):
    choices = valid_next(out); out += choices[0]       # a real decoder picks the most probable valid token
print(out)
''')
CODE["i-pd"] = ("python", '''# When does prefill/decode disaggregation pay off? Compare interference on a shared GPU.
def shared_tpot(base_tpot_ms, prefill_ms, prefills_per_s):
    # decode steps stall while prefills run on the same GPU
    stall_fraction = min(0.95, prefill_ms * prefills_per_s / 1000)
    return base_tpot_ms / (1 - stall_fraction)
for prompt_tok in (1_000, 8_000, 32_000):
    prefill_ms = prompt_tok / 10_000 * 1000           # 10k tok/s prefill
    print(f"{prompt_tok:>6}-token prompts: shared TPOT {shared_tpot(20, prefill_ms, 2):6.1f} ms vs disaggregated 20 ms")
''')
CODE["i-dist"] = ("python", '''# Choose tensor-parallel degree: smallest TP that fits weights + KV headroom per GPU.
def min_tp(params_b, bytes_w, hbm_gb, kv_headroom_gb=20, options=(1, 2, 4, 8)):
    for tp in options:
        if params_b * bytes_w / tp + kv_headroom_gb <= hbm_gb * 0.9: return tp
    return None   # needs pipeline parallelism across nodes
for p, b in [(8, 2), (70, 2), (70, 1), (405, 1)]:
    print(f"{p}B @{b} bytes/param on 80GB -> TP={min_tp(p, b, 80)}")
''')
CODE["i-lora-serve"] = ("python", '''from collections import OrderedDict
# LRU cache of LoRA adapters in GPU memory; base model is shared by all tenants.
class AdapterCache:
    def __init__(self, capacity): self.cap, self.slots, self.loads = capacity, OrderedDict(), 0
    def get(self, name):
        if name in self.slots: self.slots.move_to_end(name)
        else:
            if len(self.slots) >= self.cap: self.slots.popitem(last=False)
            self.slots[name] = f"weights:{name}"; self.loads += 1     # load from disk/host memory
        return self.slots[name]
c = AdapterCache(capacity=3)
for req in ["tone", "summarize", "tone", "sql", "proofread", "tone", "summarize"]: c.get(req)
print("adapter loads:", c.loads, "resident:", list(c.slots))
''')
CODE["i-coldstart"] = ("python", '''# Cold-start time is dominated by moving weights: size / slowest link in the path.
size_gb = 140   # 70B params in bf16
paths = {"object storage @ 1 GB/s": 1.0, "local NVMe @ 6 GB/s": 6.0, "host RAM cache @ 25 GB/s": 25.0}
for name, gbps in paths.items():
    print(f"{name:<26} {size_gb/gbps:6.0f} s")
# Pre-pull images, stream safetensors, cache weights on node, and keep warm replicas for SLOs.
''')
CODE["i-gateway"] = ("python", '''import random
# Least-outstanding-requests routing with health checks across inference replicas.
replicas = {"r1": {"inflight": 3, "healthy": True}, "r2": {"inflight": 1, "healthy": True},
            "r3": {"inflight": 0, "healthy": False}}
def pick():
    healthy = [k for k, v in replicas.items() if v["healthy"]]
    low = min(replicas[k]["inflight"] for k in healthy)
    return random.choice([k for k in healthy if replicas[k]["inflight"] == low])
chosen = pick(); replicas[chosen]["inflight"] += 1
print("routed to", chosen)
# Prefix-aware routing goes further: send requests sharing a prompt prefix to the replica holding its KV cache.
''')
CODE["i-kernel"] = ("python", '''import math
# Online softmax (the trick inside FlashAttention): one pass, running max and running sum.
def online_softmax_dot(scores, values):
    m, s, acc = -math.inf, 0.0, 0.0
    for x, v in zip(scores, values):
        m_new = max(m, x)
        s = s * math.exp(m - m_new) + math.exp(x - m_new)
        acc = acc * math.exp(m - m_new) + math.exp(x - m_new) * v
        m = m_new
    return acc / s
scores, values = [2.0, 1.0, 0.1, 3.0], [10, 20, 30, 40]
e = [math.exp(x) for x in scores]; ref = sum(w*v for w, v in zip(e, values)) / sum(e)
print(online_softmax_dot(scores, values), ref)
assert abs(online_softmax_dot(scores, values) - ref) < 1e-9
''')
CODE["i-slo"] = ("python", '''import math
# Erlang-C: probability a request waits, and replicas needed to meet a wait-time SLO.
def erlang_c(servers, load):
    s = sum(load**k / math.factorial(k) for k in range(servers))
    top = load**servers / math.factorial(servers) * servers / (servers - load)
    return top / (s + top)
def replicas_for(rps, service_s, slo_wait_s, target=0.95):
    load = rps * service_s; c = math.floor(load) + 1
    while True:
        pw = erlang_c(c, load)
        if 1 - pw * math.exp(-(c - load) * slo_wait_s / service_s) >= target: return c
        c += 1
print("slots needed:", replicas_for(rps=10, service_s=4, slo_wait_s=0.5))
''')
CODE["i-hw"] = ("python", '''# Roofline check: is decode memory-bound? arithmetic intensity vs the GPU's ridge point.
def ridge(tflops, tb_per_s): return tflops * 1e12 / (tb_per_s * 1e12)   # FLOPs per byte
def decode_intensity(batch, bytes_per_param=2): return 2 * batch / bytes_per_param  # ~2 FLOPs/param/token
gpu = {"H100 SXM (dense bf16 ~989 TFLOPS, 3.35 TB/s)": (989, 3.35)}
for name, (tf, bw) in gpu.items():
    r = ridge(tf, bw); print(name, f"ridge ~{r:.0f} FLOPs/byte")
    for b in (1, 32, 256):
        print(f"  batch {b:>3}: intensity {decode_intensity(b):5.0f} ->", "compute-bound" if decode_intensity(b) > r else "memory-bound")
''')
CODE["i-research"] = "conceptual"
CODE["f-gpu"] = ("bash", '''# Inspect GPUs: model, memory, utilization, topology, and ECC/XID health
nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu,temperature.gpu --format=csv
nvidia-smi topo -m                      # NVLink / PCIe / NUMA affinity matrix
nvidia-smi -q -d ECC | grep -i -A3 "volatile"
dmesg | grep -i xid                     # XID errors point at failing hardware or drivers
''')
CODE["f-k8s"] = ("yaml", '''# Request GPUs and land on GPU nodes (requires the NVIDIA device plugin / GPU Operator)
apiVersion: v1
kind: Pod
metadata: {name: llm-server}
spec:
  nodeSelector: {nvidia.com/gpu.product: NVIDIA-H100-80GB-HBM3}
  tolerations: [{key: nvidia.com/gpu, operator: Exists, effect: NoSchedule}]
  containers:
    - name: vllm
      image: vllm/vllm-openai:latest
      args: ["--model", "meta-llama/Llama-3.1-8B-Instruct"]
      resources: {limits: {nvidia.com/gpu: 1}}
''')
CODE["f-linux"] = ("bash", '''# Run a CUDA container and verify the driver/toolkit stack end to end
nvidia-smi                                   # host driver version
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
cat /proc/driver/nvidia/version
lsmod | grep -E "nvidia|nvidia_uvm|nvidia_peermem"
''')
CODE["f-sched"] = ("python", '''# Gang scheduling: place all workers of a job or none (prevents partial-allocation deadlock).
free = {"node1": 8, "node2": 8, "node3": 4}
def gang_place(job_gpus_per_worker, workers):
    plan, avail = [], dict(free)
    for _ in range(workers):
        node = next((n for n, g in sorted(avail.items(), key=lambda x: -x[1]) if g >= job_gpus_per_worker), None)
        if node is None: return None                    # do not start anything
        avail[node] -= job_gpus_per_worker; plan.append(node)
    free.update(avail); return plan
print("job A (2x8 GPU):", gang_place(8, 2))
print("job B (2x8 GPU):", gang_place(8, 2), "-> waits, holding nothing")
''')
CODE["f-store"] = ("python", '''# Checkpoint write time and the storage bandwidth needed to keep it under a target.
params_b, bytes_per_param_state = 70, 16      # bf16 weights + fp32 master + Adam moments ~ 16 B/param
ckpt_tb = params_b * 1e9 * bytes_per_param_state / 1e12
for target_s in (60, 300):
    print(f"{ckpt_tb:.2f} TB checkpoint in {target_s}s needs {ckpt_tb*1000/target_s:.1f} GB/s aggregate")
''')
CODE["f-net"] = ("python", '''# Ring all-reduce time: each GPU sends/receives 2*(N-1)/N of the data.
def allreduce_s(size_gb, n_gpus, link_gb_s):
    return 2 * (n_gpus - 1) / n_gpus * size_gb / link_gb_s
grads_gb = 16      # 8B params in bf16
for name, bw in [("400 Gb/s NIC (50 GB/s)", 50), ("NVLink-class (450 GB/s)", 450)]:
    print(f"{name}: {allreduce_s(grads_gb, 64, bw):.3f} s per all-reduce on 64 GPUs")
''')
CODE["f-procure"] = ("python", '''# Reserved vs on-demand vs spot: blended cost for a forecast with uncertainty.
hours = 730
prices = {"reserved_1y": 2.0, "on_demand": 4.0, "spot": 1.6}   # $/GPU-hour placeholders
baseline, peak = 64, 128                                        # GPUs
def monthly(reserved):
    burst = peak - reserved
    return reserved * prices["reserved_1y"] * hours + burst * 0.3 * hours * prices["on_demand"]  # burst used 30%
for r in (0, 64, 96, 128):
    print(f"reserve {r:>3} GPUs -> ${monthly(r):,.0f}/month")
''')
CODE["f-interconnect"] = ("bash", '''# Measure collective bandwidth with nccl-tests and enable NCCL debug output
git clone https://github.com/NVIDIA/nccl-tests && cd nccl-tests && make
NCCL_DEBUG=INFO ./build/all_reduce_perf -b 8 -e 8G -f 2 -g 8
# Compare "busbw" with expected NVLink/IB bandwidth; a slow rank points to a bad link or NIC.
''')
CODE["f-gpushare"] = ("yaml", '''# Time-slicing a GPU with the NVIDIA device plugin (no memory isolation; use MIG for that)
apiVersion: v1
kind: ConfigMap
metadata: {name: time-slicing-config, namespace: gpu-operator}
data:
  any: |-
    version: v1
    sharing:
      timeSlicing:
        resources:
          - name: nvidia.com/gpu
            replicas: 4
''')
CODE["f-obs"] = ("yaml", '''# Prometheus alert rules for GPU health (DCGM exporter metrics)
groups:
  - name: gpu
    rules:
      - alert: GPUXidErrors
        expr: increase(DCGM_FI_DEV_XID_ERRORS[10m]) > 0
        labels: {severity: page}
      - alert: GPUHighTemp
        expr: DCGM_FI_DEV_GPU_TEMP > 85
        for: 5m
      - alert: GPUIdleWhileAllocated
        expr: avg_over_time(DCGM_FI_DEV_GPU_UTIL[30m]) < 5
        labels: {severity: ticket}
''')
CODE["f-secinfra"] = ("yaml", '''# Lock down an inference pod: non-root, read-only FS, no privilege escalation, egress denied by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: {name: deny-egress, namespace: inference}
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress: []            # add explicit allow rules (e.g. to the model store) as needed
---
# in the pod spec:
# securityContext: {runAsNonRoot: true, readOnlyRootFilesystem: true, allowPrivilegeEscalation: false}
''')
CODE["f-cloud"] = "conceptual"
CODE["f-energy"] = ("python", '''# Facility power for a GPU cluster: IT load x PUE.
gpus, gpu_kw, server_overhead = 1024, 0.70, 1.5   # ~700 W per H100 SXM; CPUs, NICs, fans add ~50%
it_kw = gpus * gpu_kw * server_overhead
for pue in (1.1, 1.3, 1.5):
    mw = it_kw * pue / 1000
    print(f"PUE {pue}: {mw:.2f} MW, {mw*8760:,.0f} MWh/year")
''')
CODE["f-failops"] = ("python", '''# Goodput under failures: checkpoint interval vs lost work (Young/Daly approximation).
import math
mtbf_h = 3.0            # cluster-level mean time between interruptions
ckpt_cost_h = 0.05      # time to write a checkpoint
optimal = math.sqrt(2 * ckpt_cost_h * mtbf_h)
def goodput(interval_h, restart_h=0.25):
    waste = ckpt_cost_h / interval_h + (interval_h / 2 + restart_h) / mtbf_h
    return 1 - waste
print(f"optimal interval {optimal*60:.0f} min, goodput {goodput(optimal):.1%}")
print(f"hourly checkpoints, goodput {goodput(1.0):.1%}")
''')
CODE["f-aisec"] = ("python", '''import hashlib, pathlib, tempfile
# Verify model artifacts against pinned digests before loading (supply-chain control).
d = pathlib.Path(tempfile.mkdtemp()); (d / "model.safetensors").write_bytes(b"fake weights")
PINNED = {"model.safetensors": hashlib.sha256(b"fake weights").hexdigest()}
def verify(dirpath):
    for name, digest in PINNED.items():
        h = hashlib.sha256((dirpath / name).read_bytes()).hexdigest()
        if h != digest: raise RuntimeError(f"digest mismatch for {name}")
    bad = [p.name for p in dirpath.iterdir() if p.suffix in {".pkl", ".bin", ".pt"}]
    if bad: raise RuntimeError(f"pickle-based files not allowed: {bad}")
    return "ok"
print(verify(d))
''')
CODE["f-traininfra"] = ("python", '''# Training time estimate: FLOPs ~= 6 * params * tokens, divided by achieved cluster throughput.
def days(params_b, tokens_t, gpus, peak_tflops=989, mfu=0.40):
    flops = 6 * params_b * 1e9 * tokens_t * 1e12
    return flops / (gpus * peak_tflops * 1e12 * mfu) / 86_400
print(f"8B on 15T tokens, 1024 GPUs: {days(8, 15, 1024):.0f} days")
print(f"70B on 15T tokens, 8192 GPUs: {days(70, 15, 8192):.0f} days")
''')
CODE["f-mlops"] = ("python", '''import json, hashlib, time
# Minimal model registry entry: immutable version, lineage, eval evidence, stage.
def register(name, artifact_bytes, data_snapshot, evals, stage="staging"):
    rec = {"name": name, "version": hashlib.sha256(artifact_bytes).hexdigest()[:12],
           "data_snapshot": data_snapshot, "evals": evals, "stage": stage, "created": int(time.time())}
    if stage == "production" and evals.get("golden_set", 0) < 0.9:
        raise ValueError("promotion blocked: golden_set < 0.9")
    return rec
print(json.dumps(register("ticket-router", b"weights-v7", "s3://data/tickets@2026-10-01", {"golden_set": 0.93}), indent=1))
''')
CODE["f-econ"] = ("python", '''# Unit economics for serving: $ per million output tokens from GPU price and measured throughput.
def usd_per_mtok(gpu_hr, tok_s_per_gpu, utilization):
    return gpu_hr / (tok_s_per_gpu * 3600 * utilization) * 1e6
for batch_label, tps in [("batch 1", 80), ("batch 32", 1800), ("batch 128", 4200)]:
    print(f"{batch_label:<9} ${usd_per_mtok(3.0, tps, 0.6):7.2f} / Mtok")
''')
CODE["f-edgeinfra"] = ("bash", '''# Air-gapped model delivery: package on the connected side, verify on the isolated side
tar -cf model-bundle.tar model/ && sha256sum model-bundle.tar > model-bundle.sha256
# ... transfer by approved media ...
sha256sum -c model-bundle.sha256 && tar -xf model-bundle.tar
docker load -i vllm-image.tar        # images are mirrored too: no registry pulls inside the enclave
''')
CODE["f-finops"] = ("python", '''from collections import defaultdict
# Showback: allocate shared GPU cluster cost by measured GPU-hours, with idle cost spread proportionally.
cluster_cost = 100_000.0
usage = {"search": 3_000, "support-bot": 1_500, "research": 4_500}   # GPU-hours this month
capacity = 12_000
idle = capacity - sum(usage.values())
bill = defaultdict(float)
for team, h in usage.items():
    bill[team] = cluster_cost * h / capacity + cluster_cost * idle / capacity * h / sum(usage.values())
for t, v in bill.items(): print(f"{t:<12} ${v:,.0f}")
print("idle share:", f"{idle/capacity:.0%}")
''')
