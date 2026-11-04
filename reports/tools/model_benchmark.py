"""모델 비교표: 정확도(Val·Test) + 서비스 관점(파라미터 수, 파일 크기, CPU 1장 추론시간).

- 정확도: 각 모델 폴더의 training_report.json (best_val_accuracy) 과
          reports/data/test_eval_<name>.md 의 Test Accuracy (evaluate_test.py 결과) 를 읽는다.
- CPU 추론시간: 서비스와 같은 조건(device=-1 → CPU, 1장씩, 전처리 포함)으로
  dataset/val 이미지 N장(기본 30)을 1장씩 처리. 앞 3장은 warm-up 으로 제외, 중앙값 기록.
- 모델 선택 기준은 Validation. Test 는 참고용 1회 측정값.

실행:
  python reports/tools/model_benchmark.py \\
    --model A_head_e3=artifacts/beans_resnet18 \\
    --model B_full_e3=artifacts/beans_resnet18_full \\
    --model E1_resnet50_full=artifacts/beans_resnet50_full
결과: reports/data/model_compare.md
"""
import argparse
import json
import re
import statistics
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

DATA = Path("reports/data")
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def test_acc(name):
    p = DATA / f"test_eval_{name}.md"
    if not p.exists():
        return None
    m = re.search(r"Test Accuracy: (\d+)/(\d+) = ([0-9.]+)", p.read_text(encoding="utf-8"))
    return float(m.group(3)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="append", required=True, help="이름=모델폴더")
    ap.add_argument("--data", default="dataset/val")
    ap.add_argument("--n", type=int, default=30)
    args = ap.parse_args()

    torch.manual_seed(42)
    images = sorted(p for p in Path(args.data).rglob("*") if p.suffix.lower() in EXTS)
    step = max(1, len(images) // args.n)
    images = images[::step][:args.n]

    rows = []
    for spec in args.model:
        name, path = spec.split("=", 1)
        report = json.loads((Path(path) / "training_report.json").read_text(encoding="utf-8"))
        processor = AutoImageProcessor.from_pretrained(path)
        model = AutoModelForImageClassification.from_pretrained(path).eval()  # CPU
        params = sum(p.numel() for p in model.parameters())
        size_mb = sum(f.stat().st_size for f in Path(path).glob("*.safetensors")) / 1024 / 1024
        times = []
        with torch.inference_mode():
            for i, img_path in enumerate(images):
                with Image.open(img_path) as raw:
                    img = raw.convert("RGB")
                t0 = time.perf_counter()
                pixels = processor(images=img, return_tensors="pt")["pixel_values"]
                model(pixel_values=pixels).logits.softmax(-1)
                ms = (time.perf_counter() - t0) * 1000
                if i >= 3:
                    times.append(ms)
        rows.append({
            "name": name, "base": report.get("base_model", "?"),
            "freeze": "Head-only" if "head" in name.lower() else "Full FT",
            "aug": "있음" if (report.get("augmentation") or report.get("options", {}).get("aug")) else "없음",
            "extra": ", ".join(f"{k}={v}" for k, v in report.get("options", {}).items()
                               if (k, v) in {("image_size", 384), ("label_smoothing", 0.1)} or (k == "seed" and v != 42)) or "—",
            "val": report["best_val_accuracy"], "test": test_acc(name),
            "params": params / 1e6, "size": size_mb, "cpu": statistics.median(times),
        })
        print(f"{name}: val {report['best_val_accuracy']:.4f}, CPU {statistics.median(times):.1f} ms")

    base_cpu = rows[0]["cpu"]
    lines = ["# 모델 비교 (정확도 + 서비스 비용)", "",
             f"- CPU 추론: 서비스와 같은 CPU·1장씩·전처리 포함, val {len(images)}장 중 앞 3장 warm-up 제외 중앙값",
             f"- 실행 장치 스레드 수: {torch.get_num_threads()}",
             "- 모델 선택 기준은 Validation. Test 는 선택과 무관하게 각 1회 측정", "",
             "| 실험 | 기반 모델 | 방식 | 증강 | 기타 | Best Val | Test | 파라미터(M) | 파일(MB) | CPU 1장(ms) | 첫 행 대비 |",
             "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        t = f"{r['test']:.4f}" if r["test"] is not None else "—"
        lines.append(f"| {r['name']} | `{r['base']}` | {r['freeze']} | {r['aug']} | {r['extra']} | {r['val']:.4f} | {t} | "
                     f"{r['params']:.1f} | {r['size']:.0f} | {r['cpu']:.1f} | ×{r['cpu'] / base_cpu:.1f} |")
    best = max(rows, key=lambda r: r["val"])
    lines += ["", f"- Validation 최고: **{best['name']}** ({best['val']:.4f}, CPU {best['cpu']:.1f} ms)"]
    (DATA / "model_compare.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n저장: {DATA / 'model_compare.md'}")


if __name__ == "__main__":
    main()
