"""Module containing utility tools"""
from datetime import datetime
import os
import platform
import tempfile
from seleniumwire import webdriver
from custom.css_const import CssConst
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class UtilityTools:
    """Class containing utility tools"""
    temp_file = False

    def __init__(self, user_config, user_config_file):
        self.css = CssConst()
        self.user_config = user_config
        self.user_config_file = user_config_file
    
    def get_log_file_name(self):
        if not os.path.exists('logs'):
            os.makedirs('logs')        
        if UtilityTools.temp_file == False or UtilityTools.temp_file[20:-11] != datetime.now().strftime("%Y_%m_%d"):
            UtilityTools.temp_file = "BackPlusScript_Logs_" + datetime.now().strftime("%Y_%m_%d_%H%M%S") + ".log"
        return UtilityTools.temp_file

    def convert_date_to_api(self, date):
        """
        Takes date format Year-Month-Day, return date format Month/Day/Year
        """
        self.log(f"[ℹ] Function convert date input = {date}", True)
        dto = datetime.strptime(date, "%m/%d/%Y").date()
        dto = str(dto.strftime("%Y-%m-%d"))
        self.log(f"[ℹ] Function convert date output = {dto}", True)
        return dto

    def convert_date_to_html(self, date):
        """
        Takes date format Year-Month-Day, return date format Month/Day/Year
        """
        self.log(f"[ℹ] Function convert date input = {date}", True)
        dto = datetime.strptime(date, "%Y-%m-%d").date()
        dto = str(dto.strftime("%m/%d/%Y"))
        self.log(f"[ℹ] Function convert date output = {dto}", True)
        return dto

    def log(self, log_text, verbose=False):
        """
        Takes a log_text and a verbose boolean, print the log and save it to a log file
        """
        if self.user_config_file["token"] in log_text:
            log_text = log_text.replace(self.user_config_file["token"], "REDACTED TOKEN")
        log_formated_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S ") + log_text
        log_file = open('logs/' + self.get_log_file_name(), "a+", encoding="utf-8")
        log_file.write(log_formated_string + "\n")
        log_file.close()
        if (self.user_config["verbose"] == "y" and verbose) or not verbose:
            print(log_formated_string)

    def detect_browsers(self, headless="n", config_browser=False):
        """
        Takes the client os, return the correct driver according to client browsers
        """
        client_os = platform.system()
        browsers = []
        if client_os == "Windows":
            if os.environ["ProgramFiles"] + r"\Mozilla Firefox":
                self.log("[ℹ] Firefox detected")
                browsers.append("Firefox")
            if os.environ["ProgramFiles"] + r"\Google\Chrome\Application":
                self.log("[ℹ] Chrome detected")
                browsers.append("Google Chrome")
            if len(browsers) > 1:
                browser_choice = None
                if config_browser :
                    if config_browser == "firefox":
                        browser_choice = 0
                    if config_browser == "chrome":
                        browser_choice = 1
                if browser_choice is None:
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
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--mute-audio")
                if headless == "y":
                    options.add_argument("--start-maximized")
                    options.add_argument("disable-infobars")
                    options.add_argument("--disable-extensions")
                    options.add_argument("window-size=1920x1080")
                    options.set_headless()
                driver = webdriver.Chrome(executable_path=r"chromedriver.exe", options=options)
            elif client_browser == "Firefox":
                firefox_options = FirefoxOptions()
                if headless == "y":
                    firefox_options.headless = True
                driver = webdriver.Firefox(executable_path=r"geckodriver.exe", options=firefox_options)
            return driver

        elif client_os == "Linux":
            self.log("[⚠] Please make sure to have Chromium installed")
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--mute-audio")
            if headless == "y":
                options.add_argument("--start-maximized")
                options.add_argument("disable-infobars")
                options.add_argument("--disable-extensions")
                options.add_argument("window-size=1920x1080")
                options.set_headless()
            driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", options=options)
            return driver

        elif client_os == "Darwin":
            self.log("[⚠] Please make sure to have Firefox installed")

            firefox_options = FirefoxOptions()
            if headless == "y":
                firefox_options.headless = True
            driver = webdriver.Firefox(executable_path=r"./geckodriver", options=firefox_options)
            return driver

    def ask_strat(self):
        """
        Ask the user for strategy id
        """
        strat_ids = []
        strat_id = str(input("Enter a strategy id (ex 5f9f0342dd6ac25bd05cf515) :"))
        strat_ids.append(strat_id)
        while strat_id != "":
            self.log("Do you want to test an other strategy? (empty to next)")
            strat_id = input("Enter a strategy id (ex 5f9f0342dd6ac25bd05cf515) :")
            if strat_id != "":
                strat_ids.append(strat_id)
        return strat_ids
