#!/usr/bin/env bash
# 3차(마지막) 확인 실험 — 2차에서 찾은 '증강 학습 + TTA(hv4)' 효과가 우연이 아닌지 seed 를 바꿔 재현 확인
# + 라벨 스무딩(F3) 이 '확인 필요' 보류를 더 효율적으로 만드는지 확인
# 새 학습은 2회뿐 (D2 와 같은 설정, seed 만 1·2). 서비스 모델 A 는 그대로.
# 실행: cd ~/fastapi_resnet18 && source .venv/bin/activate && bash reports/tools/run_boost_round3.sh
set -euo pipefail
cd "$(dirname "$0")/../.."
COMMON="--data dataset --batch-size 8 --lr 0.00005 --epochs 3 --aug"   # = D2 설정

for s in 1 2; do
  out=artifacts/beans_resnet18_full_aug_seed$s
  echo "== G$s. 증강 Full FT 3ep, seed $s (D2 와 seed 만 다름) =="
  if [ -f "$out/training_report.json" ]; then echo "   이미 학습됨 → 건너뜀"
  else python -m training.finetune_plus $COMMON --seed $s --output $out 2>&1 | tee reports/data/train_log_G${s}_full_aug_seed$s.txt; fi
done

echo "== TTA hv4 고정 — 증강 모델 3개 vs 비증강 모델 3개 (각각 seed 42·1·2) =="
python reports/tools/tta_eval.py --mode hv4 --out tta_round3.md \
  --model D2_full_aug=artifacts/beans_resnet18_full_aug \
  --model G1_full_aug_seed1=artifacts/beans_resnet18_full_aug_seed1 \
  --model G2_full_aug_seed2=artifacts/beans_resnet18_full_aug_seed2 \
  --model B_full_e3=artifacts/beans_resnet18_full \
  --model F4_full_seed1=artifacts/beans_resnet18_full_seed1 \
  --model F4_full_seed2=artifacts/beans_resnet18_full_seed2

echo "== 라벨 스무딩 + 확인 필요 보류 (B 와 F3 비교) =="
for split in val test; do
  python reports/tools/predict_split.py --model artifacts/beans_resnet18_full_ls --name F3_full_ls --split $split
done
[ -f reports/data/review_flag.md ] && [ ! -f reports/data/review_flag_round1.md ] && cp reports/data/review_flag.md reports/data/review_flag_round1.md   # 1차(A·B) 결과 보존
python reports/tools/review_flag_analysis.py --name B_full_e3 --name F3_full_ls

echo
echo "완료. 터미널 출력 전체를 붙여 주세요."
