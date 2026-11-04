# Grad-CAM 오분류 분석: B_full_e3

- 모델: `artifacts/beans_resnet18_full` / 대상 층: `resnet.encoder.stages[-1]` (512x7x7) / 장치: cuda
- 히트맵은 **설명·오류 분석용**이며 정확도 개선과 무관. Test 결과를 설명만 하고 선택에 쓰지 않음

## cam_on_leaf (히트맵 에너지 중 잎 마스크 안 비율, 예측 클래스 기준)

| 구분 | n | 평균 | 중앙값 | 0.5 미만(배경 주목) 수 |
|---|---:|---:|---:|---:|
| 정분류 | 122 | 0.8424 | 0.8831 | 2 |
| 오분류 | 6 | 0.6926 | 0.6835 | 1 |

## 그림

- 오분류: `reports/figures/gradcam/gradcam_B_full_e3_errors.png` (원본 | 예측 클래스 CAM | 정답 클래스 CAM)
- 그림 약어: ALS=angular_leaf_spot, RUST=bean_rust, leaf=cam_on_leaf
- 정분류 예시: `reports/figures/gradcam/gradcam_B_full_e3_correct.png`

## 오분류 상세

| 파일 | 정답 | 예측 | score | cam_on_leaf |
|---|---|---|---:|---:|
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.7654 | 0.5761 |
| bean_rust_test.28.jpg | bean_rust | angular_leaf_spot | 0.8482 | 0.7648 |
| bean_rust_test.3.jpg | bean_rust | angular_leaf_spot | 0.5301 | 0.4893 |
| bean_rust_test.31.jpg | bean_rust | angular_leaf_spot | 0.5651 | 0.8586 |
| healthy_test.10.jpg | healthy | bean_rust | 0.8889 | 0.8645 |
| healthy_test.27.jpg | healthy | bean_rust | 0.669 | 0.6023 |
