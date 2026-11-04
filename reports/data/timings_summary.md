# 응답시간 측정 요약 (measure_timings.py 자동 생성, 단위 ms, warm-up 제외 중앙값)

- 서버: http://127.0.0.1:8000 / 반복: 5회 / 비동기 상태조회 간격: 100ms (final_ms 에 폴링 대기 포함)
- 측정 시각: 2026-11-04 10:48:02

| 경로 | 캐시 | n | HTTP 응답 중앙값 | 최종 결과 확인 중앙값 | 추론시간 중앙값 |
|---|---|---:|---:|---:|---:|
| sync | MISS | 5 | 20.6 | 20.6 | 15.78 |
| sync | HIT | 5 | 2.1 | 2.1 | null (추론 생략) |
| async | MISS | 5 | 8.5 | 116.7 | 17.86 |
| async | HIT | 5 | 7.7 | 113.4 | null (추론 생략) |

warm-up(비교 제외): sync MISS final=24.0ms, async MISS final=121.3ms
