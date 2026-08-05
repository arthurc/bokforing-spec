#!/usr/bin/env python3
"""Mekaniska kontroller av vad varje körning faktiskt skrev i bundlen.

Jämför varje körnings bundle/ mot fixturens orörda bundle och rapporterar
vilka koncepttyper som tillkommit. De assertions som handlar om grinden går
att avgöra så här i stället för att bedömas för hand.

    python3 check_bundle.py <sökväg till iteration-N>
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


def pristine_for(eval_dir):
    """Vilken startbundle evalen kopierade. Inkrementell-evalen utgår från
    bundle-partial/, där V1–V3 redan ligger — jämför mot fel baslinje och
    de tre ser ut som nyskrivna."""
    name = eval_dir.name
    return FIXTURES / ("bundle-partial" if "inkrementell" in name else "bundle")


def concepts(root):
    """Concept-ID -> type för varje .md med frontmatter (archive/ undantaget)."""
    out = {}
    for p in sorted(root.rglob("*.md")):
        if "archive" in p.relative_to(root).parts:
            continue
        m = re.match(r"^---\n(.*?)\n---", p.read_text(encoding="utf-8", errors="replace"), re.S)
        t = re.search(r"^type:\s*(.+)$", m.group(1), re.M) if m else None
        out[str(p.relative_to(root))] = t.group(1).strip() if t else None
    return out


def main(iteration):
    rows = []
    for run in sorted(pathlib.Path(iteration).glob("eval-*/*/outputs/bundle")):
        pristine = pristine_for(run.parents[2])
        base = concepts(pristine)
        cur = concepts(run)
        added = {k: v for k, v in cur.items() if k not in base}
        changed = [k for k in cur if k in base and (run / k).read_text() != (pristine / k).read_text()]
        removed = sorted(k for k in base if k not in cur)
        archive = [str(p.relative_to(run)) for p in (run / "archive").rglob("*") if p.is_file()]
        rows.append(dict(
            run="/".join(run.parts[-4:-2]),
            added_files=sorted(added),
            added_types=sorted({v for v in added.values() if v}),
            modified_files=sorted(changed),
            removed_files=removed,
            archive_files=sorted(archive),
            wrote_verifications=any(v == "Verification" for v in added.values()),
            wrote_anything=bool(added or changed or archive),
        ))
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
