"""
Script automating backtest on kryll.io and sending results to an API
Made by Thomas with the help of torkium
"""

import os
import platform
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import requests
import dateutil.relativedelta
import yaml


def user_config():
    """
    Return user config if config file exist, if not return -1
    """
    if os.path.exists("config.yaml"):
        with open(r"config.yaml") as config_file:
            return yaml.load(config_file, Loader=yaml.FullLoader)
    return -1


def log(log_text, verbose=False):
    """
    Takes a log_text and a verbose boolean, print the log and save it to a log file
    """
    log_formated_string = datetime.now().strftime("%d %B %Y %H:%M:%S -> ") + log_text
    log_file = open("Kryll_backtest.log", "a+", encoding="utf-8")
    log_file.write(log_formated_string + "\n")
    log_file.close()
    if (advanced_config["verbose"] == "y" and verbose) or not verbose:
        print(log_formated_string)


def yes_no_question(question):
    """
    Takes a question, return the answer y or n
    """
    response = input(question + " (y/n)").lower()
    while response not in ("y", "n"):
        log("invalid choice")
        response = yes_no_question(question)
    return response

def ask_strat():
    strat_ids = {}
    strat_id = input("Enter a strat id (ex 5f9f0342dd6ac25bd05cf515) :")
    while strat_id != "":
        log("Do you want to test an other strat? (empty to next)")
        strat_id = input("Enter a strat id (ex 5f9f0342dd6ac25bd05cf515) :")
        if strat_id != "":
            strat_ids[strat_id] = strat_id
    return strat_ids

def detect_browsers(client_os_detect_browsers):
    """
    Takes the client os, return the correct driver according to client browsers
    """
    browsers = []
    if client_os_detect_browsers == "Windows":
        if os.environ["ProgramFiles"] + r"\Mozilla Firefox":
            log("Firefox detected")
            browsers.append("Firefox")
        if os.environ["ProgramFiles"] + r"\Google\Chrome\Application":
            log("Chrome detected")
            browsers.append("Google Chrome")
    elif client_os_detect_browsers == "Linux":
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
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        driver = webdriver.Chrome(executable_path=r"chromedriver.exe", options=options)
    elif client_browser == "Firefox":
        driver = webdriver.Firefox(executable_path=r"geckodriver.exe")
    return driver


def advanced_configuration(advanced):
    """
    Takes if client want advanced config, return user config
    """
    user_advanced_configuration = {}
    if advanced == "y":
        user_advanced_configuration["global"] = yes_no_question(
            "Do you want to test the global period ?"
        )
        user_advanced_configuration["recently"] = yes_no_question(
            "Do you want to test the last three months ?"
        )
        user_advanced_configuration["other"] = yes_no_question(
            "Do you want to test the other periods if avaible (bear/bull...) ?"
        )
        user_advanced_configuration["every_pairs"] = yes_no_question(
            "do you want to test every pairs ?"
        )
        user_advanced_configuration["verbose"] = yes_no_question(
            "do you want to show verbose logs ?"
        )

    else:
        user_advanced_configuration["global"] = "y"
        user_advanced_configuration["recently"] = "y"
        user_advanced_configuration["other"] = "y"
        user_advanced_configuration["every_pairs"] = "n"
        user_advanced_configuration["verbose"] = "n"
    return user_advanced_configuration


def convert_date(date):
    """
    Takes date format Year-Month-Day, return date format Month/Day/Year
    """
    log(f"Function convert date input = {date}", True)
    dto = datetime.strptime(date, "%Y-%m-%d").date()
    dto = str(dto.strftime("%m/%d/%Y"))
    log(f"Function convert date output = {dto}", True)
    return dto


def get_recently(start, end):
    """
    get start backtest date and end date, return -1
    if period is less than 100 days else return the end date -3 months
    """
    log(f"Function get_recently input (start ={start}, end = {end})", True)
    start = datetime.strptime(start, "%m/%d/%Y").date()
    end = datetime.strptime(end, "%m/%d/%Y").date()
    if (end - start).days < 100:
        log("Function get_recently output = pair too recent", True)
        return -1

    start = end - dateutil.relativedelta.relativedelta(months=3)
    start = str(start.strftime("%m/%d/%Y"))
    log(f"Function get_recently output = {start}", True)
    return start


def backtest_already_did(
    pair_already_did, period_already_did, strat_already_did, token_already_did
):
    """
    Takes the pair,the period,the strat,and client token, return if backtest present in database
    """
    log(
        f"Function backtest_already_did input (pair ={pair_already_did}, period = {period_already_did}, strat= {strat_already_did})",
        True,
    )
    pair_already_did = pair_already_did.replace(" ", "")
    url_backtest_already_did = (
        "https://api.backtest.kryll.torkium.com/index.php?controller=Backtest&action=check&strat="
        + strat_already_did
        + "&pair="
        + pair_already_did
        + "&period="
        + period_already_did
        + "&token="
        + token_already_did
    )
    response = requests.request("GET", url_backtest_already_did)
    log(
        f"Requete backtest_already_did, status_code = {response.status_code}, value = {response.text}, url= {url_backtest_already_did}",
        True,
    )
    if response.status_code == 200:
        log("Please Wait...")
        return False
    log("Already tested, next")
    return True


def get_backtest_dates(pair_backtest_dates, token_backtest_dates):
    """
    Takes the pair, and client token, return precise periods if present in database
    """
    log(f"Function get_backtest_dates input (test_pair ={pair_backtest_dates})", True)
    url = (
        "https://api.backtest.kryll.torkium.com/index.php?controller=Pair&action=getPeriod&pair="
        + pair_backtest_dates.replace(" ", "")
        + "&token="
        + token_backtest_dates
    )
    response = requests.request("GET", url)
    log(
        f"Requete get_backtest_dates, code = {response.status_code}, value = {response.text}, url= {url}",
        True,
    )
    if response.status_code == 200:
        response = response.json()["data"][pair_backtest_dates.replace(" / ", "/")]
        log(
            f"Function get_recently (condition response.status_code == 200) output = {response})",
            True,
        )
        return response
    if response.status_code == 400:
        log(
            "Function get_recently (condition response.status_code == 400) output = [])",
            True,
        )
        return []
    log(
        f"get_backtest_dates output (condition other) error = (code = {response.status_code}, value = {response.text}, url= {url})",
        True,
    )
    return -1


def check_if_popup():
    """
    Check if tutorial popup is present on the screen
    """
    try:
        popup = get_element(
            "app-dialog-tutorial > div > div > div > button.btn.btn-primary"
        )
        popup.click()
    except Exception:
        pass


def get_element(element_path):
    """
    Takes a css class, return selenium element
    """
    return client_driver.find_element_by_css_selector(element_path)


def get_elements(elements_path):
    """
    Takes a css class,return list of elements
    """
    return client_driver.find_elements_by_css_selector(elements_path)


def get_element_text(element_path):
    """
    Takes a selenium element,return element text
    """
    return get_element(element_path).text


def get_element_double(element_path):
    """
    Takes a css class, return str with "+" replaced by void
    """
    return get_element_text(element_path).replace("+", "")


def get_element_percent(element_path):
    """
    Takes a css class, return str with " %" replaced by void
    """
    return get_element_text(element_path).replace(" %", "")


def get_element_days(element_path):
    """
    Takes a css class, return str with " days" replaced by void
    """
    return get_element_text(element_path).replace(" days", "")


def split_max_drawdown_informations(element_path):
    """
    Takes a css class, return list of DD informations
    """
    max_drawdown_informations = {}
    max_drawdown_informations["maximum_drawdown"] = get_element_text(
        element_path
    ).split(" %\n")[0]
    max_drawdown_dates = get_element_text(element_path).split(" %\n")[1].split(" — ")
    max_drawdown_informations["maximum_drawdown_start"] = max_drawdown_dates[0]
    max_drawdown_informations["maximum_drawdown_end"] = max_drawdown_dates[1]
    return max_drawdown_informations


def set_input_date(start, end):
    """
    Takes a start date, end date and set them in inputs
    """
    start_input.clear()
    time.sleep(2)
    start_input.send_keys(start)
    end_input.clear()
    time.sleep(2)
    end_input.send_keys(end)


def check_error_during_backtest():
    """
    Check if backtest broke return True if Bt broke and False if not
    """
    # ugly method to detect if there is an error or end page
    for _ in range(0, 10000):
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
            return True
    return False


# progress bar path :
# div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-graph > div > div.backtest-graph-top.backtest-percent
# if think we can user that to check error during backtest


def wait_for_element(element, duration):
    """
    Takes a selenium element and a duration, return True if element detected and False if not
    """
    for _ in range(0, duration):
        if len(get_elements(element)) > 0:
            return True
        time.sleep(1)
    return False


def wait_for_windows_handle(duration):
    """
    Takes a duration, return True if more than 1 window else return False
    """
    for _ in range(0, duration):
        if len(client_driver.window_handles) > 1:
            return True
        time.sleep(1)
    return False


def get_advanced_result(
    strat_name_advanced_result,
    pair_advanced_result,
    backtest_date_start_advanced_result,
    backtest_date_end_advanced_result,
    advanced_analyse_link_advanced_result,
):
    """
    Takes a strat name, a pair, a backtest start date, a backtest end date and the analyse link
    return dict of results
    """
    result = {}
    result["strat"] = strat_name_advanced_result
    result["pair"] = pair_advanced_result
    result["start"] = backtest_date_start_advanced_result.replace("-", "/")
    result["end"] = backtest_date_end_advanced_result.replace("-", "/")
    result["link"] = advanced_analyse_link_advanced_result.split("=")[1]
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


def send_result(result_send_result):
    """
    Takes a token, a pair, if strat is recommended, a strat id, a strat name, a strat version, the hold value,
    the backtest period, the backtest start date, the backtest end date
    return True if request worked else return False
    """
    advanced_analyse_link = client_driver.current_url
    result = get_advanced_result(
        result_send_result["strat_name"],
        result_send_result["pair"],
        result_send_result["backtest_date_start"],
        result_send_result["backtest_date_end"],
        advanced_analyse_link,
    )
    client_driver.close()
    client_driver.switch_to.window(client_driver.window_handles[0])
    url = "https://api.backtest.kryll.torkium.com/index.php?controller=Backtest&action=send"

    result["token"] = result_send_result["token"]
    result["recommended"] = str(result_send_result["recommended"]).replace(" ", "")
    result["strat_id"] = str(result_send_result["strat_id"])
    result["strat_version"] = str(result_send_result["strat_version"])
    result["hold"] = str(result_send_result["hold"])
    if result_send_result["backtest_date_period"] == "recently" or "global":
        result["period"] = result_send_result["backtest_date_period"]
    else:
        result["period"] = ""
    log(f"Sending result to the Database, result = {result}", True)
    response = requests.request("POST", url, data=result)

    log(
        f"Requete post, status_code = {response.status_code}, value = {response.text}",
        True,
    )
    if response.status_code == 200:
        return True
    return False


def run_backtest(
    strat_name_run_backtest,
    strat_id_run_backtest,
    pair_run_backtest,
    backtest_date_run_backtest,
):
    """
    Takes a strat name, a strat id, a pair, and a backtest date
    return True if no errors else return False
    """
    backtest_date_period = backtest_date_run_backtest["period"]
    backtest_date_start = backtest_date_run_backtest["start"]
    backtest_date_end = backtest_date_run_backtest["end"]
    log(
        f"Testing period = {backtest_date_period}, from {backtest_date_start} to {backtest_date_end}"
    )
    if not backtest_already_did(
        pair_already_did=pair_run_backtest,
        period_already_did=backtest_date_period,
        strat_already_did=strat_name_run_backtest,
        token_already_did=token,
    ):
        # set date into input
        set_input_date(backtest_date_start, backtest_date_end)
        test_btn = get_element(
            "app-dialog-strategy-backtest > app-backtest-container > div > div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-bar > div.form-inline > div:nth-child(7) > button"
        )
        time.sleep(1)
        test_btn.click()
        time.sleep(5)
        check_if_popup()

        error = check_error_during_backtest()
        if error:
            return False
        time.sleep(5)
        check_if_popup()
        hold = get_element_double(
            ".analysis > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(5) > tr:nth-child(3) > td:nth-child(1) > app-value:nth-child(1) > span:nth-child(1)"
        )
        # click on depth analysis button
        get_element(
            "div.backtest-panel:nth-child(4) > div:nth-child(1) > a:nth-child(2)"
        ).click()
        windows_handle = wait_for_windows_handle(10000)
        if not windows_handle:
            log("depth analysis button is break on kryll side, period canceled")
            return False
        client_driver.switch_to.window(client_driver.window_handles[1])

        # wait for the advanced bt page to load
        wait_for_element(
            "div > div > div > div.ant-row > div > div > div:nth-child(1) > div:nth-child(1) > div > div.ant-card-body > div > div:nth-child(1) > div:nth-child(2)",
            10000,
        )

        send_ok = send_result(
            {
                "token": token,
                "pair": pair,
                "recommended": RECOMMENDED,
                "strat_id": strat_id_run_backtest,
                "strat_name": strat_name_run_backtest,
                "strat_version": strat_version,
                "hold": hold,
                "backtest_date_period": backtest_date_period,
                "backtest_date_start": backtest_date_start,
                "backtest_date_end": backtest_date_end,
            }
        )
        if send_ok:
            log("Done.")
            return True
        log("Error during sending the result, period canceled.")
    return False


# ----------------------
# Start of the program
# ----------------------
config = user_config()
if config:
    token = config["token"]
else:
    token = input("Enter your token :")
    with open(r"config.yaml", "w") as file:
        config_yaml = yaml.dump({"token": token}, file)

advanced_user_choice = yes_no_question("Do you want to configure the script ?")
advanced_config = advanced_configuration(advanced_user_choice)
strat_ids = ask_strat()
client_os = platform.system()

client_driver = detect_browsers(client_os_detect_browsers=client_os)
client_driver.get("https://platform.kryll.io/marketplace/")
input("Login and press a key")
for strat_id in strat_ids:
    client_driver.get("https://platform.kryll.io/marketplace/" + strat_id)
    log("Initialisation, please wait...")
    time.sleep(10)
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
    strat_name = get_element_text(
        "app-marketplace-details-page > div > div.layout-body > div > div > div.col-md-12.col-xl-8.main > div > div.card-header.card-header-strong > div > div:nth-child(2) > div.card-name > h2"
    ).strip()
    log("==============================================")
    log(f"Testing strat : {strat_name}")
    log("==============================================")
    for i in total_pairs_list:
        # Get infos
        pair = i.text.strip()

        # fix 23/02 remove later
        if pair == "1INCH / BUSD":
            continue

        RECOMMENDED = 0
        if i in recommended_pairs_list:
            RECOMMENDED = 1

        # check if user want to test every pairs
        if RECOMMENDED == 0 and advanced_config["every_pairs"] == "n":
            continue

        ERROR = False
        log(f"** pair = {pair}, recommended = {RECOMMENDED}")

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
        except Exception:
            log(fr"/!\ Error recommanded pair {pair} not listed on Binance")
            continue

        # wait for have a time to get MIN_DATE and MAX_DATE
        time.sleep(5)
        # get min/max dates
        client_driver.execute_script(
            'arguments[0].removeAttribute("readonly")', start_input
        )
        client_driver.execute_script(
            'arguments[0].removeAttribute("readonly")', end_input
        )
        MIN_DATE = convert_date(start_input.get_attribute("min"))
        MAX_DATE = convert_date(end_input.get_attribute("max"))
        # get min recently
        min_recently = get_recently(start=MIN_DATE, end=MAX_DATE)

        backtest_dates = []
        # Check if user want to test global
        if advanced_config["global"] == "y":
            backtest_dates.append(
                {"period": "global", "start": MIN_DATE, "end": MAX_DATE}
            )
        # if the pair is at least 100 days old and user want to test recently we test the 3 last months
        if min_recently != -1 and advanced_config["recently"] == "y":
            backtest_dates.append(
                {"period": "recently", "start": min_recently, "end": MAX_DATE}
            )
        # If we have choose to test all pairs
        if advanced_config["other"] == "y":
            backtest_dates += get_backtest_dates(
                pair_backtest_dates=pair, token_backtest_dates=token
            )
        log(f"backtest dates list = {backtest_dates}", True)
        # run backtests on all dates
        log("** run backtest for pair " + pair + " for all selected periods")
        for backtest_date in backtest_dates:
            run_backtest(strat_name, strat_id, pair, backtest_date)

    log("==============================================")
    log(f"strat backtested : {strat_name} : Done")
    log("==============================================")
