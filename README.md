# SP!ED 2026 - AI Food Freshness Priority Scanner

[日本語](README_ja.md)

Software-only portfolio version of the AI component developed for our **SP!ED 2026** smart refrigerator prototype.

The original prototype combined an AI camera, freshness-based priority logic, Arduino motor control, and a rotary shelf. The system scanned food stored in multiple sections, decided which item should be checked first, and physically rotated the selected section toward the user.

> **Demo:** The README is intended to use a GIF/video of the original on-site prototype in `assets/`. The hardware shown in that demo is **not** reproduced by this repository.

<!--
After adding the on-site demo as assets/demo.gif, uncomment:
![SP!ED 2026 prototype demo](assets/demo.gif)
-->

## Repository Scope

This repository reproduces the **AI recognition and priority-decision flow** with only a PC and webcam.

```text
Original SP!ED 2026 prototype

Camera -> AI recognition -> Priority decision -> Arduino -> Motor -> Rotary shelf
                                      |
                                      +---- selected slot moves to the user

GitHub portfolio version

Webcam -> Manual 4-slot scan -> AI recognition -> Priority decision -> Target slot display
                 (ENTER)                                  |
                                                          +---- no hardware control
```

The physical carousel, Arduino communication, and stepper-motor control are intentionally excluded.

## How the Portfolio Demo Works

The motorized slot movement from the original prototype is replaced by a simple manual scan workflow:

1. Start the application and show the first food item to the webcam.
2. Press **ENTER** to scan **Slot 1**.
3. The app performs repeated recognition for 3 seconds and stores the majority-vote result.
4. Repeat for **Slots 2, 3, and 4**.
5. After Slot 4, the app compares all four conditions and displays the slot that should be **checked first**.
6. Press **ENTER** once to reset the result.
7. Press **ENTER** again to begin a new scan from Slot 1.

Press **Q** or **ESC** at any time to quit.

## Priority Logic

The portfolio version keeps the freshness-priority concept used in the prototype:

```text
ROTTEN  >  RIPE  >  FRESH
highest                    lowest
priority                   priority
```

The third-party model uses slightly different condition names depending on the food type. For the priority decision, labels are normalized as follows:

| Model label pattern | Priority group |
| --- | --- |
| `rotten` | `ROTTEN` |
| `ripe`, `intermediate_fresh` | `RIPE` |
| `fresh`, `unripe` | `FRESH` |

If multiple slots have the same priority, the lower slot number is selected. Model confidence is **not** treated as a spoilage-severity score.

## Stable Recognition

A single webcam frame can be affected by blur, autofocus, hand movement, or lighting. Each ENTER press therefore starts a short repeated-recognition window instead of classifying only one frame.

During the 3-second scan:

```text
Frame predictions
      ↓
Repeated inference
      ↓
Majority vote
      ↓
Stored slot result
```

If two labels receive the same number of votes, the label with the higher mean classification confidence is selected.

## Features

- Webcam-based 4-slot scanning
- ENTER-controlled scan/reset workflow
- ViT image classification using `Dhahlan2000/freshness_detector_updated`
- Automatic model download on first run
- Repeated recognition and majority voting for each slot
- Freshness-priority decision across four scanned slots
- Clear `CHECK FIRST` target visualization
- CUDA acceleration when available, with CPU fallback
- No Arduino or motor hardware required

## Setup

### 1. Create an environment

Python 3.11 is recommended.

```bash
conda create -n spied2026-freshness python=3.11
conda activate spied2026-freshness
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run

```bash
python app.py
```

The model is downloaded from Hugging Face to `models/freshness_detector_updated/` on the first run.

If the wrong webcam opens, change `CAMERA_ID` in `src/config.py`.

### Optional: run logic tests

```bash
python -m unittest discover -s tests -v
```

## Controls

| Key | Action |
| --- | --- |
| `ENTER` | Start scanning the current slot |
| `ENTER` after 4-slot result | Reset the session |
| `ENTER` after reset | Start the next Slot 1 scan |
| `Q` / `ESC` | Quit |

## Project Structure

```text
spied2026-ai-freshness/
├── app.py                 # Application loop and scan state machine
├── src/
│   ├── camera.py          # Webcam capture
│   ├── classifier.py      # ViT inference / model download
│   ├── config.py          # Camera, scan, and GUI settings
│   ├── freshness.py       # Label normalization, voting, priority logic
│   └── gui.py             # OpenCV dashboard
├── assets/                # Add the original on-site demo here
├── tests/
│   └── test_freshness.py  # Priority/voting logic tests
├── models/                # Downloaded at runtime (not committed)
├── requirements.txt
├── THIRD_PARTY_NOTICES.md
├── LICENSE
├── README.md
└── README_ja.md
```

## Original SP!ED 2026 Prototype

The original project addressed a simple refrigerator problem: food stored deeper inside can become difficult to notice, be forgotten, and eventually be wasted. Our prototype used AI recognition together with a rotary shelf so that the system could move a relevant section toward the user instead of requiring the user to search every section manually.

The prototype included two concepts:

- **Eat First / Priority mode:** scan food condition and bring the higher-priority section forward.
- **Empty Slot mode:** identify an empty section and bring it forward for newly purchased food.

This repository focuses on the first concept. Empty-slot detection and all physical control are outside the scope of this GitHub version.

## Notes on the Model

The current portfolio code uses the label set exposed by the third-party checkpoint at runtime. The checkpoint contains 30 classes across 10 food types and condition variants. The UI shows both the food name and the normalized priority group.

Model weights are not included in this repository. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## License

The source code in this repository is provided under the MIT License. Third-party model weights and assets are governed by their respective terms.
