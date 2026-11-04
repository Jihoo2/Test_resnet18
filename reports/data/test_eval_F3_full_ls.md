# Test 평가 결과: F3_full_ls

- 모델: `artifacts/beans_resnet18_full_ls`
- 데이터: `dataset/test` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)
- 장치: cuda
- **Test Accuracy: 122/128 = 0.9531**

## 클래스별 지표

| 클래스 | 이미지 수 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 43 | 0.9545 | 0.9767 | 0.9655 |
| bean_rust | 43 | 0.9130 | 0.9767 | 0.9438 |
| healthy | 42 | 1.0000 | 0.9048 | 0.9500 |
| **Macro 평균** | 128 | | | **0.9531** |

## 혼동행렬 (행 = 정답, 열 = 예측)

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| **angular_leaf_spot** | 42 | 1 | 0 |
| **bean_rust** | 1 | 42 | 0 |
| **healthy** | 1 | 3 | 38 |

## 오분류 목록 (6건)

| 파일 | 정답 | 예측 | score |
|---|---|---|---:|
| angular_leaf_spot_test.14.jpg | angular_leaf_spot | bean_rust | 0.5959 |
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.5087 |
| healthy_test.10.jpg | healthy | bean_rust | 0.5533 |
| healthy_test.25.jpg | healthy | angular_leaf_spot | 0.4436 |
| healthy_test.27.jpg | healthy | bean_rust | 0.5726 |
| healthy_test.35.jpg | healthy | bean_rust | 0.6331 |
