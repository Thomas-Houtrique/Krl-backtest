"""
Script automating backtest on kryll.io and sending results to an API
Made by Thomas with the help of torkium
"""
import os
import time
from datetime import datetime
import yaml
import dateutil.relativedelta
import requests
from selenium.webdriver.support.ui import Select
from custom.utilities import UtilityTools
from custom.css_const import CssConst
from custom.selenium_utilities import SeleniumUtilities


def user_config():
    """
    Return user config if config file exist, if not return -1
    """
    if os.path.exists("config.yaml"):
        with open(r"config.yaml") as config_file:
            return yaml.load(config_file, Loader=yaml.FullLoader)
    return -1


def get_recently(start, end):
    """
    get start backtest date and end date, return -1
    if period is less than 100 days else return the end date -3 months
    """
    tools.log(f"Function get_recently input (start ={start}, end = {end})", True)
    start = datetime.strptime(start, "%m/%d/%Y").date()
    end = datetime.strptime(end, "%m/%d/%Y").date()
    if (end - start).days < 100:
        tools.log("Function get_recently output = pair too recent", True)
        return -1

    start = end - dateutil.relativedelta.relativedelta(months=3)
    start = str(start.strftime("%m/%d/%Y"))
    tools.log(f"Function get_recently output = {start}", True)
    return start


def backtest_already_did(pair_already_did, period_already_did, strat_already_did, token_already_did):
    """
    Takes the pair,the period,the strat,and client token, return if backtest present in database
    """
    tools.log(
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
    tools.log(
        f"Requete backtest_already_did, status_code = {response.status_code}, value = {response.text}, url= {url_backtest_already_did}",
        True,
    )
    if response.status_code == 200:
        tools.log("Please Wait...")
        return False
    tools.log("Already tested, next")
    return True


def get_backtest_dates(pair_backtest_dates, token_backtest_dates):
    """
    Takes the pair, and client token, return precise periods if present in database
    """
    tools.log(f"Function get_backtest_dates input (test_pair ={pair_backtest_dates})", True)
    url = "https://api.backtest.kryll.torkium.com/index.php?controller=Pair&action=getPeriod&pair=" + pair_backtest_dates.replace(" ", "") + "&token=" + token_backtest_dates
    response = requests.request("GET", url)
    tools.log(
        f"Requete get_backtest_dates, code = {response.status_code}, value = {response.text}, url= {url}",
        True,
    )
    if response.status_code == 200:
        response = response.json()["data"][pair_backtest_dates.replace(" / ", "/")]
        tools.log(
            f"Function get_recently (condition response.status_code == 200) output = {response})",
            True,
        )
        return response
    if response.status_code == 400:
        tools.log(
            "Function get_recently (condition response.status_code == 400) output = [])",
            True,
        )
        return []
    tools.log(
        f"get_backtest_dates output (condition other) error = (code = {response.status_code}, value = {response.text}, url= {url})",
        True,
    )
    return -1


def split_max_drawdown_informations(element_path):
    """
    Takes a css class, return list of DD informations
    """
    max_drawdown_informations = {}
    max_drawdown_informations["maximum_drawdown"] = sel_tools.get_element_text(element_path).split(" %\n")[0]
    max_drawdown_dates = sel_tools.get_element_text(element_path).split(" %\n")[1].split(" — ")
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


# progress bar path :
# div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-graph > div > div.backtest-graph-top.backtest-percent
# if think we can user that to check error during backtest


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
    result["duration"] = sel_tools.get_element_days(css.ADVANCED_ANALYSE_DURATION)
    result["volatility"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_VOLATILITY)
    result["trade"] = sel_tools.get_element_text(css.ADVANCED_ANALYSE_TRADE)
    result["start_wallet"] = sel_tools.get_element_text(css.ADVANCED_ANALYSE_START_WALLET)
    result["stop_wallet"] = sel_tools.get_element_text(css.ADVANCED_ANALYSE_END_WALLET)
    result["gain"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_GAIN)
    result["relative_gain"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_RELATIVE_GAIN)
    result["winning_periods"] = sel_tools.get_element_text(css.ADVANCED_ANALYSE_WINNING_PERIOD).split(" ")[0]
    result["losing_periods"] = sel_tools.get_element_text(css.ADVANCED_ANALYSE_LOSING_PERIOD).split(" ")[0]
    result["average_win"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_AVERAGE_WIN)
    result["average_loss"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_AVERAGE_LOSS)
    result["wallet_average_investment"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_WALLET_AVERAGE_INVESTMENT)
    result["wallet_maximum_investment"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_WALLET_MAXIMUM_INVESTMENT)
    result["win_loss_ratio"] = sel_tools.get_element_text(css.ADVANCED_ANALYSE_WIN_LOSS_RATIO).replace("/", ":")
    result["risk_reward_ratio"] = sel_tools.get_element_text(css.ADVANCED_ANALYSE_RISK_REWARD_RATIO)
    result["expected_return"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_EXPECTED_RETURN)
    result["sharpe_ratio"] = sel_tools.get_element_text(css.ADVANCED_ANALYSE_SHARPE_RATIO)
    result["sortino_ratio"] = sel_tools.get_element_text(css.ADVANCED_ANALYSE_SORTINO_RATIO)
    result["risk_of_drawdown"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_RISK_OF_DRAWDOWN)
    if result["risk_of_drawdown"] == "<0.01":
        result["risk_of_drawdown"] = 0

    max_drawdown_informations = split_max_drawdown_informations(css.ADVANCED_ANALYSE_MAX_DRAWDOWN_INFORMATIONS)
    result["maximum_drawdown"] = max_drawdown_informations["maximum_drawdown"]
    result["maximum_drawdown_start"] = max_drawdown_informations["maximum_drawdown_start"]
    result["maximum_drawdown_end"] = max_drawdown_informations["maximum_drawdown_end"]
    result["average_drawdown"] = sel_tools.get_element_percent(css.ADVANCED_ANALYSE_AVERAGE_DRAWDOWN)
    return result


def send_result(result_send_result):
    """
    Takes a token, a pair, if strat is recommended, a strat id, a strat name, a strat version, the hold value,
    the backtest period, the backtest start date, the backtest end date
    return True if request worked else return False
    """
    advanced_analyse_link = sel_tools.driver.current_url
    result = get_advanced_result(
        result_send_result["strat_name"],
        result_send_result["pair"],
        result_send_result["backtest_date_start"],
        result_send_result["backtest_date_end"],
        advanced_analyse_link,
    )
    sel_tools.driver.close()
    sel_tools.driver.switch_to.window(sel_tools.driver.window_handles[0])
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
    tools.log(f"Sending result to the Database, result = {result}", True)
    response = requests.request("POST", url, data=result)

    tools.log(
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
    tools.log(f"Testing period = {backtest_date_period}, from {backtest_date_start} to {backtest_date_end}")
    if not backtest_already_did(
        pair_already_did=pair_run_backtest,
        period_already_did=backtest_date_period,
        strat_already_did=strat_name_run_backtest,
        token_already_did=token,
    ):
        # set date into input
        set_input_date(backtest_date_start, backtest_date_end)
        test_btn = sel_tools.get_element(css.BACKTEST_START_BTN)
        time.sleep(1)
        test_btn.click()
        time.sleep(5)
        sel_tools.check_if_popup()

        error = sel_tools.check_error_during_backtest()
        if error:
            return False
        time.sleep(5)
        sel_tools.check_if_popup()
        hold = sel_tools.get_element_double(css.ANALYSE_TAB_HOLD)
        # click on depth analysis button
        sel_tools.get_element(css.ANALYSE_TAB_DEEP_ANALYSE_LINK).click()
        windows_handle = sel_tools.wait_for_windows_handle(100)
        if not windows_handle:
            tools.log("depth analysis button is break on kryll side, period canceled")
            return False
        sel_tools.driver.switch_to.window(sel_tools.driver.window_handles[1])

        # wait for the advanced bt page to load
        sel_tools.wait_for_element(css.ADVANCED_ANALYSE_TRADE, 10000)

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
            tools.log("Done.")
            return True
        tools.log("Error during sending the result, period canceled.")
    return False


# ----------------------
# Start of the program
# ----------------------
tools = UtilityTools()
sel_tools = SeleniumUtilities()
css = CssConst()
config = user_config()
if config:
    token = config["token"]
else:
    token = input("Enter your token :")
    with open(r"config.yaml", "w") as file:
        config_yaml = yaml.dump({"token": token}, file)

advanced_user_choice = tools.yes_no_question(question="Do you want to configure the script ?")
advanced_config = tools.advanced_configuration(advanced=advanced_user_choice)
strat_ids = tools.ask_strat()

sel_tools.driver.get("https://platform.kryll.io/marketplace/")
input("Login and press a key")
for strat_id in strat_ids:
    sel_tools.driver.get("https://platform.kryll.io/marketplace/" + strat_id)
    tools.log("Initialisation, please wait...")
    time.sleep(10)
    recommended_pairs = sel_tools.get_elements(css.RECOMMEND_PAIRS)
    strat_version = sel_tools.get_element_text(css.STRAT_VERSION).split(" ")[1]
    recommended_pairs_list = []
    for i in recommended_pairs:
        recommended_pairs_list.append(i)
    sel_tools.get_element(css.BACKTEST_BTN).click()
    time.sleep(10)
    pairs_input = sel_tools.get_element(css.PAIRS_INPUT)
    pairs_list = pairs_input.find_elements_by_tag_name("option")

    # Backtest recommended first
    for i in pairs_list:
        if i in recommended_pairs_list:
            pairs_list.remove(i)
    total_pairs_list = recommended_pairs_list + pairs_list
    strat_name = sel_tools.get_element_text(css.STRAT_NAME).strip()
    tools.log("==============================================")
    tools.log(f"Testing strat : {strat_name}")
    tools.log("==============================================")
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
        tools.log(f"** pair = {pair}, recommended = {RECOMMENDED}")

        # Configure backtesting
        pairs_input = Select(sel_tools.get_element(css.PAIRS_INPUT))
        start_input = sel_tools.get_element(css.START_INPUT)
        end_input = sel_tools.get_element(css.END_INPUT)
        # Check if pair is listed on exchange
        try:
            pairs_input.select_by_value(pair.replace(" / ", "-"))
        except Exception:
            tools.log(fr"/!\ Error recommanded pair {pair} not listed on Binance")
            continue

        # wait for have a time to get MIN_DATE and MAX_DATE
        time.sleep(5)
        # get min/max dates
        sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', start_input)
        sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', end_input)
        MIN_DATE = tools.convert_date(start_input.get_attribute("min"))
        MAX_DATE = tools.convert_date(end_input.get_attribute("max"))
        # get min recently
        min_recently = get_recently(start=MIN_DATE, end=MAX_DATE)

        backtest_dates = []
        # Check if user want to test global
        if advanced_config["global"] == "y":
            backtest_dates.append({"period": "global", "start": MIN_DATE, "end": MAX_DATE})
        # if the pair is at least 100 days old and user want to test recently
        # we test the 3 last months
        if min_recently != -1 and advanced_config["recently"] == "y":
            backtest_dates.append({"period": "recently", "start": min_recently, "end": MAX_DATE})
        # If we have choose to test all pairs
        if advanced_config["other"] == "y":
            backtest_dates += get_backtest_dates(pair_backtest_dates=pair, token_backtest_dates=token)
        tools.log(f"backtest dates list = {backtest_dates}", True)
        # run backtests on all dates
        tools.log("** run backtest for pair " + pair + " for all selected periods")
        for backtest_date in backtest_dates:
            run_backtest(strat_name, strat_id, pair, backtest_date)

    tools.log("==============================================")
    tools.log(f"strat backtested : {strat_name} : Done")
    tools.log("==============================================")
