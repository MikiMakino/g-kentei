# 最新モデル

## Transformer

2017年の論文「Attention Is All You Need」で提案。**自然言語処理の主流** となったアーキテクチャ。

### 特徴

- RNNを使わず **Self-Attention（自己注意機構）** のみで構成
- **並列処理** が可能で学習が高速
- 長距離の依存関係を効率よく捉えられる

### Self-Attention

文中のすべての単語の関係を同時に計算する。

```
「猫が魚を食べた」
→ 「食べた」は「猫」と「魚」の両方に注意
```

### Encoder-Decoder構造

| 構成 | 役割 | 代表モデル |
|------|------|----------|
| Encoderのみ | 文の意味理解 | BERT |
| Decoderのみ | テキスト生成 | GPT |
| Encoder + Decoder | 翻訳・要約 | T5、BART |

---

## 大規模言語モデル（LLM）

### BERT（2018年, Google）

- **Bidirectional（双方向）** Transformer Encoder
- **事前学習タスク**：
  - Masked LM（穴埋め）
  - Next Sentence Prediction
- 文章分類・固有表現認識・QAで高精度

### GPT シリーズ（OpenAI）

| モデル | 年 | 特徴 |
|--------|-----|------|
| GPT-1 | 2018 | 生成型事前学習の実証 |
| GPT-2 | 2019 | 1.5B パラメータ、テキスト生成の高品質化 |
| GPT-3 | 2020 | 175B パラメータ、few-shot学習 |
| GPT-4 | 2023 | マルチモーダル（テキスト＋画像） |

### ChatGPT・RLHF

- **RLHF（人間フィードバックによる強化学習）** でモデルを人間の意図に合わせる
- InstructGPT → ChatGPT へと発展

---

## 画像生成 AI

### GAN（敵対的生成ネットワーク）

```
Generator（生成器）← フィードバック → Discriminator（識別器）
```

- GeneratorとDiscriminatorが互いに競い合いながら学習
- **StyleGAN**：高品質な顔画像生成

### VAE（変分オートエンコーダ）

- データを**潜在空間**に圧縮・復元
- 潜在変数を操作することで多様な生成が可能

### 拡散モデル（Diffusion Model）

- ノイズを加えていく過程を逆にたどってデータを生成
- **Stable Diffusion**・**DALL-E 3**・**Midjourney** で採用
- 現在の画像生成の主流

---

## マルチモーダルモデル

複数の種類のデータ（テキスト・画像・音声）を扱うモデル。

| モデル | 対応モダリティ |
|--------|--------------|
| CLIP（OpenAI） | テキスト + 画像（対応付け） |
| DALL-E | テキスト → 画像生成 |
| GPT-4V | テキスト + 画像理解 |
| Gemini | テキスト・画像・音声・動画 |

---

## 物体検出

| モデル | 特徴 |
|--------|------|
| R-CNN 系 | 領域提案 → 分類の2段階 |
| YOLO | 1段階で高速検出、リアルタイム向き |
| SSD | 複数スケールで検出 |

---

## 音声 AI

- **音声認識（ASR）**：Whisper（OpenAI）が高精度
- **音声合成（TTS）**：WaveNet（DeepMind）が転換点
- **音楽生成**：MusicLM、Suno

---

## 強化学習の最新応用

| モデル | 成果 |
|--------|------|
| AlphaGo | 囲碁で人間チャンピオンを初めて破った（2016年） |
| AlphaGo Zero | 自己対戦のみで AlphaGo を超えた |
| AlphaFold | タンパク質の立体構造を高精度予測 |

!!! note "基盤モデル（Foundation Model）"
    大規模データで事前学習し、様々なタスクに転用できる大規模モデルの総称。GPT・BERT・CLIPなどが該当。
