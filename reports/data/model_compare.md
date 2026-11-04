# 모델 비교 (정확도 + 서비스 비용)

- CPU 추론: 서비스와 같은 CPU·1장씩·전처리 포함, val 30장 중 앞 3장 warm-up 제외 중앙값
- 실행 장치 스레드 수: 10
- 모델 선택 기준은 Validation. Test 는 선택과 무관하게 각 1회 측정

| 실험 | 기반 모델 | 방식 | 증강 | 기타 | Best Val | Test | 파라미터(M) | 파일(MB) | CPU 1장(ms) | 첫 행 대비 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|
| A_head_e3 | `microsoft/resnet-18` | Head-only | 없음 | — | 0.7669 | 0.7188 | 11.2 | 43 | 14.3 | ×1.0 |
| C_head_e10 | `microsoft/resnet-18` | Head-only | 없음 | — | 0.8947 | 0.8828 | 11.2 | 43 | 14.1 | ×1.0 |
| B_full_e3 | `microsoft/resnet-18` | Full FT | 없음 | — | 0.9699 | 0.9531 | 11.2 | 43 | 14.3 | ×1.0 |
| D1_head_e10_aug | `microsoft/resnet-18` | Head-only | 있음 | — | 0.8571 | 0.8750 | 11.2 | 43 | 13.0 | ×0.9 |
| D2_full_aug | `microsoft/resnet-18` | Full FT | 있음 | — | 0.9474 | 0.9609 | 11.2 | 43 | 13.4 | ×0.9 |
| F1_full_aug_e10 | `microsoft/resnet-18` | Full FT | 있음 | — | 0.9850 | 0.9453 | 11.2 | 43 | 13.9 | ×1.0 |
| F2_full_384 | `microsoft/resnet-18` | Full FT | 없음 | image_size=384 | 0.9850 | 0.9375 | 11.2 | 43 | 33.2 | ×2.3 |
| F3_full_ls | `microsoft/resnet-18` | Full FT | 없음 | label_smoothing=0.1 | 0.9774 | 0.9531 | 11.2 | 43 | 14.3 | ×1.0 |

- Validation 최고: **F1_full_aug_e10** (0.9850, CPU 13.9 ms)
