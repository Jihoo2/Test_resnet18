"""[추가 실험용] training/finetune.py 복사본 + 실험 옵션 5개 (기본값 = 원본과 완전히 동일).

원본 finetune.py 는 그대로 둔다 (서비스 모델 A·실험 B·C 재현용).
추가 옵션 — 지정하지 않으면 원본과 같은 동작:
  --aug                 Train 전용 증강 (finetune_aug.py 와 같은 설정)
  --image-size N        입력 해상도 (기본: 전처리기 그대로 224). 384 이상이면 중앙 자르기 없이 N×N 으로 리사이즈
  --label-smoothing E   정답 확률을 1-E 로 학습 (과신 오답 완화). 0 이면 원본 손실 그대로
  --seed S              무작위 시작점 (기본 42 = 원본)
  --base-model ID       기반 모델 (기본 microsoft/resnet-18)
한 실험에서 '한 가지'만 바꿔 B(Full FT 3ep lr 5e-5)와 비교하는 데 쓴다.
"""
import argparse
import json
import random
from pathlib import Path
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from PIL import Image
from torchvision import transforms
from transformers import AutoImageProcessor, AutoModelForImageClassification

BASE_MODEL = "microsoft/resnet-18"
EXTS = {".jpg", ".jpeg", ".png", ".webp"}

AUG = transforms.Compose([
    transforms.RandomResizedCrop(256, scale=(0.6, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(),
    transforms.RandomRotation(20),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
])

class FolderImages(Dataset):
    def __init__(self, root: Path, classes: list[str], processor, transform=None):
        self.records = []
        self.processor = processor
        self.transform = transform
        for idx, name in enumerate(classes):
            folder = root / name
            if not folder.is_dir():
                raise ValueError(f"필요한 클래스 폴더가 없습니다: {folder}")
            self.records.extend((path, idx) for path in sorted(folder.iterdir())
                                if path.suffix.lower() in EXTS and path.is_file())
        if not self.records:
            raise ValueError(f"이미지가 없습니다: {root}")

    def __len__(self):
        return len(self.records)

    def __getitem__(self, index):
        path, label = self.records[index]
        with Image.open(path) as raw:
            image = raw.convert("RGB")
            if self.transform is not None:
                image = self.transform(image)
            tensor = self.processor(images=image, return_tensors="pt")["pixel_values"][0]
        return {"pixel_values": tensor, "labels": torch.tensor(label, dtype=torch.long)}

def run(args):
    random.seed(args.seed)
    torch.manual_seed(args.seed)

    data = Path(args.data)
    train_root = data / "train"
    if not train_root.is_dir():
        raise ValueError("dataset/train/ 폴더를 먼저 준비하세요.")

    classes = sorted(p.name for p in train_root.iterdir() if p.is_dir())
    if len(classes) < 2:
        raise ValueError("클래스 폴더가 2개 이상 필요합니다.")

    base_model = args.base_model
    processor = AutoImageProcessor.from_pretrained(base_model)
    if args.image_size:
        if "shortest_edge" in processor.size:
            processor.size = {"shortest_edge": args.image_size}
        else:
            processor.size = {"height": args.image_size, "width": args.image_size}
        if hasattr(processor, "crop_size") and processor.crop_size:
            processor.crop_size = {"height": args.image_size, "width": args.image_size}
    train_set = FolderImages(train_root, classes, processor, transform=AUG if args.aug else None)
    val_set = FolderImages(data / "val", classes, processor)

    train_counts = {n: sum(label == i for _, label in train_set.records) for i, n in enumerate(classes)}
    val_counts = {n: sum(label == i for _, label in val_set.records) for i, n in enumerate(classes)}

    if any(n < 2 for n in train_counts.values()) or any(n < 1 for n in val_counts.values()):
        raise ValueError("각 클래스에 학습 최소 2장, 검증 최소 1장이 필요합니다.")

    print(f"클래스: {classes} / Train: {len(train_set)}, Val: {len(val_set)}")

    model = AutoModelForImageClassification.from_pretrained(
        base_model,
        num_labels=len(classes),
        id2label={i: name for i, name in enumerate(classes)},
        label2id={name: i for i, name in enumerate(classes)},
        ignore_mismatched_sizes=True,
    )

    # 기존 1000-class 분류 헤드는 크기가 맞지 않아 새롭게 초기화됩니다.
    # 초보자 첫 학습은 Backbone을 고정하고 마지막 분류 헤드만 학습합니다.
    if args.freeze_backbone:
        for name, parameter in model.named_parameters():
            parameter.requires_grad = name.startswith("classifier.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optim = torch.optim.AdamW(
        (p for p in model.parameters() if p.requires_grad),
        lr=args.lr
    )

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_set, batch_size=args.batch_size, shuffle=False, num_workers=0)

    history = []
    best_acc = -1.0
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    for epoch in range(args.epochs):
        model.train()
        losses = []

        for batch in train_loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            optim.zero_grad()
            if args.label_smoothing > 0:
                logits = model(pixel_values=batch["pixel_values"]).logits
                loss = F.cross_entropy(logits, batch["labels"], label_smoothing=args.label_smoothing)
            else:
                result = model(**batch)   # 원본과 같은 손실
                loss = result.loss
            loss.backward()
            optim.step()
            losses.append(float(loss.item()))

        model.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in val_loader:
                pixels = batch["pixel_values"].to(device)
                logits = model(pixel_values=pixels).logits
                correct += (logits.argmax(dim=-1).cpu() == batch["labels"]).sum().item()
                total += len(batch["labels"])

        acc = correct / total
        row = {
            "epoch": epoch + 1,
            "loss": round(sum(losses) / len(losses), 4),
            "val_accuracy": round(acc, 4)
        }
        history.append(row)
        print(row)

        if acc > best_acc:
            best_acc = acc
            model.save_pretrained(str(output), safe_serialization=True)
            processor.save_pretrained(str(output))

    (output / "training_report.json").write_text(
        json.dumps(
            {
                "base_model": base_model,
                "options": {"aug": args.aug, "image_size": args.image_size or "processor default",
                            "label_smoothing": args.label_smoothing, "seed": args.seed,
                            "epochs": args.epochs, "lr": args.lr, "freeze_backbone": args.freeze_backbone},
                "classes": classes,
                "train_count": len(train_set),
                "val_count": len(val_set),
                "best_val_accuracy": best_acc,
                "history": history
            },
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    print(f"저장 완료: {output} / best val accuracy={best_acc:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="dataset")
    parser.add_argument("--output", default="artifacts/beans_resnet18")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--freeze-backbone", action="store_true")
    parser.add_argument("--aug", action="store_true")
    parser.add_argument("--image-size", type=int, default=0)
    parser.add_argument("--label-smoothing", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--base-model", default=BASE_MODEL)
    run(parser.parse_args())

