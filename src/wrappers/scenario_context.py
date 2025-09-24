from src.wrappers.webdriver_wrapper import WebDriverWrapper


class ScenarioContext:
    """Holds the WebDriver wrapper for a test scenario."""

    def __init__(self, wrapper: WebDriverWrapper):
        self.wrapper = wrapper

    def clear_context(self):
        """Option to close and quit the current context/WebDriver session."""
        self.wrapper.driver.quit()
