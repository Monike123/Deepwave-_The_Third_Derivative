"""
Export EfficientNet-B0 Deepfake Detector to ONNX
Based on TRahulsingh/DeepfakeDetector architecture
Run this once to convert .pt to .onnx
"""
import torch
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
import argparse
import os

def export_to_onnx(pt_path: str, onnx_path: str):
    """Convert PyTorch model to ONNX format."""
    
    print(f"Loading PyTorch model from: {pt_path}")
    
    # Build EfficientNet-B0 architecture (matching TRahulsingh)
    weights = EfficientNet_B0_Weights.IMAGENET1K_V1
    model = efficientnet_b0(weights=weights)
    
    # Replace classifier
    in_features = model.classifier[1].in_features
    model.classifier = torch.nn.Sequential(
        torch.nn.Dropout(0.4),
        torch.nn.Linear(in_features, 2)
    )
    
    # Load trained weights
    model.load_state_dict(torch.load(pt_path, map_location="cpu"))
    model.eval()
    
    # Create dummy input (batch=1, channels=3, height=224, width=224)
    dummy_input = torch.randn(1, 3, 224, 224)
    
    print(f"Exporting to ONNX: {onnx_path}")
    
    torch.onnx.export(
        model,
        dummy_input,
        onnx_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )
    
    print(f"✅ ONNX model saved to: {onnx_path}")
    print(f"   File size: {os.path.getsize(onnx_path) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export EfficientNet-B0 to ONNX")
    parser.add_argument("--input", default="Models/best_model-v3.pt", help="Input .pt file")
    parser.add_argument("--output", default="Models/efficientnet_deepfake.onnx", help="Output .onnx file")
    args = parser.parse_args()
    
    export_to_onnx(args.input, args.output)
