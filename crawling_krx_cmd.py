from pytz import timezone
from typing import List, Dict
from datetime import datetime
import requests
import pandas as pd
from io import BytesIO


def request_daily_market_data_using_cmd(today: str, market_code: str) -> tuple:
    """
    KRX 정보데이터시스템을 통한 시장별/일별 시세정보 요청 함수
    :param today: "YYYYMMDD"
    :param market_code:
        ("01": KRX, "02": KOSPI, "03": KOSDAQ)
    :return: tuple: 시장(외국주포함)의 (일별시가총액, 일별거래대금)
    """
    generate_cmd_url = 'http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd'
    query_params = {
        "idxIndMidclssCd": market_code,
        "trdDd": today,
        "share": "1",
        "money": "1",
        "csvxls_isNo": "false",
        "name": "fileDown",
        "url": "dbms/MDC/STAT/standard/MDCSTAT00101",
    }
    headers = {
        'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    gen_res = requests.get(generate_cmd_url, query_params, headers=headers)
    download_cmd_url = 'http://data.krx.co.kr/comm/fileDn/download_excel/download.cmd'
    form_data = {
        'code': gen_res.content
    }
    # TODO: data request, data extract 함수 분리
    download_res = requests.post(download_cmd_url, form_data, headers=headers)
    df = pd.read_excel(BytesIO(download_res.content))
    mcap = df.loc[0, "상장시가총액"]
    trd_val = df.loc[0, "거래량"]

    return mcap, trd_val


if __name__ == '__main__':
    a, b = request_daily_market_data_using_cmd("20221121", "03")
    print()


