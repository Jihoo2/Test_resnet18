"""산출물 6용 응답시간 측정 보조 스크립트 (제공 코드 아님, 제공 코드 수정 없음).

서버(FastAPI)·Worker(Celery)·Redis·PostgreSQL이 모두 켜진 상태에서 실행한다.
HTTP 클라이언트는 requirements.txt 에 이미 있는 httpx 를 사용한다.

측정 순서 (모두 dataset/test 의 서로 다른 실제 이미지 사용)
  0) warm-up  : 동기 1장 + 비동기 1장. 비교에서 제외(note=warmup)
  1) sync     : 새 이미지 N장 (보통 MISS)       → 같은 N장 재요청 (보통 HIT)
  2) async    : 또 다른 새 이미지 N장 (보통 MISS) → 1)에서 쓴 이미지 N장 (Worker도 같은 Redis 캐시 → 보통 HIT)
cache_status 는 '가정'이 아니라 응답의 cache_hit 값으로 기록한다.

실행:  python reports/tools/measure_timings.py --repeat 5
결과:  reports/data/timings.csv (원본), reports/data/timings_summary.md (중앙값)
"""
import argparse
import csv
import statistics
import time
from pathlib import Path

import httpx

CLASSES = ["angular_leaf_spot", "bean_rust", "healthy"]
EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}


def pick_images(test_root: Path, n: int) -> list[Path]:
    per_class = [[p for p in sorted((test_root / c).iterdir()) if p.suffix.lower() in EXTS] for c in CLASSES]
    out, i = [], 0
    while len(out) < n:  # 클래스를 번갈아 가며 선택
        bucket = per_class[i % 3]
        idx = i // 3
        if idx < len(bucket):
            out.append(bucket[idx])
        i += 1
        if i > 3 * max(len(b) for b in per_class):
            raise SystemExit("test 이미지가 부족합니다.")
    return out


def files_of(path: Path):
    return {"image": (path.name, path.read_bytes(), MIME[path.suffix.lower()])}


def ms(sec: float) -> float:
    return round(sec * 1000, 1)


def run_sync(client, path):
    t0 = time.perf_counter()
    r = client.post("/api/sync/classify/", files=files_of(path))
    http = ms(time.perf_counter() - t0)
    r.raise_for_status()
    j = r.json()
    return {"http_ms": http, "final_ms": http, "inference_ms": j.get("inference_ms"),
            "cache_hit": j.get("cache_hit"), "label": j["top1"]["label"], "score": round(j["top1"]["score"], 4),
            "job_id": ""}


def run_async(client, path, poll_s, timeout_s):
    t0 = time.perf_counter()
    r = client.post("/api/async/classify/", files=files_of(path))
    http = ms(time.perf_counter() - t0)
    if r.status_code != 202:
        raise SystemExit(f"비동기 접수 실패 HTTP {r.status_code}: {r.text}")
    job = r.json()
    while True:
        s = client.get(job["check_url"]).json()
        if s["status"] in ("done", "failed"):
            break
        if time.perf_counter() - t0 > timeout_s:
            raise SystemExit(f"job {job['job_id']} 이 {timeout_s}s 안에 끝나지 않음 (Worker 실행 여부 확인)")
        time.sleep(poll_s)
    final = ms(time.perf_counter() - t0)
    top1 = s.get("top1") or {}
    return {"http_ms": http, "final_ms": final, "inference_ms": s.get("inference_ms"),
            "cache_hit": s.get("cache_hit"), "label": top1.get("label", s["status"]),
            "score": round(top1["score"], 4) if top1.get("score") is not None else "",
            "job_id": job["job_id"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument("--data", default="dataset")
    ap.add_argument("--repeat", type=int, default=5)
    ap.add_argument("--poll-ms", type=int, default=100, help="비동기 상태 조회 간격(ms)")
    ap.add_argument("--timeout", type=float, default=120)
    ap.add_argument("--out", default="reports/data/timings.csv")
    args = ap.parse_args()

    n = args.repeat
    imgs = pick_images(Path(args.data) / "test", 2 + 2 * n)
    warm_sync, warm_async = imgs[0], imgs[1]
    sync_imgs, async_imgs = imgs[2:2 + n], imgs[2 + n:2 + 2 * n]

    rows = []
    def add(run_id, path_name, img, res, note=""):
        status = "HIT" if res["cache_hit"] else "MISS"
        rows.append({"run_id": run_id, "path": path_name, "cache_status": status,
                     "http_ms": res["http_ms"], "final_ms": res["final_ms"],
                     "inference_ms": "" if res["inference_ms"] is None else res["inference_ms"],
                     "job_id": res["job_id"], "image": f"{img.parent.name}/{img.name}",
                     "gt_label": img.parent.name, "pred_label": res["label"], "score": res["score"], "note": note})
        print(rows[-1])

    poll = args.poll_ms / 1000
    with httpx.Client(base_url=args.base_url, timeout=args.timeout) as c:
        assert c.get("/health").json().get("status") == "ok", "/health 실패"
        add(0, "sync", warm_sync, run_sync(c, warm_sync), "warmup")
        add(0, "async", warm_async, run_async(c, warm_async, poll, args.timeout), "warmup")
        for i, img in enumerate(sync_imgs, 1):
            add(i, "sync", img, run_sync(c, img))
        for i, img in enumerate(sync_imgs, 1):
            add(i, "sync", img, run_sync(c, img), "repeat_same_image")
        for i, img in enumerate(async_imgs, 1):
            add(i, "async", img, run_async(c, img, poll, args.timeout))
        for i, img in enumerate(sync_imgs, 1):
            add(i, "async", img, run_async(c, img, poll, args.timeout), "repeat_same_image")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    md = ["# 응답시간 측정 요약 (measure_timings.py 자동 생성, 단위 ms, warm-up 제외 중앙값)", "",
          f"- 서버: {args.base_url} / 반복: {n}회 / 비동기 상태조회 간격: {args.poll_ms}ms (final_ms 에 폴링 대기 포함)",
          f"- 측정 시각: {time.strftime('%Y-%m-%d %H:%M:%S')}", "",
          "| 경로 | 캐시 | n | HTTP 응답 중앙값 | 최종 결과 확인 중앙값 | 추론시간 중앙값 |", "|---|---|---:|---:|---:|---:|"]
    for p in ("sync", "async"):
        for cs in ("MISS", "HIT"):
            g = [r for r in rows if r["path"] == p and r["cache_status"] == cs and r["note"] != "warmup"]
            if not g:
                md.append(f"| {p} | {cs} | 0 | - | - | - |")
                continue
            inf = [r["inference_ms"] for r in g if r["inference_ms"] != ""]
            md.append(f"| {p} | {cs} | {len(g)} | {statistics.median(r['http_ms'] for r in g)} | "
                      f"{statistics.median(r['final_ms'] for r in g)} | "
                      f"{statistics.median(inf) if inf else 'null (추론 생략)'} |")
    warm = [r for r in rows if r["note"] == "warmup"]
    md += ["", "warm-up(비교 제외): " + ", ".join(f"{r['path']} {r['cache_status']} final={r['final_ms']}ms" for r in warm)]
    new_hit = [r for r in rows if r["note"] == "" and r["cache_status"] == "HIT"]
    if new_hit:
        md.append(f"\n⚠ 새 이미지인데 HIT {len(new_hit)}건: 10분(TTL 600s) 안에 같은 이미지를 이미 보낸 적이 있음. MISS 그룹이 부족하면 10분 뒤 다시 측정")
    summary = out.with_name("timings_summary.md")
    summary.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"\n저장: {out}, {summary}")


if __name__ == "__main__":
    main()
