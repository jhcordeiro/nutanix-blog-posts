"""GPT-2 124M from scratch: `pip install torch safetensors`.
The first run downloads the model files from Hugging Face. The tokenizer and
transformer are explicit; safetensors handles only safe weight deserialization.

CONCEPT MAP: tokenization → embedding → prefill/decode → sampling.
This demo collapses prefill and decode into a full forward pass for every token.
"""
import os, sys, time, urllib.request, json, re, math, torch
import torch.nn.functional as F
from safetensors.torch import load_file
BASE = "https://huggingface.co/gpt2/resolve/main/"; CACHE = "gpt2-cache"
# Config/tokenizer artifacts are kilobytes but critical; weights are the ~500 MB bulk.
FILES = "config.json", "vocab.json", "merges.txt", "model.safetensors"
def download():
    # Production (NAI): a model is imported once from Hugging Face, NGC, or a Nutanix
    # Objects bucket into a Files RWX volume that every replica mounts at /mnt/models.
    # This download-once cache is the toy equivalent of that import.
    os.makedirs(CACHE, exist_ok=True)
    for name in FILES:
        path = f"{CACHE}/{name}"
        if os.path.exists(path): continue
        print(f"Downloading {name} ..."); urllib.request.urlretrieve(BASE + name, path)
def bytes_to_unicode():
    bs = list(range(33, 127)) + list(range(161, 173)) + list(range(174, 256))
    cs, extra = bs[:], 0
    for b in range(256):
        if b not in bs: bs.append(b); cs.append(256 + extra); extra += 1
    return dict(zip(bs, map(chr, cs)))
# stdlib re lacks Unicode \p{L}/\p{N}; adequate for this English demo.
TOKEN_RE = re.compile(r"'s|'t|'re|'ve|'m|'ll|'d| ?[A-Za-z]+| ?[0-9]+| ?[^A-Za-z0-9\s]+|\s+")
# Tokenization converts text to model-consumable integers; learned BPE merges ship with the model.
class Tokenizer:
    def __init__(self, vocab_path, merges_path):
        with open(vocab_path, encoding="utf-8") as f: self.vocab = json.load(f)
        self.inverse = {v: k for k, v in self.vocab.items()}
        lines = open(merges_path, encoding="utf-8").read().splitlines()[1:]
        self.ranks = {tuple(line.split()): i for i, line in enumerate(lines)}
        self.byte_enc = bytes_to_unicode(); self.byte_dec = {v: k for k, v in self.byte_enc.items()}; self.cache = {}
    def bpe(self, token):
        if token in self.cache: return self.cache[token]
        word = tuple(token)
        while len(word) > 1:
            pair = min(zip(word, word[1:]), key=lambda p: self.ranks.get(p, math.inf))
            if pair not in self.ranks: break
            merged, i = [], 0
            while i < len(word):
                if i + 1 < len(word) and word[i:i + 2] == pair:
                    merged.append(word[i] + word[i + 1]); i += 2
                else: merged.append(word[i]); i += 1
            word = tuple(merged)
        self.cache[token] = " ".join(word); return self.cache[token]
    # Request ingress: encode UTF-8 text into token IDs.
    def encode(self, text):
        ids = []
        for piece in TOKEN_RE.findall(text):
            token = "".join(self.byte_enc[b] for b in piece.encode())
            ids.extend(self.vocab[x] for x in self.bpe(token).split())
        return ids
    # Response egress: decode generated token IDs back into UTF-8 text.
    def decode(self, ids):
        text = "".join(self.inverse[i] for i in ids)
        return bytes(self.byte_dec[c] for c in text).decode(errors="replace")
class GPT2:
    def __init__(self, config, weights): self.c, self.w = config, weights
    # One forward pass maps the current token sequence to next-token logits.
    # The first prompt pass is PREFILL: compute-bound and the main driver of TTFT.
    # Later one-token steps are DECODE: memory-bandwidth-bound and set tokens/sec.
    # This demo has no KV cache, so it recomputes the entire sequence each step.
    # Production engines cache attention keys/values and process only each new token.
    def forward(self, ids):
        c, w, d, T = self.c, self.w, self.c["n_embd"], len(ids)
        ids = torch.tensor(ids)
        # Token + position embeddings turn discrete IDs into dense hidden states.
        x = w["transformer.wte.weight"][ids] + w["transformer.wpe.weight"][:T]
        for layer in range(c["n_layer"]):
            p = f"transformer.h.{layer}."
            z = F.layer_norm(x, (d,), w[p+"ln_1.weight"], w[p+"ln_1.bias"], c["layer_norm_epsilon"])
            # Causal multi-head self-attention: project Q/K/V, then score every prior token.
            qkv = z @ w[p+"attn.c_attn.weight"] + w[p+"attn.c_attn.bias"]
            q, k, v = qkv.chunk(3, -1)
            H, D = c["n_head"], d // c["n_head"]
            q, k, v = [a.view(T, H, D).transpose(0, 1) for a in (q, k, v)]
            # The causal mask blocks future tokens; the T×T score matrix is O(T²).
            scores = q @ k.transpose(-2, -1) / math.sqrt(D)
            mask = torch.triu(torch.ones(T, T, dtype=torch.bool), diagonal=1)
            a = F.softmax(scores.masked_fill(mask, -torch.inf), dim=-1) @ v
            a = a.transpose(0, 1).contiguous().view(T, d)
            x = x + a @ w[p+"attn.c_proj.weight"] + w[p+"attn.c_proj.bias"]
            z = F.layer_norm(x, (d,), w[p+"ln_2.weight"], w[p+"ln_2.bias"], c["layer_norm_epsilon"])
            # Position-wise MLP with a 4× hidden expansion; this holds most block parameters.
            z = F.gelu(z @ w[p+"mlp.c_fc.weight"] + w[p+"mlp.c_fc.bias"], approximate="tanh")
            x = x + z @ w[p+"mlp.c_proj.weight"] + w[p+"mlp.c_proj.bias"]
        x = F.layer_norm(x, (d,), w["transformer.ln_f.weight"], w["transformer.ln_f.bias"], c["layer_norm_epsilon"])
        # Tied output weights: reuse the embedding matrix; no separate lm_head is shipped.
        return x[-1] @ w["transformer.wte.weight"].T  # tied output weights

def sample_top_p(logits, p=0.9, temperature=1.0):
    # Temperature reshapes probabilities; top-p truncates the tail; argmax is the greedy limit.
    probs, indices = torch.sort(
        torch.softmax(logits / temperature, dim=-1), descending=True
    )
    mask = probs.cumsum(-1) - probs < p
    return indices[mask][torch.multinomial(probs[mask], 1)].item()

def generate(model, tokenizer, ids, count=30, p=.95, temperature=.5):
    # Autoregressive decode: produce one token, append it to context, and repeat.
    # torch.inference_mode disables autograd; this loop is where tokens/sec is measured.
    # Full forward per token for clarity; real serving adds a KV cache.
    # The first step's latency is TTFT (prefill); the rest is decode tokens/sec.
    start = time.perf_counter()
    with torch.inference_mode():
        for i in range(count):
            token = sample_top_p(
                model.forward(ids), p=p, temperature=temperature
            )
            if i == 0: ttft = time.perf_counter() - start
            ids.append(token)
            print(tokenizer.decode([token]), end="", flush=True)
    if count > 1:
        tps = (count - 1) / (time.perf_counter() - start - ttft)
        print(f"\n[TTFT {ttft * 1000:.0f} ms · decode {tps:.1f} tokens/s]", file=sys.stderr)
def main():
    # 1. Fetch versioned model artifacts into the local staging cache.
    download()
    config = json.load(open(f"{CACHE}/config.json", encoding="utf-8"))
    # 2. Build the tokenizer from the model's vocabulary and BPE merge artifacts.
    tokenizer = Tokenizer(f"{CACHE}/vocab.json", f"{CACHE}/merges.txt")
    # 3. Load and normalize checkpoint tensors into the model's expected key namespace.
    # Hub GPT2Model keys are bare; GPT2LMHeadModel checkpoints add "transformer.".
    weights = {k if k.startswith("transformer.") else "transformer." + k: v
               for k, v in load_file(f"{CACHE}/model.safetensors").items()}
    model = GPT2(config, weights)
    
    # 4. Encode request text into token IDs.
    prompt = input("prompt: "); ids = tokenizer.encode(prompt)
    # 5. Generate token IDs autoregressively, one decode iteration at a time.
    # 6. Decode each token ID and stream its text to the client.
    print(prompt, end="", flush=True); generate(model, tokenizer, ids); print()
if __name__ == "__main__": main()

# -----------------------------------------------------------------------------
# NOTES: if this were a 1T+ parameter model serving 1000s of requests
# All figures below are approximate; architecture and precision change the math.
#
# SCALE
# - 1T parameters at FP8 occupy about 1 TB before runtime overhead: at least 13
#   H100-80GB GPUs by raw capacity, and realistically two or more 8-GPU nodes.
# - Shard weights with tensor, expert, and/or pipeline parallelism; one GPU cannot
#   hold the model. For MoE, all experts normally stay resident, but only active
#   experts consume FLOPs for a token.
# - Decode ceiling per stream ≈ memory bandwidth ÷ active-weight bytes per token.
#   Check capacity and bandwidth separately when choosing a GPU SKU.
#
# PROJECT ASTRA / COCI / AHV — GPU INFRASTRUCTURE
# - Astra images, claims, and clusters GPU servers; COCI manages up to ~128
#   compute-only GPU nodes without an HCI data path; AHV passes GPUs (and
#   east-west NICs via SR-IOV) through to NKP worker VMs.
#
# NKP + NAI — SERVING
# - NKP GPU node pools run the NVIDIA GPU Operator. NAI deploys KServe
#   InferenceServices running vLLM or NIM, behind the Envoy-based Agent Gateway.
# - NAI 2.8 Tech Previews: multi-node serving, KV-cache-aware routing (llm-d EPP),
#   and KV offload to host RAM. Prefill/decode disaggregation is on the roadmap.
# - Scale endpoint instances explicitly, keep warm instances to hide multi-minute
#   cold starts, and hibernate endpoints that can tolerate a resume delay.
#
# NUTANIX FILES — LIVE MODEL REPOSITORY
# - NAI creates one RWX PVC per model on Files; every replica reads the weights
#   from /mnt/models. NFS over RDMA shortens the load path.
#
# NUTANIX OBJECTS — DURABLE SOURCE
# - Keep versioned imports, air-gapped NIM bundles, corpora, and checkpoints in
#   S3 buckets. Promote by changing a control-plane pointer; never mutate an
#   artifact that a live deployment may already be serving.
#
# CONTROL PLANE
# - Keep only pointers and routing metadata in etcd, such as "production →
#   model-v2". Never put checkpoint blobs or per-request KV-cache tensors there.
#
# THOUSANDS OF CONCURRENT REQUESTS
# - Continuous batching keeps accelerators occupied as requests enter and leave.
# - Plan HBM from KV-cache bytes/token × context length × active sequences; with
#   long contexts and high concurrency, KV-cache capacity can exceed the weights.
#
# FABRIC AND OPERATIONS
# - Use NVLink/NVSwitch inside a node and InfiniBand or high-speed Ethernet across
#   nodes; tensor-parallel collectives make the fabric part of the accelerator.
# - Use Prism for fleet-wide visibility. Define SLOs for time to first token (TTFT)
#   and p99 inter-token latency rather than relying on average latency alone.
