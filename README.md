# PolyTruth: Multilingual Disinformation Detection Corpus

PolyTruth is a multilingual dataset for **disinformation detection** built from verified fact-checks and aligned corrective statements. It pairs **false claims** with **true statements** across **25+ languages**, designed for training and evaluating transformer-based language models on multilingual and cross-lingual disinformation classification. A preprint of the paper can be found on Arvix.org https://arxiv.org/abs/2509.10737. 

⸻

## 📑 Dataset Overview

- **Size**: 30,243 pairs (≈60k statements including both false and true)  
- **Languages**: 25+ (high-resource: Russian, Portuguese, German, Czech, Spanish, English; low-resource: Latvian, Estonian, Azerbaijani, etc.)  
- **Sources**:  
  - False statements collected from the **MindBugs Discovery** dataset (2009–2024 fact-checked claims).  
  - True statements generated via OpenAI's 4o API fact-checking sources to be factual counter-statements.  
- **Format**: CSV with three columns:  
  - `false_statement` – the disinformation claim  
  - `true_statement` – factual correction or counterclaim  
  - `citation` – source or fact-checking body (if available)  

⸻

## ⚠️ Important Notes

- Some false and true statements are in **different languages** (e.g., English claim paired with German correction).  
  - This makes PolyTruth partially **cross-lingual**, not purely same-language.  

⸻

## 📊 Recommended Tasks
- Binary classification (true vs. false)  
- Cross-lingual transfer (train on one language, test on another)  
- High-resource vs. low-resource comparison  
- Benchmarking multilingual transformers (mBERT, XLM-R, RemBERT, mT5, etc.)  

⸻


## 📈 Baseline Results  

From the accompanying paper:  
- **RemBERT** – Best performance overall (87.1% accuracy, 0.87 F1).  
- **XLM-R (base)** – Strong balance between accuracy and efficiency (85.4% accuracy).  
- **mT5** – Comparable to XLM-R (84.6% accuracy).  
- **XLM** – Mid-tier (81%).  
- **mBERT** – Lowest performance (79%).  

⸻

## 📜 Citation  

If you use PolyTruth, please cite:  

```bibtex
@inproceedings{gouliev2025polytruth,
  author    = {Zaur Gouliev and Chengqian Wang and Jennifer Waters},
  title     = {PolyTruth: Multilingual Disinformation Detection using Transformer-Based Language Models},
  booktitle = {Proceedings of the AIDEM 2025: International Tutorial and Workshop on Artificial Intelligence, Data Analytics and Democracy, 
               side event of ECML-PKDD 2025},
  series    = {Lecture Notes in Computer Science},
  year      = {2025},
  publisher = {Springer},
  address   = {Porto, Portugal},
}
