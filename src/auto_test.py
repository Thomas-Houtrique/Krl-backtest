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
    start_input.send_keys(start)
    end_input.clear()
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
    tools.log(f"[ℹ][RUN][run_backtest] : Selected exchange = {exchange}")
    tools.log(f"[ℹ][RUN][run_backtest] : Testing period = {backtest_date_period}, from {backtest_date_start} to {backtest_date_end}")
    if not api.backtest_has_failed(
        pair=pair_run_backtest,
        period=backtest_date_period,
        strat=strat_name_run_backtest,
        version=strat_version_run_backtest,
        exchange=exchange,
        start_date=backtest_date_run_backtest["start"],
        end_date=backtest_date_run_backtest["end"],
    ) and not api.backtest_already_did(
        pair=pair_run_backtest,
        period=backtest_date_period,
        strat=strat_name_run_backtest,
        version=strat_version_run_backtest,
        exchange=exchange,
        start_date=backtest_date_run_backtest["start"],
        end_date=backtest_date_run_backtest["end"],
    ):
        tools.log("[ℹ][RUN][run_backtest] : Test in progress, Please Wait...")
        # set date into input
        set_input_date(backtest_date_start, backtest_date_end)
        test_btn = sel_tools.get_element(css.BACKTEST_START_BTN)
        sel_tools.click_on_element(test_btn)

        sel_tools.check_if_popup()
        error = sel_tools.check_error_during_backtest()
        if error:
            raise Exception("Error during backtest")
        sel_tools.check_if_popup()
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

        except Exception as error:
            tools.log("[❌][RUN][run_backtest] : Sending backtest : Exception occured : " + str(error))
        sel_tools.driver.close()
        sel_tools.driver.switch_to.window(sel_tools.driver.window_handles[0])
        if send_ok:
            tools.log("[ℹ][RUN][run_backtest] : Done.")
            return True
        tools.log("[❌][RUN][run_backtest] : Error during sending the result, period canceled.")
        raise Exception("Error during backtest")
    return False


def run():
    # If more 1 tab open, closed useless tabs
    sel_tools.close_unused_tabs()
    for strat_id in strat_ids:
        sel_tools.driver.get("https://platform.kryll.io/marketplace/" + strat_id)
        try:
            recommended_pairs = sel_tools.get_elements(css.RECOMMEND_PAIRS)
        except Exception:
            tools.log("[⚠][RUN][run] : No recommanded pair")
            recommended_pairs = {}
        strat_name = sel_tools.get_element_text(css.STRAT_NAME).strip()
        tools.log(f"[ℹ][RUN][run] : Checking strat : {strat_name}")
        recommended_pairs_list = []
        for i in recommended_pairs:
            recommended_pairs_list.append(i)
        # try to install the strat
        try:
            tools.log("[ℹ][RUN][run] : Checking if strat is installed...")
            backtest_btn = sel_tools.get_element(css.BACKTEST_BTN)
        except Exception:
            tools.log("[ℹ][RUN][run] : Install in progress...")
            install_btn = sel_tools.get_element(css.INSTALL_BTN)
            sel_tools.click_on_element(install_btn)
            tools.log("[ℹ][RUN][run] : Done")
            backtest_btn = sel_tools.get_element(css.BACKTEST_BTN)

        # click on backtest btn
        tools.log("[ℹ][RUN][run] : Strat can be backtested...")
        tools.log("[ℹ][RUN][run] : Initialisation, please wait...")
        sel_tools.click_on_element(backtest_btn)
        # To wait full load of exchange select
        strat_version = sel_tools.get_element_text(css.STRAT_VERSION).split(" ")[1]
        strat_name = sel_tools.get_element_text(css.STRAT_NAME_BACKTEST).strip()
        tools.log(f"[ℹ][RUN][run] : |||||||| Testing strat : {strat_name}, version : {strat_version}")
        exchange_select = Select(sel_tools.get_element(css.EXCHANGE))
        time.sleep(4)

        if "exchanges" in user.config_file:
            exchange_options = sel_tools.get_element(css.EXCHANGE).find_elements_by_tag_name("option")
            user_exchanges = user.config_file["exchanges"]
            final_exchanges = []
            for exchange in exchange_options:
                if exchange.text in user_exchanges:
                    final_exchanges.append(exchange)
        else:
            final_exchanges = [sel_tools.get_element(css.BINANCE_EXCHANGE)]

        for exchange in final_exchanges:
            exchange = exchange.text
            if exchange:
                tools.log(f"[ℹ][RUN][run] : Testing on exchange {exchange}")
                exchange_select.select_by_visible_text(exchange)
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
                recommended = 0
                force_pair = 0
                if i in recommended_pairs_list:
                    recommended = 1

                if "pair" in user.config_file:
                    if recommended == 0 and not pair.replace(" / ", "/") in user.config_file["pair"]:
                        tools.log(f"[ℹ][RUN][run] : Pair {pair} skipped", True)
                        continue
                    if pair.replace(" / ", "/") in user.config_file["pair"]:
                        force_pair = 1
                if "accu" in user.config_file:
                    if recommended == 0 and not pair.split(" / ")[1] in user.config_file["accu"]:
                        tools.log(f"[ℹ][RUN][run] : Pair {pair} skipped", True)
                        continue

                # check if user want to test every pairs
                if force_pair == 0 and recommended == 0 and user.config["every_pairs"] == "n":
                    continue
                if recommended == 1:
                    if "skip_recommended_pair" in user.config_file and user.config_file["skip_recommended_pair"] == "y" and force_pair == 0:
                        continue
                tools.log(f"[ℹ][RUN][run] : pair = {pair}, recommended = {recommended}")

                # Configure backtesting
                pairs_input = Select(sel_tools.get_element(css.PAIRS_INPUT))
                dates_inputs = sel_tools.get_elements(css.DATES_INPUTS)
                start_input = dates_inputs[0]
                end_input = dates_inputs[1]
                # prepare date fields

                sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', start_input)
                sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', end_input)
                selected_pair = pairs_input.first_selected_option
                selected_pair_value = selected_pair.get_attribute("value")
                # Check if pair is listed on exchange
                try:
                    previous_balance_button = sel_tools.get_element_text(sel_tools.css.BALANCE_BUTTON, 10)
                    pairs_input.select_by_value(pair.replace(" / ", "-"))
                    sel_tools.wait_for_pair_loaded(previous_balance_button)
                except Exception:
                    tools.log(fr"[⚠][RUN][run] : /!\ Error recommanded pair {pair} not listed on {exchange}")
                    continue

                # get min/max dates
                min_date = sel_tools.wait_for_attribute_value(start_input, "min")
                exchange = exchange_select.first_selected_option.text.strip()
                backtest_dates = api.get_backtest_dates(min_date=min_date, strat_name=strat_name, strat_version=strat_version, pair=pair, exchange=exchange)
                # run backtests on all dates
                tools.log("[ℹ][RUN][run] : run backtest for pair " + pair + " for all selected periods")
                for backtest_date in backtest_dates:
                    backtest_done = False
                    backtest_failed = False
                    backtest_failed_screenshot = True
                    retry_order_skipped = 0
                    while backtest_done != True and backtest_failed != True:
                        try:
                            run_backtest(strat_name, strat_id, strat_version, pair, recommended, backtest_date, exchange_select)
                            backtest_done = True
                        except:
                            log = ""
                            try:
                                log = sel_tools.get_element_text(css.LOGS_LAST_LINE)
                                if retry_order_skipped<=3 and ("order too small" in log or "Too many orders skipped" in log):
                                    backtest_failed_screenshot = False
                                    retry_order_skipped = retry_order_skipped + 1
                                    if retry_order_skipped >3:
                                        backtest_failed = True
                                        tools.log(log)
                                    else:
                                        sel_tools.click_on_element(sel_tools.get_element(sel_tools.css.BALANCE_BUTTON, 2))
                                        multiplicator = 5*retry_order_skipped
                                        try:
                                            amount_one_input = sel_tools.get_element(sel_tools.css.STARTING_AMOUNT_ONE)
                                            amount_one = amount_one_input.get_attribute('value')
                                            amount_one = float(amount_one)
                                            amount_one = amount_one*multiplicator
                                            amount_one_input.clear()
                                            amount_one_input.send_keys(str(amount_one))
                                        except:
                                            pass
                                        try:
                                            amount_two_input = sel_tools.get_element(sel_tools.css.STARTING_AMOUNT_TWO)
                                            amount_two = amount_two_input.get_attribute('value')
                                            amount_two = float(amount_two)
                                            amount_two = amount_two*multiplicator
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
                                    pair=pair,
                                    period=backtest_date["period"],
                                    strat=strat_name,
                                    version=strat_version,
                                    exchange=exchange,
                                    start_date=backtest_date["start"],
                                    end_date=backtest_date["end"],
                                    log=log,
                                )
                                tools.log("[❌][RUN][run] : Backtest Failed.")
                                if backtest_failed_screenshot:
                                    screenshot_name = "backtest_fail_" + str(strat_id) + "_" + str(pair.replace(" / ", "-")) + "_" + str(exchange) + "_" + str(backtest_date["period"]) + ".png"
                                    sel_tools.save_screenshot(screenshot_name)
                                    tools.log("[❌][RUN][run] : You can see the screenshot on this file : " + screenshot_name)
            tools.log(f"[ℹ][RUN][run] : strat backtested : {strat_name}, version : {strat_version} : Done")


# ----------------------
# Start of the program
# ----------------------
user = UserConfig()
tools = UtilityTools(user_config=user.config,user_config_file=user.config_file)
css = CssConst()

client_driver = tools.detect_browsers(user.config_file["headless"])
api = Api(user_config=user.config, user_config_file=user.config_file, driver=client_driver)
sel_tools = SeleniumUtilities(user_config=user.config,user_config_file=user.config_file, driver=client_driver)
sel_tools.driver.get("https://platform.kryll.io/login")
tools.log("[ℹ][RUN][MAIN] : Login...")
if user.login:
    sel_tools.get_element(css.EMAIL_INPUT).send_keys(user.login["email"])
    sel_tools.get_element(css.PASSWORD_INPUT).send_keys(user.login["password"])
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
