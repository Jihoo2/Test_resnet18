# FastAPI Beans ResNet18 동기·비동기 평가 프로젝트

콩잎 이미지 1장을 `angular_leaf_spot`(각진잎반점병) / `bean_rust`(녹병) / `healthy`(정상)로 분류하는 Vision AI 웹 서비스.
`microsoft/resnet-18` 을 Beans 데이터로 Fine-tuning 하고 FastAPI 동기 API 와 Celery 비동기 작업 큐(Redis · PostgreSQL)로 서빙한다.

## 주요 결과

| 항목 | 값 |
|---|---|
| 서비스 모델 (Head-only 3ep) Best Validation Accuracy | **0.7669** (Test 1회 0.7188) |
| 선택 실험 Full Fine-tuning Best Validation Accuracy | **0.9699** (Test 1회 0.9531) |
| 동기 MISS / 동기 HIT / 비동기 접수 / 비동기 완료 (중앙값) | 20.6 / 2.1 / 8.5 / 116.7 ms |
| 실환경 통합 테스트 | 18 / 18 PASS (모의 테스트 01: 1 passed, 02: 4 passed) |

## 1. 환경

| 항목 | 버전 |
|---|---|
| OS | Windows + WSL2 Ubuntu 26.04.1 LTS |
| Python | 3.11.18 (`.venv`, uv 로 생성) |
| Docker | Docker Desktop 29.9.2, Compose v5.6.1 — Redis `127.0.0.1:6379`, PostgreSQL `127.0.0.1:5432` |
| WSL 프로세스 | FastAPI (Uvicorn `127.0.0.1:8000`), Celery Worker |
| GPU (선택) | 학습용. 없으면 CPU 로 학습됨. 서비스 추론은 CPU |

## 2. 데이터 준비
1. https://huggingface.co/datasets/AI-Lab-Makerere/beans/tree/main/data 에서 `train.zip`, `validation.zip`, `test.zip` 다운로드
2. 원본은 `~/beans_source/` 에 압축 해제하여 보존
3. 실행용으로 복사 — **`validation` 은 `val` 로**
   ```bash
   mkdir -p dataset/{train,val,test}/{angular_leaf_spot,bean_rust,healthy}
   cp -r ~/beans_source/train/.      dataset/train/
   cp -r ~/beans_source/validation/. dataset/val/
   cp -r ~/beans_source/test/.       dataset/test/
   python reports/tools/check_dataset.py     # 개수·중복 점검 → reports/data/dataset_check.md
   ```
데이터셋은 저장소에 포함하지 않는다 (`.gitignore`).

## 3. 설치
```bash
cd ~/fastapi_resnet18
# Ubuntu 기본 Python 이 3.11 이 아니면 uv 로 3.11 가상환경 생성
uv venv --python 3.11 --seed .venv          # 또는: python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env                        # MODEL_PATH=artifacts/beans_resnet18
```

## 4. 모델 학습
```bash
# 필수: Head-only (서비스 모델)
python -m training.finetune --data dataset --output artifacts/beans_resnet18 --epochs 3 --batch-size 8 --freeze-backbone
# 선택 실험
python -m training.finetune --data dataset --output artifacts/beans_resnet18_head_e10 --epochs 10 --batch-size 8 --freeze-backbone
python -m training.finetune --data dataset --output artifacts/beans_resnet18_full --epochs 3 --batch-size 8 --lr 0.00005
```
모델 가중치는 저장소에 포함하지 않는다 (`artifacts/*` 제외). 위 명령으로 재생성한다.

## 5. 구동 순서 (터미널 3개)
```bash
# 터미널 1 — Redis · PostgreSQL 만 기동 (서비스명 필수: 생략하면 web·worker 컨테이너까지 떠서 8000 충돌)
docker compose up -d redis postgres
docker compose exec redis redis-cli ping                               # PONG
docker compose exec postgres pg_isready -U vision_user -d vision_db    # accepting connections

# 터미널 2 — Celery Worker
source .venv/bin/activate
celery -A ai.celery_app:celery_app worker --loglevel=info --pool=solo --concurrency=1

# 터미널 3 — FastAPI
source .venv/bin/activate
uvicorn main:app --host 127.0.0.1 --port 8000
```

| 주소 | 역할 |
|---|---|
| http://127.0.0.1:8000/health | 서버 확인 |
| http://127.0.0.1:8000/vision/sync/ | 동기 분류 화면 |
| http://127.0.0.1:8000/vision/async/ | 비동기 분류 화면 |
| http://127.0.0.1:8000/docs | Swagger API 문서 |

6379 포트 충돌 시: WSL 에 설치된 redis-server 를 중지 (`sudo systemctl stop redis-server`) — 산출물 7 E-03

## 6. 테스트·측정·분석
```bash
python -m pytest -q tests/test_api.py                              # 02 모의 테스트 (Docker 불필요)
python reports/tools/measure_timings.py --repeat 5                 # 응답시간 (서버·Worker 실행 중)
python reports/tools/evaluate_test.py --model artifacts/beans_resnet18 --name A_head_e3   # Test 1회 평가

# 분석 전용 추가 패키지 (서비스에는 불필요, requirements.txt 미포함)
python -m pip install opencv-python-headless
python reports/tools/hsv_lesion_analysis.py
python reports/tools/gradcam_analysis.py --model artifacts/beans_resnet18_full --name B_full_e3
```
`test_api.py`(루트)는 01 단계 전용이며 02 구조에서는 `tests/test_api.py` 를 사용한다.

## 7. 결과물 위치

| 경로 | 내용 |
|---|---|
| `reports/01_FineTuning_결과보고서.md` ~ `reports/08_최종기술보고서.md` | 산출물 8종 |
| `reports/data/` | 원본 측정 (timings.csv, test_eval_*.md, test_pred_*.csv, hsv_*, gradcam_*, 학습 로그, setup_and_test_log.md) |
| `reports/evidence/` | 실행 캡처 |
| `reports/figures/` | 그래프(charts), 다이어그램(diagrams), HSV·Grad-CAM 그림 |
| `reports/tools/` | 보조 스크립트 (제공 코드 아님): check_dataset, measure_timings, evaluate_test, hsv_lesion_analysis, gradcam_analysis |
| `artifacts/beans_resnet18/training_report.json` | 학습 기록 (저장소 미포함, 재생성) |

## 8. 제출 및 보안
- `.env`, 비밀번호, 토큰은 저장소에 올리지 않는다 (`.gitignore`).
- `dataset/`, `artifacts/*`, `media/jobs/*` 는 저장소 제외. 확보·재생성 절차는 2·4장.
- 정지: `docker compose stop` (데이터 보존). `docker compose down -v` 는 DB·Redis 데이터를 지우므로 사용하지 않는다.
- 제공 코드(01·02)는 수정하지 않았다. 추가한 파일은 `reports/` 아래뿐이다.
