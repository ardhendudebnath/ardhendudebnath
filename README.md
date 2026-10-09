<div align="center">

![Ardhendu Debnath — machine learning engineer](3d/assets/banner.webp)

[![Live 3D profile](https://img.shields.io/badge/▶_live-3D_PROFILE-cc2936?style=for-the-badge&labelColor=0d0f13)](https://ardhendudebnath.github.io/ardhendudebnath/3d/)
[![Email](https://img.shields.io/badge/EMAIL-16191e?style=for-the-badge&logo=gmail&logoColor=eae7e0)](mailto:ardhendud430@gmail.com)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-16191e?style=flat-square&logo=linkedin&logoColor=eae7e0)](https://www.linkedin.com/in/ardhendu-debnath-b53232211)
[![X](https://img.shields.io/badge/X-16191e?style=flat-square&logo=x&logoColor=eae7e0)](https://twitter.com/cstdebnath)
[![HackerRank](https://img.shields.io/badge/HackerRank-16191e?style=flat-square&logo=hackerrank&logoColor=eae7e0)](https://www.hackerrank.com/profile/ardhendud430)
[![YouTube](https://img.shields.io/badge/YouTube-16191e?style=flat-square&logo=youtube&logoColor=eae7e0)](https://www.youtube.com/@ardhendusworld8420)
[![Instagram](https://img.shields.io/badge/Instagram-16191e?style=flat-square&logo=instagram&logoColor=eae7e0)](https://instagram.com/____ardhendu____debnath_____)

</div>

<img align="right" width="188" alt="Ardhendu Debnath" src="3d/assets/avatar.jpg">

B.Tech, India. I build machine learning systems and the unglamorous plumbing underneath them — benchmarks, evaluation harnesses, and agents that have to keep working when the inputs get messy.

Most of the current work sits in **one vertical: Indian GST**. Three repos that feed each other beat three unrelated demos, so the harness that scores the benchmark is the same harness that scores the agent.

> Every number below is measured and reported in that project's own README. Nothing here is illustrative.

<br clear="right">

---

## `01` · llm-gateway-rag

![Hybrid retrieval lifts recall@5 from 0.873 to 1.000, and identifier-only queries from 0.722 to 1.000](3d/assets/cards/llm-gateway-rag.webp)

A self-hosted LLM gateway and RAG backend. One OpenAI-compatible API in front of several providers, with automatic fallback, circuit breakers and a tenant-isolated semantic cache. Documents are ingested by background workers into Qdrant; questions come back reranked with numbered citations. No LangChain, no LlamaIndex.

**The finding:** hybrid retrieval takes recall@5 from 0.873 to **1.000**, and identifier-only queries — the ones dense embeddings are worst at — from 0.722 to **1.000**, in 14.7 ms. Adding backpressure took chat throughput from 20.6 to **156.8 req/s**; before it, unbounded inference OOM-killed the API at 50 users with 74% errors. Killing the primary provider mid-traffic produced **0 user-visible failures across 2,100 requests**, breakers opening 0.9 s after the fault. The RAG p95 target of 1 s was *not* met — it sits at 1.4 s.

![Python](https://img.shields.io/badge/Python-16191e?style=flat-square&logo=python&logoColor=eae7e0)
![FastAPI](https://img.shields.io/badge/FastAPI-16191e?style=flat-square&logo=fastapi&logoColor=eae7e0)
![Qdrant](https://img.shields.io/badge/Qdrant-16191e?style=flat-square)
![Redis](https://img.shields.io/badge/Redis-16191e?style=flat-square&logo=redis&logoColor=eae7e0)
![Celery](https://img.shields.io/badge/Celery-16191e?style=flat-square&logo=celery&logoColor=eae7e0)
![Kubernetes](https://img.shields.io/badge/Kubernetes-16191e?style=flat-square&logo=kubernetes&logoColor=eae7e0)
![Prometheus](https://img.shields.io/badge/Prometheus-16191e?style=flat-square&logo=prometheus&logoColor=eae7e0)
![ONNX](https://img.shields.io/badge/ONNX_Runtime-16191e?style=flat-square&logo=onnx&logoColor=eae7e0)

**[→ llm-gateway-rag](https://github.com/ardhendudebnath/llm-gateway-rag)**

---

## `02` · vision-rl-navigation

![Success rate by condition — the classical planner leads the learned policy in all seven](3d/assets/cards/vision-rl-navigation.webp)

Vision-conditioned reinforcement learning for mobile robot navigation, measured against a classical planner rather than against nothing. A differential-drive robot reaching a goal pose in procedurally generated arenas, 32-beam lidar, continuous `(v, ω)`. Pre-registered endpoints, exact permutation tests, six seeds per arm.

**The finding:** across seven conditions the learned policy beats the classical planner in **none of them** — closest on `dynamic` (−0.020, not significant), worst on `narrow` (−0.168). The reward asymmetry turned out to matter more than the architecture: collisions cost 20 and a full timeout cost 5, so collisions fell from 27 to 2 per 100 episodes and 21 of 25 recovered episodes simply became timeouts. RGB policies trailed depth by 0.16–0.24 on every condition. Real Nav2 over ROS 2, meanwhile, *beats* the classical baseline on the cluttered conditions.

![PPO](https://img.shields.io/badge/PPO-16191e?style=flat-square)
![ROS 2](https://img.shields.io/badge/ROS_2_Jazzy-16191e?style=flat-square&logo=ros&logoColor=eae7e0)
![Nav2](https://img.shields.io/badge/Nav2-16191e?style=flat-square)
![Gymnasium](https://img.shields.io/badge/Gymnasium-16191e?style=flat-square)
![Hydra](https://img.shields.io/badge/Hydra-16191e?style=flat-square)
![NumPy](https://img.shields.io/badge/NumPy-16191e?style=flat-square&logo=numpy&logoColor=eae7e0)

**[→ vision-rl-navigation](https://github.com/ardhendudebnath/vision-rl-navigation)**

---

## `03` · emotionedge-cpp

![Per-stage latency, CPU against GPU — end-to-end falls from 1262 ms to 365 ms](3d/assets/cards/emotionedge-cpp.webp)

Real-time speech translation that keeps the speaker's emotion. ASR, emotion detection across valence/arousal/dominance, emotion-aware translation and expressive TTS in one C++20 process with **no Python at runtime**, on ONNX Runtime.

**The finding:** moving the pipeline to GPU collapsed end-to-end p50 from 1262 ms to **365 ms**, p95 to 631 ms against an 800 ms budget, using 5 s of CPU time instead of 51 s — with quality held (RAVDESS WER 0.042, chrF 56.70 on CUDA against 56.72 on CPU). The emotion-token NLLB LoRA beats plain NLLB-600M on FLORES chrF, 56.7 to 55.8. Echo cancellation was built, measured and **not adopted**: WebRTC AEC3 removed 8.6–14.7 dB of loudspeaker echo but fragmented the transcript, so it stays off until it can be tuned on real hardware.

![C++20](https://img.shields.io/badge/C%2B%2B20-16191e?style=flat-square&logo=cplusplus&logoColor=eae7e0)
![ONNX](https://img.shields.io/badge/ONNX_Runtime-16191e?style=flat-square&logo=onnx&logoColor=eae7e0)
![CUDA](https://img.shields.io/badge/CUDA-16191e?style=flat-square&logo=nvidia&logoColor=eae7e0)
![whisper.cpp](https://img.shields.io/badge/whisper.cpp-16191e?style=flat-square)
![NLLB-200](https://img.shields.io/badge/NLLB--200-16191e?style=flat-square)
![CMake](https://img.shields.io/badge/CMake-16191e?style=flat-square&logo=cmake&logoColor=eae7e0)

**[→ emotionedge-cpp](https://github.com/ardhendudebnath/emotionedge-cpp)**

---

## `04` · symmetrynet-equivariant-gnn

![A molecule rotating while the predicted HOMO-LUMO gap stays pinned at 43.43 meV](3d/assets/cards/symmetrynet-equivariant-gnn.webp)

Predicting molecular properties with neural networks that are *provably* invariant to rotation — representation theory implemented from scratch rather than bolted on with data augmentation.

**The finding:** equivariance verified to 1.3 × 10⁻¹⁵ relative error, against 1.2 × 10⁻² for a naive GNN. On QM9 HOMO-LUMO gap, equivariant PaiNN hits 43.43 meV test MAE versus 56.03 meV for a distance-only baseline — and its advantage *widens* with data, from 1.16× at 11k molecules to 1.29× at 110k.

![PyTorch](https://img.shields.io/badge/PyTorch-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![PyG](https://img.shields.io/badge/PyTorch_Geometric-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![e3nn](https://img.shields.io/badge/e3nn-16191e?style=flat-square)
![CUDA](https://img.shields.io/badge/CUDA-16191e?style=flat-square&logo=nvidia&logoColor=eae7e0)
![MIT](https://img.shields.io/badge/MIT-16191e?style=flat-square)

**[→ symmetrynet-equivariant-gnn](https://github.com/ardhendudebnath/symmetrynet-equivariant-gnn)**

---

## `05` · gst-resilient-agent

![Retrieval recall at k — semantic reaches 89.3% at k=10, hybrid 82.1%, keyword 60.7%](3d/assets/cards/gst-resilient-agent.webp)

A multi-step agent that audits Indian GST invoice lines against hash-pinned Gazette notifications — and the chaos harness built to break it. Seven tools, a hand-rolled loop, a failure taxonomy, and eleven injected failure modes.

**The finding:** semantic retrieval reaches 89.3% recall@10 against keyword's 60.7% — and pays 715 ms for it versus 9 ms. Hybrid RRF lands in between on both axes. Chaos injection configured at 10/25/50% actually fires at 8.2/24.9/49.3%.

![Python](https://img.shields.io/badge/Python-16191e?style=flat-square&logo=python&logoColor=eae7e0)
![Claude Agent SDK](https://img.shields.io/badge/Claude_Agent_SDK-16191e?style=flat-square&logo=anthropic&logoColor=eae7e0)
![Nemotron](https://img.shields.io/badge/Nemotron_3-16191e?style=flat-square&logo=nvidia&logoColor=eae7e0)
![pypdf](https://img.shields.io/badge/pypdf-16191e?style=flat-square)
![pytest](https://img.shields.io/badge/pytest-16191e?style=flat-square&logo=pytest&logoColor=eae7e0)

**[→ gst-resilient-agent](https://github.com/ardhendudebnath/gst-resilient-agent)**

---

## `06` · register-aware-translation

![A formality dial sweeping between তুই, তুমি and আপনি](3d/assets/cards/register-aware-translation.webp)

Speech translation that gets the *register* right — তুই or আপনি, du or Sie. Standard translators collapse that distinction into an arbitrary choice; here it is a dial. 20 languages, works offline.

**The finding:** 100% register detection across all 20 languages, 98.5% exactness on Bengali, and 95.3% agreement against the external FAME-MT set over 30,281 sentences. The register layer itself costs about 1 millisecond.

![PyTorch](https://img.shields.io/badge/PyTorch-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![Whisper](https://img.shields.io/badge/Whisper-16191e?style=flat-square&logo=openai&logoColor=eae7e0)
![Transformers](https://img.shields.io/badge/Transformers-16191e?style=flat-square&logo=huggingface&logoColor=eae7e0)
![Flask](https://img.shields.io/badge/Flask-16191e?style=flat-square&logo=flask&logoColor=eae7e0)
![SQLite](https://img.shields.io/badge/SQLite-16191e?style=flat-square&logo=sqlite&logoColor=eae7e0)

**[→ register-aware-translation](https://github.com/ardhendudebnath/register-aware-translation)**

---

## `07` · chest-xray-classifier

![Per-class F1 — COVID19 0.982, PNEUMONIA 0.970, NORMAL 0.953, LUNG_OPACITY 0.929](3d/assets/cards/chest-xray-classifier.webp)

Four-class CNN over chest radiographs — NORMAL, PNEUMONIA, COVID19, LUNG_OPACITY — with Grad-CAM, SHAP, and a Mahalanobis out-of-distribution check. *Research prototype. Not a medical device, not clinically validated.*

**The finding:** ResNet18 reaches 0.9587 macro F1 over 3,175 test images, edging out ResNet50 — the smaller backbone wins. Masking to lungs only drops it to 0.9341, which is the honest number: some of the signal was never in the lungs.

![PyTorch](https://img.shields.io/badge/PyTorch-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![torchvision](https://img.shields.io/badge/torchvision-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![FastAPI](https://img.shields.io/badge/FastAPI-16191e?style=flat-square&logo=fastapi&logoColor=eae7e0)
![Grad-CAM](https://img.shields.io/badge/Grad--CAM-16191e?style=flat-square)
![SHAP](https://img.shields.io/badge/SHAP-16191e?style=flat-square)

**[→ chest-xray-classifier](https://github.com/ardhendudebnath/chest-xray-classifier)**

---

## `08` · smart-healthcare-triage

![An urgency ladder escalating from SELF_CARE through URGENT_CARE to EMERGENCY](3d/assets/cards/smart-healthcare-triage.webp)

Symptom-based triage assistant. Describe symptoms in English, Hindi or Bengali; get an urgency class, a helpline and a specialist suggestion. Works offline, audits every decision with a timestamp, and produces a structured clinical handoff.

**The finding:** follow-up questions can *escalate* a case — triage is not a single-shot classification. 79 symptoms, 487 phrases across three languages, 122 tests covering the safety overrides.

![Python](https://img.shields.io/badge/Python_3.11-16191e?style=flat-square&logo=python&logoColor=eae7e0)
![FastAPI](https://img.shields.io/badge/FastAPI-16191e?style=flat-square&logo=fastapi&logoColor=eae7e0)
![spaCy](https://img.shields.io/badge/spaCy-16191e?style=flat-square&logo=spacy&logoColor=eae7e0)
![SQLite](https://img.shields.io/badge/SQLite-16191e?style=flat-square&logo=sqlite&logoColor=eae7e0)
![PWA](https://img.shields.io/badge/PWA-16191e?style=flat-square&logo=pwa&logoColor=eae7e0)

**[→ smart-healthcare-triage](https://github.com/ardhendudebnath/smart-healthcare-triage)**

---

## `09` · neuro-sathi

![Six language packs, one native-reviewed and five hidden until review; deviation alerts are rules-only](3d/assets/cards/neuro-sathi.webp)

An offline-first multilingual companion for elderly cognitive care in North-East India — adaptive memory games, a voice companion, a memory book, medicine reminders, and a caregiver dashboard with baseline-deviation alerts. FastAPI, Flutter and Next.js over Postgres with row-level security.

**Status:** built, and deliberately not claimed as validated. **It does not diagnose.** Five of the six language packs — Assamese, Bengali, Nepali, Manipuri, Bodo — stay hidden from users until a native speaker reviews them. Deviation alerts compare the last 7 days against the previous 28 and flag changes beyond 2 SD, but the model behind them is still rules, not the trained tree-based or TFLite models planned. Clinical validation and usability studies remain outstanding.

![FastAPI](https://img.shields.io/badge/FastAPI-16191e?style=flat-square&logo=fastapi&logoColor=eae7e0)
![Flutter](https://img.shields.io/badge/Flutter-16191e?style=flat-square&logo=flutter&logoColor=eae7e0)
![Next.js](https://img.shields.io/badge/Next.js-16191e?style=flat-square&logo=nextdotjs&logoColor=eae7e0)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_RLS-16191e?style=flat-square&logo=postgresql&logoColor=eae7e0)
![Redis](https://img.shields.io/badge/Redis-16191e?style=flat-square&logo=redis&logoColor=eae7e0)
![Docker](https://img.shields.io/badge/Docker-16191e?style=flat-square&logo=docker&logoColor=eae7e0)

**[→ neuro-sathi](https://github.com/ardhendudebnath/neuro-sathi)**

---

## `10` · llm-serving-unit-economics

![A 3D measurement space — cost, quality and latency axes around three empty workload slots](3d/assets/cards/llm-serving-unit-economics.webp)

Serving an open-weight LLM on vLLM and Kubernetes, benchmarked against a paid API. Three dimensions — latency, quality, cost — pointed at one question: above what request volume does self-hosting actually win?

**Status: week 1 of 6. Build complete, nothing measured yet.** The diagram is the measurement *design*, not results — the repo's standing rule is that every number in it is **absent rather than estimated**, and those three slots stay empty until a run fills them. Defined so far: three workload profiles — `short` (606-char median prompt → 48 tokens), `long_in` (7,177 → 48), `long_out` (446 → 768) — on an RTX 5070 Ti Laptop with 12,227 MiB.

![vLLM](https://img.shields.io/badge/vLLM-16191e?style=flat-square)
![Kubernetes](https://img.shields.io/badge/Kubernetes-16191e?style=flat-square&logo=kubernetes&logoColor=eae7e0)
![Prometheus](https://img.shields.io/badge/Prometheus-16191e?style=flat-square&logo=prometheus&logoColor=eae7e0)
![Grafana](https://img.shields.io/badge/Grafana-16191e?style=flat-square&logo=grafana&logoColor=eae7e0)
![Podman](https://img.shields.io/badge/Podman-16191e?style=flat-square&logo=podman&logoColor=eae7e0)

**[→ llm-serving-unit-economics](https://github.com/ardhendudebnath/llm-serving-unit-economics)**

---

## Toolbox

<div align="center">

**Modelling**

![Python](https://img.shields.io/badge/Python-16191e?style=flat-square&logo=python&logoColor=eae7e0)
![PyTorch](https://img.shields.io/badge/PyTorch-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![PyG](https://img.shields.io/badge/PyTorch_Geometric-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![e3nn](https://img.shields.io/badge/e3nn-16191e?style=flat-square)
![TensorFlow](https://img.shields.io/badge/TensorFlow-16191e?style=flat-square&logo=tensorflow&logoColor=eae7e0)
![scikit-learn](https://img.shields.io/badge/scikit--learn-16191e?style=flat-square&logo=scikitlearn&logoColor=eae7e0)
![NumPy](https://img.shields.io/badge/NumPy-16191e?style=flat-square&logo=numpy&logoColor=eae7e0)
![Pandas](https://img.shields.io/badge/Pandas-16191e?style=flat-square&logo=pandas&logoColor=eae7e0)

**LLM &amp; NLP**

![Claude Agent SDK](https://img.shields.io/badge/Claude_Agent_SDK-16191e?style=flat-square&logo=anthropic&logoColor=eae7e0)
![Transformers](https://img.shields.io/badge/Transformers-16191e?style=flat-square&logo=huggingface&logoColor=eae7e0)
![Whisper](https://img.shields.io/badge/Whisper-16191e?style=flat-square&logo=openai&logoColor=eae7e0)
![spaCy](https://img.shields.io/badge/spaCy-16191e?style=flat-square&logo=spacy&logoColor=eae7e0)
![Gemini](https://img.shields.io/badge/Gemini-16191e?style=flat-square&logo=googlegemini&logoColor=eae7e0)
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA_NIM-16191e?style=flat-square&logo=nvidia&logoColor=eae7e0)

**Serving &amp; infra**

![FastAPI](https://img.shields.io/badge/FastAPI-16191e?style=flat-square&logo=fastapi&logoColor=eae7e0)
![Flask](https://img.shields.io/badge/Flask-16191e?style=flat-square&logo=flask&logoColor=eae7e0)
![Docker](https://img.shields.io/badge/Docker-16191e?style=flat-square&logo=docker&logoColor=eae7e0)
![AWS](https://img.shields.io/badge/AWS-16191e?style=flat-square&logo=amazonwebservices&logoColor=eae7e0)
![Linux](https://img.shields.io/badge/Linux-16191e?style=flat-square&logo=linux&logoColor=eae7e0)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-16191e?style=flat-square&logo=githubactions&logoColor=eae7e0)
![SQLite](https://img.shields.io/badge/SQLite-16191e?style=flat-square&logo=sqlite&logoColor=eae7e0)
![MySQL](https://img.shields.io/badge/MySQL-16191e?style=flat-square&logo=mysql&logoColor=eae7e0)
![MongoDB](https://img.shields.io/badge/MongoDB-16191e?style=flat-square&logo=mongodb&logoColor=eae7e0)
![pytest](https://img.shields.io/badge/pytest-16191e?style=flat-square&logo=pytest&logoColor=eae7e0)

</div>

---

## Numbers

<div align="center">

<img height="150" alt="GitHub statistics" src="https://github-readme-stats.vercel.app/api?username=ardhendudebnath&show_icons=true&hide_border=true&bg_color=0d0f13&title_color=cc2936&text_color=a8aeb8&icon_color=eae7e0" />
<img height="150" alt="Most used languages" src="https://github-readme-stats.vercel.app/api/top-langs/?username=ardhendudebnath&layout=compact&hide_border=true&bg_color=0d0f13&title_color=cc2936&text_color=a8aeb8" />

</div>

---

<div align="center">

[![Three ink plates rendered as 3D perspective cards](3d/assets/plates.jpg)](https://ardhendudebnath.github.io/ardhendudebnath/3d/)

**[Open the live 3D version →](https://ardhendudebnath.github.io/ardhendudebnath/3d/)**

<sub>Each plate is a real 3D surface there — a depth map drives per-pixel parallax in a hand-written WebGL shader, no libraries.</sub>

<br>

<sub><b>Load the bar. Then add weight.</b></sub>

</div>
