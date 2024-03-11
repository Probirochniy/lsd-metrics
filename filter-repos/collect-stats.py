from github import Github, Auth
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

auth = Auth.Token(os.getenv("GITHUB_TOKEN"))
github = Github(auth=auth)


repos = pd.read_csv("repos.csv", header=0)

with open("stats.csv", "w") as stats:
    print("name,is_archived,stars,forks,commits", file=stats)
    for (name, link, *_) in repos.itertuples(index=False):
        print(name)
        repo_name = link.removeprefix("https://github.com/").removesuffix("/")
        repo = github.get_repo(repo_name)

        is_archived = repo.archived
        stars = repo.stargazers_count
        forks = repo.forks_count

        commits = 0
        for c in repo.get_commits():
            commits += 1
            if commits == 10:
                break

        print(f"{name},{is_archived},{stars},{forks},{commits}", file=stats)
