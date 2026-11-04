# Test 평가 결과: B_full_e3

- 모델: `artifacts/beans_resnet18_full`
- 데이터: `dataset/test` (학습·모델 선택에 사용하지 않은 데이터, 1회 평가)
- 장치: cuda
- **Test Accuracy: 122/128 = 0.9531**

## 클래스별 지표

| 클래스 | 이미지 수 | Precision | Recall | F1 |
|---|---:|---:|---:|---:|
| angular_leaf_spot | 43 | 0.9149 | 1.0000 | 0.9556 |
| bean_rust | 43 | 0.9512 | 0.9070 | 0.9286 |
| healthy | 42 | 1.0000 | 0.9524 | 0.9756 |
| **Macro 평균** | 128 | | | **0.9532** |

## 혼동행렬 (행 = 정답, 열 = 예측)

| 정답 \ 예측 | angular_leaf_spot | bean_rust | healthy |
|---|---:|---:|---:|
| **angular_leaf_spot** | 43 | 0 | 0 |
| **bean_rust** | 4 | 39 | 0 |
| **healthy** | 0 | 2 | 40 |

## 오분류 목록 (6건)

| 파일 | 정답 | 예측 | score |
|---|---|---|---:|
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.7656 |
| bean_rust_test.28.jpg | bean_rust | angular_leaf_spot | 0.8479 |
| bean_rust_test.3.jpg | bean_rust | angular_leaf_spot | 0.5301 |
| bean_rust_test.31.jpg | bean_rust | angular_leaf_spot | 0.5659 |
| healthy_test.10.jpg | healthy | bean_rust | 0.8889 |
| healthy_test.27.jpg | healthy | bean_rust | 0.6689 |
