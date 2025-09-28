#!/usr/bin/env python3
"""
Generate an SVG ER diagram from the current SQLite database.

Output: docs/database_schema_diagram.svg

Layout is a simple circular arrangement suitable for small/medium schemas.
"""
import os
import sys
import math
import sqlite3
from pathlib import Path


def resolve_repo_root() -> Path:
    # Assume this script is in <repo>/scripts/database/generate_schema_svg.py
    return Path(__file__).resolve().parents[2]


def resolve_db_path() -> Path:
    """Resolve database absolute path using backend config if available.
    Tries both package layouts: `src.auto_test` (when sys.path includes backend)
    and `auto_test` (when sys.path includes backend/src). Fallback to repo_root/auto_test.db.
    """
    repo_root = resolve_repo_root()
    backend_root = repo_root / "backend"
    backend_src = backend_root / "src"

    # Try import via `src.auto_test.config` (requires sys.path to include backend)
    try:
        if str(backend_root) not in sys.path:
            sys.path.insert(0, str(backend_root))
        from src.auto_test.config import get_config  # type: ignore
        cfg = get_config()
        return Path(cfg.DATABASE_PATH)
    except Exception:
        pass

    # Try import via `auto_test.config` (requires sys.path to include backend/src)
    try:
        if str(backend_src) not in sys.path:
            sys.path.insert(0, str(backend_src))
        from auto_test.config import get_config as get_config2  # type: ignore
        cfg = get_config2()
        return Path(cfg.DATABASE_PATH)
    except Exception:
        return (repo_root / "auto_test.db").resolve()


def load_schema(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]

    columns = {}
    for t in tables:
        cur.execute(f"PRAGMA table_info({t})")
        cols = [
            {
                "cid": r[0],
                "name": r[1],
                "type": r[2],
                "notnull": r[3] == 1,
                "dflt_value": r[4],
                "pk": r[5] > 0,
            }
            for r in cur.fetchall()
        ]
        columns[t] = cols

    fks = []
    for t in tables:
        cur.execute(f"PRAGMA foreign_key_list({t})")
        for r in cur.fetchall():
            # r: (id, seq, table, from, to, on_update, on_delete, match)
            fks.append(
                {
                    "from_table": t,
                    "to_table": r[2],
                    "from_col": r[3],
                    "to_col": r[4],
                }
            )
    return tables, columns, fks


def compute_layout(n: int, radius: int = 320, cx: int = 450, cy: int = 420):
    pos = []
    for i in range(n):
        angle = 2 * math.pi * i / max(n, 1)
        x = cx + int(radius * math.cos(angle))
        y = cy + int(radius * math.sin(angle))
        pos.append((x, y))
    return pos


def make_table_box(x, y, title, fields, box_w=260, header_h=28, row_h=20):
    # Top-left corner
    tlx = x - box_w // 2
    tly = y - (header_h + row_h * len(fields)) // 2
    h = header_h + row_h * len(fields)
    svg = []
    # Outer box
    svg.append(
        f'<rect x="{tlx}" y="{tly}" width="{box_w}" height="{h}" rx="8" ry="8" fill="#fff" stroke="#333" stroke-width="1.2" />'
    )
    # Header
    svg.append(
        f'<rect x="{tlx}" y="{tly}" width="{box_w}" height="{header_h}" fill="#f2f4f7" stroke="#333" stroke-width="0.8" />'
    )
    svg.append(
        f'<text x="{tlx + 10}" y="{tly + 19}" font-family="Inter, Arial" font-size="14" font-weight="700" fill="#111">{title}</text>'
    )
    # Rows
    for idx, (name, typ, pk) in enumerate(fields):
        y0 = tly + header_h + row_h * (idx + 1) - 6
        label = ("🔑 " if pk else "") + (name or "")
        type_text = typ or ""
        svg.append(
            f'<text x="{tlx + 10}" y="{y0}" font-family="Inter, Arial" font-size="12" fill="#333">{label}</text>'
        )
        svg.append(
            f'<text x="{tlx + box_w - 10}" y="{y0}" text-anchor="end" font-family="Inter, Arial" font-size="11" fill="#666">{type_text}</text>'
        )
    return "\n".join(svg)


def arrow(from_xy, to_xy, color="#6b7280"):
    x1, y1 = from_xy
    x2, y2 = to_xy
    # line
    parts = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.2" marker-end="url(#arrow)" />'
    ]
    return "\n".join(parts)


def generate_svg(tables, columns, fks, out_path: Path):
    W, H = 900, 840
    positions = {t: xy for t, xy in zip(tables, compute_layout(len(tables)))}

    nodes_svg = []
    for t in tables:
        cols = columns[t]
        fields = [(c["name"], c["type"], c["pk"]) for c in cols]
        nodes_svg.append(make_table_box(*positions[t], t, fields))

    edges_svg = []
    for fk in fks:
        ft = fk["from_table"]
        tt = fk["to_table"]
        if ft in positions and tt in positions:
            edges_svg.append(arrow(positions[ft], positions[tt]))

    svg = f"""
<svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'>
  <defs>
    <marker id='arrow' markerWidth='10' markerHeight='10' refX='10' refY='3' orient='auto' markerUnits='strokeWidth'>
      <path d='M0,0 L0,6 L9,3 z' fill='#6b7280' />
    </marker>
  </defs>
  <rect x='0' y='0' width='{W}' height='{H}' fill='#fafafa' />
  <text x='{W//2}' y='28' text-anchor='middle' font-family='Inter, Arial' font-size='16' font-weight='700' fill='#111'>Database Schema Diagram</text>
  <g>
    {''.join(edges_svg)}
  </g>
  <g>
    {''.join(nodes_svg)}
  </g>
</svg>
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")


def main():
    db_path = resolve_db_path()
    conn = sqlite3.connect(str(db_path))
    try:
        tables, columns, fks = load_schema(conn)
    finally:
        conn.close()

    out = resolve_repo_root() / "docs" / "database_schema_diagram.svg"
    generate_svg(tables, columns, fks, out)
    print(f"Generated: {out} (from {db_path})")


if __name__ == "__main__":
    main()