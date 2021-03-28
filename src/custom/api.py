import requests
from custom.selenium_utilities import SeleniumUtilities
from custom.utilities import UtilityTools
from custom.config import Config
from custom.css_const import CssConst
import datetime


class Api:
    def __init__(self, user_config, token, driver):
        self.user_config = user_config
        self.token = token
        self.driver = driver
        self.tools = UtilityTools(user_config=self.user_config)
        self.sel_tools = SeleniumUtilities(user_config=self.user_config, driver=self.driver)
        self.config = Config()
        self.css = CssConst()

    def send_result(self, send_result):
        """
        Takes a token, a pair, if strat is recommended, a strat id, a strat name, a strat version, the hold value,
        the backtest period, the backtest start date, the backtest end date
        return True if request worked else return False
        """
        advanced_analyse_link = self.sel_tools.driver.current_url
        result = self.get_advanced_result(send_result["strat_name"], send_result["pair"], send_result["backtest_date_start"], send_result["backtest_date_end"], advanced_analyse_link,)
        if result:
            url = self.config.API_SEND_URL

            result["token"] = self.token
            result["recommended"] = str(send_result["recommended"]).replace(" ", "")
            result["strat_id"] = str(send_result["strat_id"])
            result["strat_version"] = str(send_result["strat_version"])
            result["hold"] = str(send_result["hold"])
            result["exchange"] = str(send_result["exchange"])
            result["period"] = send_result["backtest_date_period"]
            self.tools.log(f"Sending result to the Database, result = {result}", True)
            response = requests.request("POST", url, data=result)

            self.tools.log(
                f"Requete post, status_code = {response.status_code}, value = {response.text}", True,
            )
            if response.status_code == 200:
                return True
        return False

    def get_backtest_dates(self, min_date):
        """
        Takes the pair, and client token, return precise periods if present in database
        """
        self.tools.log(f"Function get_backtest_dates input )", True)
        url = self.config.API_GET_PERIOD_URL + "&min_date=" + min_date + "&token=" + self.token
        url += "&global=true"
        url += "&last_three_months=true"
        response = requests.request("GET", url)
        self.tools.log(
            f"Requete get_backtest_dates, code = {response.status_code}, value = {response.text}, url= {url}", True,
        )
        if response.status_code == 200:
            response = response.json()["data"]
            self.tools.log(
                f"Function get_backtest_dates (condition response.status_code == 200) output = {response})", True,
            )
            return response
        if response.status_code == 400:
            self.tools.log(
                "Function get_backtest_dates (condition response.status_code == 400) output = [])", True,
            )
            return []
        self.tools.log(
            f"get_backtest_dates output (condition other) error = (code = {response.status_code}, value = {response.text}, url= {url})", True,
        )
        return -1

    def backtest_already_did(self, pair, period, strat, version, exchange):
        """
        Takes the pair,the period,the strat,and client token, return if backtest present in database
        """
        self.tools.log(
            f"Function backtest_already_did input (pair ={pair}, period = {period}, exchange = {exchange}, strat= {strat}, version= {version})", True,
        )
        pair = pair.replace(" ", "")
        url_backtest_already_did = (
            self.config.API_CHECK_BACKTEST_URL + "&strat=" + strat + "&version=" + version + "&pair=" + pair + "&period=" + period + "&exchange=" + exchange + "&token=" + self.token
        )
        response = requests.request("GET", url_backtest_already_did)
        self.tools.log(
            f"Requete backtest_already_did, status_code = {response.status_code}, value = {response.text}, url= {url_backtest_already_did}", True,
        )
        if response.status_code == 200:
            self.tools.log("Please Wait...")
            return False
        self.tools.log("Already tested, next")
        return True

    def backtest_has_failed(self, pair, period, strat, version, exchange, start_date, end_date):
        """
        Takes the pair,the period,the strat,and client token, return if backtest has already failed
        """
        self.tools.log(
            f"Function backtest_has_failed input (pair ={pair}, period = {period}, exchange = {exchange}, start_date = {start_date}, end_date = {end_date}, strat= {strat}, strat_version= {version})", True,
        )
        pair = pair.replace(" ", "")
        url_backtest_has_failed = (
            self.config.API_BACKTEST_HAS_FAILED_URL + "&strat=" + strat + "&strat_version=" + version + "&pair=" + pair + "&period=" + period + "&exchange=" + exchange + "&start_date=" + start_date + "&end_date=" + end_date + "&token=" + self.token
        )
        response = requests.request("GET", url_backtest_has_failed)
        self.tools.log(
            f"Requete backtest_has_failed, status_code = {response.status_code}, value = {response.text}, url= {url_backtest_has_failed}", True,
        )
        if response.status_code == 200:
            self.tools.log("Already failed, next")
            return True
        return False

    def backtest_add_failed(self, pair, period, strat, version, exchange, start_date, end_date):
        """
        Takes the pair,the period,the strat,and client token,
        increase fail for this backtest in database
        return True if request success, false if failed
        """
        self.tools.log(
            f"Function backtest_add_failed input (pair ={pair}, period = {period}, exchange = {exchange}, start_date = {start_date}, end_date = {end_date}, strat= {strat}, strat_version= {version})", True,
        )
        pair = pair.replace(" ", "")
        
        post_data = {}
        post_data["strat"] = strat
        post_data["strat_version"] = version
        post_data["pair"] = pair
        post_data["period"] = period
        post_data["exchange"] = exchange
        post_data["start_date"] = start_date
        post_data["end_date"] = end_date
        post_data["token"] = self.token
        response = requests.request("POST", self.config.API_BACKTEST_ADD_FAILED_URL, data=post_data)
        self.tools.log(
            f"Requete backtest_add_failed, status_code = {response.status_code}, value = {response.text}, url= {self.config.API_BACKTEST_ADD_FAILED_URL}", True,
        )
        if response.status_code == 200:
            return True
        return False

    def get_advanced_result(
        self, strat_name, pair, backtest_date_start, backtest_date_end, advanced_analyse_link,
    ):
        """
        Takes a strat name, a pair, a backtest start date, a backtest end date and the analyse link
        return dict of results
        """
        result = {}
        try :
            result["trade"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_TRADE)
            result["strat"] = strat_name
            result["pair"] = pair
            result["start"] = backtest_date_start
            result["end"] = backtest_date_end
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
            end_date = advanced_analyse_dates.split(' — ')[1]
            end_date_kryll_side = datetime.datetime(int(end_date.split('-')[2]), int(end_date.split('-')[0]), int(end_date.split('-')[1]))
            api_date_end = datetime.datetime(int(backtest_date_end.split('-')[0]), int(backtest_date_end.split('-')[1]), int(backtest_date_end.split('-')[2]))
            if end_date_kryll_side < api_date_end:
                self.tools.log("==============================================")
                self.tools.log("invalid deep analysis.")
                self.tools.log("Backtest seems to be interrupt by other backtest on the same time")
                self.tools.log(f"results : {result}")
                self.tools.log("==============================================")
                return False
            self.tools.log(f"results : {result}")
            return result
        except Exception as e:
            self.tools.log("==============================================")
            self.tools.log("invalid deep analysis.")
            self.tools.log(f"results : {result}")
            self.tools.log("==============================================")
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