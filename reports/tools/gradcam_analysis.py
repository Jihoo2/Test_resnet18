"""Grad-CAM 오분류 분석 (제공 코드 아님, 제공 코드·서비스 수정 없음).

목적: 평가가이드 6-2 'Heatmap(Grad-CAM)' — ResNet18 이 이미지의 어느 부분을 근거로 판단했는지 확인한다.
      **설명·오류 분석 도구이며 히트맵 생성으로 정확도가 오르지 않는다.**
      Test 이미지는 이미 끝난 1회 평가(test_pred_<name>.csv)의 결과를 '설명'하는 데만 쓰고,
      모델·임계값 선택에는 사용하지 않는다.

방법:
  - 대상 층: model.resnet.encoder.stages[-1] (마지막 Stage, 512 x 7 x 7 특징맵)
  - Grad-CAM = ReLU( Σ_k  mean(∂y_c/∂A_k) · A_k ), 224x224 로 확대해 입력 이미지 위에 표시
  - 입력: 저장된 AutoImageProcessor 로 전처리한 224x224 (학습·서비스와 같은 전처리)
  - cam_on_leaf: 히트맵 에너지 중 HSV 잎 마스크(hsv_lesion_analysis.py 와 같은 규칙) 안에 들어간 비율
                 → 1 에 가까울수록 잎을 보고 판단, 낮을수록 흙·손 등 배경을 본 것

실행:  python reports/tools/gradcam_analysis.py --model artifacts/beans_resnet18_full --name B_full_e3
결과:  reports/figures/gradcam/gradcam_<name>_errors.png, _correct.png
       reports/data/gradcam_<name>.csv, reports/data/gradcam_<name>.md
"""
import argparse
import csv
import statistics
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification


def leaf_mask(rgb: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), cv2.COLOR_BGR2HSV)
    gy = cv2.inRange(hsv, (20, 40, 40), (90, 255, 255))
    gy = cv2.morphologyEx(gy, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    contours, _ = cv2.findContours(gy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask = np.zeros_like(gy)
    if contours:
        cv2.drawContours(mask, [max(contours, key=cv2.contourArea)], -1, 255, thickness=cv2.FILLED)
    return mask > 0


def overlay(rgb: np.ndarray, cam: np.ndarray) -> np.ndarray:
    heat = cv2.applyColorMap(np.uint8(cam * 255), cv2.COLORMAP_JET)
    heat = cv2.cvtColor(heat, cv2.COLOR_BGR2RGB)
    return np.uint8(0.55 * rgb + 0.45 * heat)


ABBR = {"angular_leaf_spot": "ALS", "bean_rust": "RUST", "healthy": "HEALTHY"}


def titled(row: np.ndarray, title: str) -> np.ndarray:
    bar = np.full((24, row.shape[1], 3), 255, np.uint8)
    cv2.putText(bar, title, (6, 17), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
    return np.vstack([bar, row])


class GradCAM:
    def __init__(self, model):
        self.model = model
        self.store = {}
        layer = model.resnet.encoder.stages[-1]
        layer.register_forward_hook(self._hook)

    def _hook(self, module, inputs, output):
        self.store["act"] = output
        output.register_hook(lambda g: self.store.__setitem__("grad", g))

    def __call__(self, pixels: torch.Tensor, class_ids: list[int]):
        logits = self.model(pixel_values=pixels).logits
        probs = torch.softmax(logits, dim=-1)[0].detach().cpu()
        cams = []
        for i, cid in enumerate(class_ids):
            self.model.zero_grad(set_to_none=True)
            logits[0, cid].backward(retain_graph=i < len(class_ids) - 1)
            act, grad = self.store["act"].detach(), self.store["grad"].detach()
            weights = grad.mean(dim=(2, 3), keepdim=True)
            cam = torch.relu((weights * act).sum(dim=1, keepdim=True))
            cam = torch.nn.functional.interpolate(cam, size=pixels.shape[-2:], mode="bilinear", align_corners=False)
            cam = cam[0, 0].cpu().numpy()
            cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
            cams.append(cam)
        return probs, cams


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--name", required=True, help="test_pred_<name>.csv 의 name")
    ap.add_argument("--data", default="dataset/test")
    ap.add_argument("--max-errors", type=int, default=12, help="그림에 넣을 오분류 최대 수 (통계는 전체)")
    ap.add_argument("--correct-per-class", type=int, default=2, help="그림에 넣을 정분류 수 (클래스별)")
    args = ap.parse_args()

    processor = AutoImageProcessor.from_pretrained(args.model)
    model = AutoModelForImageClassification.from_pretrained(args.model)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()
    label2id = {v: int(k) for k, v in model.config.id2label.items()}
    mean = np.array(processor.image_mean).reshape(1, 1, 3)
    std = np.array(processor.image_std).reshape(1, 1, 3)
    cam_fn = GradCAM(model)

    with open(f"reports/data/test_pred_{args.name}.csv", encoding="utf-8") as f:
        preds = list(csv.DictReader(f))

    rows, err_panels, ok_panels, ok_count = [], [], [], {}
    for r in preds:
        gt, pd, correct = r["gt_label"], r["pred_label"], r["correct"] == "1"
        path = Path(args.data) / r["image"]
        with Image.open(path) as raw:
            img = raw.convert("RGB")
        pixels = processor(images=img, return_tensors="pt")["pixel_values"].to(device)
        targets = [label2id[pd]] if correct else [label2id[pd], label2id[gt]]
        probs, cams = cam_fn(pixels, targets)

        rgb = (pixels[0].detach().cpu().numpy().transpose(1, 2, 0) * std + mean).clip(0, 1)
        rgb = np.uint8(rgb * 255)
        leaf = leaf_mask(rgb)
        on_leaf = float((cams[0] * leaf).sum() / (cams[0].sum() + 1e-8))
        rows.append({"image": r["image"], "gt_label": gt, "pred_label": pd, "correct": int(correct),
                     "score": round(float(probs[label2id[pd]]), 4),
                     "leaf_coverage": round(float(leaf.mean()), 4), "cam_on_leaf": round(on_leaf, 4)})

        if not correct and len(err_panels) < args.max_errors:
            row = np.hstack([rgb, overlay(rgb, cams[0]), overlay(rgb, cams[1])])
            err_panels.append(titled(row, f"{Path(r['image']).stem} GT={ABBR[gt]} PRED={ABBR[pd]} {float(probs[label2id[pd]]):.2f}"
                                          f" | CAM(PRED) | CAM(GT) | leaf={on_leaf:.2f}"))
        if correct and ok_count.get(gt, 0) < args.correct_per_class:
            ok_count[gt] = ok_count.get(gt, 0) + 1
            row = np.hstack([rgb, overlay(rgb, cams[0])])
            ok_panels.append(titled(row, f"{Path(r['image']).stem} {ABBR[gt]} OK {float(probs[label2id[pd]]):.2f}"
                                         f" | leaf={on_leaf:.2f}"))

    out_fig = Path("reports/figures/gradcam")
    out_fig.mkdir(parents=True, exist_ok=True)
    if err_panels:
        Image.fromarray(np.vstack(err_panels)).save(out_fig / f"gradcam_{args.name}_errors.png")
    if ok_panels:
        Image.fromarray(np.vstack(ok_panels)).save(out_fig / f"gradcam_{args.name}_correct.png")
    with open(f"reports/data/gradcam_{args.name}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    def summary(group):
        if not group:
            return "0 | - | - | -"
        vals = [g["cam_on_leaf"] for g in group]
        low = sum(v < 0.5 for v in vals)
        return f"{len(group)} | {statistics.mean(vals):.4f} | {statistics.median(vals):.4f} | {low}"
    ok = [r for r in rows if r["correct"]]
    bad = [r for r in rows if not r["correct"]]
    md = [f"# Grad-CAM 오분류 분석: {args.name}", "",
          f"- 모델: `{args.model}` / 대상 층: `resnet.encoder.stages[-1]` (512x7x7) / 장치: {device}",
          "- 히트맵은 **설명·오류 분석용**이며 정확도 개선과 무관. Test 결과를 설명만 하고 선택에 쓰지 않음", "",
          "## cam_on_leaf (히트맵 에너지 중 잎 마스크 안 비율, 예측 클래스 기준)", "",
          "| 구분 | n | 평균 | 중앙값 | 0.5 미만(배경 주목) 수 |", "|---|---:|---:|---:|---:|",
          f"| 정분류 | {summary(ok)} |", f"| 오분류 | {summary(bad)} |", "",
          "## 그림", "",
          f"- 오분류: `reports/figures/gradcam/gradcam_{args.name}_errors.png` (원본 | 예측 클래스 CAM | 정답 클래스 CAM)",
          "- 그림 약어: ALS=angular_leaf_spot, RUST=bean_rust, leaf=cam_on_leaf",
          f"- 정분류 예시: `reports/figures/gradcam/gradcam_{args.name}_correct.png`", "",
          "## 오분류 상세", "", "| 파일 | 정답 | 예측 | score | cam_on_leaf |", "|---|---|---|---:|---:|"]
    md += [f"| {Path(r['image']).name} | {r['gt_label']} | {r['pred_label']} | {r['score']} | {r['cam_on_leaf']} |" for r in bad]
    text = "\n".join(md) + "\n"
    Path(f"reports/data/gradcam_{args.name}.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
