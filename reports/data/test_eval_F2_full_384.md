# Test 평가 결과: F2_full_384

- 모델: `artifacts/beans_resnet18_full_384`
- 데이터: `dataset/test` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)
- 장치: cuda
- **Test Accuracy: 120/128 = 0.9375**

## 클래스별 지표

| 클래스 | 이미지 수 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 43 | 0.8776 | 1.0000 | 0.9348 |
| bean_rust | 43 | 0.9500 | 0.8837 | 0.9157 |
| healthy | 42 | 1.0000 | 0.9286 | 0.9630 |
| **Macro 평균** | 128 | | | **0.9378** |

## 혼동행렬 (행 = 정답, 열 = 예측)

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| **angular_leaf_spot** | 43 | 0 | 0 |
| **bean_rust** | 5 | 38 | 0 |
| **healthy** | 1 | 2 | 39 |

## 오분류 목록 (8건)

| 파일 | 정답 | 예측 | score |
|---|---|---|---:|
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.8715 |
| bean_rust_test.28.jpg | bean_rust | angular_leaf_spot | 0.5377 |
| bean_rust_test.3.jpg | bean_rust | angular_leaf_spot | 0.6969 |
| bean_rust_test.31.jpg | bean_rust | angular_leaf_spot | 0.6870 |
| bean_rust_test.36.jpg | bean_rust | angular_leaf_spot | 0.6861 |
| healthy_test.10.jpg | healthy | bean_rust | 0.9009 |
| healthy_test.24.jpg | healthy | angular_leaf_spot | 0.4553 |
| healthy_test.27.jpg | healthy | bean_rust | 0.3591 |
