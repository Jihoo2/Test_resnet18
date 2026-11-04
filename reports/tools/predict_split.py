"""Validation / Test 이미지별 3클래스 확률 저장 (제공 코드 아님, 분석 전용).

review_flag_analysis.py · fusion_analysis.py 의 입력을 만든다.
- 전처리는 모델 폴더에 저장된 AutoImageProcessor 사용 (학습·서비스와 동일)
- Test 는 모델 선택이 끝난 뒤 '평가용'으로만 쓴다. 이 CSV 로 기준값을 고르지 않는다.

실행:
  python reports/tools/predict_split.py --model artifacts/beans_resnet18      --name A_head_e3 --split val
  python reports/tools/predict_split.py --model artifacts/beans_resnet18      --name A_head_e3 --split test
결과:
  reports/data/pred_<split>_<name>.csv
  열: image, gt_label, p_angular_leaf_spot, p_bean_rust, p_healthy, pred_label, score, correct
"""
import argparse
import csv
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--split", choices=["val", "test"], required=True)
    ap.add_argument("--data", default="dataset")
    ap.add_argument("--batch-size", type=int, default=16)
    args = ap.parse_args()

    processor = AutoImageProcessor.from_pretrained(args.model)
    model = AutoModelForImageClassification.from_pretrained(args.model)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()

    id2label = {int(k): v for k, v in model.config.id2label.items()}
    classes = [id2label[i] for i in sorted(id2label)]
    root = Path(args.data) / args.split
    records = [(p, c) for c in classes for p in sorted((root / c).iterdir())
               if p.is_file() and p.suffix.lower() in EXTS]

    out = Path("reports/data") / f"pred_{args.split}_{args.name}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    n = correct = 0
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image", "gt_label", *[f"p_{c}" for c in classes], "pred_label", "score", "correct"])
        with torch.no_grad():
            for i in range(0, len(records), args.batch_size):
                chunk = records[i:i + args.batch_size]
                images = []
                for p, _ in chunk:
                    with Image.open(p) as raw:
                        images.append(raw.convert("RGB"))
                pixels = processor(images=images, return_tensors="pt")["pixel_values"].to(device)
                probs = torch.softmax(model(pixel_values=pixels).logits, dim=-1).cpu()
                for (p, gt), pr in zip(chunk, probs):
                    idx = int(pr.argmax())
                    ok = int(id2label[idx] == gt)
                    n += 1
                    correct += ok
                    w.writerow([f"{gt}/{p.name}", gt, *[f"{float(x):.6f}" for x in pr],
                                id2label[idx], f"{float(pr[idx]):.6f}", ok])
    print(f"{out} 저장 — {args.split} {correct}/{n} = {correct / n:.4f}")


if __name__ == "__main__":
    main()
