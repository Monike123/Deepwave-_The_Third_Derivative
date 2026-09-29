"""
Export the SRM + EfficientNet-B4 forensic checkpoint to ONNX.

Usage (from the repo root, with the project venv):

    python tools/export_forensic_onnx.py
    python tools/export_forensic_onnx.py --input Models/forensic_best.pth --output Models/forensic_classifier.onnx
"""
import argparse
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.services.forensic_net import ForensicNet  # noqa: E402


def export(pt_path: Path, onnx_path: Path, image_size: int = 380) -> None:
    model = ForensicNet()
    state = torch.load(pt_path, map_location="cpu", weights_only=False)
    model.load_state_dict(state, strict=True)
    model.eval()

    dummy = torch.randn(1, 3, image_size, image_size)
    onnx_path.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(
        model,
        dummy,
        str(onnx_path),
        input_names=["image"],
        output_names=["logit"],
        dynamic_axes={"image": {0: "batch"}, "logit": {0: "batch"}},
        opset_version=17,
    )
    print(f"Exported {pt_path.name} -> {onnx_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export forensic_best.pth to ONNX")
    parser.add_argument("--input", type=Path, default=ROOT / "Models" / "forensic_best.pth")
    parser.add_argument("--output", type=Path, default=ROOT / "Models" / "forensic_classifier.onnx")
    parser.add_argument("--image-size", type=int, default=380)
    args = parser.parse_args()
    if not args.input.exists():
        raise SystemExit(f"Checkpoint not found: {args.input}")
    export(args.input, args.output, args.image_size)


if __name__ == "__main__":
    main()
