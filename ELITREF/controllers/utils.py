import enum
import re


class MatchStatus(enum.Enum):
    ready = 1
    start = 2
    end = 3


CLEANR = re.compile(
    '<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext
