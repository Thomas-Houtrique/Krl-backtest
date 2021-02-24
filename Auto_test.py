from selenium import webdriver
import time
import requests
from datetime import datetime
import dateutil.relativedelta
from selenium.webdriver.support.ui import Select
import platform
import os


def log(log_text, verbose=False):
    log = datetime.now().strftime("%d %B %Y %H:%M:%S -> ") + log_text
    f = open("Kryll_backtest.log", "a+", encoding="utf-8")
    f.write(log + "\n")
    f.close()
    if (advanced_config["verbose"] == "y" and verbose) or not verbose:
        print(log)


def yes_no_question(question):
    response = input(question + " (y/n)").lower()
    while response != "y" and response != "n":
        log("invalid choice")
        response = yes_no_question(question)
    return response


def detect_browsers(client_os):
    browsers = []
    if client_os == "Windows":
        if os.environ["ProgramFiles"] + "\Mozilla Firefox":
            log("Firefox detected")
            browsers.append("Firefox")
        if os.environ["ProgramFiles"] + "\Google\Chrome\Application":
            log("Chrome detected")
            browsers.append("Google Chrome")
    elif client_os == "Linux":
        raise Exception("Sorry, linux is not supported yet")

    if len(browsers) > 1:
        for idx, browser in enumerate(browsers):
            print(f"{idx}) {browser}")
        browser_choice = int(
            input(f"please choice between your browsers (0 to {len(browsers) - 1})")
        )
        client_browser = browsers[browser_choice]
    elif len(browsers) == 1:
        client_browser = browsers[0]
    else:
        raise Exception("Sorry, please install Firefox or Google Chrome")

    if client_browser == "Google Chrome":
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(executable_path=r"chromedriver.exe", options=options)
    elif client_browser == "Firefox":
        driver = webdriver.Firefox(executable_path=r"geckodriver.exe")
    return driver


def advanced_configuration(advanced):
    user_config = {}
    if advanced == "y":
        user_config["global"] = yes_no_question(
            "Do you want to test the global period ?"
        )
        user_config["recently"] = yes_no_question(
            "Do you want to test the last three months ?"
        )
        user_config["other"] = yes_no_question(
            "Do you want to test the other periods if avaible (bear/bull...) ?"
        )
        user_config["every_pairs"] = yes_no_question(
            "do you want to test every pairs ?"
        )
        user_config["verbose"] = yes_no_question("do you want to show verbose logs ?")

    else:
        user_config["global"] = "y"
        user_config["recently"] = "y"
        user_config["other"] = "y"
        user_config["every_pairs"] = "y"
        user_config["verbose"] = "n"
    return user_config


def convert_date(date):
    log(f"Function convert date input = {date}", True)
    dto = datetime.strptime(date, "%Y-%m-%d").date()
    dto = str(dto.strftime("%m/%d/%Y"))
    log(f"Function convert date output = {dto}", True)
    return dto


def get_recently(start, end):
    log(f"Function get_recently input (start ={start}, end = {end})", True)
    start = datetime.strptime(start, "%m/%d/%Y").date()
    end = datetime.strptime(end, "%m/%d/%Y").date()
    if (end - start).days < 100:
        log(f"Function get_recently output = pair too recent", True)
        return -1
    else:
        start = end - dateutil.relativedelta.relativedelta(months=3)
        start = str(start.strftime("%m/%d/%Y"))
        log(f"Function get_recently output = {start}", True)
        return start


def backtest_already_did(pair, period, strat, token):
    log(
        f"Function backtest_already_did input (pair ={pair}, period = {period}, strat= {strat})",
        True,
    )
    pair = pair.replace(" ", "")
    url = (
        "https://api.backtest.kryll.torkium.com/index.php?controller=Backtest&action=check&strat="
        + strat
        + "&pair="
        + pair
        + "&period="
        + period
        + "&token="
        + token
    )
    response = requests.request("GET", url)
    log(
        f"Requete backtest_already_did, status_code = {response.status_code}, value = {response.text}, url= {url}",
        True,
    )
    if response.status_code == 200:
        log("Please Wait...")
        return False
    else:
        log("Already tested, next")
        return True


def get_backtest_dates(test_pair, token):
    log(f"Function get_backtest_dates input (test_pair ={test_pair})", True)
    url = (
        "https://api.backtest.kryll.torkium.com/index.php?controller=Pair&action=getPeriod&pair="
        + test_pair.replace(" ", "")
        + "&token="
        + token
    )
    response = requests.request("GET", url)
    log(
        f"Requete get_backtest_dates, code = {response.status_code}, value = {response.text}, url= {url}",
        True,
    )
    if response.status_code == 200:
        response = response.json()["data"][test_pair.replace(" / ", "/")]
        log(
            f"Function get_recently (condition response.status_code == 200) output = {response})",
            True,
        )
        return response
    elif response.status_code == 400:
        log(
            f"Function get_recently (condition response.status_code == 400) output = [])",
            True,
        )
        return []
    else:
        log(
            f"get_backtest_dates output (condition other) error = (code = {response.status_code}, value = {response.text}, url= {url})",
            True,
        )


def check_if_popup():
    try:
        popup = get_element(
            "app-dialog-tutorial > div > div > div > button.btn.btn-primary"
        )
        popup.click()
    except:
        pass


def get_element(element_path):
    return driver.find_element_by_css_selector(element_path)


def get_elements(elements_path):
    return driver.find_elements_by_css_selector(elements_path)


def get_element_text(element_path):
    return get_element(element_path).text


def get_element_double(element_path):
    return get_element_text(element_path).replace("+", "")


def get_element_percent(element_path):
    return get_element_text(element_path).replace(" %", "")


def get_element_days(element_path):
    return get_element_text(element_path).replace(" days", "")


def split_max_drawdown_informations(element_path):
    max_drawdown_informations = {}
    max_drawdown_informations["maximum_drawdown"] = get_element_text(
        element_path
    ).split(" %\n")[0]
    max_drawdown_dates = get_element_text(element_path).split(" %\n")[1].split(" — ")
    max_drawdown_informations["maximum_drawdown_start"] = max_drawdown_dates[0]
    max_drawdown_informations["maximum_drawdown_end"] = max_drawdown_dates[1]
    return max_drawdown_informations


def get_advanced_result():
    result = {}
    result["strat"] = strat_name
    result["pair"] = pair
    result["start"] = backtest_date_start.replace("-", "/")
    result["end"] = backtest_date_end.replace("-", "/")
    result["link"] = advanced_analyse_link.split("=")[1]
    result["duration"] = get_element_days(
        "#root > div > div > div > div.big-container > div > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(1) > div:nth-child(2)"
    )
    result["volatility"] = get_element_percent(
        "#root > div > div > div > div.big-container > div > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2) > div:nth-child(2)"
    )
    result["trade"] = get_element_text(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    )
    result["start_wallet"] = get_element_text(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    )
    result["stop_wallet"] = get_element_text(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    )
    result["gain"] = get_element_percent(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    )
    result["relative_gain"] = get_element_percent(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    )
    result["winning_periods"] = get_element_text(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).split(" ")[0]
    result["losing_periods"] = get_element_text(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    ).split(" ")[0]
    result["average_win"] = get_element_percent(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    )
    result["average_loss"] = get_element_percent(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    )
    result["wallet_average_investment"] = get_element_percent(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    )
    result["wallet_maximum_investment"] = get_element_percent(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(6) > div:nth-child(2)"
    )
    result["win_loss_ratio"] = get_element_text(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    ).replace("/", ":")
    result["risk_reward_ratio"] = get_element_text(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(2) > div:nth-child(2)"
    )
    result["expected_return"] = get_element_percent(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    )
    result["sharpe_ratio"] = get_element_text(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(4) > div:nth-child(2)"
    )
    result["sortino_ratio"] = get_element_text(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(5) > div:nth-child(2)"
    )
    result["risk_of_drawdown"] = get_element_percent(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(6) > div:nth-child(2)"
    )
    if result["risk_of_drawdown"] == "<0.01":
        result["risk_of_drawdown"] = 0

    max_drawdown_informations = split_max_drawdown_informations(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)"
    )
    result["maximum_drawdown"] = max_drawdown_informations["maximum_drawdown"]
    result["maximum_drawdown_start"] = max_drawdown_informations[
        "maximum_drawdown_start"
    ]
    result["maximum_drawdown_end"] = max_drawdown_informations["maximum_drawdown_end"]
    result["average_drawdown"] = get_element_percent(
        "#root > div > div > div > div.ant-row > div > div > div:nth-child(2) > div:nth-child(2) > div > div.ant-card-body > div > div:nth-child(3) > div:nth-child(2)"
    )
    return result


token = input("Enter your token :")
strat_id = input("Enter a strat id (ex 5f9f0342dd6ac25bd05cf515) :")
advanced_user_choice = yes_no_question("Do you want to configure the script ?")
advanced_config = advanced_configuration(advanced_user_choice)
client_os = platform.system()

driver = detect_browsers(client_os=client_os)
driver.get("https://platform.kryll.io/marketplace/" + strat_id)
input("Login and press a key")
log("Initialisation, please wait...")
recommended_pairs = get_elements(
    ".table > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2) > div:nth-child(2) > span > a"
)
strat_version = get_element_text("div.badge:nth-child(1)").split(" ")[1]
recommended_pairs_list = []
for i in recommended_pairs:
    recommended_pairs_list.append(i)
get_element("button.d-sm-inline-block").click()
time.sleep(10)
pairs_input = get_element(
    "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(2) > select"
)
pairs_list = pairs_input.find_elements_by_tag_name("option")

# Backtest recommended first
for i in pairs_list:
    if i in recommended_pairs_list:
        pairs_list.remove(i)
total_pairs_list = recommended_pairs_list + pairs_list

for i in total_pairs_list:
    # Get infos
    strat_name = get_element_text(".toolbar-col").strip()
    pair = i.text.strip()

    # fix 23/02 remove later
    if pair == "1INCH / BUSD":
        continue

    recommended = 0
    if i in recommended_pairs_list:
        recommended = 1

    # check if user want to test every pairs
    if recommended == 0 and advanced_config["every_pairs"] == "n":
        continue

    error = False
    log(f"Testing strat = {strat_name}, pair = {pair}, recommended = {recommended}")

    # Configure backtesting
    pairs_input = Select(
        get_element(
            "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(2) > select"
        )
    )
    start_input = get_element(
        "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(4) > app-form-datepicker > div > input"
    )
    end_input = get_element(
        "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(5) > app-form-datepicker > div > input"
    )
    # Check if pair is listed on exchange
    try:
        pairs_input.select_by_value(pair.replace(" / ", "-"))
    except:
        log(f"Error pair {pair} not listed", True)
        continue

    time.sleep(5)
    driver.execute_script('arguments[0].removeAttribute("readonly")', start_input)
    driver.execute_script('arguments[0].removeAttribute("readonly")', end_input)
    min_date = convert_date(start_input.get_attribute("min"))
    max_date = convert_date(end_input.get_attribute("max"))
    min_recently = get_recently(start=min_date, end=max_date)

    backtest_dates = []
    # Check if user want to test global
    if advanced_config["global"] == "y":
        backtest_dates.append({"period": "global", "start": min_date, "end": max_date})
    # if the pair is at least 100 days old and user want to test recently we test the 3 last months
    if min_recently != -1 and advanced_config["recently"] == "y":
        backtest_dates.append(
            {"period": "recently", "start": min_recently, "end": max_date}
        )
    if advanced_config["other"] == "y":
        backtest_dates += get_backtest_dates(test_pair=pair, token=token)
    log(f"backtest dates list = {backtest_dates}", True)
    for backtest_date in backtest_dates:
        backtest_date_period = backtest_date["period"]
        backtest_date_start = backtest_date["start"]
        backtest_date_end = backtest_date["end"]
        log(
            f"Testing period = {backtest_date_period}, from {backtest_date_start} to {backtest_date_end}"
        )
        if not backtest_already_did(
            pair=pair, period=backtest_date_period, strat=strat_name, token=token
        ):
            time.sleep(2)
            start_input.clear()
            start_input.clear()
            time.sleep(2)
            start_input.send_keys(backtest_date_start)
            end_input.clear()
            end_input.clear()
            time.sleep(2)
            end_input.send_keys(backtest_date_end)
            test_btn = get_element(
                "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(7) > button"
            )
            time.sleep(1)
            test_btn.click()
            time.sleep(5)
            check_if_popup()
            # ugly method to detect if there is an error or end page
            for i in range(0, 10000):
                time.sleep(10)
                check_if_popup()
                if (
                    len(
                        get_elements(
                            ".analysis > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(5) > tr:nth-child(2) > td:nth-child(3) > app-value:nth-child(1) > span:nth-child(1)"
                        )
                    )
                    > 0
                ):
                    break
                if get_element_text(".backtest-button") == "Test":
                    # double check because it can cause some pb
                    if (
                        len(
                            get_elements(
                                ".analysis > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(5) > tr:nth-child(2) > td:nth-child(3) > app-value:nth-child(1) > span:nth-child(1)"
                            )
                        )
                        > 0
                    ):
                        break
                    log("Error during the backtest")
                    error = True
                    break
            if error:
                continue
            time.sleep(5)
            check_if_popup()
            hold = get_element_double(
                ".analysis > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(5) > tr:nth-child(3) > td:nth-child(1) > app-value:nth-child(1) > span:nth-child(1)"
            )
            get_element(
                "div.backtest-panel:nth-child(4) > div:nth-child(1) > a:nth-child(2)"
            ).click()
            for i in range(0, 10000):
                if len(driver.window_handles) > 1:
                    break
                time.sleep(1)
            driver.switch_to.window(driver.window_handles[1])

            # wait for the advanced bt page to load
            for i in range(0, 10000):
                if (
                    len(
                        get_elements(
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
            url = "https://api.backtest.kryll.torkium.com/index.php?controller=Backtest&action=send"

            result["token"] = token
            result["recommended"] = str(recommended).replace(" ", "")
            result["strat_id"] = str(strat_id)
            result["strat_version"] = str(strat_version)
            result["hold"] = str(hold)
            if backtest_date_period == "recently" or "global":
                result["period"] = backtest_date_period
            else:
                result["period"] = ""
            log(f"Sending result to the Database, result = {result}", True)
            response = requests.request("POST", url, data=result)

            log(
                f"Requete post, status_code = {response.status_code}, value = {response.text}",
                True,
            )
            if response.status_code == 200:
                log("Done.")
