"""산출물 1용 데이터 점검 보조 스크립트 (제공 코드 아님, 제공 코드 수정 없음).

- dataset/{train,val,test}/{3클래스} 이미지 개수 집계
- train/train 처럼 압축 해제 중 중첩된 폴더 여부 확인
- SHA-256 해시로 Split 간 동일 파일(데이터 누출) 확인

실행:  python reports/tools/check_dataset.py --data dataset --out reports/data/dataset_check.md
"""
import argparse
import hashlib
from collections import defaultdict
from pathlib import Path

SPLITS = ["train", "val", "test"]
CLASSES = ["angular_leaf_spot", "bean_rust", "healthy"]
EXTS = {".jpg", ".jpeg", ".png", ".webp"}  # training/finetune.py 의 EXTS 와 동일


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="dataset")
    ap.add_argument("--out", default="reports/data/dataset_check.md")
    args = ap.parse_args()
    root = Path(args.data)

    lines = ["# 데이터 점검 결과 (reports/tools/check_dataset.py 자동 생성)", ""]
    problems = []

    counts = {s: {} for s in SPLITS}
    hashes = defaultdict(list)
    for s in SPLITS:
        for c in CLASSES:
            folder = root / s / c
            if not folder.is_dir():
                problems.append(f"폴더 없음: {folder}")
                counts[s][c] = 0
                continue
            files = [p for p in sorted(folder.iterdir()) if p.is_file() and p.suffix.lower() in EXTS]
            counts[s][c] = len(files)
            if not files:
                problems.append(f"이미지 0장: {folder}")
            subdirs = [p.name for p in folder.iterdir() if p.is_dir()]
            if subdirs:
                problems.append(f"하위 폴더 존재(중첩 의심): {folder} -> {subdirs}")
            for p in files:
                hashes[sha256(p)].append((s, c, p.name))
        extra = [p.name for p in (root / s).iterdir() if p.is_dir() and p.name not in CLASSES] if (root / s).is_dir() else []
        if extra:
            problems.append(f"{root / s} 안에 3클래스 외 폴더 존재: {extra}")

    lines += ["## 1. 클래스별 이미지 수", "",
              "| 클래스 | Train | Validation(val) | Test |", "|---|---:|---:|---:|"]
    for c in CLASSES:
        lines.append(f"| {c} | {counts['train'][c]} | {counts['val'][c]} | {counts['test'][c]} |")
    tot = {s: sum(counts[s].values()) for s in SPLITS}
    lines += [f"| **합계** | **{tot['train']}** | **{tot['val']}** | **{tot['test']}** |", ""]

    cross, within = [], []
    for h, locs in hashes.items():
        if len(locs) < 2:
            continue
        splits = {l[0] for l in locs}
        (cross if len(splits) > 1 else within).append((h, locs))
    lines += ["## 2. 중복·누출 점검 (SHA-256 동일 파일 기준)", "",
              f"- 검사 파일 수: {sum(tot.values())}",
              f"- Split 간 동일 파일(누출): **{len(cross)}건**",
              f"- 같은 Split 내 동일 파일: {len(within)}건",
              "- 한계: 바이트가 완전히 같은 파일만 찾음. 같은 잎을 다시 찍은 유사 사진은 이 방법으로 찾을 수 없음", ""]
    for h, locs in (cross + within)[:30]:
        lines.append(f"- `{h[:12]}…` : " + ", ".join(f"{s}/{c}/{n}" for s, c, n in locs))

    lines += ["", "## 3. 구조 점검", ""]
    lines += [f"- ⚠ {p}" for p in problems] or ["- 이상 없음 (3개 Split × 3개 클래스 폴더, 모두 이미지 존재, 중첩 폴더 없음)"]

    text = "\n".join(lines) + "\n"
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(text)
    print(f"저장: {out}")


if __name__ == "__main__":
    main()
