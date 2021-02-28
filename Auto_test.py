"""
Script automating backtest on kryll.io and sending results to an API
Made by Thomas with the help of torkium
"""
import time
from selenium.webdriver.support.ui import Select
from custom.user_config import UserConfig
from custom.utilities import UtilityTools
from custom.css_const import CssConst
from custom.selenium_utilities import SeleniumUtilities
from custom.api import Api


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
    backtest_date_start = tools.convert_date_to_html(backtest_date_run_backtest["start"])
    backtest_date_end = tools.convert_date_to_html(backtest_date_run_backtest["end"])
    tools.log(f"Testing period = {backtest_date_period}, from {backtest_date_start} to {backtest_date_end}")
    if not api.backtest_already_did(
        pair_already_did=pair_run_backtest,
        period_already_did=backtest_date_period,
        strat_already_did=strat_name_run_backtest,
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

        send_ok = api.send_result(
            {
                "pair": pair,
                "recommended": RECOMMENDED,
                "strat_id": strat_id_run_backtest,
                "strat_name": strat_name_run_backtest,
                "strat_version": strat_version,
                "hold": hold,
                "backtest_date_period": backtest_date_period,
                "backtest_date_start": tools.convert_date_to_api(backtest_date_start),
                "backtest_date_end": tools.convert_date_to_api(backtest_date_end),
            }
        )
        sel_tools.driver.close()
        sel_tools.driver.switch_to.window(sel_tools.driver.window_handles[0])
        if send_ok:
            tools.log("Done.")
            return True
        tools.log("Error during sending the result, period canceled.")
    return False


# ----------------------
# Start of the program
# ----------------------

user = UserConfig()
tools = UtilityTools(user_config=user.config)
client_driver = tools.detect_browsers()
sel_tools = SeleniumUtilities(user_config=user.config, driver=client_driver)
css = CssConst()

api = Api(user_config=user.config, token=user.config_file["token"], driver=client_driver)

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

        RECOMMENDED = 0
        if i in recommended_pairs_list:
            RECOMMENDED = 1

        # check if user want to test every pairs
        if RECOMMENDED == 0 and user.config["every_pairs"] == "n":
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
        MIN_DATE = start_input.get_attribute("min")
        MAX_DATE = end_input.get_attribute("max")

        backtest_dates = api.get_backtest_dates(pair_backtest_dates=pair, min_date_backtest_dates=MIN_DATE)
        tools.log(f"backtest dates list = {backtest_dates}", True)
        # run backtests on all dates
        tools.log("** run backtest for pair " + pair + " for all selected periods")
        for backtest_date in backtest_dates:
            run_backtest(strat_name, strat_id, pair, backtest_date)

    tools.log("==============================================")
    tools.log(f"strat backtested : {strat_name} : Done")
    tools.log("==============================================")
