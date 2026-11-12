"""Recoverable reset of the local MIZAN demonstration database only."""

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "RESET MIZAN DEMO"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", required=True)
    args = parser.parse_args()
    if args.confirm != EXPECTED:
        raise SystemExit(f"Confirmation must be exactly: {EXPECTED}")
    database = (ROOT / "mizan.db").resolve()
    if database.parent != ROOT.resolve():
        raise SystemExit("Refusing a database outside the project root")
    if not database.exists():
        raise SystemExit("Local mizan.db does not exist")
    with sqlite3.connect(database) as connection:
        tables = {row[0] for row in connection.execute("select name from sqlite_master where type='table'")}
        if "work_items" in tables:
            non_demo = connection.execute("select count(*) from work_items where simulated = 0").fetchone()[0]
            if non_demo:
                raise SystemExit(f"Refusing reset: {non_demo} non-simulated work item(s) exist")
        config = connection.execute("select payload from records where kind='configuration' limit 1").fetchone()
        if not config or "MIZAN DEMO" not in json.loads(config[0]).get("environment", ""):
            raise SystemExit("Refusing reset: database is not identified as the MIZAN demo environment")
    backup_dir = ROOT / "data" / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_dir / f"mizan-before-reset-{stamp}.db"
    shutil.copy2(database, backup)
    database.unlink()
    env = os.environ.copy()
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            env[key] = value
    env["DATABASE_URL"] = "sqlite:///" + str(database).replace("\\", "/")
    env["EVIDENCE_DIR"] = str(ROOT / "data" / "evidence")
    python = ROOT / ".venv" / "Scripts" / "python.exe"
    subprocess.run([python, "-m", "alembic", "upgrade", "head"], cwd=ROOT / "backend", env=env, check=True)
    subprocess.run([python, "-m", "app.seed"], cwd=ROOT / "backend", env=env, check=True)
    print(f"Reset complete. Recoverable backup: {backup}")
    print("Local secrets and evidence files were preserved.")


if __name__ == "__main__":
    main()
