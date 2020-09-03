import json
import os
from pathlib import Path
from subprocess import check_output
from uuid import uuid4

d = Path.home() / ".password-store"
os.chdir(d)


def process_dir(d, data, dir_id=None):
    for f in d.iterdir():
        if f.name.startswith("."):
            continue

        if f.is_file() and f.name.endswith(".gpg"):
            name = f.name[:-4]
            pass_name = str(f)[:-4]
            lines = (
                check_output(["pass", "show", pass_name], encoding="utf-8")
                .strip()
                .splitlines()
            )
            password = lines[0]
            username = None
            notes = ""
            for l in lines[1:]:
                if l.startswith("login:"):
                    username = l.split(":", maxsplit=1)[1].strip()
                    continue

                notes += l + "\n"

            notes = notes.strip()
            if not notes:
                notes = None

            data["items"].append(
                {
                    "id": str(uuid4()),
                    "folderId": dir_id,
                    "type": 1,
                    "name": name,
                    "notes": notes,
                    "login": {"username": username, "password": password,},
                }
            )
        elif f.is_dir():
            new_dir_id = str(uuid4())
            data["folders"].append(
                {"id": new_dir_id, "name": str(f),}
            )
            process_dir(f, data, new_dir_id)


data = {
    "folders": [],
    "items": [],
}
process_dir(Path(), data)

with open("out.json", "w") as f:
    json.dump(data, f)
