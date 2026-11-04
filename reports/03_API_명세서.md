# 산출물 3. API 명세서

Base URL: `http://127.0.0.1:8000` · Swagger UI: `/docs`

## 1. API 목록

| API ID | Method | URL | 요청 | 성공 | 주요 응답 | 실패 | 구현 |
|---|---|---|---|---:|---|---|---|
| API-01 | GET | `/health` | 없음 | 200 | `status` | 서버 미실행 시 응답 없음 | `main.py` `health()` |
| API-02 | POST | `/api/sync/classify/` | `multipart/form-data`, 필드 `image` | 200 | `model_id`, `top1`, `all`, `inference_ms`, `cache_hit` | 400, 413, 422 | `ai/router_sync.py` `classify_sync()` |
| API-03 | POST | `/api/async/classify/` | `multipart/form-data`, 필드 `image` | **202** | `job_id`, `status`, `check_url` | 400, 413, 422, **503** | `ai/router_async.py` `enqueue_classify()` |
| API-04 | GET | `/api/async/jobs/{job_id}/` | 경로변수 정수 | 200 | `job_id`, `status`, `model_id`, `top1`, `all`, `inference_ms`, `cache_hit`, `error_message` | 404, 422 | `ai/router_async.py` `get_job()` |
| WEB-00 | GET | `/` | 없음 | 307 | `/vision/sync/` 로 리다이렉트 | — | `router_web.home()` |
| WEB-01 | GET | `/vision/sync/` | 없음 | 200 | HTML | — | `router_web.sync_page()` |
| WEB-02 | GET | `/vision/async/` | 없음 | 200 | HTML | — | `router_web.async_page()` |

422 는 FastAPI 자동 검증 오류(필드 `image` 누락, 정수가 아닌 `job_id`)이며 본 평가에서는 실측하지 않았다.

## 2. 입력 검증 규칙

| 규칙 | 위치 | HTTP | `detail` |
|---|---|---:|---|
| 5MB(5,242,880 B) 초과 | 라우터: `file.read(MAX+1)` 후 길이 비교 | 413 | `5MB 이하 파일만 허용합니다.` |
| 0바이트 | `load_rgb_image()` | 400 | `이미지 파일은 1바이트 이상, 5MB 이하이어야 합니다.` |
| 디코딩 결과 JPEG/PNG/WEBP 아님 (확장자 무관) | `load_rgb_image()` | 400 | `JPG, PNG, WEBP 이미지만 허용합니다.` |
| 1,200만 픽셀 초과 | `load_rgb_image()` | 400 | `이미지 해상도가 너무 큽니다(최대 1200만 픽셀).` |
| 이미지로 열 수 없음 | `load_rgb_image()` | 400 | `올바른 이미지 파일이 아닙니다.` |

## 3. API-02 동기 분류

| 항목 | 내용 |
|---|---|
| 동작 | 추론(또는 캐시 조회)이 끝날 때까지 응답 대기 |
| `model_id` | 사용 모델 경로 |
| `top1` | 최고 점수 `{label, score}` |
| `all` | 점수 내림차순 목록 (3클래스) |
| `inference_ms` | 모델 추론 시간. **캐시 HIT 이면 `null` (추론 생략, 0ms 아님)** |
| `cache_hit` | Redis 결과 재사용 여부 |
| DB 기록 | 없음 |

**성공 (MISS)** — angular_leaf_spot_test.30.jpg, HTTP 200 / 3,972ms
```json
{
  "model_id": "artifacts/beans_resnet18",
  "top1": {"label": "angular_leaf_spot", "score": 0.6318308711051941},
  "all": [
    {"label": "angular_leaf_spot", "score": 0.6318308711051941},
    {"label": "bean_rust", "score": 0.24226535856723785},
    {"label": "healthy", "score": 0.12590382993221283}
  ],
  "inference_ms": 3934,
  "cache_hit": false
}
```
(FastAPI 프로세스의 첫 요청이라 `inference_ms` 에 모델 로딩 시간이 포함됨)

**같은 이미지 재요청 (HIT)** — HTTP 200 / 13ms
```json
{
  "model_id": "artifacts/beans_resnet18",
  "top1": {"label": "angular_leaf_spot", "score": 0.6318308711051941},
  "all": [ "...(위와 동일)..." ],
  "inference_ms": null,
  "cache_hit": true
}
```

**오류 (`test.txt` 업로드)** — HTTP 400 / 10ms
```json
{"detail": "올바른 이미지 파일이 아닙니다."}
```

**오류 (5.8MB 파일)** — HTTP 413
```json
{"detail":"5MB 이하 파일만 허용합니다."}
```

## 4. API-03 비동기 접수

| 항목 | 내용 |
|---|---|
| 동작 | 크기 확인 → 이미지 검증 → `media/jobs/<uuid>.bin` 저장 → `image_jobs`(queued) INSERT → `classify_job.delay(job_id)` → 202 |
| 의미 | **202 = 접수 완료, 분석 완료 아님** |
| 503 | Broker(Redis) 등록 실패. 해당 행을 `failed` + `error_message` 로 갱신 후 503 |

**접수** — bean_rust_test.30.jpg, 접수 20ms
```json
{"job_id": 2, "status": "queued", "check_url": "/api/async/jobs/2/"}
```

**Broker 장애 (Redis 정지)** — HTTP 503
```json
{"detail": "작업 큐 등록 실패: Redis 연결을 확인하세요."}
```

## 5. API-04 상태 조회

| `status` | `top1` / `all` | `error_message` |
|---|---|---|
| `queued` | null | null |
| `running` | null | null |
| `done` | 결과 | null |
| `failed` | null | 실패 원인 |

`all` 은 API 응답 필드명, `all_scores` 는 DB 컬럼명이다.

**완료 (job 2)** — 접수 20ms / 전체 3,071ms
```json
{
  "job_id": 2, "status": "done", "model_id": "artifacts/beans_resnet18",
  "top1": {"label": "angular_leaf_spot", "score": 0.4447840750217438},
  "all": [
    {"label": "angular_leaf_spot", "score": 0.4447840750217438},
    {"label": "bean_rust", "score": 0.40506160259246826},
    {"label": "healthy", "score": 0.15015432238578796}
  ],
  "inference_ms": 2474.15, "cache_hit": false, "error_message": null
}
```
※ 정답은 bean_rust — **API 는 정상, 모델 오분류** (1·2위 차 0.04)

**완료 (job 3, Worker 재시작 후)**
```json
{"job_id":3,"status":"done","model_id":"artifacts/beans_resnet18","top1":{"label":"healthy","score":0.7499070763587952},"all":[{"label":"healthy","score":0.7499070763587952},{"label":"angular_leaf_spot","score":0.14340545237064362},{"label":"bean_rust","score":0.1066875234246254}],"inference_ms":2493.43,"cache_hit":false,"error_message":null}
```

**없는 작업** — HTTP 404
```json
{"detail":"해당 작업이 없습니다."}
```

## 6. 실행 근거표

| 검증 ID | 입력 | 기대 | 실제 | 증빙 |
|---|---|---:|---:|---|
| API-01-T01 | GET `/health` | 200 | 200 | `evidence/uvicorn_log_status_codes.png` |
| API-02-T01 | angular_leaf_spot_test.30.jpg | 200 | 200 (MISS) | `evidence/sync_miss.png` |
| API-02-T02 | 같은 파일 재요청 | 200 | 200 (HIT) | `evidence/sync_hit.png` |
| API-02-T03 | `test.txt` | 400 | 400 | `evidence/api_sync_400.png` |
| API-02-T04 | 5.8MB 무작위 파일 | 413 | 413 | `evidence/redis_recover_failed_row_413.png` |
| API-02-T05 | Redis 정지 + healthy_test.32.jpg | 200 (폴백) | 200 | `evidence/redis_down_sync_200.png` |
| API-03-T01 | bean_rust_test.30.jpg | 202 | 202 | `evidence/ui_async.png` |
| API-03-T02 | Redis 정지 + healthy_test.32.jpg | 503 | 503 | `evidence/redis_down_async_503.png` |
| API-04-T01 | job_id=2 | 200 / done | 200 / done | `evidence/ui_async.png` |
| API-04-T02 | job_id=3 (Worker 재시작 후) | 200 / done | 200 / done | `evidence/api_job_done.png` |
| API-04-T03 | job_id=999999 | 404 | 404 | `evidence/api_404.png`, `evidence/uvicorn_log_status_codes.png` |
| WEB-01·02 | 화면 | 200 | 200 | `evidence/uvicorn_log_status_codes.png` |
