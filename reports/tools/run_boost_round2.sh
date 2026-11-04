#!/usr/bin/env bash
# 2차 성능 향상 실험 — 1차 결과를 근거로 '상승 가능성이 높은 것'만, 한 번에 한 가지씩 B 와 비교
# 서비스 모델 A 와 기존 B·C·D1·D2 는 건드리지 않는다. 새 모델은 모두 별도 폴더.
# 실행: cd ~/fastapi_resnet18 && source .venv/bin/activate && bash reports/tools/run_boost_round2.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p reports/data
COMMON="--data dataset --batch-size 8 --lr 0.00005"   # B 와 같은 Full FT 설정

train () {  # 이름 폴더 [옵션...]
  local name=$1 out=$2; shift 2
  if [ -f "$out/training_report.json" ]; then echo "   $name 이미 학습됨 → 건너뜀"; return; fi
  python -m training.finetune_plus $COMMON --output "$out" "$@" 2>&1 | tee "reports/data/train_log_${name}.txt"
}

echo "== F0. 재현 확인: finetune_plus 기본값 = 원본 B 와 같은지 (B 0.9699 가 다시 나와야 정상) =="
train F0_repro_B artifacts/beans_resnet18_full_repro --epochs 3

echo "== F1. 증강 + epoch 10 (D2 는 3 epoch 에서 아직 오르는 중이었음 → epoch 만 늘림) =="
train F1_full_aug_e10 artifacts/beans_resnet18_full_aug_e10 --epochs 10 --aug

echo "== F2. 해상도 384 (작은 녹병 돌기가 224 에서 뭉개짐 → 해상도만 올림) =="
train F2_full_384 artifacts/beans_resnet18_full_384 --epochs 3 --image-size 384

echo "== F3. 라벨 스무딩 0.1 (B 가 0.8 이상 확신하며 틀린 사례 → 과신 완화) =="
train F3_full_ls artifacts/beans_resnet18_full_ls --epochs 3 --label-smoothing 0.1

echo "== F4. seed 반복 (B 결과가 우연이 아닌지: seed 1, 2) =="
train F4_full_seed1 artifacts/beans_resnet18_full_seed1 --epochs 3 --seed 1
train F4_full_seed2 artifacts/beans_resnet18_full_seed2 --epochs 3 --seed 2

echo "== Test 1회 평가 =="
for pair in F1_full_aug_e10:artifacts/beans_resnet18_full_aug_e10 F2_full_384:artifacts/beans_resnet18_full_384 \
            F3_full_ls:artifacts/beans_resnet18_full_ls F4_full_seed1:artifacts/beans_resnet18_full_seed1 \
            F4_full_seed2:artifacts/beans_resnet18_full_seed2; do
  python reports/tools/evaluate_test.py --model "${pair#*:}" --name "${pair%%:*}"
done

echo "== TTA (재학습 없음) =="
python reports/tools/tta_eval.py \
  --model B_full_e3=artifacts/beans_resnet18_full --model D2_full_aug=artifacts/beans_resnet18_full_aug \
  --model F1_full_aug_e10=artifacts/beans_resnet18_full_aug_e10 --model F2_full_384=artifacts/beans_resnet18_full_384 \
  --model F3_full_ls=artifacts/beans_resnet18_full_ls

echo "== 전체 비교표 (정확도 + 크기 + CPU 추론시간) =="
ARGS=()
for pair in A_head_e3:beans_resnet18 C_head_e10:beans_resnet18_head_e10 B_full_e3:beans_resnet18_full \
            D1_head_e10_aug:beans_resnet18_head_e10_aug D2_full_aug:beans_resnet18_full_aug \
            F1_full_aug_e10:beans_resnet18_full_aug_e10 F2_full_384:beans_resnet18_full_384 \
            F3_full_ls:beans_resnet18_full_ls \
            E1_resnet50_full:beans_resnet50_full E2_effnetb0_full:beans_effnetb0_full \
            E3_convnext_tiny_full:beans_convnext_tiny_full E4_vit_base_full:beans_vit_base_full; do
  d="artifacts/${pair#*:}"; [ -f "$d/training_report.json" ] && ARGS+=(--model "${pair%%:*}=$d")
done
python reports/tools/model_benchmark.py "${ARGS[@]}"

echo
echo "완료. 터미널 출력 전체(또는 train_log_F*.txt 의 epoch 줄 + tta_eval.md + model_compare.md)를 붙여 주세요."
