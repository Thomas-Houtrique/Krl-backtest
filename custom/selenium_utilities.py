import time
from custom.utilities import UtilityTools
from custom.errors import ElementNotFound
from custom.css_const import CssConst


class SeleniumUtilities:
    def __init__(self):
        self.css = CssConst()
        self.tools = UtilityTools()
        self.driver = self.tools.detect_browsers()

    def get_element(self, element_path):
        """
        Takes a css class, return selenium element
        """
        for i in range(0, 10):
            if len(self.driver.find_elements_by_css_selector(element_path)) > 0:
                return self.driver.find_element_by_css_selector(element_path)
            self.tools.log(f"can't find element {element_path} retry {i+1}/10", verbose=True)
            time.sleep(1)
        raise ElementNotFound(element_path)

    def get_elements(self, elements_path):
        """
        Takes a css class,return list of ele
        """
        return self.driver.find_elements_by_css_selector(elements_path)

    def get_element_text(self, element_path):
        """
        Takes a selenium element,return element text
        """
        return self.get_element(element_path).text

    def get_element_double(self, element_path):
        """
        Takes a css class, return str with "+" replaced by void
        """
        return self.get_element_text(element_path).replace("+", "")

    def get_element_percent(self, element_path):
        """
        Takes a css class, return str with " %" replaced by void
        """
        return self.get_element_text(element_path).replace(" %", "")

    def get_element_days(self, element_path):
        """
        Takes a css class, return str with " days" replaced by void
        """
        return self.get_element_text(element_path).replace(" days", "")

    def check_error_during_backtest(self):
        """
        Check if backtest broke return True if Bt broke and False if not
        """
        # ugly method to detect if there is an error or end page
        for _ in range(0, 1000):
            time.sleep(10)
            if len(self.get_elements(self.css.ANALYSE_TAB_DEEP_ANALYSE_LINK)) > 0:
                break
            if self.get_element_text(self.css.BACKTEST_START_BTN) == "Test":
                # double check because it can cause some pb
                if len(self.get_elements(self.css.ANALYSE_TAB_DEEP_ANALYSE_LINK)) > 0:
                    break
                self.tools.log("Error during the backtest")
                return True
        return False

    def wait_for_element(self, element, duration):
        """
        Takes a selenium element and a duration, return True if element detected and False if not
        """
        for _ in range(0, duration):
            if len(self.get_elements(element)) > 0:
                return True
            time.sleep(1)
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

    def check_if_popup(self):
        """
        Check if tutorial popup is present on the screen
        """
        try:
            popup = self.get_element(self.css.POPUP)
            popup.click()
        except Exception:
            pass