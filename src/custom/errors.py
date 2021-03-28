class ElementNotFound(Exception):
    """Exception raised when element not found in page

    Attributes:
        css_class -- css class which caused the error
        message -- explanation of the error
    """

    def __init__(self, css_class, message="Can't find this css selector on page"):
        self.css_class = css_class
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} -> {self.css_class}"
