import requests

def get_backtest_dates(test_pair):
    url = "http://backtest.kryll.torkium.com/index.php?controller=Main&action=getPeriod&token=lol"
    response = requests.request("GET", url)
    for pair,periods in response.json()['data'].items():
        if pair == test_pair:
            return periods

result = get_backtest_dates('BTC / USDT')
