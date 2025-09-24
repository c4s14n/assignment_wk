from contextlib import contextmanager

from dependency_injector import containers, providers

from src.wrappers.scenario_context import ScenarioContext
from src.wrappers.webdriver_wrapper import WebDriverWrapper


@contextmanager
def webdriver_wrapper_resource():
    """Yield a WebDriverWrapper and ensure it is quit afterward."""
    wd_wrapper = WebDriverWrapper()
    try:
        yield wd_wrapper
    finally:
        wd_wrapper.quit()


class AppContainer(containers.DeclarativeContainer):
    """Main DI container wiring Selenium driver and scenario context."""
    wiring_config = containers.WiringConfiguration(packages=["src.pages", "tests"])
    settings = providers.Configuration()
    driver_wrapper = providers.Resource(webdriver_wrapper_resource)

    scenario_context = providers.Singleton(
        ScenarioContext,
        wrapper=driver_wrapper,
    )
