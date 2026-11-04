#!/usr/bin/env bash
# 추가 성능 실험 일괄 실행 (가이드 6-3 의 C·D + 00 문서 권장 1순위 '이미지 증강')
# 실행: cd ~/fastapi_resnet18 && source .venv/bin/activate && bash reports/tools/run_extra_experiments.sh
# 서비스 모델 artifacts/beans_resnet18 (A) 은 건드리지 않는다. 새 모델은 모두 별도 폴더.
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p reports/data

echo "== 0. 분석 전용 패키지 =="
python -m pip install -q scikit-learn opencv-python-headless

echo "== 1. 증강 실험 (원본 finetune.py 는 그대로, finetune_aug.py 사용) =="
# D1: C(Head-only 10ep) 와 비교 — 바뀐 것은 증강 하나
python -m training.finetune_aug --data dataset --output artifacts/beans_resnet18_head_e10_aug \
  --epochs 10 --batch-size 8 --freeze-backbone 2>&1 | tee reports/data/train_log_head_e10_aug.txt
# D2: B(Full FT 3ep, lr 5e-5) 와 비교 — 바뀐 것은 증강 하나
python -m training.finetune_aug --data dataset --output artifacts/beans_resnet18_full_aug \
  --epochs 3 --batch-size 8 --lr 0.00005 2>&1 | tee reports/data/train_log_full_aug.txt

echo "== 2. 증강 모델 Test 1회 평가 (모델 선택은 위 Validation 결과로 끝난 뒤) =="
python reports/tools/evaluate_test.py --model artifacts/beans_resnet18_head_e10_aug --name D1_head_e10_aug
python reports/tools/evaluate_test.py --model artifacts/beans_resnet18_full_aug     --name D2_full_aug

echo "== 3. 클래스별 확률 저장 (A 서비스 모델, B Full FT) =="
for split in val test; do
  python reports/tools/predict_split.py --model artifacts/beans_resnet18      --name A_head_e3 --split $split
  python reports/tools/predict_split.py --model artifacts/beans_resnet18_full --name B_full_e3 --split $split
done

echo "== 4. CNN + 규칙: '확인 필요' 보류 (가이드 6-3 C) =="
python reports/tools/review_flag_analysis.py --name A_head_e3 --name B_full_e3

echo "== 5. CNN + ML 융합 (가이드 6-3 D) =="
python reports/tools/fusion_analysis.py --name A_head_e3 --name B_full_e3

echo
echo "완료. 아래 파일을 채팅에 붙여 주세요:"
echo "  reports/data/train_log_head_e10_aug.txt  reports/data/train_log_full_aug.txt"
echo "  reports/data/test_eval_D1_head_e10_aug.md  reports/data/test_eval_D2_full_aug.md"
echo "  reports/data/review_flag.md  reports/data/fusion_analysis.md"
