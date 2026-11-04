# Grad-CAM 오분류 분석: A_head_e3

- 모델: `artifacts/beans_resnet18` / 대상 층: `resnet.encoder.stages[-1]` (512x7x7) / 장치: cuda
- 히트맵은 **설명·오류 분석용**이며 정확도 개선과 무관. Test 결과를 설명만 하고 선택에 쓰지 않음

## cam_on_leaf (히트맵 에너지 중 잎 마스크 안 비율, 예측 클래스 기준)

| 구분 | n | 평균 | 중앙값 | 0.5 미만(배경 주목) 수 |
|---|---:|---:|---:|---:|
| 정분류 | 92 | 0.8113 | 0.8615 | 7 |
| 오분류 | 36 | 0.7216 | 0.8036 | 5 |

## 그림

- 오분류: `reports/figures/gradcam/gradcam_A_head_e3_errors.png` (원본 | 예측 클래스 CAM | 정답 클래스 CAM)
- 그림 약어: ALS=angular_leaf_spot, RUST=bean_rust, leaf=cam_on_leaf
- 정분류 예시: `reports/figures/gradcam/gradcam_A_head_e3_correct.png`

## 오분류 상세

| 파일 | 정답 | 예측 | score | cam_on_leaf |
|---|---|---|---:|---:|
| angular_leaf_spot_test.12.jpg | angular_leaf_spot | bean_rust | 0.4507 | 0.4536 |
| angular_leaf_spot_test.14.jpg | angular_leaf_spot | bean_rust | 0.4815 | 0.78 |
| angular_leaf_spot_test.15.jpg | angular_leaf_spot | bean_rust | 0.4683 | 0.8745 |
| angular_leaf_spot_test.16.jpg | angular_leaf_spot | bean_rust | 0.5161 | 0.5634 |
| angular_leaf_spot_test.19.jpg | angular_leaf_spot | healthy | 0.5393 | 0.9633 |
| angular_leaf_spot_test.20.jpg | angular_leaf_spot | healthy | 0.3987 | 0.2235 |
| angular_leaf_spot_test.21.jpg | angular_leaf_spot | bean_rust | 0.6161 | 0.8442 |
| angular_leaf_spot_test.24.jpg | angular_leaf_spot | healthy | 0.4175 | 0.8272 |
| angular_leaf_spot_test.36.jpg | angular_leaf_spot | healthy | 0.4999 | 0.9116 |
| angular_leaf_spot_test.38.jpg | angular_leaf_spot | healthy | 0.3773 | 0.928 |
| angular_leaf_spot_test.41.jpg | angular_leaf_spot | bean_rust | 0.4808 | 0.7035 |
| angular_leaf_spot_test.42.jpg | angular_leaf_spot | healthy | 0.3745 | 0.8762 |
| angular_leaf_spot_test.5.jpg | angular_leaf_spot | bean_rust | 0.4293 | 0.9898 |
| bean_rust_test.10.jpg | bean_rust | angular_leaf_spot | 0.3825 | 0.6559 |
| bean_rust_test.13.jpg | bean_rust | healthy | 0.4221 | 0.9769 |
| bean_rust_test.15.jpg | bean_rust | angular_leaf_spot | 0.5266 | 0.5095 |
| bean_rust_test.19.jpg | bean_rust | angular_leaf_spot | 0.4119 | 0.6185 |
| bean_rust_test.20.jpg | bean_rust | angular_leaf_spot | 0.4118 | 0.5906 |
| bean_rust_test.28.jpg | bean_rust | healthy | 0.4718 | 0.8316 |
| bean_rust_test.29.jpg | bean_rust | healthy | 0.4372 | 0.917 |
| bean_rust_test.3.jpg | bean_rust | healthy | 0.4101 | 0.5846 |
| bean_rust_test.30.jpg | bean_rust | angular_leaf_spot | 0.4446 | 0.6995 |
| bean_rust_test.31.jpg | bean_rust | angular_leaf_spot | 0.4865 | 0.9556 |
| bean_rust_test.34.jpg | bean_rust | healthy | 0.4938 | 0.9167 |
| bean_rust_test.36.jpg | bean_rust | angular_leaf_spot | 0.4144 | 0.5653 |
| bean_rust_test.37.jpg | bean_rust | angular_leaf_spot | 0.4405 | 0.9911 |
| bean_rust_test.39.jpg | bean_rust | angular_leaf_spot | 0.577 | 0.4906 |
| bean_rust_test.40.jpg | bean_rust | angular_leaf_spot | 0.4111 | 0.8468 |
| bean_rust_test.41.jpg | bean_rust | healthy | 0.4867 | 0.8347 |
| bean_rust_test.5.jpg | bean_rust | angular_leaf_spot | 0.3923 | 0.6906 |
| bean_rust_test.6.jpg | bean_rust | angular_leaf_spot | 0.5423 | 0.2617 |
| bean_rust_test.7.jpg | bean_rust | healthy | 0.387 | 0.5537 |
| bean_rust_test.9.jpg | bean_rust | angular_leaf_spot | 0.4464 | 0.715 |
| healthy_test.10.jpg | healthy | bean_rust | 0.4998 | 0.8536 |
| healthy_test.25.jpg | healthy | bean_rust | 0.3804 | 0.8986 |
| healthy_test.40.jpg | healthy | bean_rust | 0.4186 | 0.0789 |
