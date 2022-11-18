from github import Github, Repository


def get_github_repo(access_token: str, repository_name: str) -> Repository:
    """
    GitHub repo object를 얻는 함수
    :param access_token: GitHub access token
    :param repository_name: repo 이름
    :return: repo object
    """
    g = Github(access_token)
    return g.get_user().get_repo(repository_name)


def upload_github_issue(repo: Repository, title: str, body: str) -> None:
    """
    해당 repo에 title 이름으로 issue를 생성하고, 내용을 body로 채우는 함수
    :param repo: repo 이름
    :param title: issue title
    :param body: issue body
    :return: None
    """
    repo.create_issue(title=title, body=body)
