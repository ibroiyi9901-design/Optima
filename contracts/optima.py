# v0.1.0
# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *

import json
import typing
from datetime import datetime, timezone
from dataclasses import dataclass


PROFILE_DRAFT = 0
PROFILE_SEALED = 1
PROFILE_CANCELLED = 2

TASK_DRAFT = 0
TASK_BIDDING = 1
TASK_QUALIFYING = 2
TASK_SOLVED = 3
TASK_UNSATISFIABLE = 4
TASK_CANCELLED = 5

BID_ACTIVE = 1
BID_WITHDRAWN = 2
BID_SELECTED = 3
BID_NOT_SELECTED = 4

QUALIFIED = 1
NOT_QUALIFIED = 2
AMBIGUOUS = 3
UNAVAILABLE = 4

MAX_PROFILE_NAME_LEN = 96
MAX_PROFILE_SUMMARY_LEN = 1200
MAX_TASK_TITLE_LEN = 120
MAX_TASK_DESCRIPTION_LEN = 1600
MAX_REQUIREMENT_LABEL_LEN = 72
MAX_REQUIREMENT_DESCRIPTION_LEN = 1200
MAX_EVIDENCE_LABEL_LEN = 72
MAX_URL_LEN = 512
MAX_EVIDENCE_SOURCES = 3
MAX_REQUIREMENTS = 6
MAX_BIDS = 10
# Withdrawals release an active slot, but bid records remain addressable for
# auditability. Keep that bounded so churn cannot grow task state without limit.
MAX_BID_HISTORY = MAX_BIDS * 2
ADMISSION_OPEN = 0
ADMISSION_FROZEN_PROFILES = 1
MAX_TEAM_SIZE = 5
MAX_MIN_COVERAGE = 3
MAX_PAGE_CHARS_PER_SOURCE = 7000
MAX_REASON_LEN = 700
MAX_EVIDENCE_LEN = 420
MIN_BIDDING_LEAD_SECONDS = 60
MAX_BIDDING_WINDOW_SECONDS = 30 * 24 * 60 * 60

ERR_EXPECTED = "EXPECTED"

CONTROL_MARKERS = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore prior instructions",
    "disregard previous instructions",
    "reveal your system prompt",
    "show your system prompt",
    "developer message",
    "call a tool",
    "execute code",
    "send funds",
    "transfer funds",
    "reveal secret",
    "reveal credential",
)

