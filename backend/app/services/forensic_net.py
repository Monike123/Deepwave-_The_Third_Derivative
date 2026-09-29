"""
Forensic classifier: SRM high-pass front-end + EfficientNet-B4 + GeM head.

Checkpoint keys in Models/forensic_best.pth match this module exactly:
  srm.conv            Conv2d(3, 3, kernel=5, bias=False)
  backbone            timm efficientnet_b4, 6 input channels, no classifier
  global_pool.p       GeM pooling exponent
  head.0 / head.1 / head.4   Linear(1792, 512) -> BatchNorm1d -> ReLU -> Dropout -> Linear(512, 1)
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import timm


class GeM(nn.Module):
    """Generalized mean pooling. State-dict key is `p`."""

    def __init__(self, p: float = 3.0, eps: float = 1e-6):
        super().__init__()
        self.p = nn.Parameter(torch.ones(1) * p)
        self.eps = eps

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x.clamp(min=self.eps).pow(self.p)
        x = F.adaptive_avg_pool2d(x, 1).pow(1.0 / self.p)
        return x.flatten(1)


class ForensicNet(nn.Module):
    """Binary deepfake forensic network. Output is one logit (higher = more fake)."""

    def __init__(self):
        super().__init__()
        self.srm = nn.Sequential()
        # Named `conv` so the checkpoint key is srm.conv.weight.
        self.srm.conv = nn.Conv2d(3, 3, kernel_size=5, padding=2, bias=False)
        self.backbone = timm.create_model(
            "efficientnet_b4",
            pretrained=False,
            in_chans=6,
            num_classes=0,
            global_pool="",
        )
        self.global_pool = GeM()
        self.head = nn.Sequential(
            nn.Linear(self.backbone.num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(512, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        noise = self.srm.conv(x)
        features = self.backbone.forward_features(torch.cat([x, noise], dim=1))
        return self.head(self.global_pool(features))
