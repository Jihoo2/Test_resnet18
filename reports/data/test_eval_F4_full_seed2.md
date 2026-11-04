# Test 평가 결과: F4_full_seed2

- 모델: `artifacts/beans_resnet18_full_seed2`
- 데이터: `dataset/test` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)
- 장치: cuda
- **Test Accuracy: 124/128 = 0.9688**

## 클래스별 지표

| 클래스 | 이미지 수 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 43 | 0.9545 | 0.9767 | 0.9655 |
| bean_rust | 43 | 0.9535 | 0.9535 | 0.9535 |
| healthy | 42 | 1.0000 | 0.9762 | 0.9880 |
| **Macro 평균** | 128 | | | **0.9690** |

## 혼동행렬 (행 = 정답, 열 = 예측)

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| **angular_leaf_spot** | 42 | 1 | 0 |
| **bean_rust** | 2 | 41 | 0 |
| **healthy** | 0 | 1 | 41 |

## 오분류 목록 (4건)

| 파일 | 정답 | 예측 | score |
|---|---|---|---:|
| angular_leaf_spot_test.36.jpg | angular_leaf_spot | bean_rust | 0.5761 |
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.6718 |
| bean_rust_test.36.jpg | bean_rust | angular_leaf_spot | 0.6436 |
| healthy_test.27.jpg | healthy | bean_rust | 0.7280 |
