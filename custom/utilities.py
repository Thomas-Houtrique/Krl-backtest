"""Module containing utility tools"""
from datetime import datetime
import os
import platform
from selenium import webdriver
from custom.css_const import CssConst


class UtilityTools:
    """Class containing utility tools"""

    def __init__(self, user_config):
        self.css = CssConst()
        self.user_config = user_config

    def convert_date_to_api(self, date):
        """
        Takes date format Year-Month-Day, return date format Month/Day/Year
        """
        self.log(f"Function convert date input = {date}", True)
        dto = datetime.strptime(date, "%m/%d/%Y").date()
        dto = str(dto.strftime("%Y-%m-%d"))
        self.log(f"Function convert date output = {dto}", True)
        return dto

    def convert_date_to_html(self, date):
        """
        Takes date format Year-Month-Day, return date format Month/Day/Year
        """
        self.log(f"Function convert date input = {date}", True)
        dto = datetime.strptime(date, "%Y-%m-%d").date()
        dto = str(dto.strftime("%m/%d/%Y"))
        self.log(f"Function convert date output = {dto}", True)
        return dto

    def log(self, log_text, verbose=False):
        """
        Takes a log_text and a verbose boolean, print the log and save it to a log file
        """
        log_formated_string = datetime.now().strftime("%d %B %Y %H:%M:%S -> ") + log_text
        log_file = open("Kryll_backtest.log", "a+", encoding="utf-8")
        log_file.write(log_formated_string + "\n")
        log_file.close()
        if (self.user_config["verbose"] == "y" and verbose) or not verbose:
            print(log_formated_string)

    def detect_browsers(self):
        """
        Takes the client os, return the correct driver according to client browsers
        """
        client_os = platform.system()
        browsers = []
        if client_os == "Windows":
            if os.environ["ProgramFiles"] + r"\Mozilla Firefox":
                self.log("Firefox detected")
                browsers.append("Firefox")
            if os.environ["ProgramFiles"] + r"\Google\Chrome\Application":
                self.log("Chrome detected")
                browsers.append("Google Chrome")
        elif client_os == "Linux":
            raise Exception("Sorry, linux is not supported yet")

        if len(browsers) > 1:
            for idx, browser in enumerate(browsers):
                print(f"{idx}) {browser}")
            browser_choice = int(input(f"please choice between your browsers (0 to {len(browsers) - 1})"))
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

    def ask_strat(self):
        """
        Ask the user for strat id
        """
        strat_ids = []
        strat_id = str(input("Enter a strat id (ex 5f9f0342dd6ac25bd05cf515) :"))
        strat_ids.append(strat_id)
        while strat_id != "":
            self.log("Do you want to test an other strat? (empty to next)")
            strat_id = input("Enter a strat id (ex 5f9f0342dd6ac25bd05cf515) :")
            if strat_id != "":
                strat_ids.append(strat_id)
        return strat_ids
