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

## `01` · gst-eval-harness

![Slab accuracy across five identical runs: 53.6, 50.0, 53.6, 50.0, 64.3](3d/assets/cards/gst-eval-harness.webp)

An open, hand-labelled benchmark for Indian GST rate-slab classification. India's slabs changed on 22 Sep 2025 and the 12% slab was abolished — this measures how often LLMs still answer from the old table.

**The finding:** run the *same* prompt against the *same* model five times and slab accuracy swings from 50.0% to 64.3%. Self-agreement is 53.6% — the model reproduces its own answer on only 15 of 28 rows. An abolished slab is recited somewhere in the response 11.4% of the time.

![Python](https://img.shields.io/badge/Python_3.11-16191e?style=flat-square&logo=python&logoColor=eae7e0)
![pypdf](https://img.shields.io/badge/pypdf-16191e?style=flat-square)
![NVIDIA NIM](https://img.shields.io/badge/NVIDIA_NIM-16191e?style=flat-square&logo=nvidia&logoColor=eae7e0)
![Docker](https://img.shields.io/badge/Docker-16191e?style=flat-square&logo=docker&logoColor=eae7e0)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-16191e?style=flat-square&logo=githubactions&logoColor=eae7e0)

**[→ gst-eval-harness](https://github.com/ardhendudebnath/gst-eval-harness)**

---

## `02` · gst-resilient-agent

![Retrieval recall at k: semantic reaches 89.3% at k=10, hybrid 82.1%, keyword 60.7%](3d/assets/cards/gst-resilient-agent.webp)

A multi-step agent that audits GST invoice lines against hash-pinned Gazette notifications — and the chaos harness built to break it. Seven tools, a hand-rolled loop, a failure taxonomy, and eleven injected failure modes.

**The finding:** semantic retrieval reaches 89.3% recall@10 against keyword's 60.7% — and pays 715ms for it versus 9ms. Hybrid RRF lands in between on both axes. Chaos injection configured at 10/25/50% actually fires at 8.2/24.9/49.3%.

![Python](https://img.shields.io/badge/Python-16191e?style=flat-square&logo=python&logoColor=eae7e0)
![Claude Agent SDK](https://img.shields.io/badge/Claude_Agent_SDK-16191e?style=flat-square&logo=anthropic&logoColor=eae7e0)
![Nemotron](https://img.shields.io/badge/Nemotron_3-16191e?style=flat-square&logo=nvidia&logoColor=eae7e0)
![pypdf](https://img.shields.io/badge/pypdf-16191e?style=flat-square)
![pytest](https://img.shields.io/badge/pytest-16191e?style=flat-square&logo=pytest&logoColor=eae7e0)

**[→ gst-resilient-agent](https://github.com/ardhendudebnath/gst-resilient-agent)**

---

## `03` · register-aware-translation

![A formality dial sweeping between তুই, তুমি and আপনি](3d/assets/cards/register-aware-translation.webp)

Speech translation that gets the *register* right — তুই or আপনি, du or Sie. Standard translators collapse that distinction into an arbitrary choice; here it is a dial. 20 languages, works offline.

**The finding:** 100% register detection across all 20 languages, 98.5% exactness on Bengali, and 95.3% agreement against the external FAME-MT set over 30,281 sentences. The register layer itself costs about 1 millisecond.

![PyTorch](https://img.shields.io/badge/PyTorch-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![Whisper](https://img.shields.io/badge/Whisper-16191e?style=flat-square&logo=openai&logoColor=eae7e0)
![Transformers](https://img.shields.io/badge/Transformers-16191e?style=flat-square&logo=huggingface&logoColor=eae7e0)
![Flask](https://img.shields.io/badge/Flask-16191e?style=flat-square&logo=flask&logoColor=eae7e0)
![Socket.IO](https://img.shields.io/badge/Socket.IO-16191e?style=flat-square&logo=socketdotio&logoColor=eae7e0)
![SQLite](https://img.shields.io/badge/SQLite-16191e?style=flat-square&logo=sqlite&logoColor=eae7e0)

**[→ register-aware-translation](https://github.com/ardhendudebnath/register-aware-translation)**

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

## `05` · chest-xray-classifier

![Per-class F1: COVID19 0.982, PNEUMONIA 0.970, NORMAL 0.953, LUNG_OPACITY 0.929](3d/assets/cards/chest-xray-classifier.webp)

Four-class CNN over chest radiographs — NORMAL, PNEUMONIA, COVID19, LUNG_OPACITY — with Grad-CAM, SHAP, and a Mahalanobis out-of-distribution check. *Research prototype. Not a medical device, not clinically validated.*

**The finding:** ResNet18 reaches 0.9587 macro F1 over 3,175 test images, edging out ResNet50 — the smaller backbone wins. Masking to lungs only drops it to 0.9341, which is the honest number: some of the signal was never in the lungs.

![PyTorch](https://img.shields.io/badge/PyTorch-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![torchvision](https://img.shields.io/badge/torchvision-16191e?style=flat-square&logo=pytorch&logoColor=eae7e0)
![FastAPI](https://img.shields.io/badge/FastAPI-16191e?style=flat-square&logo=fastapi&logoColor=eae7e0)
![Grad-CAM](https://img.shields.io/badge/Grad--CAM-16191e?style=flat-square)
![SHAP](https://img.shields.io/badge/SHAP-16191e?style=flat-square)
![MIT](https://img.shields.io/badge/MIT-16191e?style=flat-square)

**[→ chest-xray-classifier](https://github.com/ardhendudebnath/chest-xray-classifier)**

---

## `06` · smart-healthcare-triage

![An urgency ladder escalating from SELF_CARE through URGENT_CARE to EMERGENCY](3d/assets/cards/smart-healthcare-triage.webp)

Symptom-based triage assistant. Describe symptoms in English, Hindi or Bengali; get an urgency class, a helpline, and a specialist suggestion. Works offline, audits every decision with a timestamp, and produces a structured clinical handoff.

**The finding:** follow-up questions can *escalate* a case — triage is not a single-shot classification. 79 symptoms, 487 phrases across three languages, 122 tests covering the safety overrides.

![Python](https://img.shields.io/badge/Python_3.11-16191e?style=flat-square&logo=python&logoColor=eae7e0)
![FastAPI](https://img.shields.io/badge/FastAPI-16191e?style=flat-square&logo=fastapi&logoColor=eae7e0)
![spaCy](https://img.shields.io/badge/spaCy-16191e?style=flat-square&logo=spacy&logoColor=eae7e0)
![SQLite](https://img.shields.io/badge/SQLite-16191e?style=flat-square&logo=sqlite&logoColor=eae7e0)
![Gemini](https://img.shields.io/badge/Gemini_API-16191e?style=flat-square&logo=googlegemini&logoColor=eae7e0)
![PWA](https://img.shields.io/badge/PWA-16191e?style=flat-square&logo=pwa&logoColor=eae7e0)

**[→ smart-healthcare-triage](https://github.com/ardhendudebnath/smart-healthcare-triage)**

---

## Earlier work

| Repo | What | Year |
|---|---|---|
| [Chatbot_customer_satisfaction-project](https://github.com/ardhendudebnath/Chatbot_customer_satisfaction-project) | Customer sentiment chatbot — NLP preprocessing, word-frequency and heatmap analysis | 2024 |
| [predicting_customer_churn...](https://github.com/ardhendudebnath/predicting_customer_churn_for_a_telecommunications_company) | Telecom churn prediction and retention signals | 2024 |
| [House_price_prediction](https://github.com/ardhendudebnath/House_price_prediction) | Regression on housing data | 2024 |
| [sonar_rock-vs-mine-prediction-](https://github.com/ardhendudebnath/sonar_rock-vs-mine-prediction-) | Binary classification on sonar returns | 2024 |
| [Cognifyz-Internship-Project](https://github.com/ardhendudebnath/Cognifyz-Internship-Project) | Machine learning and data analysis internship work | 2025 |
| [Image_Classification_Project-](https://github.com/ardhendudebnath/Image_Classification_Project-) | Image classification practice | 2025 |

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
