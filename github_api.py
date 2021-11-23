from github import Github
from pprint import pprint
import pandas as pd
import json
from tqdm.notebook import tqdm



def get_repo_dict(repo):
    return {"Full name": repo.full_name,
            "Description": repo.description,
            "Date created": repo.created_at,
            "Date of last push": repo.pushed_at,
            "Home Page": repo.homepage,
            "Language": repo.language,
            "Number of forks": repo.forks,
            "Number of stars": repo.stargazers_count,
            "Topics": repo.get_topics(),
            "Labels": [i._rawData for i in repo.get_labels()],
            "Contributors": [i._rawData for i in repo.get_contributors()],
            "Contributors Count": repo.get_contributors().totalCount,
            #"Subscribers": [i._rawData for i in repo.get_subscribers()],
            "Subscribers Count": repo.get_subscribers().totalCount,
            #"Watchers": [i._rawData for i in repo.get_watchers()],
            "Watchers Count": repo.get_watchers().totalCount            
           }


g = Github()
TOPIC = "interview-practice"
all_repo = g.search_repositories(f'topic:{TOPIC}')
print(all_repo.totalCount)

top_repo = []
for i, repo in enumerate(all_repo):
    top_repo.append(repo)
    if i == 99:
        break


repo_list = []
for repo in tqdm(top_repo, total=len(top_repo)):
    repo_list.append(get_repo_dict(repo))

with open(f'{TOPIC}_top.json', 'w', encoding='utf-8') as f:
    json.dump(repo_list, f, ensure_ascii=False, indent=4, default=str)  
repos_df = pd.DataFrame(repo_list)
repos_df