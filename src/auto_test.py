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
from custom.backtest_config import BacktestConfig
from custom.api import Api
from getpass import getpass


def set_input_date(start, end):
    """
    Takes a start date, end date and set them in inputs
    """
    dates_inputs = sel_tools.get_elements(css.DATES_INPUTS)
    start_input = dates_inputs[0]
    end_input = dates_inputs[1]
    sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', start_input)
    sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', end_input)
    start_input.clear()
    start_input.send_keys(start)
    end_input.clear()
    end_input.send_keys(end)

def exec_backtest(backtest_config):
    """
    Takes a strat name, a strat id, a pair, and a backtest date
    return True if no errors else return False
    """
    if not api.backtest_has_failed(backtest_config) and not api.backtest_already_did(backtest_config):
        tools.log("[ℹ][RUN][run_backtest] : Test in progress, Please Wait...")
        # set date into input
        set_input_date(backtest_config.getStart(), backtest_config.getEnd())
        test_btn = sel_tools.get_element(css.BACKTEST_START_BTN)
        sel_tools.click_on_element(test_btn)

        error = sel_tools.check_error_during_backtest()
        if error:
            raise Exception("Error during backtest")
        sel_tools.wait_network_calls_loaded()
        hold = sel_tools.get_element_double(css.ANALYSE_TAB_HOLD)
        # click on depth analysis button
        sel_tools.click_on_element(sel_tools.get_element(css.ANALYSE_TAB_DEEP_ANALYSE_LINK))
        windows_handle = sel_tools.wait_for_windows_handle(120)
        if not windows_handle:
            tools.log("[❌][RUN][run_backtest] : depth analysis button is break on kryll side, period canceled")
            raise Exception("depth analysis button is break on kryll side, period canceled")
        send_ok = False
        try:
            sel_tools.driver.switch_to.window(sel_tools.driver.window_handles[1])
            # wait for the advanced bt page to load
            depth_analysis_page_loaded = sel_tools.wait_for_element(css.ADVANCED_ANALYSE_TRADE, 120)
            if not depth_analysis_page_loaded:
                tools.log("[⚠][RUN][run_backtest] : depth analysis tab seems to don't load, refresh and retry...")
                # retry
                sel_tools.refresh()
                depth_analysis_page_loaded = sel_tools.wait_for_element(css.ADVANCED_ANALYSE_TRADE, 120)
            if depth_analysis_page_loaded:
                send_ok = api.send_result(backtest_config, {"hold": hold})

        except Exception as error:
            tools.log("[❌][RUN][run_backtest] : Sending backtest : Exception occured : " + str(error))
        
        if not send_ok:
            screenshot_name = "backtest_fail_deep_analysis_" + str(backtest_config.getId()) + ".png"
            sel_tools.save_screenshot(screenshot_name)
            tools.log("[❌][RUN][run] : You can see the screenshot on this file : " + screenshot_name)
        sel_tools.driver.close()
        sel_tools.driver.switch_to.window(sel_tools.driver.window_handles[0])
        if send_ok:
            tools.log("[ℹ][RUN][run_backtest] : Done.")
            return True
        tools.log("[❌][RUN][run_backtest] : Error during sending the result, period canceled.")
        raise Exception("Error during backtest")
    return False

def install_strat_if_needed():
    try:
        tools.log("[ℹ][RUN][run] : Checking if strat is installed...")
        backtest_btn = sel_tools.get_element(css.BACKTEST_BTN)
    except Exception:
        tools.log("[ℹ][RUN][run] : Install in progress...")
        install_btn = sel_tools.get_element(css.INSTALL_BTN)
        sel_tools.click_on_element(install_btn)
        tools.log("[ℹ][RUN][run] : Done")
        backtest_btn = sel_tools.get_element(css.BACKTEST_BTN)

    return True

def get_recommended_pairs():
    try:
        recommended_pairs = sel_tools.get_elements(css.RECOMMEND_PAIRS)
    except Exception:
        tools.log("[⚠][RUN][run] : No recommanded pair")
        recommended_pairs = {}
    strat_name = sel_tools.get_element_text(css.STRAT_NAME).strip()
    recommended_pairs_list = []
    for i in recommended_pairs:
        recommended_pairs_list.append(i)
    return recommended_pairs_list

def get_exchanges_to_test():
    if "exchanges" in user.config_file:
        exchange_options = sel_tools.get_element(css.EXCHANGE).find_elements_by_tag_name("option")
        user_exchanges = user.config_file["exchanges"]
        final_exchanges = []
        for exchange in exchange_options:
            if exchange.text in user_exchanges:
                final_exchanges.append(exchange)
    else:
        final_exchanges = [sel_tools.get_element(css.BINANCE_EXCHANGE)]
    return final_exchanges

def get_pairs_to_test():
    recommended_pairs_list = get_recommended_pairs()
    final_pairs = []
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
        recommended = 0
        force_pair = 0
        if i in recommended_pairs_list:
            recommended = 1

        if "pair" in user.config_file:
            if not pair.replace(" / ", "/") in user.config_file["pair"]:
                continue
            if pair.replace(" / ", "/") in user.config_file["pair"]:
                force_pair = 1
        if "accu" in user.config_file:
            if not pair.split(" / ")[1] in user.config_file["accu"]:
                continue

        # check if user want to test every pairs
        if force_pair == 0 and recommended == 0 and user.config["every_pairs"] == "n":
            continue
        if recommended == 1:
            if "skip_recommended_pair" in user.config_file and user.config_file["skip_recommended_pair"] == "y" and force_pair == 0:
                continue
        final_pairs.append(i)
    return final_pairs


def select_exchange(exchange):
    exchange_text = exchange.text
    exchange_select = Select(sel_tools.get_element(css.EXCHANGE))
    exchange_select.select_by_visible_text(exchange_text)
    sel_tools.wait_network_calls_loaded()
    return True

def select_pair(pair):
    pair_text = pair.text
    pairs_input = Select(sel_tools.get_element(css.PAIRS_INPUT))
    pairs_input.select_by_value(pair_text.replace(" / ", "-"))
    sel_tools.wait_network_calls_loaded()

def is_pair_listed(pair):
    pairs_input = Select(sel_tools.get_element(css.PAIRS_INPUT))
    try:
        pairs_input.select_by_value(pair.text.strip().replace(" / ", "-"))
    except Exception as error:
        return False
    return True

def get_periods(backtest_config):
    dates_inputs = sel_tools.get_elements(css.DATES_INPUTS)
    start_input = dates_inputs[0]
    end_input = dates_inputs[1]
    min_date = sel_tools.wait_for_attribute_value(start_input, "min")
    tools.log(f"[ℹ][RUN][run] : min date : {min_date}...")
    backtest_dates = api.get_backtest_dates(min_date=min_date, backtest_config=backtest_config)
    return backtest_dates

def click_on_backtest_button():
    backtest_page_loaded = False
    while not backtest_page_loaded:
        try:
            sel_tools.click_on_element(sel_tools.get_element(css.BACKTEST_BTN))
            sel_tools.wait_network_calls_loaded()
            sel_tools.get_element_text(css.STRAT_NAME_BACKTEST)
            sel_tools.get_element_text(css.STRAT_VERSION)
            backtest_page_loaded = True
        except:
            tools.log(f"[ℹ][RUN][run] : White page... Retry")
            sel_tools.refresh()
            sel_tools.wait_network_calls_loaded()
            continue

def is_recommended_pair(pair):
    recommended_pairs_list = get_recommended_pairs()
    return (pair in recommended_pairs_list)

def run_backtest(backtest_config):
    backtest_done = False
    backtest_failed = False
    backtest_failed_screenshot = True
    retry_order_skipped = 0
    while backtest_done != True and backtest_failed != True:
        # Try to exec the backtest
        try:
            exec_backtest(backtest_config)
            backtest_done = True
        # If backtest failed, check if order too small or too many order skipped. If yes, retry x3 with more start wallet
        except:
            log = ""
            try:
                log = sel_tools.get_element_text(css.LOGS_LAST_LINE)
                if retry_order_skipped <= 3 and ("order too small" in log or "Too many orders skipped" in log):
                    backtest_failed_screenshot = False
                    retry_order_skipped = retry_order_skipped + 1
                    if retry_order_skipped > 3:
                        backtest_failed = True
                        tools.log(log)
                    else:
                        sel_tools.click_on_element(sel_tools.get_element(sel_tools.css.BALANCE_BUTTON, 2))
                        multiplicator = 5 * retry_order_skipped
                        try:
                            amount_one_input = sel_tools.get_element(sel_tools.css.STARTING_AMOUNT_ONE)
                            amount_one = amount_one_input.get_attribute("value")
                            amount_one = float(amount_one)
                            amount_one = amount_one * multiplicator
                            amount_one_input.clear()
                            amount_one_input.send_keys(str(amount_one))
                        except:
                            pass
                        try:
                            amount_two_input = sel_tools.get_element(sel_tools.css.STARTING_AMOUNT_TWO)
                            amount_two = amount_two_input.get_attribute("value")
                            amount_two = float(amount_two)
                            amount_two = amount_two * multiplicator
                            amount_two_input.clear()
                            amount_two_input.send_keys(str(amount_two))
                        except:
                            pass
                        tools.log(f"[❌][RUN][run] : Too many order skipped, retry with x{multiplicator} amount {retry_order_skipped}/3.")
                else:
                    backtest_failed = True
                    tools.log(log)
            except:
                backtest_failed = True
                pass
            if "missing data" in log:
                tools.log(f"[❌][RUN][run] : {log}")
                backtest_failed_screenshot = False
                backtest_failed = True
            if backtest_failed:
                api.backtest_add_failed(
                    backtest_config=backtest_config,
                    log=log
                )
                tools.log("[❌][RUN][run] : Backtest Failed.")
                if backtest_failed_screenshot:
                    screenshot_name = "backtest_fail_" + str(backtest_config.getId()) + ".png"
                    sel_tools.save_screenshot(screenshot_name)
                    tools.log("[❌][RUN][run] : You can see the screenshot on this file : " + screenshot_name)

def run():
    # If more 1 tab open, closed useless tabs
    sel_tools.close_unused_tabs()
    for strat_id in strat_ids:
        backtest_config = BacktestConfig()
        backtest_config.setStratId(strat_id)
        # Go to strat page
        tools.log("[ℹ][RUN][run] : Go to strat page...")
        sel_tools.get("https://platform.kryll.io/marketplace/" + strat_id)
        # Check if strat is installed, and install it
        install_strat_if_needed()
        # Click on backtest button
        tools.log("[ℹ][RUN][run] : Click on backtest button...", True)
        click_on_backtest_button()
        # Get strat name, strat version
        tools.log("[ℹ][RUN][run] : Get Strat name and version...", True)
        backtest_config.setStratName(sel_tools.get_element_text(css.STRAT_NAME_BACKTEST).strip())
        backtest_config.setStratVersion(sel_tools.get_element_text(css.STRAT_VERSION).split(" ")[1])
        tools.log(f"[ℹ][RUN][run] : ****************************************************************")
        tools.log(f"[ℹ][RUN][run] :     Testing strat : {backtest_config.getStratName()}, version : {backtest_config.getStratVersion()}")
        tools.log(f"[ℹ][RUN][run] : ****************************************************************")
        # Get recommended pairs list
        tools.log("[ℹ][RUN][run] : Get recommended pair list...", True)
        recommended_pairs = get_recommended_pairs()
        # Get Exchanges to test
        tools.log("[ℹ][RUN][run] : Get exchanges to test...", True)
        exchanges = get_exchanges_to_test()
        # For each exchange
        for exchange in exchanges:
            backtest_config.setExchange(exchange.text)
            # Select exchange and wait network pair load
            tools.log(f"[ℹ][RUN][run] : Select exchange {backtest_config.getExchange()}...")
            select_exchange(exchange)
            # Get pairs to test
            tools.log("[ℹ][RUN][run] : Get pairs...", True)
            pairs = get_pairs_to_test()
            # For each pairs
            for pair in pairs:
                backtest_config.setPair(pair.text)
                backtest_config.setRecommended(pair in recommended_pairs)
                # Check if pair exist on exchange
                if not is_pair_listed(pair):
                    tools.log(f"[ℹ][RUN][run] : Pair {backtest_config.getPair()} not listed...")
                    continue
                # Select pair wait network dates load and get min date
                tools.log(f"[ℹ][RUN][run] : Select pair {backtest_config.getPair()}...")
                select_pair(pair)
                # Get periods to test
                tools.log("[ℹ][RUN][run] : Get periods to test...", True)
                periods = get_periods(backtest_config)
                # For each period
                for period in periods:
                    backtest_config.setPeriod(period["period"])
                    backtest_config.setStart(period["start"])
                    backtest_config.setEnd(period["end"])
                    tools.log(f"[ℹ][RUN][run] : ----- run backtest [{backtest_config.getStratName()}][v{backtest_config.getStratVersion()}][{backtest_config.getExchange()}][{backtest_config.getPair()}][{backtest_config.getPeriod()}][{backtest_config.getStart()} {backtest_config.getEnd()}]...")
                    # Run backtest
                    run_backtest(backtest_config)
        # Strat backtested, next 
        tools.log(f"[ℹ][RUN][run] : strat backtested : {backtest_config.getStratName()}, version : {backtest_config.getStratVersion()} : Done")
    return True


# ----------------------
# Start of the program
# ----------------------
user = UserConfig()
tools = UtilityTools(user_config=user.config, user_config_file=user.config_file)
css = CssConst()

client_driver = tools.detect_browsers(user.config_file["headless"])
api = Api(user_config=user.config, user_config_file=user.config_file, driver=client_driver)
sel_tools = SeleniumUtilities(user_config=user.config, user_config_file=user.config_file, driver=client_driver)
sel_tools.driver.get("https://platform.kryll.io/login")
tools.log("[ℹ][RUN][MAIN] : Login...")
if user.login:
    sel_tools.get_element(css.EMAIL_INPUT).send_keys(user.login["email"])
    sel_tools.get_element(css.PASSWORD_INPUT).send_keys(user.login["password"])
else:
    sel_tools.get_element(css.EMAIL_INPUT).send_keys(input("email :"))
    sel_tools.get_element(css.PASSWORD_INPUT).send_keys(getpass("password :"))
twofa = input("2FA :").lower()
sel_tools.get_element(css.TWO_FA_INPUT).send_keys(twofa)
sel_tools.click_on_element(sel_tools.get_element(css.LOG_IN_BTN))

sel_tools.wait_for_element(css.USER_DROPDOWN, 100000)
if "update_strat" in user.config_file and user.config_file["update_strat"] == "y":
    tools.log("[ℹ][RUN][MAIN] : Strat update in progress...")
    sel_tools.driver.get("https://platform.kryll.io/marketplace/top")
    ids = sel_tools.get_elements(
        "div.col-sm-12 > app-card-strategy-user:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > h3:nth-child(1) > a:nth-child(1)"
    )
    strat_ids = []
    for strat_id in ids:
        strat_ids.append(strat_id.get_attribute("href").split("/")[4])
    tools.log("[ℹ][RUN][MAIN] : Done!")
else:
    if "strat_ids" in user.config_file:
        strat_ids = user.config_file["strat_ids"]
    else:
        strat_ids = tools.ask_strat()

COUNT_QUICK_FAIL = 0
EXECUTION_ID = 0
while COUNT_QUICK_FAIL < 3:
    EXECUTION_ID = EXECUTION_ID + 1
    start = time.time()
    try:
        random.shuffle(strat_ids)
        run()
    except Exception as error:
        SCREENSHOT_NAME = "screen_fail_" + str(EXECUTION_ID) + ".png"
        sel_tools.save_screenshot(SCREENSHOT_NAME)
        tools.log("[❌][RUN][MAIN] : Exception occured on execution " + str(EXECUTION_ID) + " : " + str(error))
        tools.log("[❌][RUN][MAIN] : You can see the screenshot on this file : " + SCREENSHOT_NAME)
        tools.log("[❌][RUN][MAIN] : Retry...")
    end = time.time()
    elapsed = end - start
    if elapsed < 30:
        COUNT_QUICK_FAIL = COUNT_QUICK_FAIL + 1
        tools.log("[❌][RUN][MAIN][❌] : Quick fail : " + str(COUNT_QUICK_FAIL) + "/3")
    else:
        COUNT_QUICK_FAIL = 0