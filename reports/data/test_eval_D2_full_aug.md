# Test 평가 결과: D2_full_aug

- 모델: `artifacts/beans_resnet18_full_aug`
- 데이터: `dataset/test` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)
- 장치: cuda
- **Test Accuracy: 123/128 = 0.9609**

## 클래스별 지표

| 클래스 | 이미지 수 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 43 | 0.9750 | 0.9070 | 0.9398 |
| bean_rust | 43 | 0.9130 | 0.9767 | 0.9438 |
| healthy | 42 | 1.0000 | 1.0000 | 1.0000 |
| **Macro 평균** | 128 | | | **0.9612** |

## 혼동행렬 (행 = 정답, 열 = 예측)

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| **angular_leaf_spot** | 39 | 4 | 0 |
| **bean_rust** | 1 | 42 | 0 |
| **healthy** | 0 | 0 | 42 |

## 오분류 목록 (5건)

| 파일 | 정답 | 예측 | score |
|---|---|---|---:|
| angular_leaf_spot_test.14.jpg | angular_leaf_spot | bean_rust | 0.9897 |
| angular_leaf_spot_test.36.jpg | angular_leaf_spot | bean_rust | 0.7220 |
| angular_leaf_spot_test.4.jpg | angular_leaf_spot | bean_rust | 0.4774 |
| angular_leaf_spot_test.42.jpg | angular_leaf_spot | bean_rust | 0.8476 |
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.8293 |
