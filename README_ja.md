# SP!ED 2026 - AI Food Freshness Priority Scanner


[English](README.md) | **日本語**


<p>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch">
  <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/Hugging_Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black" alt="Hugging Face">
</p>


冷蔵庫内の食品をAIで認識し、**次に確認すべき食品を提示するスマート冷蔵庫プロトタイプ**です。


本プロジェクトは **[SP!ED 2026](https://ire-asia.org/ire/spied/)** の国際チーム開発で制作しました。  
現地では、AIによる食品状態認識と回転棚を組み合わせ、食品の状態に応じて確認すべき区画をユーザー側へ移動させるシステムを開発しました。


私は主に **AIによる食品状態認識部分の実装・検証**を担当しました。


本リポジトリでは、Arduino・モーター・回転棚などのハードウェアがなくても主要なAI処理を体験できるよう、**4スロットの手動スキャンとPriority Logicを組み合わせたPC向けポートフォリオ版**として公開しています。<p align="center">  <img src="assets/refrigerator-inside.png" width="850" alt="SP!ED 2026 smart refrigerator prototype"></p>


---


## 📖 プロジェクト概要


冷蔵庫に食品を入れた後、奥に置かれた食品ほど見えにくくなり、存在を忘れてしまうことがあります。


特に野菜や果物などの生鮮食品は、加工食品のように賞味期限やバーコードだけで状態を判断できるとは限りません。  
色や見た目などから状態を確認する必要があるため、冷蔵庫の奥にある食品は、


```text
Stored
  ↓
Hidden
  ↓
Forgotten
  ↓
Loss of freshness / Food waste
```


という流れにつながる可能性があります。


そこで本プロジェクトでは、


**「ユーザーが食品を探しに行くのではなく、確認すべき食品をシステム側から提示する」**


という考え方で、AIカメラと回転棚を組み合わせたスマート冷蔵庫収納システムを開発しました。


---


## 💡 解決したい課題


一般的な冷蔵庫は食品を保存できますが、**どの食品を先に確認すべきか**までは教えてくれません。


特に冷蔵庫の奥は、


- 食品が見えにくい
- 何を入れたか忘れやすい
- 毎回奥まで確認する必要がある
- 食品の状態変化に気づきにくい


といった「見えない領域」になりやすいと考えました。


そこで、


```text
Camera
  ↓
AI Recognition
  ↓
Priority Decision
  ↓
Physical Action
  ↓
対象スロットをユーザー側へ提示
```


という仕組みを設計しました。


単にAIで食品を分類するだけではなく、**認識結果を実世界の動作につなげること**をプロジェクトの中心に置いています。


---


## 🏗️ システム構成


SP!ED 2026で開発したオリジナルシステムは、AIとハードウェアを組み合わせた構成です。


```text
Camera
  │
  └─ 各スロットを撮影
        ↓
AI Model
  │
  └─ 食品の種類・状態を認識
        ↓
Priority Decision
  │
  └─ 確認すべきスロットを決定
        ↓
Arduino
  │
  └─ ステッピングモーターを制御
        ↓
Rotary Shelf
  │
  └─ 対象スロットをユーザー側へ回転
```


<p align="center">
  <img src="assets/rotary-shelf.png" width="430" alt="Rotary shelf prototype">
</p>


---


## 🎛️ オリジナルプロトタイプの2つのモード


### 1 PUSH - Freshness Scan


ボタンを1回押すと、各スロットの食品を順番に撮影し、AIが食品の種類と状態を認識します。


認識結果をもとに優先度を計算し、**最初に確認すべき食品が入っているスロット**を選択します。


その後、Arduinoでステッピングモーターを制御し、対象スロットをユーザー側へ回転させます。


```text
Scan
  ↓
Food / Condition Recognition
  ↓
Priority Decision
  ↓
Target Slot
  ↓
Rotation
```


### 2 PUSH - Empty Slot Mode


ボタンを2回押すと、**新しい食品を収納するための空きスロットを手前へ移動させるモード**に切り替わります。


今回のプロトタイプでは、専用の `Empty` クラスを学習したモデルは使用していません。


実機環境で検証した際、背景や対象外の物体など、対象となる果物・野菜が写っていない場合に、モデルが **`Rotten Cucumber`** と判定する傾向が確認されました。


そこでプロトタイプでは、


- 実際のスロットには **キュウリを使用しない**
- `Rotten Cucumber` と判定されたスロットを **Empty Slotの候補**として扱う


という条件を設けました。


```text
Camera
  ↓
Food Classification Model
  ↓
Rotten Cucumber
  ↓
Empty Slot として扱う
  ↓
対象スロットを手前へ回転
```


これは、短期間のプロトタイプ開発において既存モデルの挙動を利用した**ヒューリスティックな実装**です。


一般的なEmpty Slot Detectionを実現する方法ではなく、**「実際にはキュウリを使用しない」ことを前提とした本プロトタイプ固有の方法**です。


---


## 💻 GitHubポートフォリオ版


本GitHubリポジトリでは、ArduinoやモーターなどのハードウェアがなくてもAI部分を試せるようにしています。


実機で行っていた「回転棚によるスロット切り替え」を、**ENTERキーによる手動スキャン**に置き換えました。


```text
Webcam
  ↓
Slot 1 をスキャン
  ↓
Slot 2 をスキャン
  ↓
Slot 3 をスキャン
  ↓
Slot 4 をスキャン
  ↓
Priority Decision
  ↓
CHECK FIRST
```


4つのスロットを順番に登録すると、AIの認識結果をもとに最初に確認すべきスロットを表示します。GitHub版では、オリジナルプロトタイプのうち **1 PUSH - Freshness Scan / Priority Decision** に焦点を当てています。Empty Slot Modeと物理的な回転制御は、本リポジトリでは実装していません。


---


## 🎬 Demonstration


SP!ED 2026現地で制作した実機プロトタイプの動作デモです。


<p align="center">
  <img src="assets/demonstration.gif" width="760" alt="SP!ED 2026 prototype demonstration">
</p>


GIFでは、**Freshness ScanとEmpty Slot Modeを含む実機動作の一部**を確認できます。


**[▶ フルデモ動画を見る](assets/demo-video.mp4)**


フル動画では、主に食品状態の認識、Priority Decision、回転棚による物理動作を確認できます。  
※ フル動画には `2 PUSH - Empty Slot Mode` の動作は含まれていません。


---


## 🔍 4-Slot Priority Scanner


GitHub版では、4つの仮想スロットを順番にスキャンします。


### 操作フロー


1. Webカメラに食品を映します。
2. **ENTER** を押してSlot 1をスキャンします。
3. 3秒間、複数フレームに対してAI推論を行います。
4. Majority VoteでSlot 1の結果を確定します。
5. 同様にSlot 2、Slot 3、Slot 4を登録します。
6. 4スロットが揃うとPriority Logicを実行します。
7. 最初に確認すべきスロットを **CHECK FIRST** として表示します。
8. 結果画面で **ENTER** を押すとリセットします。
9. もう一度 **ENTER** を押すとSlot 1から再度スキャンできます。


終了するときは **Q** または **ESC** を押します。


---


## 🧠 AIによる食品状態認識


画像分類には、Hugging Faceで公開されているViTベースの学習済みモデルを利用しています。

**[Dhahlan2000/freshness_detector_updated](https://huggingface.co/Dhahlan2000/freshness_detector_updated)**


モデルは10種類の食品について、状態を含めた**30クラス分類**を行います。


### 対応食品


| Food | Condition |
| --- | --- |
| Bell Pepper | Fresh / Intermediate Fresh / Rotten |
| Carrot | Fresh / Intermediate Fresh / Rotten |
| Cucumber | Fresh / Intermediate Fresh / Rotten |
| Potato | Fresh / Intermediate Fresh / Rotten |
| Tomato | Fresh / Intermediate Fresh / Rotten |
| Apple | Unripe / Ripe / Rotten |
| Banana | Unripe / Ripe / Rotten |
| Mango | Unripe / Ripe / Rotten |
| Orange | Unripe / Ripe / Rotten |
| Strawberry | Unripe / Ripe / Rotten |


初回実行時にモデルをHugging Faceから自動的にダウンロードします。


モデルファイルは、

```text
models/freshness_detector_updated/
```


に保存され、Gitの管理対象には含めていません。


---


## ⚖️ Priority Logic


食品状態を比較するため、モデルの出力ラベルを3つのPriority Groupへ変換します。


```text
ROTTEN
  ↓
RIPE
  ↓
FRESH
```


優先順位は、


```text
ROTTEN > RIPE > FRESH
```


です。


| Model Label | Priority Group |
| --- | --- |
| `rotten` | `ROTTEN` |
| `ripe` | `RIPE` |
| `intermediate_fresh` | `RIPE` |
| `fresh` | `FRESH` |
| `unripe` | `FRESH` |


4スロットの中で最もPriorityが高いものを **CHECK FIRST** として表示します。


同じPriorityのスロットが複数ある場合は、結果を決定的にするため、スロット番号の小さい方を選択します。


分類時のConfidenceは「腐敗の程度」を表す値ではないため、Priorityの比較には使用していません。


---


## 🔁 Stable Recognition


Webカメラの1フレームだけで判定すると、


- 手ブレ
- オートフォーカス
- 照明
- 食品の向き
- 一時的な誤分類


などの影響を受ける可能性があります。


そこでGitHub版では、1回のスキャンで複数フレームを推論し、最終結果をMajority Voteで決定します。


```text
Frame 1 ─┐
Frame 2 ─┤
Frame 3 ─┤
   ...   ├─→ Majority Vote → Slot Result
Frame N ─┘
```


票数が同じ場合のみ、各候補の平均Confidenceをタイブレークに利用します。


---


## ✨ 主な機能


### 📷 Webcam Scan


PCのWebカメラを使って食品をリアルタイムに撮影します。


- 4スロットを順番に登録
- ENTERキーによるスキャン開始
- リアルタイムAI推論


### 🧠 Food Condition Classification


ViTを利用して食品と状態を分類します。


- 10種類の食品
- 30クラス分類
- CPU / GPUの自動選択


### 🔁 Repeated Recognition


1スロットにつき3秒間、複数回推論します。


- 複数フレーム推論
- Majority Vote
- 同票時は平均Confidenceで判定


### ⚖️ Priority Decision


4スロットを比較し、確認すべき食品を決定します。


- `ROTTEN > RIPE > FRESH`
- CHECK FIRST表示
- Confidenceを腐敗度として扱わない設計


---


## 🛠️ 使用技術


### AI / Deep Learning


- Python
- PyTorch
- TorchVision
- Transformers
- Hugging Face Hub
- Vision Transformer (ViT)


### Computer Vision


- OpenCV
- Pillow
- NumPy


### Original Prototype


- USB Camera
- Arduino
- Stepper Motor
- Rotary Shelf


### Development


- Git
- GitHub
- Anaconda / Conda


---


## 👨‍💻 担当範囲


私は主に**AIによる食品状態認識部分の実装・検証**を担当しました。


特に、


- 学習済みViTモデルを利用した食品状態分類
- Webカメラを用いたリアルタイム推論
- OpenCVによる推論結果の表示
- 実機プロトタイプにおけるAI認識部分の検証


に取り組みました。


また、GitHubポートフォリオ版では、実機がなくてもプロジェクトの中核となるAI処理を体験できるよう、


- 4スロットスキャン
- Repeated Recognition
- Majority Vote
- Priority Logic
- CHECK FIRST表示
- モデルの自動ダウンロード
- Unit Test


を含む形に再構成しています。


---


## 🚧 開発時に直面した課題


### AI認識を物理動作につなげる


本プロジェクトでは、AIが食品を分類するだけではなく、その結果をもとに「どのスロットを動かすか」を決める必要がありました。


そのため、


```text
Recognition
   ↓
Decision
   ↓
Motor Control
   ↓
Physical Action
```


という一連の流れとしてシステムを設計しました。


### Emptyクラスを持たないモデルで空きスロットを扱う


使用した食品分類モデルには、Empty Slot専用のクラスが存在しませんでした。


一方、実機環境で検証すると、食品が存在しない背景や対象外の物体に対して `Rotten Cucumber` と分類する傾向が確認されました。


そこで、**キュウリを実際のスロットでは使用しない**という制約を設け、`Rotten Cucumber` をEmpty Slotの代理ラベルとして利用しました。


これはモデルの誤分類傾向を利用したプロトタイプ上の工夫であり、汎用的な空き検出手法ではありません。


### 認識結果の安定化


Webカメラによるリアルタイム認識では、照明や食品の向きなどによって推論結果が変動する可能性があります。


GitHub版では、単一フレームの結果だけに依存せず、複数回の推論とMajority Voteを利用することで判定を安定化させています。


### ハードウェアなしで再現できるポートフォリオ化


オリジナル版は回転棚やArduinoを必要とするため、そのままでは第三者が簡単に試すことができません。


そこでGitHub版では、


```text
Physical Slot Rotation
        ↓
Manual ENTER Scan
```


へ置き換え、一般的なPCとWebカメラだけで主要な処理を体験できるようにしました。


---


## 🚀 ローカルで実行する


### 1. RepositoryをClone


```bash
git clone https://github.com/atsu-4444/spied2026-ai-freshness.git
cd spied2026-ai-freshness
```


### 2. 仮想環境を作成


Python 3.11を推奨します。


```bash
conda create -n spied2026-freshness python=3.11
conda activate spied2026-freshness
```


### 3. Dependenciesをインストール


```bash
pip install -r requirements.txt
```


### 4. 起動


```bash
python app.py
```


初回起動時のみ、Hugging Faceからモデルが自動的にダウンロードされます。


専用GPUは必須ではありません。  
CUDA対応GPUが利用可能な場合はGPUを、利用できない場合はCPUを自動的に使用します。


別のWebカメラが起動する場合は、`src/config.py` の


```python
CAMERA_ID = 0
```


を変更してください。


---


## ⌨️ 操作方法


| Key | Action |
| --- | --- |
| `ENTER` | 現在のSlotをスキャン |
| 結果表示後の `ENTER` | セッションをリセット |
| リセット後の `ENTER` | Slot 1から再スタート |
| `Q` / `ESC` | 終了 |


---


## 🧪 Test


Priority LogicやMajority VoteはUnit Testで確認できます。


```bash
python -m unittest discover -s tests -v
```


---


## 📁 Directory Structure


```text
spied2026-ai-freshness/
├── app.py
│
├── src/
│   ├── __init__.py
│   ├── camera.py
│   ├── classifier.py
│   ├── config.py
│   ├── freshness.py
│   └── gui.py
│
├── tests/
│   └── test_freshness.py
│
├── assets/
│   ├── refrigerator-inside.png
│   ├── rotary-shelf.png
│   ├── demonstration.gif
│   └── demo-video.mp4
│
├── models/
│   └── freshness_detector_updated/
│
├── requirements.txt
├── README.md
├── README_ja.md
└── LICENSE
```


`models/` は初回実行時に自動生成され、Gitの管理対象には含まれません。


---


## 🎓 SP!ED 2026


本プロジェクトは **[SP!ED 2026](https://ire-asia.org/ire/spied/)** における国際チームでのプロジェクトとして開発しました。


異なる国・専門・言語背景を持つ学生と協力しながら、AIを日常生活の課題解決につなげるプロトタイプを制作しました。


本プロジェクトでは、


**「冷蔵庫の中で食品が見えなくなり、忘れられてしまう」**


という課題に対して、


```text
AI Recognition
      +
Priority Decision
      +
Rotary Shelf
```


を組み合わせたスマート冷蔵庫収納システムを提案・開発しました。


---


## ⚠️ Disclaimer


本リポジトリは教育・研究・ポートフォリオを目的としたプロトタイプです。


AIによる分類結果は、食品の実際の安全性、品質、可食性、消費期限を保証するものではありません。


食品を食べられるかどうかの判断には、保存状態、期限、臭い、外観、その他の情報も確認してください。


また、本GitHub版にはオリジナルプロトタイプで使用したArduino、モーター、回転棚などのハードウェア制御は含まれていません。Empty Slot Modeで使用した `Rotten Cucumber` 判定も、実機検証時に確認されたモデルの挙動を利用したプロトタイプ上のヒューリスティックであり、一般的な空き検出性能を保証するものではありません。


---


## 📄 License


This project is licensed under the terms of the [LICENSE](LICENSE) file.
