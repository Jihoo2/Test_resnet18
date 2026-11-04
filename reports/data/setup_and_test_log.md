# 실행 환경·설치·테스트 터미널 기록 (원문 발췌)

> 2026-11-04 작업 중 실제 터미널 출력에서 옮긴 기록이다. 캡처가 없는 항목(환경 확인, 설치 오류, pytest)의 증빙으로 사용한다.

## 1. OS

```text
$ lsb_release -a
Distributor ID: Ubuntu
Description:    Ubuntu 26.04.1 LTS
Release:        26.04
Codename:       resolute
```
Celery 배너: `Linux-6.18.54.1-microsoft-standard-WSL2-x86_64-with-glibc2.43`

## 2. Python 3.11 — 오류 E-01 (설치되어 있지 않음)

```text
$ python3.11 --version
명령어 'python3.11' 을(를) 찾을 수 없습니다. 다음 명령어로 시도하시겠습니까:
  deb python3.14 ...
```
조치: uv 로 Python 3.11 만 별도 설치 (시스템 Python 미변경)
```text
$ curl -LsSf https://astral.sh/uv/install.sh | sh
uv 0.13.7 (x86_64-unknown-linux-gnu)
$ uv venv --python 3.11 --seed .venv
Using CPython 3.11.18
Creating virtual environment with seed packages at: .venv
$ python --version
Python 3.11.18
$ pip --version
pip 26.3 from /home/user1/fastapi_resnet18/.venv/lib/python3.11/site-packages/pip (python 3.11)
```

## 3. 주요 패키지·GPU

```text
$ python -c "import torch, transformers, fastapi; print(torch.__version__, transformers.__version__, fastapi.__version__, 'cuda:', torch.cuda.is_available())"
2.15.0+cu132 4.57.6 0.162.0 cuda: True

$ nvidia-smi
| NVIDIA GeForce RTX 3060   ... |  951MiB / 12288MiB |
```
02 설치 시 추가: sqlalchemy 2.1.8, psycopg 3.3.7 (+psycopg-binary), redis 6.4.0, celery 5.6.3, kombu 5.7.0 / 기존: uvicorn 0.54.0, pillow 12.3.0, torchvision 0.29.2, httpx 0.28.1, pytest 9.2.0
분석 전용(서비스 미사용, requirements.txt 미포함): opencv-python-headless 5.0.0.93

## 4. Docker — 오류 E-02 (WSL 연동 미적용)

```text
$ docker --version
The command 'docker' could not be found in this WSL 2 distro.
We recommend to activate the WSL integration in Docker Desktop settings.

$ wsl.exe -l -v
  NAME              STATE           VERSION
* Ubuntu            Running         2
  docker-desktop    Running         2
  Ubuntu-22.04      Stopped         2
```
확인: Docker Desktop → Settings → WSL integration 에 기본 배포판·UBUNTU 이미 활성화 → `wsl.exe --shutdown` 후 재접속
```text
$ docker --version
Docker version 29.9.2, build a82e528
$ docker compose version
Docker Compose version v5.6.1
```
(기존 다른 실습 컨테이너 `sentiment-redis` 127.0.0.1:6380, `fastapi_sentiment-postgres-1` 127.0.0.1:5433 실행 중 — 본 프로젝트 포트와 무관)

## 5. Redis 6379 포트 충돌 — 오류 E-03 (캡처: evidence/E01_redis_port_conflict.png)

```text
$ docker compose up -d redis postgres
Error response from daemon: ports are not available: exposing port TCP 127.0.0.1:6379 -> 127.0.0.1:0: /forwards/expose returned unexpected status: 500

$ sudo ss -ltnp | grep 6379
LISTEN 0 511 127.0.0.1:6379 0.0.0.0:* users:(("redis-server",pid=119,fd=8))
LISTEN 0 511     [::1]:6379    [::]:* users:(("redis-server",pid=119,fd=9))
$ systemctl is-active redis-server
active

$ sudo systemctl stop redis-server
$ sudo systemctl disable redis-server
$ docker compose up -d redis postgres
 ✔ Container fastapi_resnet18-redis-1    Started
PONG
/var/run/postgresql:5432 - accepting connections
```
복원 방법(평가 후): `sudo systemctl enable --now redis-server`

## 6. 모의 테스트 (pytest)

01 단계 (`test_api.py`, 01 버전 main.py):
```text
$ pytest -q test_api.py
.                                                                        [100%]
StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
1 passed, 1 warning in 0.24s
```

02 단계 (`tests/test_api.py`, SQLite + 가짜 분류기 + 가짜 Broker):
```text
$ python -m py_compile ai/*.py main.py tests/test_api.py && echo "02 문법 OK"
02 문법 OK
$ python -m pytest -q tests/test_api.py
....                                                                     [100%]
4 passed, 1 warning in 0.55s
```
경고는 라이브러리 버전 안내(DeprecationWarning)이며 테스트 결과와 무관.

## 7. Head-only 학습 결과 파일

```text
$ ls -lh artifacts/beans_resnet18/
-rw-r--r-- 1 user1 user1 808 Nov  4 10:10 config.json
-rw------- 1 user1 user1 43M Nov  4 10:10 model.safetensors
-rw-r--r-- 1 user1 user1 352 Nov  4 10:10 preprocessor_config.json
-rw-r--r-- 1 user1 user1 468 Nov  4 10:10 training_report.json
```

## 8. 413 실환경 확인

```text
$ head -c 6000000 /dev/urandom > reports/data/big_6mb.jpg
-rw-r--r-- 1 user1 user1 5.8M Nov  4 11:20 reports/data/big_6mb.jpg
$ curl -i -X POST -F "image=@reports/data/big_6mb.jpg" http://127.0.0.1:8000/api/sync/classify/
HTTP/1.1 100 Continue

HTTP/1.1 413 Request Entity Too Large
server: uvicorn
content-type: application/json

{"detail":"5MB 이하 파일만 허용합니다."}
```
(시험 파일은 확인 후 삭제)
