import pandas as pd
from subprocess import run
import json

repos = pd.read_csv("repos.csv", header=0)

with open("lines.csv", "w") as out:
    for (name, _link, approved, *_) in repos.itertuples(index=False):
        if approved != "Approval ✅":
            print(f"{name},-1", file=out)
            continue

        tokei = run(
            ["tokei", "--output", "json", "--type", "Python", name],
            capture_output=True,
            text=True,
        )
        result = json.loads(tokei.stdout)["Total"]
        loc = result["code"] + result["comments"] + result["blanks"]

        print(f"{name},{loc}", file=out)
