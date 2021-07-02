import datetime
import sys
import time
import requests
import json
from pprint import pprint
from yaml import tokens
from custom.selenium_utilities import SeleniumUtilities
from custom.utilities import UtilityTools
from custom.config import Config
from custom.css_const import CssConst


class Api:
    def __init__(self, user_config_file, driver):
        self.user_config_file = user_config_file
        self.driver = driver
        self.token = self.user_config_file["token"]
        self.tools = UtilityTools(user_config_file=self.user_config_file)
        self.sel_tools = SeleniumUtilities(user_config_file=user_config_file, driver=self.driver)
        self.config = Config()
        self.css = CssConst()

    def log_response(self, method, url, data, response):
        self.tools.log(
            f"[ℹ][{method}][Request][URL] : {url}",
            True,
        )
        self.tools.log(
            f"[ℹ][{method}][data] : {data}",
            True,
        )
        self.tools.log(
            f"[ℹ][{method}][Response] : {response}",
            True,
        )

    def send_request(self, method, url, data=False):
        """
        Generic function to send request
        """
        response = False
        retry = 1
        success = False
        url = url + "&api_version=" + self.config.API_VERSION
        while success is False and retry < 5:
            try:
                if method.upper() == "GET":
                    response = requests.get(url, params=data)
                else:
                    response = requests.post(url, data=data)
                if response.status_code == 501 and response.reason == "not supported version":
                    self.log_response("send_request", url, data, response)
                    self.tools.log("[❌] Votre version n'est plus à jour, veuillez télécharger la nouvelle version.")
                    input("Appuyez sur une touche pour quitter")
                    sys.exit()
                elif response.status_code == 503 and response.reason == "maintenance":
                    self.tools.log("[⚠] Maintenance de l'API en cours, veuillez patienter...")
                    time.sleep(300)
                elif response.status_code in (500, 404):
                    self.tools.log("[⚠] Impossible d'envoyer la requête en raison d'un problème serveur. Nouvelle tentative dans 5 minutes...")
                    time.sleep(300)
                else:
                    success = True
                    self.log_response("send_request", url, data, response)
            except Exception as error:
                self.tools.log("[❌] " + str(error), True)
                self.tools.log("[⚠] Retry " + str(retry), True)
                time.sleep(2)
                retry = retry + 1
        if retry == 5:
            self.tools.log("[❌] Unable to send the request")
        return response

    def  send_result(self, backtest_config, send_result):
        """
        Takes a token, a pair, if strategy is recommended, a strategy id, a strategy name, a strategy version, the hold value,
        the backtest period, the backtest start date, the backtest end date
        return True if request worked else return False
        """
        advanced_analyse_link = self.sel_tools.driver.current_url
        result = self.get_advanced_result(backtest_config, advanced_analyse_link, send_result["hold"])
        if result:
            self.user_config_file
            if ("my_strats" in self.user_config_file) or ("save_results" in self.user_config_file):
                filename = self.user_config_file['save_results'] + result['strat']+'_v'+result['strat_version']+'_'+(result["pair"].replace('/', '-'))+'@'+result["exchange"]+'_'+result["start"]+'_'+result["end"] + '.json';
                self.tools.log("[ℹ] Saving results to file: " + filename, True)
                try:
                    with open(filename, 'w') as fp:
                        dump_result = result
                        del dump_result['token']
                        json.dump(dump_result, fp)
                        self.tools.log("[ℹ] Results saved to file: " + filename, True)
                except Exception as error:
                    self.tools.log("[❌] Fail saving results to file")
                    self.tools.log("[❌] " + str(error), True)
            #if ("disable_send" not in self.user_config_file) or (self.user_config_file["disable_send"] != "y"):
            if not ("my_strats" in self.user_config_file) and not ("periods" in self.user_config_file) :
                url = self.config.API_SEND_URL
                self.tools.log(f"[ℹ] Sending result to the Database, result = {result}", True)
                response = self.send_request("POST", url, data=result)
                if response is not False and response.status_code == 200:
                    return True
            else:
                self.tools.log(f"[❌] Sending result to the Database disabled in config, result = {result}", True)
                return True
        return False

    def get_backtest_dates(self, min_date, backtest_config):
        """
        Takes the pair, and client token, return precise periods if present in database
        """
        self.tools.log(f"[ℹ] ({backtest_config.toString()})", True)
        url = self.config.API_GET_PERIOD_URL

        data = {}
        data["min_date"] = min_date
        data["strat_id"] = backtest_config.getStratId()
        data["strat_name"] = backtest_config.getStratName()
        data["strat_version"] = backtest_config.getStratVersion()
        data["pair"] = backtest_config.getPair()
        data["exchange"] = backtest_config.getExchange()
        data["token"] = self.token
        response = self.send_request("GET", url, data)
        if response is not False and response.status_code == 200:
            response = response.json()["data"]
            self.tools.log("[ℹ] **************************************")
            self.tools.log("[ℹ] *        Dates to backtest           *")
            self.tools.log("[ℹ] **************************************")
            for i in response:
                self.tools.log(f"[ℹ] * {i['period']} from {i['start']} to {i['end']}")
            return response
        if response is not False and response.status_code == 400:
            self.tools.log("[ℹ] No dates to backtest, next.", False)
            return []
        return []

    def backtest_already_did(self, backtest_config):
        """
        Takes the pair,the period,the strategy,and client token, return if backtest present in database
        """
        self.tools.log(
            f"[ℹ] ({backtest_config.toString()})",
            True,
        )
        url_backtest_already_did = self.config.API_CHECK_BACKTEST_URL
        data = {}
        data["strat_id"] = backtest_config.getStratId()
        data["strat"] = backtest_config.getStratName()
        data["version"] = backtest_config.getStratVersion()
        data["pair"] = backtest_config.getPair().replace(" ", "")
        data["period"] = backtest_config.getPeriod()
        data["exchange"] = backtest_config.getExchange()
        data["start_date"] = backtest_config.getStart()
        data["end_date"] = backtest_config.getEnd()
        data["token"] = self.token
        response = self.send_request("GET", url_backtest_already_did, data)
        if response is not False and response.status_code == 200:
            self.tools.log("[ℹ] Can be tested", True)
            return False
        self.tools.log("[ℹ] Already tested, next")
        return True

    def backtest_has_failed(self, backtest_config):
        """
        Takes the pair,the period,the strategy,and client token, return if backtest has already failed
        """
        self.tools.log(
            f"[ℹ] ({backtest_config.toString()})",
            True,
        )
        url_backtest_has_failed = self.config.API_BACKTEST_HAS_FAILED_URL
        data = {}
        data["strat_id"] = backtest_config.getStratId()
        data["strat"] = backtest_config.getStratName()
        data["version"] = backtest_config.getStratVersion()
        data["pair"] = backtest_config.getPair().replace(" ", "")
        data["period"] = backtest_config.getPeriod()
        data["exchange"] = backtest_config.getExchange()
        data["start_date"] = backtest_config.getStart()
        data["end_date"] = backtest_config.getEnd()
        data["token"] = self.token
        response = self.send_request("GET", url_backtest_has_failed, data)
        if response is not False and response.status_code == 200:
            self.tools.log("[⚠] Already failed, next")
            return True
        return False

    def backtest_add_failed(self, backtest_config, log):
        """
        Takes the pair,the period,the strategy,and client token,
        increase fail for this backtest in database
        return True if request success, false if failed
        """
        self.tools.log(
            f"Function backtest_add_failed input ({backtest_config.toString()})",
            True,
        )
        post_data = {}
        post_data["strat_id"] = backtest_config.getStratId()
        post_data["strat"] = backtest_config.getStratName()
        post_data["version"] = backtest_config.getStratVersion()
        post_data["pair"] = backtest_config.getPair().replace(" ", "")
        post_data["period"] = backtest_config.getPeriod()
        post_data["exchange"] = backtest_config.getExchange()
        post_data["start_date"] = backtest_config.getStart()
        post_data["end_date"] = backtest_config.getEnd()
        post_data["token"] = self.token
        post_data["log"] = log
        response = self.send_request("POST", self.config.API_BACKTEST_ADD_FAILED_URL, data=post_data)
        if response is not False and response.status_code == 200:
            return True
        return False

    def get_advanced_result(self, backtest_config, advanced_analyse_link, hold):
        """
        Takes a strategy name, a pair, a backtest start date, a backtest end date and the analyse link
        return dict of results
        """
        result = {}
        result["hold"] = hold
        result["token"] = self.token
        result["recommended"] = backtest_config.getRecommended()
        result["strat"] = str(backtest_config.getStratName())
        result["strat_id"] = str(backtest_config.getStratId())
        result["strat_version"] = str(backtest_config.getStratVersion())
        result["exchange"] = str(backtest_config.getExchange())
        result["pair"] = str(backtest_config.getPair()).replace(" ", "")
        result["period"] = backtest_config.getPeriod()
        try:
            result["trade"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_TRADE)
            result["start"] = backtest_config.getStart()
            result["end"] = backtest_config.getEnd()
            result["link"] = advanced_analyse_link.split("=")[1]
            result["duration"] = self.sel_tools.get_element_days(self.css.ADVANCED_ANALYSE_DURATION)
            result["volatility"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_VOLATILITY)
            result["start_wallet"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_START_WALLET)
            result["stop_wallet"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_END_WALLET)
            result["gain"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_GAIN)
            result["relative_gain"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_RELATIVE_GAIN)
            result["winning_periods"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_WINNING_PERIOD).split(" ")[0]
            result["losing_periods"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_LOSING_PERIOD).split(" ")[0]
            result["average_win"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_AVERAGE_WIN)
            result["average_loss"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_AVERAGE_LOSS)
            result["wallet_average_investment"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_WALLET_AVERAGE_INVESTMENT)
            result["wallet_maximum_investment"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_WALLET_MAXIMUM_INVESTMENT)
            result["win_loss_ratio"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_WIN_LOSS_RATIO).replace("/", ":")
            result["risk_reward_ratio"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_RISK_REWARD_RATIO)
            result["expected_return"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_EXPECTED_RETURN)
            result["sharpe_ratio"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_SHARPE_RATIO)
            result["sortino_ratio"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_SORTINO_RATIO)
            result["risk_of_drawdown"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_RISK_OF_DRAWDOWN)
            if result["risk_of_drawdown"] == "<0.01":
                result["risk_of_drawdown"] = 0

            max_drawdown_informations = self.__split_max_drawdown_informations(self.css.ADVANCED_ANALYSE_MAX_DRAWDOWN_INFORMATIONS)
            result["maximum_drawdown"] = max_drawdown_informations["maximum_drawdown"]
            result["maximum_drawdown_start"] = max_drawdown_informations["maximum_drawdown_start"]
            result["maximum_drawdown_end"] = max_drawdown_informations["maximum_drawdown_end"]
            result["average_drawdown"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_AVERAGE_DRAWDOWN)

            # check if date_end on analysis is the same as date end backtested
            advanced_analyse_dates = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_DATES)
            start_date = advanced_analyse_dates.split(" — ")[0]
            start_date_kryll_side = datetime.datetime(int(start_date.split("-")[2]), int(start_date.split("-")[0]), int(start_date.split("-")[1]))
            api_date_start = datetime.datetime(int(result["start"].split("-")[0]), int(result["start"].split("-")[1]), int(result["start"].split("-")[2]))
            end_date = advanced_analyse_dates.split(" — ")[1]
            end_date_kryll_side = datetime.datetime(int(end_date.split("-")[2]), int(end_date.split("-")[0]), int(end_date.split("-")[1]))
            api_date_end = datetime.datetime(int(result["end"].split("-")[0]), int(result["end"].split("-")[1]), int(result["end"].split("-")[2]))

            days_kryll_side = self._get_number_of_days(start_date_kryll_side, end_date_kryll_side)
            days_api_side = self._get_number_of_days(api_date_start, api_date_end)
            diff = abs(days_kryll_side - days_api_side)

            # If date end on deep analysis < date end required, the backtest was interrupt
            if end_date_kryll_side < api_date_end:
                self.tools.log("[❌] invalid deep analysis.")
                self.tools.log("[❌] Backtest seems to be interrupt by other backtest on the same time")
                self.tools.log(f"[❌] {result}", True)
                return False

            # If more than 2 days on deep analysis period, error occurs
            if diff > 2:
                self.tools.log(f"[❌] {diff} days difference between required period and deep analysis period. Canceled.")
                self.tools.log(f"[❌] {result}", True)
                return False

            self.tools.log(f"[ℹ] {result}", True)
            return result
        except Exception:
            self.tools.log("[❌] invalid deep analysis.")
            self.tools.log(f"[❌] results : {result}", True)
        return False

    def __split_max_drawdown_informations(self, element_path):
        """
        Takes a css class, return list of DD informations
        """
        max_drawdown_informations = {}
        max_drawdown_informations["maximum_drawdown"] = self.sel_tools.get_element_text(element_path).split(" %\n")[0]
        max_drawdown_dates = self.sel_tools.get_element_text(element_path).split(" %\n")[1].split(" — ")
        max_drawdown_informations["maximum_drawdown_start"] = self.tools.convert_date_to_api(max_drawdown_dates[0])
        max_drawdown_informations["maximum_drawdown_end"] = self.tools.convert_date_to_api(max_drawdown_dates[1])
        return max_drawdown_informations

    @staticmethod
    def _get_number_of_days(date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""
        timedelta = date_to - date_from
        diff_day = timedelta.days
        return diff_day
