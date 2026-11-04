"""CNN + ML 융합: ResNet18 클래스별 확률 + HSV 특징 → 보조 분류기 (평가가이드 6-3 D).

설계 (실행 전 고정)
- 특징: CNN 확률 3개 (p_angular_leaf_spot, p_bean_rust, p_healthy)
        + HSV 6개 (leaf_coverage, lesion_ratio, spot_count, mean_h, mean_s, mean_v)
- 보조 분류기: LogisticRegression(표준화) / RandomForest(300그루, random_state=42)
- 학습·비교 데이터: Validation 133장의 5겹 층화 교차검증 (random_state=42)
    * Train 1,034장은 CNN 이 이미 학습한 사진이라 CNN 확률이 과하게 정확함 → 융합 학습에 쓰면 누출
    * 따라서 CNN 이 보지 않은 Validation 안에서 교차검증 (한계: Val 은 CNN 모델 선택에도 쓰였음)
- 비교 대상 (같은 133장): CNN 단독 / HSV 단독(RF) / 융합 LR / 융합 RF
- 최종: 교차검증 정확도가 높은 융합 모델 1개를 Val 전체로 다시 학습 → Test 에 1회 적용

입력: reports/data/pred_{val,test}_<name>.csv, reports/data/hsv_features_val.csv
      (Test HSV 특징은 이 스크립트가 hsv_lesion_analysis 의 같은 함수로 계산해 hsv_features_test.csv 로 저장)
실행: python -m pip install scikit-learn opencv-python-headless   (분석 전용)
      python reports/tools/fusion_analysis.py --name A_head_e3 --name B_full_e3
결과: reports/data/fusion_analysis.md
"""
import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hsv_lesion_analysis import analyse_split  # noqa: E402  (같은 HSV 특징 정의 재사용)

DATA = Path("reports/data")
CLASSES = ["angular_leaf_spot", "bean_rust", "healthy"]
P_COLS = [f"p_{c}" for c in CLASSES]
HSV_COLS = ["leaf_coverage", "lesion_ratio", "spot_count", "mean_h", "mean_s", "mean_v"]


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def hsv_table(split, data_root):
    path = DATA / f"hsv_features_{split}.csv"
    if not path.exists():
        rows = analyse_split(Path(data_root), split)
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print(f"{path} 생성 ({len(rows)}장)")
    return {r["image"]: r for r in read_csv(path)}


def build(split, name, hsv):
    pred = read_csv(DATA / f"pred_{split}_{name}.csv")
    missing = [r["image"] for r in pred if r["image"] not in hsv]
    if missing:
        raise SystemExit(f"HSV 특징이 없는 이미지 {len(missing)}장: {missing[:3]}")
    x_cnn = np.array([[float(r[c]) for c in P_COLS] for r in pred])
    x_hsv = np.array([[float(hsv[r["image"]][c]) for c in HSV_COLS] for r in pred])
    y = np.array([CLASSES.index(r["gt_label"]) for r in pred])
    images = [r["image"] for r in pred]
    return x_cnn, x_hsv, y, images


def models():
    return {
        "융합 LR": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
        "융합 RF": RandomForestClassifier(n_estimators=300, random_state=42),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", action="append", required=True)
    ap.add_argument("--data", default="dataset")
    args = ap.parse_args()

    hsv_val, hsv_test = hsv_table("val", args.data), hsv_table("test", args.data)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    out = ["# CNN + ML 융합 분석 (가이드 6-3 D)", "",
           "- 특징: CNN 확률 3개 + HSV 6개 / 보조 분류기: LogisticRegression, RandomForest",
           "- Validation 133장 5겹 층화 교차검증으로 비교 → 더 나은 융합 모델 1개만 Test 에 1회 적용",
           "- 한계: Train 은 CNN 이 학습한 사진이라 사용 불가 → Val 안에서 교차검증. Val 은 CNN 모델 선택에도 쓰였음",
           "", "| 모델 | 방법 | Val 정확도 (5겹 CV) | Test 정확도 (1회) | 판정 |", "|---|---|---:|---:|---|"]
    detail = []
    for name in args.name:
        xc, xh, y, _ = build("val", name, hsv_val)
        tc, th, ty, timg = build("test", name, hsv_test)
        x_all, t_all = np.hstack([xc, xh]), np.hstack([tc, th])

        cnn_val = float((xc.argmax(1) == y).mean())
        cnn_test = float((tc.argmax(1) == ty).mean())
        hsv_only = cross_val_predict(RandomForestClassifier(n_estimators=300, random_state=42), xh, y, cv=cv)
        res = {"CNN 단독": cnn_val, "HSV 단독 (RF)": float((hsv_only == y).mean())}
        for label, m in models().items():
            res[label] = float((cross_val_predict(m, x_all, y, cv=cv) == y).mean())

        best_label = max(["융합 LR", "융합 RF"], key=lambda k: res[k])
        final = models()[best_label].fit(x_all, y)
        fused_test_pred = final.predict(t_all)
        fused_test = float((fused_test_pred == ty).mean())
        verdict = ("향상" if fused_test > cnn_test else "동일" if fused_test == cnn_test else "하락")

        out.append(f"| {name} | CNN 단독 | {cnn_val:.4f} | {cnn_test:.4f} | 기준선 |")
        out.append(f"| {name} | HSV 단독 (RF) | {res['HSV 단독 (RF)']:.4f} | — | 참고 |")
        for k in ("융합 LR", "융합 RF"):
            sel = k == best_label
            out.append(f"| {name} | {k}{' ← 선택' if sel else ''} | {res[k]:.4f} | "
                       f"{f'{fused_test:.4f}' if sel else '—'} | "
                       f"{f'Test {verdict} ({(fused_test - cnn_test) * 100:+.2f}%p)' if sel else ''} |")

        changed = [(img, CLASSES[c], CLASSES[f], CLASSES[g]) for img, c, f, g
                   in zip(timg, tc.argmax(1), fused_test_pred, ty) if c != f]
        detail += [f"## {name} — 융합이 CNN 판정을 바꾼 Test 이미지 ({len(changed)}장)", "",
                   "| 이미지 | CNN | 융합 | 정답 | 결과 |", "|---|---|---|---|---|"]
        detail += [f"| {i} | {c} | {f} | {g} | {'✅ 고침' if f == g else ('❌ 망침' if c == g else '− 둘 다 오답')} |"
                   for i, c, f, g in changed] or ["| (없음) | | | | |"]
        detail.append("")
        if best_label == "융합 RF":
            imp = sorted(zip(P_COLS + HSV_COLS, final.feature_importances_), key=lambda x: -x[1])
            detail += ["RF 특징 중요도: " + ", ".join(f"{k} {v:.3f}" for k, v in imp), ""]

    (DATA / "fusion_analysis.md").write_text("\n".join(out + [""] + detail), encoding="utf-8")
    print("\n".join(out))
    print(f"\n저장: {DATA / 'fusion_analysis.md'}")


if __name__ == "__main__":
    main()
