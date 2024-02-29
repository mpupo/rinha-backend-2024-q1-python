import logging

import pytest

from src.rinha.config.settings import settings

settings.ECHO_SQL = True
settings.DEBUG = True

logger_blocklist = [
    "faker.factory",
]
logger_allowlist = ["sqlalchemy.engine", "sqlalchemy.pool"]

for module in logger_blocklist:
    logging.getLogger(module).setLevel(logging.WARNING)

for module in logger_allowlist:
    logging.getLogger(module).setLevel(logging.DEBUG)

pytest.register_assert_rewrite("tests.utils.asserts")
