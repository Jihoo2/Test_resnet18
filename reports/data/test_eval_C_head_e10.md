# Test 평가 결과: C_head_e10

- 모델: `artifacts/beans_resnet18_head_e10`
- 데이터: `dataset/test` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)
- 장치: cuda
- **Test Accuracy: 113/128 = 0.8828**

## 클래스별 지표

| 클래스 | 이미지 수 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 43 | 0.8039 | 0.9535 | 0.8723 |
| bean_rust | 43 | 0.8919 | 0.7674 | 0.8250 |
| healthy | 42 | 0.9750 | 0.9286 | 0.9512 |
| **Macro 평균** | 128 | | | **0.8829** |

## 혼동행렬 (행 = 정답, 열 = 예측)

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| **angular_leaf_spot** | 41 | 2 | 0 |
| **bean_rust** | 9 | 33 | 1 |
| **healthy** | 1 | 2 | 39 |

## 오분류 목록 (15건)

| 파일 | 정답 | 예측 | score |
|---|---|---|---:|
| angular_leaf_spot_test.14.jpg | angular_leaf_spot | bean_rust | 0.7416 |
| angular_leaf_spot_test.36.jpg | angular_leaf_spot | bean_rust | 0.4655 |
| bean_rust_test.10.jpg | bean_rust | angular_leaf_spot | 0.4278 |
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.6175 |
| bean_rust_test.28.jpg | bean_rust | angular_leaf_spot | 0.4747 |
| bean_rust_test.3.jpg | bean_rust | healthy | 0.3949 |
| bean_rust_test.30.jpg | bean_rust | angular_leaf_spot | 0.5531 |
| bean_rust_test.31.jpg | bean_rust | angular_leaf_spot | 0.7100 |
| bean_rust_test.36.jpg | bean_rust | angular_leaf_spot | 0.5559 |
| bean_rust_test.37.jpg | bean_rust | angular_leaf_spot | 0.4653 |
| bean_rust_test.7.jpg | bean_rust | angular_leaf_spot | 0.4289 |
| bean_rust_test.9.jpg | bean_rust | angular_leaf_spot | 0.5857 |
| healthy_test.10.jpg | healthy | bean_rust | 0.8018 |
| healthy_test.25.jpg | healthy | bean_rust | 0.3844 |
| healthy_test.27.jpg | healthy | angular_leaf_spot | 0.3905 |
