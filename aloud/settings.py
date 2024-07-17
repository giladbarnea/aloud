import os
import sys
import time

from lazy_object_proxy import Proxy
from pydantic import computed_field
from pydantic_settings import BaseSettings


class DevSettings(BaseSettings):
    """Only honored in development environments."""

    dev_allow_concurrency: bool = False

    @computed_field
    def running_pytest(self) -> bool:
        return os.getenv('PYTEST_CURRENT_TEST') or 'pytest' in sys.argv[0]


class Settings(BaseSettings):
    parse_images: bool = True

    def __init__(self, *args, **kwargs):
        time.sleep(5)
        super().__init__(*args, **kwargs)


dev_settings = Proxy(DevSettings)
settings = Proxy(Settings)
