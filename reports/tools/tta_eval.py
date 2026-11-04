"""TTA (Test-Time Augmentation): 재학습 없이, 추론할 때 뒤집은 사진들의 확률을 평균.

- 방식 (실행 전 고정):
    none : 원본 1장 (기존과 동일)
    h2   : 원본 + 좌우반전 → 2장 평균
    hv4  : 원본 + 좌우 + 상하 + 좌우상하 → 4장 평균
- 모델별로 Validation 정확도가 가장 높은 방식을 선택 (동률이면 장수가 적은 쪽 = 더 빠른 쪽)
- 선택된 방식을 Test 에 1회 적용. 추론 비용은 장수만큼 늘어남을 함께 기록

실행:
  python reports/tools/tta_eval.py --model B_full_e3=artifacts/beans_resnet18_full --model ...
결과: reports/data/tta_eval.md
"""
import argparse
from pathlib import Path

import torch
from PIL import Image, ImageOps
from transformers import AutoImageProcessor, AutoModelForImageClassification

DATA = Path("reports/data")
EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MODES = {
    "none": [lambda im: im],
    "h2": [lambda im: im, ImageOps.mirror],
    "hv4": [lambda im: im, ImageOps.mirror, ImageOps.flip, lambda im: ImageOps.flip(ImageOps.mirror(im))],
}


def evaluate(model, processor, records, device, views, bs=16):
    correct = 0
    with torch.no_grad():
        for i in range(0, len(records), bs):
            chunk = records[i:i + bs]
            imgs = []
            for p, _ in chunk:
                with Image.open(p) as raw:
                    imgs.append(raw.convert("RGB"))
            prob = 0
            for v in views:
                px = processor(images=[v(im) for im in imgs], return_tensors="pt")["pixel_values"].to(device)
                prob = prob + torch.softmax(model(pixel_values=px).logits, -1)
            pred = prob.argmax(-1).cpu()
            correct += sum(int(pred[j]) == gt for j, (_, gt) in enumerate(chunk))
    return correct, len(records)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="append", required=True, help="이름=모델폴더")
    ap.add_argument("--data", default="dataset")
    ap.add_argument("--mode", choices=list(MODES), default=None,
                    help="지정하면 Val 선택 없이 이 방식으로 고정 (사전에 정한 방식의 재현 확인용)")
    ap.add_argument("--out", default="tta_eval.md")
    args = ap.parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    lines = ["# TTA (추론 시 증강 평균) 평가", "",
             "- 방식: none(원본) / h2(원본+좌우반전) / hv4(원본+좌우+상하+좌우상하)",
             "- 모델별로 Validation 최고 방식을 선택 (동률이면 장수가 적은 쪽) → Test 1회", "",
             "| 모델 | Val none | Val h2 | Val hv4 | 선택 | Test none | Test 선택 방식 | 변화 | 추론 비용 |",
             "|---|---:|---:|---:|---|---:|---:|---:|---:|"]
    for spec in args.model:
        name, path = spec.split("=", 1)
        processor = AutoImageProcessor.from_pretrained(path)
        model = AutoModelForImageClassification.from_pretrained(path).to(device).eval()
        id2label = {int(k): v for k, v in model.config.id2label.items()}
        label2id = {v: k for k, v in id2label.items()}

        def recs(split):
            root = Path(args.data) / split
            return [(p, label2id[c]) for c in label2id for p in sorted((root / c).iterdir())
                    if p.suffix.lower() in EXTS]
        val, test = recs("val"), recs("test")
        vacc = {}
        for m, views in MODES.items():
            c, n = evaluate(model, processor, val, device, views)
            vacc[m] = c / n
        order = list(MODES)
        best = args.mode or max(order, key=lambda m: (vacc[m], -order.index(m)))
        tc0, tn = evaluate(model, processor, test, device, MODES["none"])
        tcb, _ = evaluate(model, processor, test, device, MODES[best]) if best != "none" else (tc0, tn)
        diff = (tcb - tc0) / tn * 100
        lines.append(f"| {name} | {vacc['none']:.4f} | {vacc['h2']:.4f} | {vacc['hv4']:.4f} | **{best}** | "
                     f"{tc0 / tn:.4f} | {tcb / tn:.4f} | {diff:+.2f}%p | ×{len(MODES[best])} |")
        print(lines[-1])
    if args.mode:
        lines.insert(4, f"- **이번 실행은 방식 고정: {args.mode}** (이전 실험에서 Val 로 정한 방식의 재현 확인)")
    (DATA / args.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n저장: {DATA / args.out}")


if __name__ == "__main__":
    main()
