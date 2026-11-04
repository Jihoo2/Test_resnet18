# Test 평가 결과: D1_head_e10_aug

- 모델: `artifacts/beans_resnet18_head_e10_aug`
- 데이터: `dataset/test` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)
- 장치: cuda
- **Test Accuracy: 112/128 = 0.8750**

## 클래스별 지표

| 클래스 | 이미지 수 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 43 | 0.9706 | 0.7674 | 0.8571 |
| bean_rust | 43 | 0.8000 | 0.9302 | 0.8602 |
| healthy | 42 | 0.8864 | 0.9286 | 0.9070 |
| **Macro 평균** | 128 | | | **0.8748** |

## 혼동행렬 (행 = 정답, 열 = 예측)

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| **angular_leaf_spot** | 33 | 7 | 3 |
| **bean_rust** | 1 | 40 | 2 |
| **healthy** | 0 | 3 | 39 |

## 오분류 목록 (16건)

| 파일 | 정답 | 예측 | score |
|---|---|---|---:|
| angular_leaf_spot_test.12.jpg | angular_leaf_spot | bean_rust | 0.5759 |
| angular_leaf_spot_test.14.jpg | angular_leaf_spot | bean_rust | 0.9145 |
| angular_leaf_spot_test.19.jpg | angular_leaf_spot | healthy | 0.4443 |
| angular_leaf_spot_test.21.jpg | angular_leaf_spot | bean_rust | 0.5446 |
| angular_leaf_spot_test.33.jpg | angular_leaf_spot | healthy | 0.3560 |
| angular_leaf_spot_test.36.jpg | angular_leaf_spot | bean_rust | 0.5864 |
| angular_leaf_spot_test.38.jpg | angular_leaf_spot | healthy | 0.4101 |
| angular_leaf_spot_test.4.jpg | angular_leaf_spot | bean_rust | 0.4447 |
| angular_leaf_spot_test.42.jpg | angular_leaf_spot | bean_rust | 0.4859 |
| angular_leaf_spot_test.9.jpg | angular_leaf_spot | bean_rust | 0.4671 |
| bean_rust_test.28.jpg | bean_rust | healthy | 0.3677 |
| bean_rust_test.3.jpg | bean_rust | healthy | 0.4322 |
| bean_rust_test.31.jpg | bean_rust | angular_leaf_spot | 0.7525 |
| healthy_test.10.jpg | healthy | bean_rust | 0.7202 |
| healthy_test.25.jpg | healthy | bean_rust | 0.5255 |
| healthy_test.40.jpg | healthy | bean_rust | 0.4658 |
