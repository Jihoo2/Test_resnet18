# CNN + 규칙: '확인 필요' 보류 분석 (가이드 6-3 C)

- 규칙: top1 score < t 이면 보류, 아니면 AI 결과 수용. 3클래스 예측은 바꾸지 않음
- t 선택: Validation 에서 **보류율 ≤ 20%** 인 t 중 수용 정확도 최대 (실행 전 고정)
- Test 는 선택된 t 로 1회만 확인

용어: 보류율 = 사람이 다시 볼 비율 / 수용 정확도 = 보류 안 된 것 중 정답 비율 / 통과한 오답 = 보류되지 않고 그대로 나간 오답 ÷ 전체
## 요약

| 모델 | 구분 | CNN 단독 정확도 | 선택 t | 보류율 | 수용 정확도 | 통과한 오답 |
|---|---|---:|---:|---:|---:|---:|
| A_head_e3 | Val | 0.7669 | 0.35 | 0.8% | 0.7727 | 22.6% |
| A_head_e3 | Test | 0.7188 | 0.35 | 0.0% | 0.7188 | 28.1% |
| B_full_e3 | Val | 0.9699 | 0.85 | 15.8% | 1.0000 | 0.0% |
| B_full_e3 | Test | 0.9531 | 0.85 | 19.5% | 0.9903 | 0.8% |


## A_head_e3

### Validation (133장) — 기준값 후보

| 기준 t | 보류 (보류율) | 수용 정확도 | 통과한 오답 | 잡아낸 오답 | 보류 중 실제 오답 |
|---:|---:|---:|---:|---:|---:|
| 0.35 ← 선택 | 1/133 (0.8%) | 0.7727 | 22.6% | 1/31 | 100.0% |
| 0.40 | 7/133 (5.3%) | 0.7619 | 22.6% | 1/31 | 14.3% |
| 0.45 | 19/133 (14.3%) | 0.7719 | 19.5% | 5/31 | 26.3% |
| 0.50 | 42/133 (31.6%) | 0.8571 | 9.8% | 18/31 | 42.9% |
| 0.55 | 70/133 (52.6%) | 0.9048 | 4.5% | 25/31 | 35.7% |
| 0.60 | 84/133 (63.2%) | 0.9388 | 2.3% | 28/31 | 33.3% |
| 0.65 | 95/133 (71.4%) | 0.9737 | 0.8% | 30/31 | 31.6% |
| 0.70 | 104/133 (78.2%) | 1.0000 | 0.0% | 31/31 | 29.8% |
| 0.75 | 113/133 (85.0%) | 1.0000 | 0.0% | 31/31 | 27.4% |
| 0.80 | 122/133 (91.7%) | 1.0000 | 0.0% | 31/31 | 25.4% |
| 0.85 | 128/133 (96.2%) | 1.0000 | 0.0% | 31/31 | 24.2% |
| 0.90 | 131/133 (98.5%) | 1.0000 | 0.0% | 31/31 | 23.7% |
| 0.95 | 132/133 (99.2%) | 1.0000 | 0.0% | 31/31 | 23.5% |

### Test (128장) — t = 0.35 1회 적용

| 기준 t | 보류 (보류율) | 수용 정확도 | 통과한 오답 | 잡아낸 오답 | 보류 중 실제 오답 |
|---:|---:|---:|---:|---:|---:|
| 0.35 | 0/128 (0.0%) | 0.7188 | 28.1% | 0/36 | 0.0% |

보류되지 않고 통과한 Test 오답 (자신 있게 틀린 사례):

- angular_leaf_spot/angular_leaf_spot_test.12.jpg → bean_rust (0.4504)
- angular_leaf_spot/angular_leaf_spot_test.14.jpg → bean_rust (0.4816)
- angular_leaf_spot/angular_leaf_spot_test.15.jpg → bean_rust (0.4683)
- angular_leaf_spot/angular_leaf_spot_test.16.jpg → bean_rust (0.5163)
- angular_leaf_spot/angular_leaf_spot_test.19.jpg → healthy (0.5390)
- angular_leaf_spot/angular_leaf_spot_test.20.jpg → healthy (0.3987)
- angular_leaf_spot/angular_leaf_spot_test.21.jpg → bean_rust (0.6159)
- angular_leaf_spot/angular_leaf_spot_test.24.jpg → healthy (0.4176)
- angular_leaf_spot/angular_leaf_spot_test.36.jpg → healthy (0.4999)
- angular_leaf_spot/angular_leaf_spot_test.38.jpg → healthy (0.3774)
- angular_leaf_spot/angular_leaf_spot_test.41.jpg → bean_rust (0.4809)
- angular_leaf_spot/angular_leaf_spot_test.42.jpg → healthy (0.3744)
- angular_leaf_spot/angular_leaf_spot_test.5.jpg → bean_rust (0.4295)
- bean_rust/bean_rust_test.10.jpg → angular_leaf_spot (0.3824)
- bean_rust/bean_rust_test.13.jpg → healthy (0.4224)
- bean_rust/bean_rust_test.15.jpg → angular_leaf_spot (0.5266)
- bean_rust/bean_rust_test.19.jpg → angular_leaf_spot (0.4119)
- bean_rust/bean_rust_test.20.jpg → angular_leaf_spot (0.4118)
- bean_rust/bean_rust_test.28.jpg → healthy (0.4719)
- bean_rust/bean_rust_test.29.jpg → healthy (0.4374)
- bean_rust/bean_rust_test.3.jpg → healthy (0.4101)
- bean_rust/bean_rust_test.30.jpg → angular_leaf_spot (0.4447)
- bean_rust/bean_rust_test.31.jpg → angular_leaf_spot (0.4863)
- bean_rust/bean_rust_test.34.jpg → healthy (0.4941)
- bean_rust/bean_rust_test.36.jpg → angular_leaf_spot (0.4144)
- bean_rust/bean_rust_test.37.jpg → angular_leaf_spot (0.4406)
- bean_rust/bean_rust_test.39.jpg → angular_leaf_spot (0.5770)
- bean_rust/bean_rust_test.40.jpg → angular_leaf_spot (0.4111)
- bean_rust/bean_rust_test.41.jpg → healthy (0.4865)
- bean_rust/bean_rust_test.5.jpg → angular_leaf_spot (0.3922)
- bean_rust/bean_rust_test.6.jpg → angular_leaf_spot (0.5423)
- bean_rust/bean_rust_test.7.jpg → healthy (0.3871)
- bean_rust/bean_rust_test.9.jpg → angular_leaf_spot (0.4465)
- healthy/healthy_test.10.jpg → bean_rust (0.4997)
- healthy/healthy_test.25.jpg → bean_rust (0.3803)
- healthy/healthy_test.40.jpg → bean_rust (0.4184)

## B_full_e3

### Validation (133장) — 기준값 후보

| 기준 t | 보류 (보류율) | 수용 정확도 | 통과한 오답 | 잡아낸 오답 | 보류 중 실제 오답 |
|---:|---:|---:|---:|---:|---:|
| 0.35 | 0/133 (0.0%) | 0.9699 | 3.0% | 0/4 | 0.0% |
| 0.40 | 1/133 (0.8%) | 0.9773 | 2.3% | 1/4 | 100.0% |
| 0.45 | 1/133 (0.8%) | 0.9773 | 2.3% | 1/4 | 100.0% |
| 0.50 | 1/133 (0.8%) | 0.9773 | 2.3% | 1/4 | 100.0% |
| 0.55 | 5/133 (3.8%) | 0.9844 | 1.5% | 2/4 | 40.0% |
| 0.60 | 7/133 (5.3%) | 0.9841 | 1.5% | 2/4 | 28.6% |
| 0.65 | 8/133 (6.0%) | 0.9920 | 0.8% | 3/4 | 37.5% |
| 0.70 | 10/133 (7.5%) | 0.9919 | 0.8% | 3/4 | 30.0% |
| 0.75 | 10/133 (7.5%) | 0.9919 | 0.8% | 3/4 | 30.0% |
| 0.80 | 13/133 (9.8%) | 0.9917 | 0.8% | 3/4 | 23.1% |
| 0.85 ← 선택 | 21/133 (15.8%) | 1.0000 | 0.0% | 4/4 | 19.0% |
| 0.90 | 30/133 (22.6%) | 1.0000 | 0.0% | 4/4 | 13.3% |
| 0.95 | 43/133 (32.3%) | 1.0000 | 0.0% | 4/4 | 9.3% |

### Test (128장) — t = 0.85 1회 적용

| 기준 t | 보류 (보류율) | 수용 정확도 | 통과한 오답 | 잡아낸 오답 | 보류 중 실제 오답 |
|---:|---:|---:|---:|---:|---:|
| 0.85 | 25/128 (19.5%) | 0.9903 | 0.8% | 5/6 | 20.0% |

보류되지 않고 통과한 Test 오답 (자신 있게 틀린 사례):

- healthy/healthy_test.10.jpg → bean_rust (0.8889)
