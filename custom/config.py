""""Module containing configuration"""


class Config:
    """"Class containing configuration"""

    # API URL
    API_BASE_URL = "https://api.torkryll.torkium.com/"
    API_CHECK_BACKTEST_URL = API_BASE_URL + "index.php?controller=Backtest&action=check"
    API_GET_PERIOD_URL = API_BASE_URL + "index.php?controller=Period&action=get"
    API_SEND_URL = API_BASE_URL + "index.php?controller=Backtest&action=send"
