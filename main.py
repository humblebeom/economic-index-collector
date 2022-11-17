import os
from typing import List, Dict
from datetime import datetime
from pytz import timezone
from dotenv import dotenv_values


from crawling_krx_api import request_daily_market_data, aggregate, make_content
from github_utils import get_github_repo, upload_github_issue


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config = dotenv_values(os.path.join(base_dir, ".env"))
    github_token = config.get('MY_GITHUB_TOKEN')
    krx_token = config.get('KRX_API_KEY')
    krx_endpoint = config.get('KRX_API_ENDPOINT')

    seoul_timezone = timezone('Asia/Seoul')
    today = datetime.now(seoul_timezone)
    today_date = today.strftime("%Y%m%d")

    kospi_url = krx_endpoint + 'kospi_dd_trd'
    kosdaq_url = krx_endpoint + 'kosdaq_dd_trd'

    kospi_data = request_daily_market_data(krx_token, kospi_url, today_date)
    kosdaq_data = request_daily_market_data(krx_token, kosdaq_url, today_date)
    result_data = aggregate(kospi_data, kosdaq_data)
    upload_contents = make_content(today, result_data)

