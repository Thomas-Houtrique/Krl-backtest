"""
Script automating backtest on kryll.io and sending results to an API
Made by Thomas with the help of torkium
"""
from pprint import pp, pprint
import time
import random
import sys
import datetime
import argparse
import json
import csv
import hashlib
import requests
import os
import shutil
from selenium.webdriver.support.ui import Select
from custom.user_config import UserConfig
from custom.utilities import UtilityTools
from custom.css_const import CssConst
from custom.selenium_utilities import SeleniumUtilities
from custom.backtest_config import BacktestConfig
from custom.api import Api
from getpass import getpass


def set_input_date(start_input_date, end_input_date):
    """
    Takes a start date, end date and set them in inputs
    """
    dates_inputs = sel_tools.get_elements(css.DATES_INPUTS)
    start_input = dates_inputs[0]
    end_input = dates_inputs[1]
    sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', start_input)
    sel_tools.driver.execute_script('arguments[0].removeAttribute("readonly")', end_input)
    start_input.clear()
    start_input.send_keys(start_input_date)
    end_input.clear()
    end_input.send_keys(end_input_date)


def exec_backtest(backtest_config, blocks_md5 = False):
    """
    Takes a strategy name, a strategy id, a pair, and a backtest date
    return True if no errors else return False
    """
    if blocks_md5 or ("periods" in user.config_file) or (not api.backtest_has_failed(backtest_config) and not api.backtest_already_did(backtest_config)):
        tools.log("[ℹ] Test in progress, Please Wait...")
        bt_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # set date into input
        set_input_date(backtest_config.getStart(), backtest_config.getEnd())


        if blocks_md5:
            try:
                csv_data = [
                    blocks_md5,
                    backtest_config.getStratId(),
                    backtest_config.getStratName(),
                    backtest_config.getStratVersion(),
                    backtest_config.getPair(),
                    backtest_config.getExchange(),
                    backtest_config.getPeriod(),
                    backtest_config.getStart(),
                    backtest_config.getEnd(),
                    user.config_file['email'],
                    bt_start,
                    '' 
                    #bt_end
                ]
                with open('my_strats.log', 'a') as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerow(csv_data)
                tools.log("[ℹ] Backtest data added to my_strats.log file.", True)
            except Exception as error:
                tools.log("[❌] Fail saving data to my_strats.log file:\n" + str(error), True)



        test_btn = sel_tools.get_element(css.BACKTEST_START_BTN)
        sel_tools.clean_network_calls()
        sel_tools.click_on_element(test_btn)

        error_during_backtest = sel_tools.check_error_during_backtest()
        if error_during_backtest:
            if blocks_md5:
                update_my_strat_done(backtest_config, blocks_md5, bt_start, 'FAIL')
            raise Exception("Error during backtest")
        sel_tools.clean_network_calls()
        hold = sel_tools.get_element_double(css.ANALYSE_TAB_HOLD)
        gain = sel_tools.get_element_double(css.ANALYSE_TAB_GAIN)
        bt_end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tools.log("[ℹ] Test finished, waiting depth analysis Please Wait...")

        # click on download logs button
        if blocks_md5 and ('save_logs' in user.config_file):
            try:
                sel_tools.click_on_element(sel_tools.get_element(css.TAB_BTN_LOGS))
                sel_tools.click_on_element(sel_tools.get_element(css.save_logs_LINK))
                sel_tools.click_on_element(sel_tools.get_element(css.TAB_BTN_ANALYSE))
                filename = max([user.config_file['save_logs'] + f for f in os.listdir(user.config_file['save_logs'])],key=os.path.getctime)
                newfilename = backtest_config.getStratName() + '_v' + str(backtest_config.getStratVersion())+'_'+(backtest_config.getPair().replace('/', '-'))+'@'+backtest_config.getExchange()+'_'+backtest_config.getStart()+'_'+backtest_config.getEnd() + '.txt';
                #shutil.move(filename,os.path.join(user.config_file['save_logs'],r"newfilename.txt"))
                shutil.move(filename,os.path.join(user.config_file['save_logs'],r"{}".format(newfilename)))
            except Exception as error:
                tools.log("[❌] Fail to download logs\n" + str(error))

        # click on depth analysis button
        sel_tools.click_on_element(sel_tools.get_element(css.ANALYSE_TAB_DEEP_ANALYSE_LINK))
        windows_handle = sel_tools.wait_for_windows_handle(300)
        if not windows_handle:
            if blocks_md5:
                update_my_strat_done(backtest_config, blocks_md5, bt_start, 'FAIL')
            tools.log("[❌] depth analysis button is break on kryll side, period canceled")
            raise Exception("depth analysis button is break on kryll side, period canceled")
        send_ok = False
        try:
            sel_tools.driver.switch_to.window(sel_tools.driver.window_handles[1])
            # wait for the advanced bt page to load
            depth_analysis_page_loaded = sel_tools.wait_for_element(css.ADVANCED_ANALYSE_TRADE, 300)
            if not depth_analysis_page_loaded:
                tools.log("[⚠] depth analysis tab seems to don't load, refresh and retry...")
                # retry
                sel_tools.refresh()
                depth_analysis_page_loaded = sel_tools.wait_for_element(css.ADVANCED_ANALYSE_TRADE, 120)
            if depth_analysis_page_loaded:
                send_ok = api.send_result(backtest_config, {"hold": hold})

                if blocks_md5:                    
                    update_my_strat_done(backtest_config, blocks_md5, bt_start, bt_end)

                if "history" in user.config_file:
                    try:
                        csv_data = [
                            backtest_config.getStratId(),
                            backtest_config.getStratName(),
                            backtest_config.getStratVersion(),
                            backtest_config.getPair(),
                            backtest_config.getExchange(),
                            backtest_config.getPeriod(),
                            backtest_config.getStart(),
                            backtest_config.getEnd(),
                            hold.replace(',',''),
                            gain.replace(',',''),
                            '', #todo : deep analyse id if available
                        ]
                        with open(user.config_file['history'], 'a') as f:
                            csv_writer = csv.writer(f)
                            csv_writer.writerow(csv_data)
                        tools.log("[ℹ] Backtest data added to history CSV file: " + user.config_file['history'])
                    except Exception as error:
                        tools.log("[❌] Fail saving data to history CSV file: "+ user.config_file['history'] + "\n" + str(error))


        except Exception as error:
            tools.log("[❌] Sending backtest : Exception occured : " + str(error))

        if not send_ok:
            if blocks_md5:
                update_my_strat_done(backtest_config, blocks_md5, bt_start, 'FAIL')
            screenshot_name = "backtest_fail_deep_analysis_" + str(backtest_config.getId()) + ".png"
            sel_tools.save_screenshot(screenshot_name)
            tools.log("[❌] You can see the screenshot on this file : " + screenshot_name)
        sel_tools.driver.close()
        sel_tools.driver.switch_to.window(sel_tools.driver.window_handles[0])
        if send_ok:
            return True
        tools.log("[❌] Error during sending the result, period canceled.")
        raise Exception("Error during backtest")
    return False

def update_my_strat_done(backtest_config, blocks_md5, bt_start, finish_date):
    tools.log("[ℹ] Update my_strats.log Finish date: " + finish_date, True)
    csv_data = None
    try:
        with open('my_strats.log', 'r') as f:
            csv_data = list(csv.reader(f))
    except Exception as error:
        pprint(error)
        tools.log("[❌] Fail to open my_strats log file", True)
        csv_data = None

    if csv_data is not None:
        try:
            for i,strat_done in enumerate(csv_data):
                if (strat_done[0] == blocks_md5) and (strat_done[2] == backtest_config.getStratName()) and (strat_done[4] == backtest_config.getPair()) and (strat_done[5] == backtest_config.getExchange()) and (strat_done[7] == backtest_config.getStart()) and (strat_done[8] == backtest_config.getEnd()) and (strat_done[10] == bt_start):
                    strat_done[11] = finish_date
                    csv_data[i] = strat_done
                    break;
        except Exception as error:
            pprint(error)
            tools.log("[❌] Fail to read my_strats log file", True)
            csv_data = None

    if csv_data is not None:
        try:
            with open('my_strats.log', 'w') as f:
                csv_writer = csv.writer(f)
                csv_writer.writerows(csv_data)
        except:
            tools.log("[❌] Fail to write my_strats log file", True)    

def install_strat_if_needed():
    try:
        tools.log("[ℹ] Checking if strategy is installed...")
        sel_tools.get_element(css.BACKTEST_BTN)
    except Exception:
        tools.log("[ℹ] Install in progress...")
        install_btn = sel_tools.get_element(css.INSTALL_BTN)
        sel_tools.click_on_element(install_btn)
    return True


def update_strat_if_needed():
    tools.log("[ℹ] Checking if strategy needs to be updated")
    time.sleep(5)
    if "btn-warning" in sel_tools.get_element(css.UPDATE_BTN).get_attribute("class").split():
        tools.log("[ℹ] Updating the strategy...")
        update_btn = sel_tools.get_element(css.UPDATE_BTN)
        sel_tools.click_on_element(update_btn)
    else:
        tools.log("[ℹ] Strategy is up to date")


def get_recommended_pairs():
    try:
        recommended_pairs = sel_tools.get_elements(css.RECOMMEND_PAIRS)
    except Exception:
        tools.log("[⚠] No recommanded pair")
        recommended_pairs = {}
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


def get_pairs_to_test(recommended_pairs = True):
    if recommended_pairs == True:
        recommended_pairs_list = get_recommended_pairs()
    else:
        recommended_pairs_list = []
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
        if "accu" in user.config_file and not pair.split(" / ")[1] in user.config_file["accu"]:
            continue

        # check if user want to test every pairs
        if force_pair == 0 and recommended == 0 and user.config_file["every_pairs"] == "n":
            continue
        if recommended == 1 and "skip_recommended_pair" in user.config_file and user.config_file["skip_recommended_pair"] == "y" and force_pair == 0:
            continue
        final_pairs.append(i)
    return final_pairs


def select_exchange(exchange):
    sel_tools.clean_network_calls()
    exchange_text = exchange.text
    exchange_select = Select(sel_tools.get_element(css.EXCHANGE))
    exchange_select.select_by_visible_text(exchange_text)
    sel_tools.wait_network_calls_loaded(5)
    return True


def select_pair(pair):
    sel_tools.clean_network_calls()
    pair_text = pair.text
    pairs_input = Select(sel_tools.get_element(css.PAIRS_INPUT))
    pairs_input.select_by_value(pair_text.replace(" / ", "-"))
    sel_tools.wait_network_calls_loaded(5)


def is_pair_listed(pair):
    pairs_input = Select(sel_tools.get_element(css.PAIRS_INPUT))
    try:
        pairs_input.select_by_value(pair.text.strip().replace(" / ", "-"))
    except Exception:
        return False
    return True


def get_periods(backtest_config, from_config = False):
    dates_inputs = sel_tools.get_elements(css.DATES_INPUTS)
    start_input = dates_inputs[0]
    min_date = sel_tools.wait_for_attribute_value(start_input, "min")
    tools.log(f"[ℹ] min date : {min_date}", verbose=True)
    if from_config:
        backtest_dates = []
        periods = user.config_file['periods']
        for period in periods:
            min_dt = datetime.datetime.strptime(min_date, '%Y-%m-%d').date()
            start_dt = periods[period][0]
            end_dt = periods[period][1]
            if(min_dt > start_dt):
                #we add one day because first day of pair prices on an exchange is usualy not revelant
                start_dt = min_dt + datetime.timedelta(days=1)
            if(end_dt > start_dt):
                backtest_dates.append({
                    'period': period,
                    'start': str(start_dt),
                    'end': str(end_dt)
                })
    else:
        backtest_dates = api.get_backtest_dates(min_date=min_date, backtest_config=backtest_config)
    return backtest_dates


def click_on_backtest_button(bt_button = False):
    if bt_button == False:
        bt_button = sel_tools.get_element(css.BACKTEST_BTN)
    backtest_page_loaded = False
    while not backtest_page_loaded:
        try:
            sel_tools.click_on_element(bt_button, True)
            sel_tools.get_element_text(css.STRAT_NAME_BACKTEST)
            if bt_button == False:
                sel_tools.get_element_text(css.STRAT_VERSION)
            backtest_page_loaded = True
        except:
            tools.log("[ℹ] White page... Retry")
            sel_tools.refresh()
            continue


def is_recommended_pair(pair):
    recommended_pairs_list = get_recommended_pairs()
    return pair in recommended_pairs_list


def run_backtest(backtest_config, blocks_md5):
    backtest_done = False
    backtest_failed = False
    backtest_failed_screenshot = True
    retry_order_skipped = 0
    while True not in (backtest_done, backtest_failed):
        # Try to exec the backtest
        try:
            exec_backtest(backtest_config, blocks_md5)
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
                        tools.log(f"[❌] {log}")
                    else:
                        sel_tools.click_on_element(sel_tools.get_element(sel_tools.css.BALANCE_BUTTON, 2))
                        multiplicator = 1000 * retry_order_skipped
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
                        tools.log(f"[❌] Too many order skipped, retry with x{multiplicator} amount {retry_order_skipped}/3.")
                else:
                    backtest_failed = True
                    tools.log(f"[❌] {log}")
            except:
                backtest_failed = True
            if "missing data" in log:
                tools.log(f"[❌] {log}")
                backtest_failed_screenshot = False
                backtest_failed = True
            if backtest_failed:
                api.backtest_add_failed(backtest_config=backtest_config, log=log)
                tools.log("[❌] Backtest Failed.")
                if backtest_failed_screenshot:
                    screenshot_name = "backtest_fail_" + str(backtest_config.getId()) + ".png"
                    sel_tools.save_screenshot(screenshot_name)
                    tools.log("[❌] You can see the screenshot on this file : " + screenshot_name)


def run(my_strats = False):
    # If more 1 tab open, closed useless tabs
    sel_tools.close_unused_tabs()

    for strat_id in strat_ids:
        backtest_config = BacktestConfig()
        backtest_config.setStratId(strat_id)

        if(my_strats != False):
            strat_file = None
            strat_found = False
            recommended_pairs = []
            if strat_id.endswith('.kryll'):
                strat_file = strat_id
                try:
                    with open('my_strats/' + strat_file,'r') as f:
                        strat_data = json.loads(f.read())
                    strat_name = strat_data['name']
                    tools.log("[ℹ] Strategy file found, strategy name: " + strat_name, True)
                except:
                    tools.log("[❌] Fail to open strategy file: " + strat_file)
                    break

            sel_tools.driver.get("https://platform.kryll.io/strategies")
            try:
                my_strats_cards = sel_tools.get_elements(css.MY_STRATS)
                if(my_strats_cards):
                    #we browse "my strategies" section and try to find the strategy name
                    tools.log('[ℹ] Looking for strategy "' + strat_name + '" in My Strategies', True)
                    for my_strat_card in my_strats_cards:
                        strat_card_name = my_strat_card.find_elements_by_tag_name('h3')[0].text
                        if strat_card_name.lower().startswith(strat_name.lower()):
                            backtest_config.setStratName(strat_name)
                            backtest_config.setStratVersion(1)
                            bt_button = my_strat_card.find_elements_by_class_name('d-none')[0]
                            tools.log("[ℹ] Strategy found, click on backtest button of " + strat_name, True)
                            strat_found = True
                            click_on_backtest_button(bt_button)
                            response = json.loads(sel_tools.get_response_body('/users/me/strategies/'))
                            strat_data = response['data']
                            break
            except:
                tools.log("[ℹ] Mine Strategies seems to be empty", True)
            #don't found, if there is a file, we import it
            if strat_file and (not strat_found):
                try:
                    tools.log("[ℹ] strategy not found, try to import: " + strat_file, True)
                    headers = {'x-access-token': auth_token, 'Content-Type': 'application/json'}
                    response = requests.post(url = 'https://platform.kryll.io/api/users/me/strategies', json = strat_data, headers = headers)
                    if response.status_code == 200:
                        strat_data = response.json()['data']
                        strat_id = strat_data['id']
                        tools.log("[ℹ] Strategy imported successfully: " + strat_name, True)
                        sel_tools.driver.get("https://platform.kryll.io/strategies")
                        my_strats_cards = sel_tools.get_elements(css.MY_STRATS)
                        #we browse "my strategies" section and try to find the strategy name
                        tools.log('[ℹ] Looking for strategy "' + strat_name + '" in My Strategies', True)
                        for my_strat_card in my_strats_cards:
                            strat_card_name = my_strat_card.find_elements_by_tag_name('h3')[0].text
                            if strat_card_name.lower().startswith(strat_name.lower()):
                                backtest_config.setStratName(strat_name)
                                backtest_config.setStratVersion(1)
                                bt_button = my_strat_card.find_elements_by_class_name('d-none')[0]
                                tools.log("[ℹ] Strategy found, click on backtest button of " + strat_name, True)
                                click_on_backtest_button(bt_button)
                                break
                    else:
                        tools.log("[❌] Fail to import strategy file: " + strat_file)
                        break
                except:
                    tools.log("[❌] Fail to import strategy: " + strat_file)
                    break
            backtest_config.setStratId(strat_data['id'])
            blocks_md5 = hashlib.md5(json.dumps(strat_data['blocks']).encode()).hexdigest()
        else:
            # Go to strategy page
            tools.log("[ℹ] Go to strategy page...")
            sel_tools.get("https://platform.kryll.io/marketplace/" + strat_id)
            # Check if strategy is installed, and install it
            install_strat_if_needed()
            # Check if strategy needs to be updated
            update_strat_if_needed()
            # Click on backtest button
            tools.log("[ℹ] Click on backtest button...", True)
            click_on_backtest_button()
            # Get strategy name, strategy version
            tools.log("[ℹ] Get strategy name and version...", True)
            backtest_config.setStratName(sel_tools.get_element_text(css.STRAT_NAME_BACKTEST).strip())
            backtest_config.setStratVersion(sel_tools.get_element_text(css.STRAT_VERSION).split(" ")[1])
            # Get recommended pairs list
            tools.log("[ℹ] Get recommended pair list...", True)
            recommended_pairs = get_recommended_pairs()

        # Get Exchanges to test
        tools.log("[ℹ] Get exchanges to test...", True)
        exchanges = get_exchanges_to_test()
        # For each exchange
        for exchange in exchanges:
            backtest_config.setExchange(exchange.text)
            # Select exchange and wait network pair load
            tools.log(f"[ℹ] Select exchange {backtest_config.getExchange()}...")
            select_exchange(exchange)
            # Get pairs to test
            tools.log("[ℹ] Get pairs...", True)
            pairs = get_pairs_to_test(not my_strats)
            # For each pairs
            for pair in pairs:
                backtest_config.setPair(pair.text)
                backtest_config.setRecommended(pair in recommended_pairs)
                # Check if pair exist on exchange
                if not is_pair_listed(pair):
                    tools.log(f"[ℹ] Pair {backtest_config.getPair()} not listed...")
                    continue
                # Select pair wait network dates load and get min date
                tools.log(f"[ℹ] Select pair {backtest_config.getPair()}...")
                select_pair(pair)
                # Get periods to test
                tools.log("[ℹ] Get periods to test...", True)
                periods = get_periods(backtest_config, my_strats or "periods" in user.config_file)
                # For each period
                for period in periods:
                    backtest_config.setPeriod(period["period"])
                    backtest_config.setStart(period["start"])
                    backtest_config.setEnd(period["end"])
                    tools.log("[ℹ] **************************************")
                    tools.log("[ℹ] *         Running backtest           *")
                    tools.log("[ℹ] **************************************")
                    tools.log(f"[ℹ] * Strategy name : {backtest_config.getStratName()}")
                    tools.log(f"[ℹ] * Strategy version : {backtest_config.getStratVersion()}")
                    tools.log(f"[ℹ] * Exchange : {backtest_config.getExchange()}")
                    tools.log(f"[ℹ] * Backtest pair : {backtest_config.getPair()}")
                    tools.log(f"[ℹ] * Backtest period : {backtest_config.getPeriod()}")
                    tools.log(f"[ℹ] * From : {backtest_config.getStart()} to {backtest_config.getEnd()}")
                    tools.log("[ℹ] ***************************************")
                    # Run backtest
                    if(my_strats != False):
                        my_strats_done = []
                        try:
                            with open('my_strats.log', 'r') as f:
                                my_strats_done = list(csv.reader(f))
                        except Exception as error:
                            tools.log("[❌] Fail to load my_strats.log", True)
                            
                        backtest_already_done = False
                        if 'force' in user.config_file and user.config_file['force'] == 'y':
                            tools.log("[ℹ] Skip already done verification")
                        else:
                            for strat_done in my_strats_done:
                                if (strat_done[0] == blocks_md5) and (strat_done[2] == backtest_config.getStratName()) and (strat_done[4] == backtest_config.getPair()) and (strat_done[5] == backtest_config.getExchange()) and (strat_done[7] == backtest_config.getStart()) and (strat_done[8] == backtest_config.getEnd()):
                                    finish_date = strat_done[11]
                                    if finish_date == '':
                                        begin_date = strat_done[10]
                                        if strat_done[10]:
                                            begin_date = datetime.datetime.strptime(strat_done[10], "%Y-%m-%d %H:%M:%S")
                                        else:
                                            begin_date = None
                                        if (begin_date is not None) and ((datetime.datetime.now() - begin_date).total_seconds() < 3600):
                                            tools.log("[ℹ] Backtest in progress (not finished for an hour)", True)
                                            backtest_already_done = True
                                            break
                                    elif finish_date.upper()!='FAIL':
                                        backtest_already_done = True
                                        tools.log("[ℹ] Backtest already done: " + finish_date, True)
                                        break
                        if not backtest_already_done:
                            run_backtest(backtest_config, blocks_md5)
                        else:
                            tools.log("[ℹ] Backtest already done")
                    else:
                        run_backtest(backtest_config, my_strats)
        # strategy backtested, next
        tools.log("[ℹ] strategy backtested !")
    return True


def command(command):
    headers = {'x-access-token': auth_token, 'Content-Type': 'application/json'}
    tools.log("[ℹ] COMMAND MODE: " + command)
    if command == 'delete_strats':
        response = requests.get(url = 'https://platform.kryll.io/api/users/me/strategies', headers = headers)
        res = response.json()
        for strat in res['data']:
            if strat['name'].lower().startswith(user.config_file['delete_strats'].lower()):
                response = requests.delete(url = 'https://platform.kryll.io/api/users/me/strategies/' + strat['id'], headers = headers)
                if response.status_code == 200:
                    tools.log("[ℹ] Strategy deleted: " + strat['name'])

# ----------------------
# Start of the program
# ----------------------

# Toutes les options booleenne doivent être à False par défaut donc certaines options d'origines sont inversées
parser = argparse.ArgumentParser(description='Commande line arguments override options set in config file')
parser.add_argument('-2', '--disable_2fa', help='Disable Google Authenticator Code (2FA)', action="store_true")
parser.add_argument('-a', '--accu', help='Asset to accumulate to backtest, ex: USDT')
parser.add_argument('-B', '--browser', help="Browser : chrome or firefox")
parser.add_argument('-c', '--config', help='Name of the yaml config file (default: config.yaml)')
parser.add_argument('-d', '--periods', help='Periods to backtest, period name followed by colon followed by 2 dates separated by two dots, ex: year2020:2020-01-01..2020-12-31, many periods can be separated by coma')
parser.add_argument('-D', '--delete_strats', help='Use carefully: delete all strategies that start with the given name')
parser.add_argument('-e', '--every_pairs', help='Backtest every pairs and not only recommanded pairs', action="store_true")
parser.add_argument('-E', '--email', help='E-mail of Kryll account to use')
parser.add_argument('-H', '--history', help='Append to a csv specified file each backtest processed')
parser.add_argument('-f', '--force', help='Force backtest even if it is already done', action="store_true")
parser.add_argument('-l', '--save_logs', help='Save logs to specified (absolute) directory')
parser.add_argument('-m', '--disable_marketplace', help='Disable pick strategies from marketplace randomly', action="store_true")
parser.add_argument('-o', '--open_browser', help="Open browser", action="store_true")
parser.add_argument('-p', '--pairs', help='Pairs to backtest separated by comas')
parser.add_argument('-P', '--password', help='Password of Kryll account to use')
parser.add_argument('-r', '--save_results', help='Save results to json file')
parser.add_argument('-s', '--strat_ids', help='Strategy ids to backtest separated by coma')
parser.add_argument('-S', '--my_strats', help='Strategy names to backtest separated by two comas, if value end with .kryll, load the kryll file from strategies directory')
parser.add_argument('-T', '--token', help='Backplus Token')
parser.add_argument('-u', '--upgrade_strat', help='Upgrade a strategy if needed', action="store_true")
parser.add_argument('-v', '--verbose', help='Display debug information', action="store_true")
parser.add_argument('-V', '--version', help='Version of BackPlus Script', action='version', version='BackPlusScript 2.0')
parser.add_argument('-x', '--exchanges', help='Exchanges to backtest separated by comas')

user = UserConfig(parser.parse_args())
tools = UtilityTools(user_config_file=user.config_file)
if user.config_filename != "config.yaml":
    tools.log("[ℹ] Config File: " + user.config_filename)

css = CssConst()
if "browser" in user.config_file:
    config_browser = user.config_file["browser"].lower()
else:
    config_browser = False
client_driver = tools.detect_browsers(user.config_file["headless"], config_browser)
api = Api(user_config_file=user.config_file, driver=client_driver)
sel_tools = SeleniumUtilities(user_config_file=user.config_file, driver=client_driver)
sel_tools.driver.get("https://platform.kryll.io/login")
if user.login:
    tools.log("[ℹ] Login using account: " + user.login["email"])
    sel_tools.get_element(css.EMAIL_INPUT).send_keys(user.login["email"])
    sel_tools.get_element(css.PASSWORD_INPUT).send_keys(user.login["password"])
else:
    sel_tools.get_element(css.EMAIL_INPUT).send_keys(input("email :"))
    sel_tools.get_element(css.PASSWORD_INPUT).send_keys(getpass("password :"))

if user.config_file["ask_2fa"] == "n":
    sel_tools.click_on_element(sel_tools.get_element(css.LOG_IN_BTN))
else:
    twofa = input("2FA :").lower()
    sel_tools.get_element(css.TWO_FA_INPUT).send_keys(twofa)

sel_tools.wait_for_element(css.USER_DROPDOWN, 100000)

try:
    response = json.loads(sel_tools.get_response_body('/users/auth'))
    auth_token = response['data']['auth_token']
    tools.log("[ℹ] Auth Token OK", True)
except Exception as error:
    tools.log("[❌] Can't retrieve Auth Token, please relaunch script.")
    sys.exit()

if ('command' in user.config_file) and user.config_file['command']:
    command(user.config_file['command'])
    tools.log("[ℹ] Command done :)")
    sys.exit()

if "my_strats" in user.config_file:
    strat_ids = user.config_file["my_strats"]
    run(True)
    tools.log("[ℹ] Job done :)")
    sys.exit()
else:
    if user.config_file["get_strategies_from_marketplace"] == "y":
        tools.log("[ℹ] Getting strategies from the marketplace...")
        sel_tools.driver.get("https://platform.kryll.io/marketplace/top")
        ids = sel_tools.get_elements(
            "div.col-sm-12 > app-card-strategy-user:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > h3:nth-child(1) > a:nth-child(1)"
        )
        strat_ids = []
        for strategy_id in ids:
            strat_ids.append(strategy_id.get_attribute("href").split("/")[4])
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
            tools.log("[❌] Exception occured on execution " + str(EXECUTION_ID) + " : " + str(error))
            tools.log("[❌] You can see the screenshot on this file : " + SCREENSHOT_NAME)
            tools.log("[❌] Retry...")
        end = time.time()
        elapsed = end - start
        if elapsed < 30:
            COUNT_QUICK_FAIL = COUNT_QUICK_FAIL + 1
            tools.log("[❌] Quick fail : " + str(COUNT_QUICK_FAIL) + "/3")
        else:
            COUNT_QUICK_FAIL = 0
