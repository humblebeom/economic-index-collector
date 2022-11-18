import requests
from typing import List, Dict, Tuple
from datetime import datetime


def request_daily_market_data(token: str, url: str, today: str) -> List[Dict]:
    """
    KRX Open API를 통한 시장별/일별 시세정보 요청 함수
    :param token: KRX Open API token
    :param url: 시장별(KOSPI, KOSDAQ) Endpoint
    :param today:'YYYYMMDD'
    :return: List[Dict]
        * Description
            'BAS_DD': "기준일자",
            'IDX_CLSS': "계열구분",
            'IDX_NM': "지수명",
            'CLSPRC_IDX': "종가",
            'CMPPREVDD_IDX': "대비",
            'FLUC_RT': "등락률",
            'OPNPRC_IDX': "시가",
            'HGPRC_IDX': "고가",
            'LWPRC_IDX': "저가",
            'ACC_TRDVOL': "거래량",
            'ACC_TRDVAL': "거래대금",
            'MKTCAP': "상장시가총액",
    """
    headers = {
        'AUTH_KEY': token,
        'basDd': today
    }
    response = requests.get(
        url=url,
        params=headers
    )
    data = []
    if response.status_code == 200:
        data = response.json()

    return data.get('OutBlock_1', [])


def extract_market_data(data: List[Dict]) -> tuple:
    """
    일별 시장 시세정보에서 시장전체의 시가총액, 거래대금, 거래대금 비율을 반환
        * 거래대금 비율 = 거래대금 / 시가총액
    :param data: 일별시세정보
    :return: tuple
    """
    trd_val = data[0].get('ACC_TRDVAL')  # 일별 거래대금
    mcap = data[0].get('MKTCAP') # 시가총액

    if trd_val and mcap:
        trd_val = int(trd_val)
        mcap = int(mcap)

    return mcap, trd_val


def aggregate(*args):
    mcap = 0
    trd_val = 0
    for arg in args:
        data = extract_market_data(arg)
        mcap += data[0]
        trd_val += data[1]

    return mcap, trd_val, trd_val / mcap


def make_title(today: datetime, data: Tuple[float]) -> str:
    mcap = data[0]
    trd_val = data[1]
    ratio = data[2]
    trillion = 1_000_000_000_000
    contents = f"[{today.strftime('%Y-%m-%d')}] KOSPI, KOSDAQ " \
               f"시총(KRW): {mcap / trillion:.1f} 조, " \
               f"거래대금(KRW): {trd_val / trillion:.1f} 조, " \
               f"거래대금/시총: {ratio * 100:.2f} %\n"

    return contents
