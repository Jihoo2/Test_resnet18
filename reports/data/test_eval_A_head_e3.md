# Test 평가 결과: A_head_e3

- 모델: `artifacts/beans_resnet18`
- 데이터: `dataset/test` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)
- 장치: cuda
- **Test Accuracy: 92/128 = 0.7188**

## 클래스별 지표

| 클래스 | 이미지 수 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 43 | 0.6977 | 0.6977 | 0.6977 |
| bean_rust | 43 | 0.6970 | 0.5349 | 0.6053 |
| healthy | 42 | 0.7500 | 0.9286 | 0.8298 |
| **Macro 평균** | 128 | | | **0.7109** |

## 혼동행렬 (행 = 정답, 열 = 예측)

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| **angular_leaf_spot** | 30 | 7 | 6 |
| **bean_rust** | 13 | 23 | 7 |
| **healthy** | 0 | 3 | 39 |

## 오분류 목록 (36건)

| 파일 | 정답 | 예측 | score |
|---|---|---|---:|
| angular_leaf_spot_test.12.jpg | angular_leaf_spot | bean_rust | 0.4504 |
| angular_leaf_spot_test.14.jpg | angular_leaf_spot | bean_rust | 0.4816 |
| angular_leaf_spot_test.15.jpg | angular_leaf_spot | bean_rust | 0.4683 |
| angular_leaf_spot_test.16.jpg | angular_leaf_spot | bean_rust | 0.5163 |
| angular_leaf_spot_test.19.jpg | angular_leaf_spot | healthy | 0.5390 |
| angular_leaf_spot_test.20.jpg | angular_leaf_spot | healthy | 0.3987 |
| angular_leaf_spot_test.21.jpg | angular_leaf_spot | bean_rust | 0.6159 |
| angular_leaf_spot_test.24.jpg | angular_leaf_spot | healthy | 0.4176 |
| angular_leaf_spot_test.36.jpg | angular_leaf_spot | healthy | 0.4999 |
| angular_leaf_spot_test.38.jpg | angular_leaf_spot | healthy | 0.3774 |
| angular_leaf_spot_test.41.jpg | angular_leaf_spot | bean_rust | 0.4809 |
| angular_leaf_spot_test.42.jpg | angular_leaf_spot | healthy | 0.3744 |
| angular_leaf_spot_test.5.jpg | angular_leaf_spot | bean_rust | 0.4295 |
| bean_rust_test.10.jpg | bean_rust | angular_leaf_spot | 0.3824 |
| bean_rust_test.13.jpg | bean_rust | healthy | 0.4224 |
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.5266 |
| bean_rust_test.19.jpg | bean_rust | angular_leaf_spot | 0.4119 |
| bean_rust_test.20.jpg | bean_rust | angular_leaf_spot | 0.4118 |
| bean_rust_test.28.jpg | bean_rust | healthy | 0.4719 |
| bean_rust_test.29.jpg | bean_rust | healthy | 0.4374 |
| bean_rust_test.3.jpg | bean_rust | healthy | 0.4101 |
| bean_rust_test.30.jpg | bean_rust | angular_leaf_spot | 0.4447 |
| bean_rust_test.31.jpg | bean_rust | angular_leaf_spot | 0.4863 |
| bean_rust_test.34.jpg | bean_rust | healthy | 0.4941 |
| bean_rust_test.36.jpg | bean_rust | angular_leaf_spot | 0.4144 |
| bean_rust_test.37.jpg | bean_rust | angular_leaf_spot | 0.4406 |
| bean_rust_test.39.jpg | bean_rust | angular_leaf_spot | 0.5770 |
| bean_rust_test.40.jpg | bean_rust | angular_leaf_spot | 0.4111 |
| bean_rust_test.41.jpg | bean_rust | healthy | 0.4865 |
| bean_rust_test.5.jpg | bean_rust | angular_leaf_spot | 0.3922 |
| bean_rust_test.6.jpg | bean_rust | angular_leaf_spot | 0.5423 |
| bean_rust_test.7.jpg | bean_rust | healthy | 0.3871 |
| bean_rust_test.9.jpg | bean_rust | angular_leaf_spot | 0.4465 |
| healthy_test.10.jpg | healthy | bean_rust | 0.4997 |
| healthy_test.25.jpg | healthy | bean_rust | 0.3803 |
| healthy_test.40.jpg | healthy | bean_rust | 0.4184 |
