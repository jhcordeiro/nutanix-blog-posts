# Video script: Inference is an infrastructure problem

Companion explainer for [Inference is an infrastructure problem](../blog.html) (Inference engineering at Nutanix, Part 1).

- **Runtime:** about 7 minutes 40 seconds (about 1,150 spoken words at 150 words per minute)
- **Audience:** internal only, matching the post footer
- **Narration source:** the files in [`narration/`](narration/). They are plain spoken prose, meant to be fed to the text-to-speech (TTS) model one scene at a time, in file-name order. The **Narration** block in each scene below repeats its file word for word, so editors can read the script without switching files. If you change the wording, change it in both places.

## How to use this script

Each scene lists:

- **Source:** the post section the scene summarizes.
- **Visual:** direction for the editor or animator.
- **On screen:** exact text, numbers, and formulas to display. Nothing here is read aloud.
- **Narration:** what the TTS model reads, taken from the matching `.txt` file.

Timecodes are estimates based on narration length. Retime them against the generated audio.

## Pronunciation guide

The narration files already spell these out phonetically, so the TTS model needs no extra hints. The guide exists so that on-screen text and any re-recorded lines stay consistent.

| Written | Spoken in narration |
| --- | --- |
| AI / API | "A-I" / "A-P-I" |
| vLLM | "v-L-L-M" |
| GPT-2 | "G-P-T two" |
| gpt-oss-120b | "G-P-T O-S-S one-twenty-B" |
| Llama 3.1 405B | "Llama three point one, four hundred five billion", then "Llama four-oh-five B" |
| DeepSeek V3.1 | "DeepSeek V three point one" |
| Kimi K2 | "Kimi K two" |
| H100 / B300 | "H one hundred" / "B three hundred" |
| RTX PRO 6000 | "R-T-X Pro six thousand" |
| FP8 | "F-P eight" |
| KV cache | "K-V cache" |
| NVLink | "N-V Link" |
| NAI 2.8 | "N-A-I two point eight" |
| NKP / AHV | "N-K-P" / "A-H-V" |
| NICo | "NVIDIA Infra Controller" (the abbreviation is not spoken) |
| NIM (Nutanix Infra Manager) | "Nutanix Infra Manager" (never "NIM", to avoid confusion with NVIDIA NIM) |
| COCI | Not spoken. The narration says "compute-only GPU clusters"; "COCI" appears on screen only. |
| SKU | Not spoken. The narration says "GPU type"; the on-screen quote keeps "GPU SKU". |

## Editor notes before publishing

- All figures are approximate planning numbers from the post, not benchmarks. Keep the "≈" signs on screen.
- KV-cache-aware routing, KV offload to host RAM, and multi-node serving are **Tech Preview** in NAI 2.8. Label them that way on screen.
- **Confirm the GPU Farm inventory (scene 8) before the video leaves the team.** Internal records differ on whether it is 90 or 96 GPUs. The script uses 96, matching the post.
- GPU Farm figures (tokens per week, user count) are from the TaaS report dated September 25, 2026.

## Animated deck

The visuals are Manim animations in [`animations/`](animations/). [`scenes.py`](animations/scenes.py) has one class per scene, and [`theme.py`](animations/theme.py) holds the shared colors and layout pieces. Each step pauses on its last frame until you press the right arrow, space, or click. Every step corresponds to one paragraph of the scene's narration file. The render fails if a scene's step count and its paragraph count ever drift apart.

| Scene | Class | Steps |
| --- | --- | --- |
| 1. Hook and what inference is | `S01Hook` | 6 |
| 2. GPT-2 on a laptop | `S02Gpt2` | 6 |
| 3. Two phases | `S03Phases` | 6 |
| 4. The two numbers that describe a GPU | `S04GpuNumbers` | 6 |
| 5. Do the math | `S05Math` | 6 |
| 6. KV cache | `S06KvCache` | 4 |
| 7. Where Nutanix fits | `S07Nutanix` | 4 |
| 8. GPU Farm | `S08GpuFarm` | 5 |
| 9. Takeaways | `S09Takeaways` | 3 |

**Recording:** open `animations/deck/index.html` in a browser and press `F` for full screen. Play each narration file, then press the right arrow when the next paragraph starts. Press `S` to open the speaker view, which shows the current paragraph as notes.

**Building the deck** (from `animations/`, about 3 minutes at 1080p60):

```bash
brew install cairo pkg-config   # one-time: pycairo has no macOS wheels
UV_NATIVE_TLS=1 uv sync
uv run manim-slides render --quality h scenes.py S01Hook S02Gpt2 S03Phases S04GpuNumbers S05Math S06KvCache S07Nutanix S08GpuFarm S09Takeaways
uv run manim-slides convert --one-file --offline S01Hook S02Gpt2 S03Phases S04GpuNumbers S05Math S06KvCache S07Nutanix S08GpuFarm S09Takeaways deck/index.html
```

- Use `--quality h`, not `-qh`: manim-slides reads `-qh` as its own `-h` (help) flag. For fast drafts, use `--quality l`.
- `--one-file --offline` embeds the clips and reveal.js in a single ~30 MB HTML file. On networks that inspect TLS, the reveal.js download fails with a certificate error. Export the macOS trust store first:

  ```bash
  security find-certificate -a -p /Library/Keychains/System.keychain \
    /System/Library/Keychains/SystemRootCertificates.keychain > /tmp/macos-ca.pem
  export SSL_CERT_FILE=/tmp/macos-ca.pem REQUESTS_CA_BUNDLE=/tmp/macos-ca.pem
  ```

- `media/`, `slides/`, and `deck/` are build output and are ignored by git.

---

## Scene 1: Hook and what inference is

- **Time:** 0:00 to 1:15
- **Source:** [What inference is](../blog.html#what) and [Why this matters](../blog.html#why)
- **Narration file:** [`narration/01-hook.txt`](narration/01-hook.txt)

**Visual:** Open on a single chat window with a streaming answer. Pull back to reveal the answer is coming from a rack of GPU servers, then a whole row of racks, and label it "inference". Then two panels: in "Training", a grid of weights keeps changing; the finished grid copies into "Inference", where it stays fixed while requests flow in and answers flow out. Then the request path as five boxes, with a request travelling right and answer tokens streaming back left. Highlight the serving framework as our layer and flash the others. Finish with the questions and the title card.

**On screen:**

- "Inference: a request in, an answer out"
- Training: the model learns · weights change on every step · one long job, days to weeks
- Inference: the model answers · weights stay fixed · always-on service, every request, all day
- Request path: Application (chat, IDE agent, RAG) → API gateway (auth, quotas, routing) → Serving framework (vLLM, SGLang) → Model runtime (PyTorch, GPU kernels) → GPU (memory, bandwidth)
- "Our team operates this layer" (on the serving framework)
- *Any layer in the path can set the speed limit.* To the user, every bottleneck looks like a slow answer.
- "Which model is best?" → struck through → "How many GPUs? How many nodes? What fails first?"
- Title card: **Inference is an infrastructure problem**
- Closing line: *Choosing a model is choosing the physical shape of the service.*

**Narration:**

```text
Every time you ask an A-I model a question, a trained model computes the answer on GPUs somewhere. That is called inference.

Inference is the second half of a model's life. In training, the model learns: billions of numbers, called weights, get adjusted over days or weeks. In inference, the weights are frozen, and the model answers requests as they arrive, all day long.

Each request passes through layers. An application calls an A-P-I gateway. The gateway routes it to a serving framework, like v-L-L-M. The framework runs the model, and the GPU does the math.

Our team is about to operate that serving layer as a service, not just call it. But any layer in the path can set the speed limit, and to the user, every one of them looks like a slow answer.

That changes the questions we ask. "Which model is best?" becomes: how many GPUs does this model need, how many servers does that span, and what fails first when a thousand coding agents hit it at once?

Here is the idea behind this video. Choosing a model is choosing the physical shape of the service.
```

---

## Scene 2: Start small with GPT-2 on a laptop

- **Time:** 1:15 to 2:15
- **Source:** [Start small: GPT-2 on a laptop](../blog.html#gpt2)
- **Narration file:** [`narration/02-gpt2-laptop.txt`](narration/02-gpt2-laptop.txt)

**Visual:** Screen recording of `python code/gpt2-inference.py`. Type a prompt, let the 30-token continuation stream, and hold on the timing line. Then show a two-column mapping (laptop step to production step) that builds one row at a time. Finish with three arrows labeled with the multipliers, growing outward from a small "72 KB/token" box.

**On screen:**

- `[TTFT … ms · decode … tokens/s]` (highlight this line from the terminal)
- GPT-2: 124M parameters, ≈500 MB of FP32 weights, ≈140 lines of Python
- Mapping:
  - `download()` ≈550 MB → model import: hundreds of GB to ≈1 TB
  - `print(..., flush=True)` → streaming through the NAI Agent Gateway
- "No KV cache in the demo script"
- KV cache per token: GPT-2 ≈72 KB · Kimi K2 ≈70 KB
- The three multipliers:
  - Context: 1K → 128K tokens
  - Concurrency: 1 → thousands of sessions
  - Weights: no longer fit on one device

**Narration:**

```text
Let's start small. G-P-T two, with one hundred twenty-four million parameters, running on a laptop.

The companion script is about one hundred forty lines of Python. It tokenizes your prompt, runs the transformer, streams the answer, and reports two numbers: time to first token, and decode speed.

Every step in that script comes back later as an infrastructure decision.

The script also skips the most important production trick, the K-V cache. Real engines store each layer's attention keys and values, so each step only processes the newest token.

For G-P-T two, that cache costs about seventy-two kilobytes per token. Kimi K two, a trillion-parameter model, stores about the same.

So the per-token cost is not what explodes. Three things around it do. Context grows from one thousand tokens to one hundred twenty-eight thousand. One user becomes thousands. And the weights no longer fit on one device.
```

---

## Scene 3: Two phases, two bottlenecks

- **Time:** 2:15 to 3:05
- **Source:** [Two phases, two bottlenecks](../blog.html#phases)
- **Narration file:** [`narration/03-two-phases.txt`](narration/03-two-phases.txt)

**Visual:** Split screen. Left: "Prefill", a whole prompt lighting up at once. Right: "Decode", tokens appearing one by one. Then a horizontal timeline bar for one request where the decode segment dwarfs everything else. Finish with a latency histogram, highlighting the long p99 tail.

**On screen:**

- Prefill: compute-bound → sets TTFT (time to first token)
- Decode: memory-bandwidth-bound → sets tokens per second (TPOT)
- Example request: ≈2,000-token prompt, ≈500-token answer

| Stage | Time |
| --- | --- |
| Ingress | ≈40 ms |
| Queue | ≈110 ms |
| Prefill | ≈300 ms |
| Decode | ≈10,000 ms |
| Egress | ≈50 ms |
| **Total** | **≈10.5 s** |

- First visible token: ≈500 ms · Decode: ≈97% of model time
- Two budgets: first-token budget and completion budget, tracked at p50 and p99
- Pull quote: *The average tells you the machine is healthy. The tail tells you whether users agree.*

**Narration:**

```text
Every request has two phases, and they stress different hardware.

Prefill processes the whole prompt in parallel. It is usually compute-bound, and it sets the time to first token.

Decode produces one token at a time. Every step rereads the model's weights, so it is usually limited by memory bandwidth. It sets how fast the answer streams.

In a typical request, the first token shows up in about half a second, but the full answer takes about ten and a half seconds. Decode is about ninety-seven percent of the model's time.

So we write two budgets, one for the first token and one for completion, and we track the ninety-ninth percentile, not just the average.

The average tells you the machine is healthy. The tail tells you whether users agree.
```

---

## Scene 4: The two numbers that describe a GPU

- **Time:** 3:05 to 3:55
- **Source:** [The two numbers that describe a GPU](../blog.html#gpus)
- **Narration file:** [`narration/04-gpu-numbers.txt`](narration/04-gpu-numbers.txt)

**Visual:** A GPU card drawn as a bucket (capacity) with a pipe (bandwidth). Show the ceiling formula, then two scenario cards. For the MoE card, animate a router sending a token to two of many expert blocks while the rest stay lit but idle, to show they still occupy memory.

**On screen:**

- **Capacity**: does it fit? · **Bandwidth**: how fast does decode run?
- Formula: `decode ceiling (tokens/s per stream) ≤ memory bandwidth ÷ active-weight bytes per token`
- Llama 3.1 405B (dense), FP8, 8×H100: ≈26.8 TB/s ÷ ≈405 GB → **≈66 tokens/s**
- gpt-oss-120b (MoE), MXFP4, 1× RTX PRO 6000: ≈1.6 TB/s ÷ ≈3 GB active → **≈530 tokens/s**
- "MoE: pressure moves from bandwidth to capacity"

**Narration:**

```text
For inference, a GPU comes down to two numbers: how many bytes its memory holds, and how fast it can read them.

Capacity decides whether the model fits. Bandwidth decides how fast decode runs once it does.

For a single stream, tokens per second can't beat memory bandwidth divided by the bytes of weights read for each token.

Llama three point one, four hundred five billion, in F-P eight on eight H one hundreds, tops out around sixty-six tokens per second.

Mixture-of-Experts models send each token to only a few experts, so far fewer bytes are read. G-P-T O-S-S one-twenty-B, on one R-T-X Pro six thousand, has a ceiling around five hundred thirty tokens per second.

But every expert still has to sit in memory. The pressure moves from bandwidth to capacity.
```

---

## Scene 5: Do the math

- **Time:** 3:55 to 4:50
- **Source:** [Do the math: what today's open models require](../blog.html#math)
- **Narration file:** [`narration/05-do-the-math.txt`](narration/05-do-the-math.txt)

**Visual:** Show the four formulas as a stack. Then build the model table one row at a time, with each row filling in 8-GPU server outlines. Kimi K2 fills two servers. Then swap the H100 servers for B300 and watch Kimi K2 collapse into half of one server. End on the pull quote.

**On screen:**

```text
weight memory = parameters × bytes per parameter   (BF16 = 2, FP8 = 1, INT4 ≈ 0.5)
KV per token  ≈ 2 × layers × kv_heads × head_dim × bytes
GPU count     = ceil[(weights + live KV) ÷ usable memory per GPU]
node count    = ceil(GPUs ÷ 8 per node)
```

Assumptions: FP8 weights, 72 GB usable per 80 GB H100, one 128K-token session of KV cache.

| Model | FP8 weights | H100s provisioned | Nodes |
| --- | --- | --- | --- |
| gpt-oss-120b | ≈117 GB | 2 | 1 |
| Qwen3-235B-A22B | ≈235 GB | 4 | 1 |
| Llama 3.1 405B | ≈405 GB | 8 | 1 |
| DeepSeek V3.1 | ≈685 GB | 16 | 2 |
| Kimi K2 | ≈1 TB | 16 | 2 |

- Two nodes means: collectives leave NVLink · rack-level power (≈10.2 kW per DGX H100) · failures move ≈1 TB
- Kimi K2 on B300 (≈259 GB usable): **4 GPUs, one NVLink domain**
- Pull quote: *Choosing a GPU SKU really means choosing how many failure domains a replica spans.*

**Narration:**

```text
Model selection is capacity planning, and four formulas get you most of the way.

Weight memory is parameters times bytes per parameter. In F-P eight, that's one byte each. Add K-V cache for the live tokens, divide by the usable memory on each GPU, and round up.

On H one hundreds, with one long session of cache each, G-P-T O-S-S one-twenty-B needs two GPUs, and Llama four-oh-five B needs eight, one full server. Kimi K two, at a trillion parameters, needs sixteen. That's two full servers.

That jump from one server to two changes the problem. Traffic between GPUs leaves the fast N-V Link domain, the replica draws rack-level power, and any failure moves nearly a terabyte.

On B three hundreds, Kimi K two fits in four GPUs, inside one server.

Choosing a GPU type really means choosing how many failure domains a replica spans.
```

---

## Scene 6: KV cache, the concurrency multiplier

- **Time:** 4:50 to 5:30
- **Source:** [KV cache: the concurrency multiplier](../blog.html#kv)
- **Narration file:** [`narration/06-kv-cache.txt`](narration/06-kv-cache.txt)

**Visual:** A memory bar for one 8×H100 replica. The weights block fills most of it; two 64 GB session blocks squeeze into the rest, and a third bounces off. Then swap to an MLA model, where the session blocks shrink to slivers. End with two small cards for the Tech Preview features.

**On screen:**

- Llama 3.1 405B: ≈500 KB of KV per token (BF16) → ≈64 GB per 128K session
- 8×H100 at 90% usable, after ≈405 GB of weights: ≈170 GB free → **2 full-length sessions**
- "The model fits. The workload does not."
- MLA models (DeepSeek V3.1, Kimi K2): ≈70 KB/token
- NAI 2.8, **Tech Preview**: KV-cache-aware routing (llm-d) · KV-cache offload to host RAM

**Narration:**

```text
Weights decide whether one replica fits. K-V cache decides how many requests it can serve at once.

Llama four-oh-five B stores about five hundred kilobytes of cache per token. One full session of one hundred twenty-eight thousand tokens is about sixty-four gigabytes. After the weights, eight H one hundreds have room for just two of those sessions. The model fits. The workload doesn't.

Models with multi-head latent attention, like DeepSeek and Kimi, compress that cache to about seventy kilobytes per token. Attention design is an infrastructure input.

N-A-I two point eight adds cache-aware routing and cache offload to host memory, both in Tech Preview.
```

---

## Scene 7: Where Nutanix fits

- **Time:** 5:30 to 6:20
- **Source:** [Where Nutanix fits](../blog.html#nutanix)
- **Narration file:** [`narration/07-where-nutanix-fits.txt`](narration/07-where-nutanix-fits.txt)

**Visual:** An animated stack that builds from the bottom up, one layer per sentence of narration, under a "Project Astra" banner. Then a left-to-right pipeline for the cold path: Objects bucket → Files volume → GPU memory, with a stopwatch.

**On screen:**

- Banner: **Project Astra**: "user intent → ready-to-use GPU or inference service"
- Stack, bottom to top:
  - GPU servers
  - Foundation Central + NICo (NVIDIA Infra Controller): discover, health-check, image
  - NIM (Nutanix Infra Manager): claim nodes, build clusters
  - AHV + COCI: GPU VMs on compute-only nodes
  - Prism Central projects: tenancy for GPUs and networks
  - NKP: Kubernetes workload clusters
  - NAI: governed model endpoints
- Small caption: "Nutanix Infra Manager, not NVIDIA NIM"
- Cold path: Objects → Files (RWX volume at `/mnt/models`) → GPU memory
- `cold-start lower bound = model bytes ÷ effective load bandwidth`
- ≈400 GB ÷ ≈10 GB/s ≈ **40 s floor**, before deserialization, KV allocation, and health checks
- Pull quote: *Measure the load; don't derive it from a spec sheet.*

**Narration:**

```text
So where does Nutanix fit? The model server is one layer, and Nutanix supplies the layers around it.

Project Astra packages them into an A-I factory. Foundation Central and NVIDIA Infra Controller discover and image the GPU servers. Nutanix Infra Manager claims them and builds clusters. A-H-V attaches the GPUs to virtual machines on compute-only GPU clusters. Prism Central handles tenancy. N-K-P runs Kubernetes. And N-A-I turns it all into governed model endpoints.

Then there's the cold start. Weights flow from Nutanix Objects into a shared Files volume, and every new replica reads them from there. A four-hundred-gigabyte model at about ten gigabytes per second takes at least forty seconds, before any setup. Real loads can be far slower.

Measure the load. Don't derive it from a spec sheet.
```

---

## Scene 8: Field notes from our GPU Farm

- **Time:** 6:20 to 7:05
- **Source:** [Field notes: our own GPU Farm](../blog.html#gpu-farm)
- **Narration file:** [`narration/08-gpu-farm.txt`](narration/08-gpu-farm.txt)

**Visual:** A request pipeline from developer to GPU Farm, then three stat cards, then two lesson cards. Then horizontal bars comparing FP8 weight sizes against a dashed line for what one RTX PRO 6000 holds. Finish with one GPU's memory bar, most of it filled by a single agent session's KV cache.

**On screen:**

- **96 × RTX PRO 6000**: 12 nodes × 8, 96 GB GDDR7 each, PCIe Gen5, no NVLink *(confirm 90 vs 96 before external use)*
- **≈42B tokens / week**: TaaS report, September 25, 2026
- **619 onboarded users**: up 62%, planning for ≈1,500 and then ≈3,000
- Lessons:
  - Capacity is cheap; interconnect is not
  - PCIe favors models that fit on one card (Qwen3.6-35B-A3B on one RTX PRO 6000: fast to serve, not frontier-class)
- FP8 weights vs. one GPU (≈86 GB usable): Qwen3.6-35B-A3B ≈35 GB · DeepSeek V3.1 ≈685 GB · Kimi K2 ≈1 TB
- "Frontier open models need 8–12× what one GPU holds."
- One RTX PRO 6000: a 128K-token agent session ≈64 GB (KV cache at Llama 3.1 405B's ≈500 KB per token, before any weights)
- Pull quote: *Usable LLMs for agentic work need a GPU farm.*

**Narration:**

```text
Our internal GPU Farm already runs this stack, serving tokens to Nutanix engineers, mostly for coding agents.

It runs 96 RTX Pro 6000 GPUs, generates about 40 billion tokens a week, and serves over 600 onboarded users.

The lessons match the math. Without N-V Link, splitting a model across cards hurts latency, so this hardware favors models that fit on one card. A small Mixture-of-Experts model on one GPU is fast and cheap to serve.

But fast to serve isn't the same as capable. Models small enough to fit on one GPU are far from the frontier of open-source models.

Add the memory needed for agent context at 64GB per 128k tokens and GPU farms are the only way to host usable LLMs for agentic work.
```

---

## Scene 9: Takeaways and close

- **Time:** 7:05 to 7:40
- **Source:** [Takeaways](../blog.html#takeaways) and [Coming next in this series](../blog.html#next)
- **Narration file:** [`narration/09-takeaways.txt`](narration/09-takeaways.txt)

**Visual:** Takeaways appear as a checklist, one per sentence. Then a "Part 2" teaser card and an end card with the post title.

**On screen:**

- Prefill sets TTFT; decode sets completion time. Measure both at p99.
- Check capacity **and** bandwidth for every model–GPU pair.
- KV cache, not weights, usually limits concurrency.
- The GPU SKU decides how many failure domains a replica spans.
- Teaser: **Part 2: Parallelism and the fabric**
- End card: *Inference is an infrastructure problem*: read the full post

**Narration:**

```text
To recap. Prefill sets the first token, and decode sets completion. Measure both, at the tail. Check capacity and bandwidth for every model and GPU pair. K-V cache, not weights, usually limits concurrency. And the GPU you choose decides how many failure domains each replica spans.

In part two, we'll look at parallelism and the network fabric, and why the interconnect becomes part of the accelerator.

The full post, with all the math, is linked with this video. Thanks for watching.
```
