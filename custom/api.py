import requests
from custom.selenium_utilities import SeleniumUtilities
from custom.utilities import UtilityTools
from custom.config import Config
from custom.css_const import CssConst


class Api:
    def __init__(self, user_config, token, driver):
        self.user_config = user_config
        self.token = token
        self.driver = driver
        self.tools = UtilityTools(user_config=self.user_config)
        self.sel_tools = SeleniumUtilities(user_config=self.user_config, driver=self.driver)
        self.config = Config()
        self.css = CssConst()

    def send_result(self, result_send_result):
        """
        Takes a token, a pair, if strat is recommended, a strat id, a strat name, a strat version, the hold value,
        the backtest period, the backtest start date, the backtest end date
        return True if request worked else return False
        """
        advanced_analyse_link = self.sel_tools.driver.current_url
        result = self.get_advanced_result(
            result_send_result["strat_name"],
            result_send_result["pair"],
            result_send_result["backtest_date_start"],
            result_send_result["backtest_date_end"],
            advanced_analyse_link,
        )
        url = Config.API_SEND_URL

        result["token"] = result_send_result["token"]
        result["recommended"] = str(result_send_result["recommended"]).replace(" ", "")
        result["strat_id"] = str(result_send_result["strat_id"])
        result["strat_version"] = str(result_send_result["strat_version"])
        result["hold"] = str(result_send_result["hold"])
        result["period"] = result_send_result["backtest_date_period"]
        self.tools.log(f"Sending result to the Database, result = {result}", True)
        response = requests.request("POST", url, data=result)

        self.tools.log(
            f"Requete post, status_code = {response.status_code}, value = {response.text}",
            True,
        )
        if response.status_code == 200:
            return True
        return False

    def get_backtest_dates(self, pair_backtest_dates, min_date_backtest_dates):
        """
        Takes the pair, and client token, return precise periods if present in database
        """
        self.tools.log(f"Function get_backtest_dates input (test_pair ={pair_backtest_dates})", True)
        url = Config.API_GET_PERIOD_URL + "&pair=" + pair_backtest_dates.replace(" ", "") + "&min_date=" + min_date_backtest_dates + "&token=" + self.token
        if self.user_config["global"] == "y":
            url += "&global=true"
        if self.user_config["recently"] == "y":
            url += "&recently=true"
        if self.user_config["last_year"] == "y":
            url += "&last_year=true"
        if self.user_config["other"] == "y":
            url += "&other=true"
        response = requests.request("GET", url)
        self.tools.log(
            f"Requete get_backtest_dates, code = {response.status_code}, value = {response.text}, url= {url}",
            True,
        )
        if response.status_code == 200:
            response = response.json()["data"][pair_backtest_dates.replace(" / ", "/")]
            self.tools.log(
                f"Function get_backtest_dates (condition response.status_code == 200) output = {response})",
                True,
            )
            return response
        if response.status_code == 400:
            self.tools.log(
                "Function get_backtest_dates (condition response.status_code == 400) output = [])",
                True,
            )
            return []
        self.tools.log(
            f"get_backtest_dates output (condition other) error = (code = {response.status_code}, value = {response.text}, url= {url})",
            True,
        )
        return -1

    def backtest_already_did(self, pair_already_did, period_already_did, strat_already_did):
        """
        Takes the pair,the period,the strat,and client token, return if backtest present in database
        """
        self.tools.log(
            f"Function backtest_already_did input (pair ={pair_already_did}, period = {period_already_did}, strat= {strat_already_did})",
            True,
        )
        pair_already_did = pair_already_did.replace(" ", "")
        url_backtest_already_did = Config.API_CHECK_BACKTEST_URL + "&strat=" + strat_already_did + "&pair=" + pair_already_did + "&period=" + period_already_did + "&token=" + self.token
        response = requests.request("GET", url_backtest_already_did)
        self.tools.log(
            f"Requete backtest_already_did, status_code = {response.status_code}, value = {response.text}, url= {url_backtest_already_did}",
            True,
        )
        if response.status_code == 200:
            self.tools.log("Please Wait...")
            return False
        self.tools.log("Already tested, next")
        return True

    def get_advanced_result(
        self,
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
        result["duration"] = self.sel_tools.get_element_days(self.css.ADVANCED_ANALYSE_DURATION)
        result["volatility"] = self.sel_tools.get_element_percent(self.css.ADVANCED_ANALYSE_VOLATILITY)
        result["trade"] = self.sel_tools.get_element_text(self.css.ADVANCED_ANALYSE_TRADE)
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
        return result

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
