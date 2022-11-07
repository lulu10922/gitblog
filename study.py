import argparse
import re

from github import Github

MD_HEAD = """## Gitblog
My personal blog using issues and GitHub Actions (随意转载，无需署名)
[RSS Feed](https://raw.githubusercontent.com/{repo_name}/master/feed.xml)
"""

FRIENDS_LABEL = ["Friends"]
FRIENDS_TABLE_HEAD = "| Name | Link | Desc | \n | ---- | ---- | ---- |\n"
FRIENDS_TABLE_TEMPLATE = "| {name} | {link} | {desc} |\n"
FRIENDS_INFO_DICT = {
    "名字": "",
    "链接": "",
    "描述": "",
}

IGNORE_LABELS = [FRIENDS_LABEL]

def gen_header(md, repo_name):
    with open(md, 'w', encoding='utf-8') as md:
        md.write(MD_HEAD.format(repo_name = repo_name))

def is_hearted_by_me(comment, me):
    reactions =  list(comment.get_reactions())
    for reaction in reactions:
        if reaction.content == 'heart' and reaction.user.login == me:
            return True
        
    return False

def _make_friend_table_string(s):
    str = re.split('：|\r\n', s)
    for key in FRIENDS_INFO_DICT.keys():
        pos = str.index(key)
        FRIENDS_INFO_DICT[key] = str[pos + 1]
    
    return FRIENDS_TABLE_TEMPLATE.format(name = FRIENDS_INFO_DICT["名字"],
                                    link = FRIENDS_INFO_DICT["链接"],
                                    desc = FRIENDS_INFO_DICT["描述"])

def gen_friends(md, repo, me):

    s = "## 友情链接\n"
    s += FRIENDS_TABLE_HEAD

    issues = list(repo.get_issues(labels = FRIENDS_LABEL))
    for issue in issues:
        for comment in issue.get_comments():
            if is_hearted_by_me(comment, me):
                s += _make_friend_table_string(comment.body)

    with open(md, 'a+', encoding='utf-8') as md:
        md.write(s)

def gen_other_labels(md, repo, me):
    labels = repo.get_labels()
    s = ""
    for label in labels:
        if label.name in IGNORE_LABELS:
            continue

        issue_created_by_me = False
        issues = repo.get_issues(labels = [label])
        for issue in issues:
            if issue.user.login == me:
                if not issue_created_by_me:
                    issue_created_by_me = True
                    s += f"## {label.name}\n"
                s += f"[{issue.title}]({issue.html_url})\n"
    
    with open(md, 'a+', encoding='utf-8') as md:
        md.write(s)

def main(token, repo_name, issue_number):
    g = Github(token)
    repo = g.get_repo(repo_name)
    me = g.get_user().login

    gen_header("README.md", repo_name)
    for func in [gen_friends, gen_other_labels]:
        func("README.md", repo, me)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('token')
    parser.add_argument('repo_name')
    parser.add_argument('--issue_number')

    args = parser.parse_args()
    main(args.token, args.repo_name, args.issue_number)