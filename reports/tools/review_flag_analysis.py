"""CNN + 규칙: 낮은 확신도 예측을 '확인 필요'로 보류 (평가가이드 6-2 규칙 후처리 · 6-3 C).

- 규칙: top1 score < t 이면 판정 보류(review_required), 아니면 AI 결과 그대로 수용.
  3클래스 예측 자체는 바꾸지 않는다 (가이드: 병명 라벨을 강제 변경하지 않음).
- 기준값 t 는 Validation 으로만 고른다. 선택 규칙은 실행 전에 고정:
    "Val 보류율 ≤ MAX_REVIEW(20%) 인 t 중 수용 정확도 최대, 동률이면 보류율이 낮은 t"
- 고른 t 를 Test 에 1번만 적용해 확인한다.
- 정확도와 보류율을 항상 함께 기록한다 (보류를 늘리면 수용 정확도는 당연히 오르기 때문).

입력: reports/data/pred_val_<name>.csv, pred_test_<name>.csv  (predict_split.py)
실행: python reports/tools/review_flag_analysis.py --name A_head_e3 --name B_full_e3
결과: reports/data/review_flag.md
"""
import argparse
import csv
from pathlib import Path

DATA = Path("reports/data")
THRESHOLDS = [round(0.35 + 0.05 * i, 2) for i in range(13)]  # 0.35 ~ 0.95


def load(split, name):
    with (DATA / f"pred_{split}_{name}.csv").open(encoding="utf-8") as f:
        return [{"score": float(r["score"]), "correct": int(r["correct"]), "image": r["image"],
                 "gt": r["gt_label"], "pred": r["pred_label"]} for r in csv.DictReader(f)]


def stats(rows, t):
    n = len(rows)
    flagged = [r for r in rows if r["score"] < t]
    accepted = [r for r in rows if r["score"] >= t]
    acc_ok = sum(r["correct"] for r in accepted)
    wrong_flagged = sum(1 - r["correct"] for r in flagged)
    return {
        "t": t, "n": n, "flag": len(flagged), "review_rate": len(flagged) / n,
        "accepted_acc": acc_ok / len(accepted) if accepted else 0.0,
        "wrong_passed": (len(accepted) - acc_ok) / n,          # 보류 안 되고 통과한 오답 / 전체
        "flag_precision": wrong_flagged / len(flagged) if flagged else 0.0,  # 보류된 것 중 실제 오답
        "errors_caught": wrong_flagged, "errors_total": n - sum(r["correct"] for r in rows),
    }


def choose(rows, max_review):
    cands = [stats(rows, t) for t in THRESHOLDS]
    ok = [s for s in cands if s["review_rate"] <= max_review]
    return max(ok, key=lambda s: (round(s["accepted_acc"], 6), -s["review_rate"])), cands


def fmt(s, mark=""):
    return (f"| {s['t']:.2f}{mark} | {s['flag']}/{s['n']} ({s['review_rate']:.1%}) | {s['accepted_acc']:.4f} | "
            f"{s['wrong_passed']:.1%} | {s['errors_caught']}/{s['errors_total']} | {s['flag_precision']:.1%} |")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", action="append", required=True)
    ap.add_argument("--max-review", type=float, default=0.20)
    args = ap.parse_args()

    head = ("| 기준 t | 보류 (보류율) | 수용 정확도 | 통과한 오답 | 잡아낸 오답 | 보류 중 실제 오답 |\n"
            "|---:|---:|---:|---:|---:|---:|")
    out = ["# CNN + 규칙: '확인 필요' 보류 분석 (가이드 6-3 C)", "",
           f"- 규칙: top1 score < t 이면 보류, 아니면 AI 결과 수용. 3클래스 예측은 바꾸지 않음",
           f"- t 선택: Validation 에서 **보류율 ≤ {args.max_review:.0%}** 인 t 중 수용 정확도 최대 (실행 전 고정)",
           "- Test 는 선택된 t 로 1회만 확인", "",
           "용어: 보류율 = 사람이 다시 볼 비율 / 수용 정확도 = 보류 안 된 것 중 정답 비율 / "
           "통과한 오답 = 보류되지 않고 그대로 나간 오답 ÷ 전체", ""]
    summary = ["## 요약", "",
               "| 모델 | 구분 | CNN 단독 정확도 | 선택 t | 보류율 | 수용 정확도 | 통과한 오답 |",
               "|---|---|---:|---:|---:|---:|---:|"]
    for name in args.name:
        val, test = load("val", name), load("test", name)
        best, cands = choose(val, args.max_review)
        tst = stats(test, best["t"])
        base_v = sum(r["correct"] for r in val) / len(val)
        base_t = sum(r["correct"] for r in test) / len(test)
        out += [f"## {name}", "", f"### Validation ({len(val)}장) — 기준값 후보", "", head]
        out += [fmt(s, " ← 선택" if s["t"] == best["t"] else "") for s in cands]
        out += ["", f"### Test ({len(test)}장) — t = {best['t']:.2f} 1회 적용", "", head, fmt(tst), ""]
        missed = [r for r in test if r["score"] >= best["t"] and not r["correct"]]
        if missed:
            out += ["보류되지 않고 통과한 Test 오답 (자신 있게 틀린 사례):", ""]
            out += [f"- {r['image']} → {r['pred']} ({r['score']:.4f})" for r in missed]
            out.append("")
        summary.append(f"| {name} | Val | {base_v:.4f} | {best['t']:.2f} | {best['review_rate']:.1%} | "
                       f"{best['accepted_acc']:.4f} | {best['wrong_passed']:.1%} |")
        summary.append(f"| {name} | Test | {base_t:.4f} | {best['t']:.2f} | {tst['review_rate']:.1%} | "
                       f"{tst['accepted_acc']:.4f} | {tst['wrong_passed']:.1%} |")
    text = "\n".join(out[:7] + summary + [""] + out[7:])
    (DATA / "review_flag.md").write_text(text, encoding="utf-8")
    print("\n".join(summary))
    print(f"\n저장: {DATA / 'review_flag.md'}")


if __name__ == "__main__":
    main()
