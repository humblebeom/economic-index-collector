from typing import Dict, Tuple
import requests
from copy import copy
import pandas as pd
from io import BytesIO
import warnings
from datetime import datetime


class KRXCrawler:
    def __init__(self, target_date: str):
        """
        :param target_date: "YYYYMMDD"
        """
        self.target_date = target_date
        self.uri = {
            "gen_otp": "http://data.krx.co.kr/comm/fileDn/GenerateOTP/generate.cmd",
            "download_excel": "http://data.krx.co.kr/comm/fileDn/download_excel/download.cmd",
        }
        self.headers = {
            'Referer': 'http://data.krx.co.kr/contents/MDC/MDI/mdiLoader',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
        self.query_params = {
            "trdDd": target_date,
            "share": "1",
            "money": "1",
            "csvxls_isNo": "false",
            "name": "fileDown",
            "url": "dbms/MDC/STAT/standard/MDCSTAT00101",
        }
        self.trillion = 1_000_000_000_000

    def run(self, market_code: str) -> pd.DataFrame:
        """
        시장의 일별시세정보를 반환
        :param market_code: 시장 코드("01": KRX, "02": KOSPI, "03": KOSDAQ)
        :return: df
        """
        form_data = self.request_otp(market_code)
        content = self.request_data(market_code, form_data)
        df = self.make_dataframe(content)

        return df

    def request_otp(self, market_code: str) -> Dict:
        """
        KRX 정보데이터시스템에 일별시세조회를 위한 OTP 생성 요청
        :param market_code: 시장 코드("01": KRX, "02": KOSPI, "03": KOSDAQ)
        :return: form_data
        """
        query_params = copy(self.query_params)
        query_params["idxIndMidclssCd"] = market_code
        url = self.uri.get('gen_otp')
        res = requests.get(url, query_params, headers=self.headers)
        form_data = {
            'code': res.content
        }

        return form_data

    def request_data(self, market_code: str, form_data: Dict) -> bytes:
        """
        KRX 정보데이터시스템에 시장의 일별시세정보 요청
        :param market_code: 시장 코드("01": KRX, "02": KOSPI, "03": KOSDAQ)
        :param form_data: KRX 정보데이터시스템 조회를 위한 OTP
        :return: bytes data
        """
        query_params = copy(self.query_params)
        query_params["idxIndMidclssCd"] = market_code
        url = self.uri.get('download_excel')
        res = requests.post(url, form_data, headers=self.headers)

        return res.content

    @staticmethod
    def make_dataframe(content: bytes) -> pd.DataFrame:
        """
        bytes 데이터를 pandas dataframe으로 변환
        :param content: bytes
        :return: df
        """
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            df = pd.read_excel(BytesIO(content), engine="openpyxl")

        return df

    @staticmethod
    def make_contents(kospi: pd.DataFrame, kosdaq: pd.DataFrame) -> Tuple:
        mcap = kospi.loc[0, "상장시가총액"] + kosdaq.loc[0, "상장시가총액"]
        trd_val = kospi.loc[0, "거래대금"] + kosdaq.loc[0, "거래대금"]

        return mcap, trd_val, trd_val / mcap

    def make_title(self, data: Tuple[float]) -> str:
        mcap = data[0]
        trd_val = data[1]
        ratio = data[2]
        trillion = 1_000_000_000_000
        td = datetime.strptime(self.target_date, "%Y%m%d")
        contents = f"[{td.strftime('%Y-%m-%d')}] KOSPI+KOSDAQ " \
                   f"시총(KRW): {mcap / trillion:.1f} 조, " \
                   f"거래대금(KRW): {trd_val / trillion:.1f} 조, " \
                   f"거래대금/시총: {ratio * 100:.2f} %\n"

        return contents


if __name__ == '__main__':
    today = "20221121"
    crawler = KRXCrawler(today)
    df_ = crawler.run("02")
