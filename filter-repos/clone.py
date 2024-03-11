import pandas as pd
from subprocess import run

repos = pd.read_csv("repos.csv", header=0)
approved = repos[repos.iloc[:, 2] == "Approval ✅"]

for (name, link, *_) in approved.itertuples(index=False):
    print(f"Cloning {link}...")
    run(["git", "clone", "--depth", "1", link, name])
    print()
