# CNN + ML 융합 분석 (가이드 6-3 D)

- 특징: CNN 확률 3개 + HSV 6개 / 보조 분류기: LogisticRegression, RandomForest
- Validation 133장 5겹 층화 교차검증으로 비교 → 더 나은 융합 모델 1개만 Test 에 1회 적용
- 한계: Train 은 CNN 이 학습한 사진이라 사용 불가 → Val 안에서 교차검증. Val 은 CNN 모델 선택에도 쓰였음

| 모델 | 방법 | Val 정확도 (5겹 CV) | Test 정확도 (1회) | 판정 |
|---|---|---:|---:|---|
| A_head_e3 | CNN 단독 | 0.7669 | 0.7188 | 기준선 |
| A_head_e3 | HSV 단독 (RF) | 0.6541 | — | 참고 |
| A_head_e3 | 융합 LR | 0.7594 | — |  |
| A_head_e3 | 융합 RF ← 선택 | 0.7895 | 0.7812 | Test 향상 (+6.25%p) |
| B_full_e3 | CNN 단독 | 0.9699 | 0.9531 | 기준선 |
| B_full_e3 | HSV 단독 (RF) | 0.6541 | — | 참고 |
| B_full_e3 | 융합 LR ← 선택 | 0.9624 | 0.9375 | Test 하락 (-1.56%p) |
| B_full_e3 | 융합 RF | 0.9474 | — |  |

## A_head_e3 — 융합이 CNN 판정을 바꾼 Test 이미지 (27장)

| 이미지 | CNN | 융합 | 정답 | 결과 |
|---|---|---|---|---|
| angular_leaf_spot/angular_leaf_spot_test.0.jpg | angular_leaf_spot | bean_rust | angular_leaf_spot | ❌ 망침 |
| angular_leaf_spot/angular_leaf_spot_test.13.jpg | angular_leaf_spot | bean_rust | angular_leaf_spot | ❌ 망침 |
| angular_leaf_spot/angular_leaf_spot_test.14.jpg | bean_rust | angular_leaf_spot | angular_leaf_spot | ✅ 고침 |
| angular_leaf_spot/angular_leaf_spot_test.15.jpg | bean_rust | angular_leaf_spot | angular_leaf_spot | ✅ 고침 |
| angular_leaf_spot/angular_leaf_spot_test.18.jpg | angular_leaf_spot | bean_rust | angular_leaf_spot | ❌ 망침 |
| angular_leaf_spot/angular_leaf_spot_test.20.jpg | healthy | bean_rust | angular_leaf_spot | − 둘 다 오답 |
| angular_leaf_spot/angular_leaf_spot_test.24.jpg | healthy | bean_rust | angular_leaf_spot | − 둘 다 오답 |
| angular_leaf_spot/angular_leaf_spot_test.36.jpg | healthy | bean_rust | angular_leaf_spot | − 둘 다 오답 |
| angular_leaf_spot/angular_leaf_spot_test.37.jpg | angular_leaf_spot | bean_rust | angular_leaf_spot | ❌ 망침 |
| angular_leaf_spot/angular_leaf_spot_test.38.jpg | healthy | bean_rust | angular_leaf_spot | − 둘 다 오답 |
| angular_leaf_spot/angular_leaf_spot_test.41.jpg | bean_rust | angular_leaf_spot | angular_leaf_spot | ✅ 고침 |
| angular_leaf_spot/angular_leaf_spot_test.42.jpg | healthy | bean_rust | angular_leaf_spot | − 둘 다 오답 |
| angular_leaf_spot/angular_leaf_spot_test.5.jpg | bean_rust | angular_leaf_spot | angular_leaf_spot | ✅ 고침 |
| angular_leaf_spot/angular_leaf_spot_test.7.jpg | angular_leaf_spot | bean_rust | angular_leaf_spot | ❌ 망침 |
| bean_rust/bean_rust_test.10.jpg | angular_leaf_spot | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.15.jpg | angular_leaf_spot | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.19.jpg | angular_leaf_spot | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.20.jpg | angular_leaf_spot | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.28.jpg | healthy | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.29.jpg | healthy | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.3.jpg | healthy | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.40.jpg | angular_leaf_spot | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.41.jpg | healthy | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.6.jpg | angular_leaf_spot | bean_rust | bean_rust | ✅ 고침 |
| bean_rust/bean_rust_test.7.jpg | healthy | bean_rust | bean_rust | ✅ 고침 |
| healthy/healthy_test.27.jpg | healthy | bean_rust | healthy | ❌ 망침 |
| healthy/healthy_test.36.jpg | healthy | bean_rust | healthy | ❌ 망침 |

RF 특징 중요도: p_healthy 0.226, p_bean_rust 0.184, p_angular_leaf_spot 0.173, leaf_coverage 0.112, mean_h 0.088, lesion_ratio 0.070, mean_s 0.062, spot_count 0.044, mean_v 0.041

## B_full_e3 — 융합이 CNN 판정을 바꾼 Test 이미지 (2장)

| 이미지 | CNN | 융합 | 정답 | 결과 |
|---|---|---|---|---|
| bean_rust/bean_rust_test.37.jpg | bean_rust | healthy | bean_rust | ❌ 망침 |
| healthy/healthy_test.40.jpg | healthy | angular_leaf_spot | healthy | ❌ 망침 |
