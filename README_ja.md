# SP!ED 2026 - AI Food Freshness Priority Scanner

[English](README.md)

**SP!ED 2026** で制作したスマート冷蔵庫プロトタイプのうち、AI認識と優先度判定部分をPC単体で再現できるよう整理したポートフォリオ版です。

現地の実機では、AIカメラによる食品状態の認識、優先度判定、Arduinoによるモーター制御、回転棚を組み合わせ、確認すべき食品の区画をユーザー側へ移動させるシステムを制作しました。

> **Demo:** README冒頭には、SP!ED 2026現地で撮影した実機デモのGIF/動画を `assets/` に追加して掲載する想定です。動画に映る回転棚などのハードウェアは、本リポジトリでは再実装しません。

<!--
assets/demo.gif を追加後、以下を有効化してください。
![SP!ED 2026 prototype demo](assets/demo.gif)
-->

## Repository Scope

本リポジトリでは、**AI認識から優先度決定まで**をWebカメラだけで体験できるようにしています。

```text
SP!ED 2026 現地版

Camera -> AI recognition -> Priority decision -> Arduino -> Motor -> Rotary shelf
                                      |
                                      +---- 対象区画をユーザー側へ回転

GitHub ポートフォリオ版

Webcam -> 4スロット手動Scan -> AI recognition -> Priority decision -> Target表示
              (ENTER)                                      |
                                                           +---- ハード制御なし
```

Arduino通信、ステッピングモーター、回転棚の制御は意図的に公開版から切り離しています。

## 操作フロー

実機で行っていたスロット移動を、GitHub版では **ENTERによる手動スキャン**に置き換えます。

1. アプリを起動し、Slot 1として登録したい食品をWebカメラに映します。
2. **ENTER** を押すと Slot 1 のスキャンを開始します。
3. 3秒間、複数フレームに対して推論を行い、多数決で結果を確定します。
4. 同様に Slot 2、3、4 を順番に登録します。
5. 4スロットが揃うと、自動的に優先度を比較し、**最初に確認すべきスロット（CHECK FIRST）**を表示します。
6. 結果画面で **ENTER** を1回押すとリセットします。
7. もう一度 **ENTER** を押すと、新しいSlot 1のスキャンを開始します。

終了するときは **Q** または **ESC** を押します。

## Priority Logic

現地プロトタイプで用いた鮮度ベースの優先度を、GitHub版でも残しています。

```text
ROTTEN  >  RIPE  >  FRESH
最優先                   低優先度
```

利用している第三者モデルは食品によって状態ラベルの表現が異なるため、Priority Logicでは以下の3グループへ正規化します。

| モデルのラベル | Priority Group |
| --- | --- |
| `rotten` | `ROTTEN` |
| `ripe`, `intermediate_fresh` | `RIPE` |
| `fresh`, `unripe` | `FRESH` |

同じ優先度のスロットが複数ある場合は、スロット番号の小さい方を選択します。分類Confidenceは「腐敗の程度」を表す値ではないため、優先度の同率判定には使用しません。

## Stable Recognition

ENTERを押した瞬間の1フレームだけを判定すると、手ブレ、オートフォーカス、照明などの影響を受けやすくなります。そのため、1回のスキャンで複数回推論を行います。

```text
複数フレーム
    ↓
Repeated inference
    ↓
Majority vote
    ↓
Slot結果を確定
```

多数決が同数の場合のみ、平均分類Confidenceが高いラベルを採用します。

## Features

- Webカメラを利用した4スロットスキャン
- ENTERだけで進められるScan / Reset操作
- `Dhahlan2000/freshness_detector_updated` を利用したViT画像分類
- 初回実行時のモデル自動ダウンロード
- 各スロットでの複数回推論＋多数決
- 4スロット間のPriority Logic
- 最優先スロットの `CHECK FIRST` 表示
- CUDA利用可能時はGPU、利用できない場合はCPUを自動使用
- Arduinoやモーターなどのハードウェアは不要

## Setup

### 1. 仮想環境

Python 3.11を推奨します。

```bash
conda create -n spied2026-freshness python=3.11
conda activate spied2026-freshness
```

### 2. ライブラリのインストール

```bash
pip install -r requirements.txt
```

### 3. 実行

```bash
python app.py
```

初回実行時にHugging Faceからモデルを `models/freshness_detector_updated/` へダウンロードします。

別のWebカメラが起動する場合は `src/config.py` の `CAMERA_ID` を変更してください。

### 任意: ロジックテスト

```bash
python -m unittest discover -s tests -v
```

## Controls

| Key | Action |
| --- | --- |
| `ENTER` | 現在のSlotをスキャン |
| 4スロット結果表示後の `ENTER` | セッションをリセット |
| リセット後の `ENTER` | 新しいSlot 1をスキャン |
| `Q` / `ESC` | 終了 |

## Project Structure

```text
spied2026-ai-freshness/
├── app.py                 # アプリ本体・スキャン状態管理
├── src/
│   ├── camera.py          # Webカメラ取得
│   ├── classifier.py      # ViT推論・モデル取得
│   ├── config.py          # カメラ・Scan・GUI設定
│   ├── freshness.py       # ラベル正規化・多数決・Priority Logic
│   └── gui.py             # OpenCVダッシュボード
├── assets/                # 現地実機デモを追加
├── tests/
│   └── test_freshness.py  # Priority / 多数決ロジックのテスト
├── models/                # 実行時に取得（Git管理対象外）
├── requirements.txt
├── THIRD_PARTY_NOTICES.md
├── LICENSE
├── README.md
└── README_ja.md
```

## SP!ED 2026 Original Prototype

現地では、冷蔵庫の奥に置いた食品が見えにくくなり、忘れられ、最終的に廃棄につながるという問題に着目しました。AI認識と回転棚を組み合わせることで、ユーザーが毎回奥まで探すのではなく、システム側から対象区画を手前へ提示することを目指しました。

プロトタイプには主に次の2つの考え方がありました。

- **Eat First / Priority mode:** 食品状態を認識し、優先度の高い区画を手前へ提示する。
- **Empty Slot mode:** 空いている区画を検出し、新しい食品を収納しやすい位置へ回転する。

GitHub版では前者に焦点を当てています。Empty Slot検出と物理的な回転制御は対象外です。

## Modelについて

現在のポートフォリオ版は、利用している第三者チェックポイントが持つラベルセットを実行時にそのまま利用します。チェックポイントは10種類の食品と状態の組み合わせによる30クラスを持ち、GUIでは食品名とPriority Groupの両方を表示します。

モデル重みは本リポジトリに含めません。詳細は [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。

## License

本リポジトリのソースコードはMIT Licenseで公開します。第三者のモデルや素材にはそれぞれの利用条件が適用されます。
