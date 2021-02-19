from selenium import webdriver
import time
import requests

strat = input(
    "Link to the strat (ex https://platform.kryll.io/marketplace/5f9f0342dd6ac25bd05cf515)"
)


def backtest_already_did(pair,period,strat):
    pair = pair.replace(" ", "")
    url = "http://backtest.kryll.torkium.com/index.php?controller=Main&action=checkBacktest&strat=" + strat +"&pair="+ pair +"&period=" + period
    response = requests.request("GET", url)
    print(url)
    print(f'Requete get backtest_already_did, code = {response.status_code}, value = {response.text}')
    return response.status_code

def get_backtest_dates(test_pair):
    url = (
        "http://backtest.kryll.torkium.com/index.php?controller=Main&action=getPeriod&pair="
        + test_pair.replace(" ", "")
    )
    response = requests.request("GET", url)
    print(f'Requete get date, code = {response.status_code}, value = {response.text}')
    if response.status_code == 200:
        return response.json()["data"][test_pair]
    elif response.status_code == 400:
        return []
    else:
        print(f'get_backtest_dates error, code = {response.status_code}, content = {response.text}')


def check_if_popup():
    try:
        popup = driver.find_element_by_css_selector(
            "app-dialog-tutorial > div > div > div > button.btn.btn-primary"
        )
        popup.click()
    except:
        print("no popup")
    return


def get_advanced_result():
    result = {}
    result["strat"] = strat_name
    result["pair"] = pair
    result["start"] = backtest_date_start.replace('-','/')
    result["end"] = backtest_date_end.replace('-','/')
    result["link"] = advanced_analyse_link.split('=')[1]
    result["duration"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.big-container > div > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)"
    ).text.replace(' days','')
    result["volatility"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.big-container > div > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)"
    ).text.replace(' %','')
    result["trade"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).text
    result["start_wallet"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    ).text
    result["stop_wallet"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ).text
    result["gain"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    ).text.replace(' %','')
    result["relative_gain"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    ).text.replace(' %','')
    result["winning_periods"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).text.split(' ')[0]
    result["losing_periods"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    ).text.split(' ')[0]
    result["average_win"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ).text.replace(' %','')
    result["average_loss"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    ).text.replace(' %','')
    result["wallet_average_investment"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    ).text.replace(' %','')
    result["wallet_maximum_investment"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(6) > div:nth-child(2)"
    ).text.replace(' %','')
    result["win_loss_ratio"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).text.replace("/", ":")
    result["risk_reward_ratio"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    ).text
    result["expected_return"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ).text.replace(' %','')
    result["sharpe_ratio"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    ).text
    result["sortino_ratio"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    ).text
    result["risk_of_drawdown"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(6) > div:nth-child(2)"
    ).text.replace(' %','')
    if result["risk_of_drawdown"] == '<0.01':
        result["risk_of_drawdown"] = 0
    result["maximum_drawdown"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).text.split(' %\n')[0]
    result["maximum_drawdown_start"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).text.split(' %\n')[1].split(' — ')[0]
    result["maximum_drawdown_end"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).text.split(' %\n')[1].split(' — ')[1]
    result["average_drawdown"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ).text.replace(' %','')
    return result

token = input('please enter your token')
driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
driver.get(strat)
input("Login and press a key")
recommeded_pairs = driver.find_elements_by_css_selector('.table > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > div:nth-child(2) > span > a')
recommeded_pairs_list = []
for i in recommeded_pairs:
    recommeded_pairs_list.append(i.text)
driver.find_element_by_css_selector("button.d-sm-inline-block").click()
time.sleep(5)
paires_input = driver.find_element_by_css_selector(
    "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(2) > select"
)
paire_list = paires_input.find_elements_by_tag_name("option")


for i in paire_list:
    pair = i.text.strip()
    recommended = 0
    if pair in recommeded_pairs_list:
        recommeded = 1
    error = False

    # Configure backtesting
    paires_input.send_keys(pair)
    start_input = driver.find_element_by_css_selector(
        "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(4) > app-form-datepicker > div > input"
    )
    end_input = driver.find_element_by_css_selector(
        "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(5) > app-form-datepicker > div > input"
    )
    driver.execute_script('arguments[0].removeAttribute("readonly")', start_input)
    driver.execute_script('arguments[0].removeAttribute("readonly")', end_input)
    time.sleep(5)
    backtest_dates = []
    min_date = start_input.get_attribute("min")
    max_date = start_input.get_attribute("max")
    backtest_dates = get_backtest_dates(pair)
    globale = {"periode": "global", "start": min_date, "end": max_date}
    backtest_dates.append(globale)
    strat_name = driver.find_element_by_css_selector('.toolbar-col').text.strip()
    print(backtest_dates)
    for backtest_date in backtest_dates:
        backtest_date_period = backtest_date["periode"]
        backtest_date_start = backtest_date["start"]
        backtest_date_end = backtest_date["end"]
        print(backtest_date)
        if backtest_already_did(pair=pair,period=backtest_date_period,strat=strat_name) == 200:
            start_input.clear()
            time.sleep(2)
            start_input.send_keys(backtest_date_start)
            end_input.clear()
            time.sleep(2)
            end_input.send_keys(backtest_date_end)
            test_btn = driver.find_element_by_css_selector(
                "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(7) > button"
            )
            time.sleep(1)
            check_if_popup()
            test_btn.click()
            time.sleep(5)
            check_if_popup()

            # ugly method to detect if there is an error or end page
            for i in range(0, 10000):
                time.sleep(1)
                if (
                    len(
                        driver.find_elements_by_css_selector(
                            ".analysis > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(5) > tr:nth-child(2) > td:nth-child(3) > app-value:nth-child(1) > span:nth-child(1)"
                        )
                    )
                    > 0
                ):
                    break
                if driver.find_element_by_css_selector(".backtest-button").text == "Test":
                    error = True
                    break
            if error:
                continue

            check_if_popup()
            driver.find_element_by_css_selector(
                "div.backtest-panel:nth-child(4) > div:nth-child(1) > a:nth-child(2)"
            ).click()
            time.sleep(5)
            driver.switch_to.window(driver.window_handles[1])

            # wait for the advanced bt page to load
            for i in range(0, 10000):
                if (
                    len(
                        driver.find_elements_by_css_selector(
                            "div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
                        )
                    )
                    > 0
                ):
                    break
                time.sleep(1)

            advanced_analyse_link = driver.current_url
            result = get_advanced_result()
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            url = "http://backtest.kryll.torkium.com/index.php?controller=Main&action=sendBacktest"
            
            result['token'] = token
            result['recommended'] = str(recommended).replace(' ','')
            
            print(result)
            response = requests.request("POST", url, data=result)

            print(f'Requete post, code = {response.status_code}, value = {response.text}')
