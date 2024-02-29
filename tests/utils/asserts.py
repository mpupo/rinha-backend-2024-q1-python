import datetime

import pytz
from dateutil import parser


def assert_date_includes_timezone(date: str, timezone: str):
    tz = pytz.timezone(timezone)
    parsed_date = parser.isoparse(date)
    control = datetime.datetime.now(tz=tz)
    assert parsed_date.utcoffset() == control.utcoffset()
