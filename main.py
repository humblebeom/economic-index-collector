import os
from datetime import datetime
from pytz import timezone

from crawling_krx import KRXCrawler
from github_utils import get_github_repo, upload_github_issue


if __name__ == '__main__':
    seoul_timezone = timezone('Asia/Seoul')
    today = datetime.now(seoul_timezone)
    today_str = today.strftime("%Y%m%d")

    krx_crawler = KRXCrawler(today_str)
    kospi_df = krx_crawler.run("02")
    kosdaq_df = krx_crawler.run("03")
    if kospi_df.empty and kosdaq_df.empty:
        issue_title = f"[{today.strftime('%Y-%m-%d')}] 증시휴장일"
    else:
        contents = krx_crawler.make_contents(kospi_df, kosdaq_df)
        issue_title = krx_crawler.make_title(contents)

    my_github_token = os.getenv("MY_GITHUB_TOKEN")
    repository_name = "economic-index-collector"
    repo = get_github_repo(my_github_token, repository_name)
    upload_github_issue(repo, issue_title, issue_title)
