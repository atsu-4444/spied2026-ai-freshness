import time
from pathlib import Path

import cv2
import torch
from huggingface_hub import snapshot_download
from PIL import Image
from transformers import AutoModelForImageClassification, ViTImageProcessor


class FreshnessClassifier:
    """ViT-based food freshness classifier used in the SP!ED 2026 prototype."""

    def __init__(self, model_id, model_dir):
        self.model_id = model_id
        self.model_dir = Path(model_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        local_path = self._ensure_model()
        self.processor = ViTImageProcessor.from_pretrained(
            local_path,
            local_files_only=True,
        )
        self.model = AutoModelForImageClassification.from_pretrained(
            local_path,
            local_files_only=True,
        )
        self.model.to(self.device)
        self.model.eval()

    def _model_is_downloaded(self):
        required = ["config.json", "preprocessor_config.json"]
        has_config = all((self.model_dir / name).exists() for name in required)
        has_weights = any(
            (self.model_dir / name).exists()
            for name in ("model.safetensors", "pytorch_model.bin")
        )
        return has_config and has_weights

    def _ensure_model(self):
        self.model_dir.mkdir(parents=True, exist_ok=True)

        if not self._model_is_downloaded():
            print(f"Downloading model: {self.model_id}")
            print(f"Destination: {self.model_dir}")
            snapshot_download(
                repo_id=self.model_id,
                local_dir=str(self.model_dir),
                allow_patterns=[
                    "config.json",
                    "preprocessor_config.json",
                    "model.safetensors",
                    "pytorch_model.bin",
                ],
            )
            print("Model download completed.")
        else:
            print(f"Using local model: {self.model_dir}")

        return str(self.model_dir)

    @property
    def num_labels(self):
        return self.model.config.num_labels

    def predict(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb)

        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        start = time.perf_counter()
        with torch.inference_mode():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=-1)[0]
        inference_time = time.perf_counter() - start

        confidence, predicted_id = torch.max(probabilities, dim=0)
        predicted_id = predicted_id.item()
        label = self.model.config.id2label.get(predicted_id, str(predicted_id))

        return label, confidence.item(), inference_time
