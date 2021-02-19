import requests

def backtest_already_did():
    url = 'http://backtest.kryll.torkium.com/index.php?controller=Main&action=checkBacktest&strat=🐙 OCTO BOT [V2]&pair=AAVEUP/USDT&period=global'
    response = requests.request("GET", url)
    print(response.text)

backtest_already_did()