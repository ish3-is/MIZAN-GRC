"""Synchronize document-level provenance records from the versioned source register."""

import json
import os
import sys
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("DATABASE_URL", "sqlite:///" + str(ROOT / "mizan.db").replace("\\", "/"))

from app.db import Record, Session  # noqa: E402


def sync():
    sources = json.loads((ROOT / "regulatory" / "sources.json").read_text(encoding="utf-8"))
    with Session() as session:
        existing = {
            record.payload.get("framework_id"): record
            for record in session.scalars(select(Record).where(Record.kind == "source"))
        }
        for source in sources:
            item = existing.get(source["framework_id"])
            if item:
                item.title = source["source_title"]
                item.payload = source
                item.version += 1
            else:
                session.add(
                    Record(
                        kind="source",
                        title=source["source_title"],
                        department="Governance",
                        payload=source,
                    )
                )
        session.commit()
    print(f"Synchronized {len(sources)} provenance records.")


if __name__ == "__main__":
    sync()
