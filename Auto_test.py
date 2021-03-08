"""
Script automating backtest on kryll.io and sending results to an API
Made by Thomas with the help of torkium
"""
import time
import random
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
    dates_inputs = sel_tools.get_elements(css.DATES_INPUTS)
    start_input = dates_inputs[0]
    end_input = dates_inputs[1]
    start_input.clear()
    time.sleep(2)
    start_input.send_keys(start)
    end_input.clear()
    time.sleep(2)
    end_input.send_keys(end)


# progress bar path :
# div.backtest-container-body > div.backtest-container-backtest > app-backtest > div.backtest-graph > div > div.backtest-graph-top.backtest-percent
# if think we can user that to check error during backtest


def run_backtest(strat_name_run_backtest, strat_id_run_backtest, strat_version_run_backtest, pair_run_backtest, recommanded_run_backtest, backtest_date_run_backtest, exchange_select_run_backtest):
    """
    Takes a strat name, a strat id, a pair, and a backtest date
    return True if no errors else return False
    """
    backtest_date_period = backtest_date_run_backtest["period"]
    backtest_date_start = tools.convert_date_to_html(backtest_date_run_backtest["start"])
    backtest_date_end = tools.convert_date_to_html(backtest_date_run_backtest["end"])
    exchange = exchange_select_run_backtest.first_selected_option.text.strip()
    tools.log(f"Selected exchange = {exchange}")
    tools.log(f"Testing period = {backtest_date_period}, from {backtest_date_start} to {backtest_date_end}")
    if not api.backtest_already_did(
        pair=pair_run_backtest,
        period=backtest_date_period,
        strat=strat_name_run_backtest,
        version=strat_version_run_backtest,
        exchange=exchange,
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
        windows_handle = sel_tools.wait_for_windows_handle(120)
        if not windows_handle:
            tools.log("depth analysis button is break on kryll side, period canceled")
            return False
        sel_tools.driver.switch_to.window(sel_tools.driver.window_handles[1])
        time.sleep(10)
        # wait for the advanced bt page to load
        depth_analysis_page_loaded = sel_tools.wait_for_element(css.ADVANCED_ANALYSE_TRADE, 120)
        if not depth_analysis_page_loaded:
            tools.log("depth analysis tab seems to don't load, refresh and retry...")
            # retry
            sel_tools.refresh()
            depth_analysis_page_loaded = sel_tools.wait_for_element(css.ADVANCED_ANALYSE_TRADE, 120)
        send_ok = False
        if depth_analysis_page_loaded:
            send_ok = api.send_result(
                {
                    "pair": pair_run_backtest,
                    "recommended": recommanded_run_backtest,
                    "strat_id": strat_id_run_backtest,
                    "strat_name": strat_name_run_backtest,
                    "strat_version": strat_version_run_backtest,
                    "hold": hold,
                    "exchange": exchange,
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


def run():
    # If more 1 tab open, closed useless tabs
    sel_tools.close_unused_tabs()
    for strat_id in strat_ids:
        sel_tools.driver.get("https://platform.kryll.io/marketplace/" + strat_id)
        tools.log("Initialisation, please wait...")
        time.sleep(10)
        recommended_pairs = sel_tools.get_elements(css.RECOMMEND_PAIRS)
        strat_version = sel_tools.get_element_text(css.STRAT_VERSION).split(" ")[1]
        recommended_pairs_list = []
        for i in recommended_pairs:
            recommended_pairs_list.append(i)
        try:
            sel_tools.get_element(css.BACKTEST_BTN).click()
        except Exception:
            sel_tools.get_element(css.INSTALL_BTN).click()
            time.sleep(5)
            sel_tools.get_element(css.BACKTEST_BTN).click()

        time.sleep(10)
        exchange_select = Select(sel_tools.get_element(css.EXCHANGE))
        if user.config["exchanges"] == "y":
            exchange_options = sel_tools.get_element(css.EXCHANGE).find_elements_by_tag_name("option")
        else:
            exchange_options = [sel_tools.get_element(css.BINANCE_EXCHANGE)]

        strat_name = sel_tools.get_element_text(css.STRAT_NAME).strip()
        tools.log("==============================================")
        tools.log(f"Testing strat : {strat_name}, version : {strat_version}")
        tools.log("==============================================")
        for exchange in exchange_options:
            if exchange:
                exchange_text = exchange.text.strip()
                tools.log(f"Testing on exchange {exchange_text}")
                exchange_select.select_by_visible_text(exchange_text)
                time.sleep(2)
                sel_tools.check_if_server_problem()
            pairs_input = sel_tools.get_element(css.PAIRS_INPUT)
            pairs_list = pairs_input.find_elements_by_tag_name("option")
            random.shuffle(pairs_list)
            # Backtest recommended first
            for i in pairs_list:
                if i in recommended_pairs_list:
                    pairs_list.remove(i)
            total_pairs_list = recommended_pairs_list + pairs_list

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
                dates_inputs = sel_tools.get_elements(css.DATES_INPUTS)
                start_input = dates_inputs[0]
                end_input = dates_inputs[1]
                # Check if pair is listed on exchange
                try:
                    pairs_input.select_by_value(pair.replace(" / ", "-"))
                except Exception:
                    tools.log(fr"/!\ Error recommanded pair {pair} not listed on {exchange_text}")
                    continue

                # wait for have a time to get MIN_DATE and MAX_DATE
                time.sleep(5)
                # get min/max dates
                sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', start_input)
                sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', end_input)
                MIN_DATE = start_input.get_attribute("min")
                MAX_DATE = end_input.get_attribute("max")

                backtest_dates = api.get_backtest_dates(pair=pair, min_date=MIN_DATE)
                tools.log(f"backtest dates list = {backtest_dates}", True)
                # run backtests on all dates
                tools.log("** run backtest for pair " + pair + " for all selected periods")
                for backtest_date in backtest_dates:
                    run_backtest(strat_name, strat_id, strat_version, pair, RECOMMENDED, backtest_date, exchange_select)

            tools.log("==============================================")
            tools.log(f"strat backtested : {strat_name}, version : {strat_version} : Done")
            tools.log("==============================================")


# ----------------------
# Start of the program
# ----------------------
user = UserConfig()
tools = UtilityTools(user_config=user.config)
css = CssConst()

client_driver = tools.detect_browsers()
api = Api(user_config=user.config, token=user.config_file["token"], driver=client_driver)
sel_tools = SeleniumUtilities(user_config=user.config, driver=client_driver)
sel_tools.driver.get("https://platform.kryll.io/login")
if user.login:
    sel_tools.get_element(css.EMAIL_INPUT).send_keys(user.login["email"])
    sel_tools.get_element(css.PASSWORD_INPUT).send_keys(user.login["password"])
    input("Login and press a key")
else:
    input("Login and press a key")
if "strat_ids" in user.config_file:
    if "update_strat" in user.config_file:
        if user.config_file["update_strat"] == "y":
            sel_tools.driver.get("https://platform.kryll.io/marketplace/top")
            time.sleep(5)
            ids = sel_tools.get_elements(
                "div.col-sm-12 > app-card-strategy-user:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > h3:nth-child(1) > a:nth-child(1)"
            )
            strat_ids = []
            for strat_id in ids:
                strat_ids.append(strat_id.get_attribute("href").split("/")[4])
            user.write_config(key="strat_ids", value=strat_ids)
        else:
            strat_ids = user.config_file["strat_ids"]
    else:
        strat_ids = user.config_file["strat_ids"]
else:
    strat_ids = tools.ask_strat()

count_quick_fail = 0
while count_quick_fail < 3:
    start = time.time()
    try:
        random.shuffle(strat_ids)
        run()
    except Exception as e:
        tools.log("==============================================")
        tools.log("Exception occured : " + str(e))
        tools.log("Retry...")
        tools.log("==============================================")
    end = time.time()
    elapsed = end - start
    if elapsed < 30:
        count_quick_fail = count_quick_fail + 1
        tools.log("Quick fail : " + str(count_quick_fail) + "/3")
    else:
        count_quick_fail = 0
