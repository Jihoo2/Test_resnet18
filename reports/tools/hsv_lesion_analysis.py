"""교과 9 OpenCV HSV 병반 특징 분석 (제공 코드 아님, 제공 코드·서비스 수정 없음).

목적: 평가가이드 6-2 'HSV 색공간 / Morphology / Contour' 제안의 근거를 실제 데이터로 측정한다.
      서비스(ResNet18) 결과를 바꾸지 않는 '분석 실험'이며 성능 향상을 주장하지 않는다.

처리 (이미지 1장):
  1) RGB → HSV (OpenCV: H 0~179, S/V 0~255)
  2) 잎 마스크  : 녹색~황색(H 20~90, S>=40, V>=40) → Closing → 가장 큰 Contour 내부 채움
                  (잎 안의 갈색 병반도 잎 영역에 포함되도록 내부를 채움, 붉은 흙 배경은 제외)
  3) 병반 후보  : 잎 마스크 안에서 '건강한 녹색'(H 35~90, S>=60)이 아닌 픽셀 → Opening
  4) 특징값     : lesion_ratio = 병반 후보 / 잎 픽셀, spot_count(면적 >= min_area 인 Contour 수),
                  leaf_coverage = 잎 픽셀 / 전체, 잎 영역 평균 H·S·V

규칙 기반 참고 베이스라인 (가이드 6-3 'B. OpenCV Rule 단독'):
  healthy vs 질병(angular_leaf_spot + bean_rust) 2분류를 lesion_ratio 임계값 하나로 판정.
  임계값은 Train 에서만 정하고 Validation 에서 1회 확인한다. Test 는 사용하지 않는다.

실행:  python reports/tools/hsv_lesion_analysis.py
결과:  reports/data/hsv_features_{train,val}.csv, reports/data/hsv_analysis.md, reports/figures/hsv/*.png
"""
import argparse
import csv
import statistics
from pathlib import Path

import cv2
import numpy as np

CLASSES = ["angular_leaf_spot", "bean_rust", "healthy"]
EXTS = {".jpg", ".jpeg", ".png", ".webp"}
SIZE = 256  # 분석 해상도 (원본 500x500 → 256x256, 처리 속도·노이즈 감소)


def leaf_and_lesion(bgr: np.ndarray, min_area: int = 12):
    img = cv2.resize(bgr, (SIZE, SIZE), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    green_yellow = cv2.inRange(hsv, (20, 40, 40), (90, 255, 255))
    green_yellow = cv2.morphologyEx(green_yellow, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    contours, _ = cv2.findContours(green_yellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    leaf = np.zeros_like(green_yellow)
    if contours:
        biggest = max(contours, key=cv2.contourArea)
        cv2.drawContours(leaf, [biggest], -1, 255, thickness=cv2.FILLED)

    healthy_green = cv2.inRange(hsv, (35, 60, 0), (90, 255, 255))
    lesion = cv2.bitwise_and(leaf, cv2.bitwise_not(healthy_green))
    lesion = cv2.morphologyEx(lesion, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    spots, _ = cv2.findContours(lesion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    spot_count = sum(1 for c in spots if cv2.contourArea(c) >= min_area)

    leaf_px = int(np.count_nonzero(leaf))
    lesion_px = int(np.count_nonzero(lesion))
    sel = leaf > 0
    feats = {
        "leaf_coverage": round(leaf_px / leaf.size, 4),
        "lesion_ratio": round(lesion_px / leaf_px, 4) if leaf_px else 0.0,
        "spot_count": spot_count,
        "mean_h": round(float(h[sel].mean()), 2) if leaf_px else 0.0,
        "mean_s": round(float(s[sel].mean()), 2) if leaf_px else 0.0,
        "mean_v": round(float(v[sel].mean()), 2) if leaf_px else 0.0,
    }
    return img, leaf, lesion, feats


def panel(img, leaf, lesion, title: str) -> np.ndarray:
    """원본 | 잎 마스크 | 병반 후보(빨강) 오버레이 를 가로로 붙인 시각화."""
    leaf_bgr = cv2.cvtColor(leaf, cv2.COLOR_GRAY2BGR)
    over = img.copy()
    over[lesion > 0] = (0, 0, 255)
    over = cv2.addWeighted(img, 0.45, over, 0.55, 0)
    row = np.hstack([img, leaf_bgr, over])
    bar = np.full((24, row.shape[1], 3), 255, np.uint8)
    cv2.putText(bar, title, (6, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return np.vstack([bar, row])


def analyse_split(root: Path, split: str):
    rows = []
    for c in CLASSES:
        for p in sorted((root / split / c).iterdir()):
            if p.suffix.lower() not in EXTS:
                continue
            bgr = cv2.imread(str(p))
            if bgr is None:
                continue
            _, _, _, f = leaf_and_lesion(bgr)
            rows.append({"split": split, "image": f"{c}/{p.name}", "gt_label": c, **f})
    return rows


def best_threshold(rows):
    """Train 에서 healthy(<=t) / 질병(>t) 판정 정확도가 최대인 lesion_ratio 임계값."""
    vals = sorted({r["lesion_ratio"] for r in rows})
    cands = [(a + b) / 2 for a, b in zip(vals, vals[1:])] or vals
    def acc(t):
        return sum((r["lesion_ratio"] > t) == (r["gt_label"] != "healthy") for r in rows) / len(rows)
    t = max(cands, key=acc)
    return round(t, 4), acc(t)


def rule_eval(rows, t):
    tp = sum(r["gt_label"] != "healthy" and r["lesion_ratio"] > t for r in rows)
    tn = sum(r["gt_label"] == "healthy" and r["lesion_ratio"] <= t for r in rows)
    fp = sum(r["gt_label"] == "healthy" and r["lesion_ratio"] > t for r in rows)
    fn = sum(r["gt_label"] != "healthy" and r["lesion_ratio"] <= t for r in rows)
    return tp, tn, fp, fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="dataset")
    ap.add_argument("--samples", type=int, default=2, help="클래스별 시각화 샘플 수 (train)")
    args = ap.parse_args()
    root = Path(args.data)
    out_data, out_fig = Path("reports/data"), Path("reports/figures/hsv")
    out_data.mkdir(parents=True, exist_ok=True)
    out_fig.mkdir(parents=True, exist_ok=True)

    result = {}
    for split in ("train", "val"):
        rows = analyse_split(root, split)
        result[split] = rows
        with (out_data / f"hsv_features_{split}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    panels = []
    for c in CLASSES:
        files = [p for p in sorted((root / "train" / c).iterdir()) if p.suffix.lower() in EXTS][: args.samples]
        for p in files:
            img, leaf, lesion, f = leaf_and_lesion(cv2.imread(str(p)))
            panels.append(panel(img, leaf, lesion,
                                f"{c}/{p.name}  lesion_ratio={f['lesion_ratio']}  spots={f['spot_count']}"))
    cv2.imwrite(str(out_fig / "hsv_mask_examples.png"), np.vstack(panels))

    md = ["# HSV 병반 특징 분석 (교과 9 OpenCV, 분석 실험)", "",
          "- 스크립트: `reports/tools/hsv_lesion_analysis.py` / 서비스 코드 미변경 / 성능 개선 주장 없음",
          f"- 분석 해상도 {SIZE}x{SIZE}, OpenCV HSV(H 0~179)",
          "- 잎: H 20~90·S>=40·V>=40 → Closing 7x7 → 최대 Contour 내부 채움",
          "- 병반 후보: 잎 내부 중 '건강한 녹색'(H 35~90·S>=60)이 아닌 픽셀 → Opening 3x3",
          "- 데이터: Train(기준 개발), Validation(확인). **Test 미사용**", ""]
    md += ["## 1. 클래스별 특징값 (중앙값)", "",
           "| Split | 클래스 | n | lesion_ratio | spot_count | leaf_coverage | 잎 평균 H | 잎 평균 S |",
           "|---|---|---:|---:|---:|---:|---:|---:|"]
    for split in ("train", "val"):
        for c in CLASSES:
            g = [r for r in result[split] if r["gt_label"] == c]
            med = lambda k: round(statistics.median(r[k] for r in g), 4)
            md.append(f"| {split} | {c} | {len(g)} | {med('lesion_ratio')} | {med('spot_count')} | "
                      f"{med('leaf_coverage')} | {med('mean_h')} | {med('mean_s')} |")

    t, train_acc = best_threshold(result["train"])
    md += ["", "## 2. 규칙 기반 참고 베이스라인: healthy vs 질병 (lesion_ratio 임계값 1개)", "",
           f"- 임계값: **lesion_ratio > {t} → 질병** (Train {len(result['train'])}장에서 정확도 최대가 되도록 결정)", "",
           "| Split | 정확도 | TP(질병→질병) | TN(정상→정상) | FP(정상→질병) | FN(질병→정상) |",
           "|---|---:|---:|---:|---:|---:|"]
    for split in ("train", "val"):
        tp, tn, fp, fn = rule_eval(result[split], t)
        n = tp + tn + fp + fn
        md.append(f"| {split} | {(tp + tn) / n:.4f} ({tp + tn}/{n}) | {tp} | {tn} | {fp} | {fn} |")

    md += ["", "## 3. 병명 구분(angular_leaf_spot vs bean_rust)에 대한 관찰", "",
           "- 위 1번 표에서 두 질병의 lesion_ratio·spot_count 중앙값 차이를 확인한다.",
           "- 면적비는 '병반이 있는가'에는 반응하지만 '어떤 병인가'를 구분하는 근거로는 약할 수 있다 → 수치로 판단",
           "", "## 4. 시각화", "", "![HSV 마스크 예시](../figures/hsv/hsv_mask_examples.png)", "",
           "## 5. 한계", "",
           "- 임계값은 이 데이터 촬영 조건(우간다 밭, 자연광)에 맞춘 값이며 조명·흙 색이 바뀌면 다시 정해야 함",
           "- 노랗게 시든 정상 잎, 그림자, 손가락 등이 병반·잎 마스크에 섞일 수 있음",
           "- HSV 마스크는 병명을 확정하는 농업학적 진단 근거가 아님"]
    text = "\n".join(md) + "\n"
    (out_data / "hsv_analysis.md").write_text(text, encoding="utf-8")
    print(text)
    print("저장: reports/data/hsv_analysis.md, hsv_features_train.csv, hsv_features_val.csv, figures/hsv/hsv_mask_examples.png")


if __name__ == "__main__":
    main()
