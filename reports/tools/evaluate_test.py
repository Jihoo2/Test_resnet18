"""Test 1회 평가 보조 스크립트 (제공 코드 아님, 제공 코드 수정 없음).

- 모델 선택은 이미 Validation 으로 끝난 뒤에 실행한다 (Test 로 모델/하이퍼파라미터를 고르지 않음).
- 전처리는 training/finetune.py 와 동일하게 저장된 AutoImageProcessor 를 사용한다.
- 출력: 정확도, 클래스별 Precision/Recall/F1, 혼동행렬, 오분류 목록

실행:
  python reports/tools/evaluate_test.py --model artifacts/beans_resnet18 --name A_head_e3
결과:
  reports/data/test_eval_<name>.md, reports/data/test_pred_<name>.csv
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
    ap.add_argument("--data", default="dataset/test")
    ap.add_argument("--batch-size", type=int, default=16)
    args = ap.parse_args()

    processor = AutoImageProcessor.from_pretrained(args.model)
    model = AutoModelForImageClassification.from_pretrained(args.model)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()

    id2label = {int(k): v for k, v in model.config.id2label.items()}
    classes = [id2label[i] for i in sorted(id2label)]
    root = Path(args.data)
    records = [(p, c) for c in classes for p in sorted((root / c).iterdir())
               if p.is_file() and p.suffix.lower() in EXTS]

    preds = []
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
                preds.append((p, gt, id2label[idx], float(pr[idx])))

    n = len(preds)
    correct = sum(gt == pd for _, gt, pd, _ in preds)
    cm = {g: {p: 0 for p in classes} for g in classes}
    for _, gt, pd, _ in preds:
        cm[gt][pd] += 1

    lines = [f"# Test 평가 결과: {args.name}", "",
             f"- 모델: `{args.model}`",
             f"- 데이터: `{args.data}` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)",
             f"- 장치: {device}",
             f"- **Test Accuracy: {correct}/{n} = {correct / n:.4f}**", "",
             "## 클래스별 지표", "",
             "| 클래스 | 이미지 수 | Precision | Recall | F1 |", "|---|---:|---:|---:|---:|"]
    f1s = []
    for c in classes:
        tp = cm[c][c]
        fp = sum(cm[g][c] for g in classes if g != c)
        fn = sum(cm[c][p] for p in classes if p != c)
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        f1s.append(f1)
        lines.append(f"| {c} | {sum(cm[c].values())} | {prec:.4f} | {rec:.4f} | {f1:.4f} |")
    lines.append(f"| **Macro 평균** | {n} | | | **{sum(f1s) / len(f1s):.4f}** |")

    lines += ["", "## 혼동행렬 (행 = 정답, 열 = 예측)", "",
              "| 정답 \\ 예측 | " + " | ".join(classes) + " |",
              "|---|" + "---:|" * len(classes)]
    for g in classes:
        lines.append(f"| **{g}** | " + " | ".join(str(cm[g][p]) for p in classes) + " |")

    wrong = [(p, gt, pd, s) for p, gt, pd, s in preds if gt != pd]
    lines += ["", f"## 오분류 목록 ({len(wrong)}건)", "", "| 파일 | 정답 | 예측 | score |", "|---|---|---|---:|"]
    lines += [f"| {p.name} | {gt} | {pd} | {s:.4f} |" for p, gt, pd, s in wrong]

    out_dir = Path("reports/data")
    out_dir.mkdir(parents=True, exist_ok=True)
    md = out_dir / f"test_eval_{args.name}.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (out_dir / f"test_pred_{args.name}.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["image", "gt_label", "pred_label", "score", "correct"])
        for p, gt, pd, s in preds:
            w.writerow([f"{gt}/{p.name}", gt, pd, round(s, 4), int(gt == pd)])
    print("\n".join(lines))
    print(f"\n저장: {md}")


if __name__ == "__main__":
    main()
