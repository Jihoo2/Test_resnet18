# Test 평가 결과: F1_full_aug_e10

- 모델: `artifacts/beans_resnet18_full_aug_e10`
- 데이터: `dataset/test` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)
- 장치: cuda
- **Test Accuracy: 121/128 = 0.9453**

## 클래스별 지표

| 클래스 | 이미지 수 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 43 | 0.9512 | 0.9070 | 0.9286 |
| bean_rust | 43 | 0.8913 | 0.9535 | 0.9213 |
| healthy | 42 | 1.0000 | 0.9762 | 0.9880 |
| **Macro 평균** | 128 | | | **0.9460** |

## 혼동행렬 (행 = 정답, 열 = 예측)

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| **angular_leaf_spot** | 39 | 4 | 0 |
| **bean_rust** | 2 | 41 | 0 |
| **healthy** | 0 | 1 | 41 |

## 오분류 목록 (7건)

| 파일 | 정답 | 예측 | score |
|---|---|---|---:|
| angular_leaf_spot_test.14.jpg | angular_leaf_spot | bean_rust | 0.9881 |
| angular_leaf_spot_test.36.jpg | angular_leaf_spot | bean_rust | 0.6229 |
| angular_leaf_spot_test.5.jpg | angular_leaf_spot | bean_rust | 0.5404 |
| angular_leaf_spot_test.6.jpg | angular_leaf_spot | bean_rust | 0.5318 |
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.7842 |
| bean_rust_test.31.jpg | bean_rust | angular_leaf_spot | 0.6486 |
| healthy_test.35.jpg | healthy | bean_rust | 0.6728 |
