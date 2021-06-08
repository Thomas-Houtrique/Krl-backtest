import time
from tqdm import tqdm
from selenium.common.exceptions import NoSuchElementException
from custom.utilities import UtilityTools
from custom.errors import ElementNotFound
from custom.css_const import CssConst
import os


class SeleniumUtilities:
    def __init__(self, user_config_file, driver):
        self.css = CssConst()
        self.tools = UtilityTools(user_config_file=user_config_file)
        self.driver = driver

    def get_element(self, element_path, duration=10):
        """
        Takes a css class, return selenium element
        """
        element = self.wait_for_element(element_path, duration)
        if element:
            return element
        raise ElementNotFound(element_path)

    def get_elements(self, elements_path, duration=10):
        """
        Takes a css class,return list of ele
        """
        elements = self.wait_for_element(elements_path, duration, True)
        if elements:
            return elements
        raise ElementNotFound(elements_path)

    def get_element_text(self, element_path, duration=10):
        """
        Takes a selenium element,return element text
        """
        element = self.get_element(element_path, duration)
        return element.text

    def get_element_double(self, element_path, duration=10):
        """
        Takes a css class, return str with "+" replaced by void
        """
        element = self.get_element_text(element_path, duration)
        return element.replace("+", "")

    def get_element_percent(self, element_path, duration=10):
        """
        Takes a css class, return str with " %" replaced by void
        """
        element = self.get_element_text(element_path, duration)
        return element.replace(" %", "").replace("%", "")

    def get_element_days(self, element_path, duration=10):
        """
        Takes a css class, return str with " days" replaced by void
        """
        element = self.get_element_text(element_path, duration)
        return element.replace(" days", "")

    def check_error_during_backtest(self):
        """
        Check if backtest broke return True if Bt broke and False if not
        """
        # ugly method to detect if there is an error or end page
        i = 0
        pbar = tqdm(range(100), dynamic_ncols=True)
        analyse_tab = False
        backtest_start_btn = False
        for _ in range(0, 10000):
            if i != 0:
                self.refresh_pbar(pbar)
            i = i + 10
            time.sleep(10)
            try:
                backtest_start_btn = self.get_element_text(self.css.BACKTEST_START_BTN)
                if backtest_start_btn and backtest_start_btn == "Test":
                    # Check if analysis tab is open
                    analyse_tab = self.get_elements(self.css.ANALYSE_TAB_DEEP_ANALYSE_LINK)
                    if analyse_tab:
                        self.refresh_pbar(pbar, 100)
                        pbar.close()
                        return False
                    # If btn test is active, but analyse tab no, we have an error
                    self.tools.log(f"[ℹ] {self.get_element_text(self.css.PROGRESS_PERCENT).rjust(20, '.')}")
                    self.tools.log("[❌] Error during the backtest")
                    self.tools.log("[❌] i={i}, analyse_tab={analyse_tab}, backtest_start_btn={backtest_start_btn}", True)
                    try:
                        self.tools.log(self.get_element_text(self.css.LOGS_LAST_LINE))
                    except Exception:
                        pbar.close()
                    self.refresh_pbar(pbar)
                    pbar.close()
                    return True
            except Exception:
                pbar.close()
                break
        pbar.close()
        self.tools.log("[❌] Error during the backtest")
        self.tools.log("[❌] i={i}, analyse_tab={analyse_tab}, backtest_start_btn={backtest_start_btn}", True)
        try:
            self.tools.log(self.get_element_text(self.css.LOGS_LAST_LINE))
        except Exception:
            pass
        return True

    def refresh_pbar(self, pbar, value=False):
        pbar.clear()
        if value is False:
            percent = int(self.get_element_percent(self.css.PROGRESS_PERCENT))
            pbar.update(percent - pbar.n)
            pbar.refresh()
        else:
            pbar.update(value - pbar.n)
            pbar.refresh()

    def check_if_element_exist(self, element_path, multiple=False):
        """
        Check if an element existe in DOM. return True or False
        """
        try:
            if multiple:
                return self.driver.find_elements_by_css_selector(element_path)
            return self.driver.find_element_by_css_selector(element_path)
        except NoSuchElementException:
            return False

    def wait_for_element(self, element_path, duration, multiple=False):
        """
        Takes a selenium element and a duration, return element if element detected and False if not
        """
        for i in range(0, duration):
            element = self.check_if_element_exist(element_path, multiple)
            if element:
                return element
            self.tools.log(f"[ℹ] can't find element {element_path} retry {i+1}/10", verbose=True)
            time.sleep(1)
        return False

    @staticmethod
    def wait_for_attribute_value(element, attribute, duration=10):
        """
        Takes a selenium element and a duration, return attribute value when attribute value is not empty
        """
        for _ in range(0, duration):
            attribute_value = element.get_attribute(attribute)
            if attribute_value != "":
                return attribute_value
            time.sleep(1)
        return ""

    def wait_network_calls_loaded(self, duration=False, path=False):
        if duration:
            time.sleep(duration)
        if path:
            self.driver.wait_for_request(path, 90)
            return True
        new_requests = True
        while new_requests:
            request_counter = len(self.driver.requests)
            for request in self.driver.requests:
                self.driver.wait_for_request(request.path, 90)
            if request_counter == len(self.driver.requests):
                new_requests = False
        return True

    def wait_network_call_start(self, pattern, duration=10):
        return self.driver.wait_for_request(pattern, duration)

    def clean_network_calls(self):
        del self.driver.requests
        return True

    def wait_for_pair_loaded(self, previous_balance_button, duration=10):
        for _ in range(0, duration):
            if self.get_element_text(self.css.BALANCE_BUTTON, 1) != previous_balance_button:
                return True
        return False

    def wait_for_windows_handle(self, duration):
        """
        Takes a duration, return True if more than 1 window else return False
        """
        for _ in range(0, duration):
            if len(self.driver.window_handles) > 1:
                return True
            time.sleep(1)
        return False

    def check_if_popup(self, duration=10):
        """
        Check if tutorial popup is present on the screen
        """
        try:
            popup = self.get_element(self.css.POPUP, duration)
            popup.click()
        except Exception:
            pass

    def check_if_server_problem(self):
        """
        Check if tutorial popup is present on the screen
        """
        try:
            server_problem = self.get_element(self.css.SERVER_PROBLEM)
            self.click_on_element(server_problem)
        except Exception:
            pass

    def count_tabs_opened(self):
        """
        Count how many tabs are opened
        """
        return len(self.driver.window_handles)

    def close_unused_tabs(self):
        """
        Close unused tabs and let just the first tab
        """
        count_tabs = self.count_tabs_opened()
        if count_tabs > 1:  # Will execute if more than 1 tabs found.
            for i in range(count_tabs - 1, 0, -1):
                self.driver.switch_to.window(self.driver.window_handles[i])  # will close the last tab first.
                self.driver.close()
                self.tools.log("[ℹ] Closed Tab No", i)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switching the driver focus to First tab.
        else:
            self.tools.log("[ℹ] Found only Single tab.", True)

    def refresh(self):
        """
        Refresh current tab
        """
        self.clean_network_calls()
        self.driver.refresh()
        self.wait_network_calls_loaded()

    def click_on_element(self, element, wait=False):
        """
        Click on element
        """
        self.clean_network_calls()
        try:
            element.click()
        except Exception:
            self.check_if_popup(10)
            element.click()
        if wait:
            time.sleep(5)
            self.wait_network_calls_loaded()

    def save_screenshot(self, filename):
        """
        Save a screenshot of page
        """
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        self.driver.set_window_size(1920, 1080)  # the trick
        self.driver.save_screenshot("screenshots/" + filename)

    def get(self, url):
        self.driver.get(url)
        self.clean_network_calls()
