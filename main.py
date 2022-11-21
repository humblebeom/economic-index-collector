import os
from datetime import datetime, timedelta
from pytz import timezone
from dotenv import dotenv_values


from crawling_krx_api import request_daily_market_data, aggregate, make_title
from github_utils import get_github_repo, upload_github_issue


if __name__ == '__main__':
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    # config = dotenv_values(os.path.join(base_dir, ".env"))
    # krx_token = config.get("KRX_API_KEY")
    # my_github_token = config.get('MY_GITHUB_TOKEN')
    krx_token = os.getenv('KRX_API_KEY')
    my_github_token = os.getenv("MY_GITHUB_TOKEN")

    seoul_timezone = timezone('Asia/Seoul')
    today = datetime.now(seoul_timezone) - timedelta(days=1)
    today_date = today.strftime("%Y%m%d")

    krx_endpoint = "http://data-dbg.krx.co.kr/svc/apis/idx/"
    kospi_url = krx_endpoint + "kospi_dd_trd"
    kosdaq_url = krx_endpoint + "kosdaq_dd_trd"

    kospi_data = request_daily_market_data(krx_token, kospi_url, today_date)
    kosdaq_data = request_daily_market_data(krx_token, kosdaq_url, today_date)

    try:
        result_data = aggregate(kospi_data, kosdaq_data)
        issue_title = make_title(today, result_data)
    except IndexError as e:
        issue_title = f"[{today.strftime('%Y-%m-%d')}] 증시휴장일"

    upload_contents = issue_title
    repository_name = "economic-index-collector"
    repo = get_github_repo(my_github_token, repository_name)
    upload_github_issue(repo, issue_title, upload_contents)
