import time
from custom.utilities import UtilityTools
from custom.errors import ElementNotFound
from selenium.common.exceptions import NoSuchElementException
from custom.css_const import CssConst


class SeleniumUtilities:
    def __init__(self, user_config, driver):
        self.user_config = user_config
        self.css = CssConst()
        self.tools = UtilityTools(user_config=self.user_config)
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
        return element.replace(" %", "")

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
        for _ in range(0, 1000):
            time.sleep(10)
            try :
                backtest_start_btn = self.get_element_text(self.css.BACKTEST_START_BTN)
                if backtest_start_btn and backtest_start_btn == "Test":
                    # Check if analysis tab is open
                    analyse_tab = self.get_elements(self.css.ANALYSE_TAB_DEEP_ANALYSE_LINK)
                    if analyse_tab:
                        return False
                    # If btn test is active, but analyse tab no, we have an error
                    self.tools.log("Error during the backtest")
                    try :
                        self.tools.log(self.get_element_text(self.css.LOGS_LAST_LINE))
                    except :
                        pass
                    return True
            except :
                break
        self.tools.log("Error during the backtest")
        try :
            self.tools.log(self.get_element_text(self.css.LOGS_LAST_LINE))
        except :
            pass
        return True

        """
        Check if an element existe in DOM. return True or False
        """

    def check_if_element_exist(self, element_path, multiple=False):
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
            self.tools.log(f"can't find element {element_path} retry {i+1}/10", verbose=True)
            time.sleep(1)
        return False

    def wait_for_attribute_value(self, element, attribute, duration=10):
        """
        Takes a selenium element and a duration, return attribute value when attribute value is not empty
        """
        for i in range(0, duration):
            attribute_value = element.get_attribute(attribute)
            if attribute_value != "":
                return attribute_value
            time.sleep(1)
        return ""

    def wait_for_windows_handle(self, duration):
        """
        Takes a duration, return True if more than 1 window else return False
        """
        for _ in range(0, duration):
            if len(self.driver.window_handles) > 1:
                return True
            time.sleep(1)
        return False

    def check_if_popup(self):
        """
        Check if tutorial popup is present on the screen
        """
        try:
            popup = self.get_element(self.css.POPUP)
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
                self.tools.log("Closed Tab No. ", i)
            self.driver.switch_to.window(self.driver.window_handles[0])  # Switching the driver focus to First tab.
        else:
            self.tools.log("Found only Single tab.")

    def refresh(self):
        """
        Refresh current tab
        """
        self.driver.refresh()
        time.sleep(10)

    def click_on_element(self, element):
        self.check_if_popup()
        element.click()
