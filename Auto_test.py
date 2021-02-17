from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv

strat = input('Link to the strat (ex https://platform.kryll.io/marketplace/5f9f0342dd6ac25bd05cf515)')

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
    result["pair"] = pair
    result["min_date"] = min_date
    result["max_date"] = max_date
    result["advanced_analyse_link"] = advanced_analyse_link
    result["duration"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.big-container > div > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)"
    ).text
    result["volatility"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.big-container > div > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)"
    ).text
    result["number_of_trade"] = driver.find_element_by_css_selector(
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
    ).text
    result["relative_gain"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    ).text
    result["winning_periods"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).text
    result["losing_periods"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    ).text
    result["average_win"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ).text
    result["average_loss"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    ).text
    result["wallet_average_investment"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    ).text
    result["wallet_maximum_investment"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(6) > div:nth-child(2)"
    ).text
    result["win/Loss_ratio"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).text.replace('/', ':')
    result["risk/reward_ratio"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    ).text
    result["expected_return"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ).text
    result["sharpe_ratio"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    ).text
    result["sortino_ratio"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    ).text
    result["risk_of_drawdown"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(6) > div:nth-child(2)"
    ).text
    result["maximum_drawdown"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).text
    result["average_drawdown"] = driver.find_element_by_css_selector(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    ).text
    return result


driver = webdriver.Chrome(executable_path=r"chromedriver.exe")
driver.get(strat)
input("Press Enter to continue...")

driver.find_element_by_css_selector("button.d-sm-inline-block").click()
time.sleep(5)
paires_input = driver.find_element_by_css_selector(
    "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(2) > select"
)
paire_list = paires_input.find_elements_by_tag_name("option")


for i in paire_list:
    pair = i.text.strip()
    already_did = False
    error = False
    with open('backtest.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for line in csv_reader:
            if line[0] == pair:
                already_did = True
    if already_did:
        continue

    paires_input.send_keys(pair)
    start = driver.find_element_by_css_selector(
        "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(4) > app-form-datepicker > div > input"
    )
    end = driver.find_element_by_css_selector("input.ng-pristine")
    driver.execute_script('arguments[0].removeAttribute("readonly")', start)
    driver.execute_script('arguments[0].removeAttribute("readonly")', end)
    time.sleep(5)
    min_date = start.get_attribute("min")
    max_date = start.get_attribute("max")
    start.clear()
    time.sleep(2)
    start.send_keys(min_date)
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
        if len(driver.find_elements_by_css_selector(".analysis > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(5) > tr:nth-child(2) > td:nth-child(3) > app-value:nth-child(1) > span:nth-child(1)")) > 0:
            break
        if driver.find_element_by_css_selector('.backtest-button').text == 'Test':
            error = True
            break
    if error:
        with open("EnigmaV4.csv", "a+", newline="") as csv_file:
            writer = csv.writer(csv_file, delimiter=";")
            writer.writerow([pair,'error'])
        continue

    check_if_popup()
    driver.find_element_by_css_selector(
        "div.backtest-panel:nth-child(4) > div:nth-child(1) > a:nth-child(2)"
    ).click()
    driver.switch_to.window(driver.window_handles[1])

    # wait for the advanced bt page to load
    for i in range(0, 10000):
        if len(driver.find_elements_by_css_selector(".analysis > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(5) > tr:nth-child(2) > td:nth-child(3) > app-value:nth-child(1) > span:nth-child(1)")) > 0:
            break
        time.sleep(1)

    advanced_analyse_link = driver.current_url
    result = get_advanced_result()
    print(result)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    temp = []
    for i in result:
        temp.append(result[i])
    with open("backtest.csv", "a+", newline="") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(temp)
