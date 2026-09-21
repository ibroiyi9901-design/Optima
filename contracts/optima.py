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


@allow_storage
@dataclass
class ProviderProfile:
    owner: Address
    name: str
    summary: str
    status: u8
    created_at: u256
    sealed_at: u256
    evidence_ids: DynArray[u256]
    profile_hash: str


@allow_storage
@dataclass
class EvidenceSource:
    profile_id: u256
    label: str
    url: str


@allow_storage
@dataclass
class Task:
    creator: Address
    title: str
    description: str
    budget: u256
    max_team_size: u8
    bidding_deadline: u256
    status: u8
    created_at: u256
    sealed_at: u256
    closed_at: u256
    solved_at: u256
    requirement_ids: DynArray[u256]
    bid_ids: DynArray[u256]
    selected_bid_ids: DynArray[u256]
    total_cost: u256
    definition_hash: str
    solution_hash: str
    reason: str
    admission_mode: u8
    admitted_profile_ids: DynArray[u256]
    matrix_hash: str


@allow_storage
@dataclass
class Requirement:
    task_id: u256
    label: str
    description: str
    min_coverage: u8


@allow_storage
@dataclass
class Bid:
    task_id: u256
    profile_id: u256
    bidder: Address
    price: u256
    status: u8
    created_at: u256
    qualification_ids: DynArray[u256]


@allow_storage
@dataclass
class Qualification:
    task_id: u256
    bid_id: u256
    requirement_id: u256
    resolver: Address
    verdict: u8
    reason: str
    evidence: str
    source_url: str
    resolved_at: u256
    receipt_hash: str


@gl.contract_interface
class IOptima:
    class View:
        def get_provider(self, profile_id: u256) -> dict: ...
        def get_evidence_source(self, evidence_id: u256) -> dict: ...
        def get_task(self, task_id: u256) -> dict: ...
        def get_requirement(self, requirement_id: u256) -> dict: ...
        def get_bid(self, bid_id: u256) -> dict: ...
        def get_qualification(self, qualification_id: u256) -> dict: ...
        def get_solution(self, task_id: u256) -> dict: ...
        def is_qualification(self, qualification_id: u256, expected_receipt_hash: str) -> bool: ...
        def is_solution(self, task_id: u256, expected_definition_hash: str, expected_solution_hash: str) -> bool: ...
        def is_solution_bundle(self, task_id: u256, expected_definition_hash: str, expected_matrix_hash: str, expected_solution_hash: str) -> bool: ...
        def get_status_dictionary(self) -> dict: ...

    class Write:
        def create_provider(self, name: str, summary: str) -> u256: ...
        def add_provider_evidence(self, profile_id: u256, label: str, url: str) -> u256: ...
        def seal_provider(self, profile_id: u256) -> None: ...
        def cancel_provider_draft(self, profile_id: u256) -> None: ...
        def create_task(self, title: str, description: str, budget: u256, max_team_size: u8, bidding_deadline: u256) -> u256: ...
        def add_requirement(self, task_id: u256, label: str, description: str, min_coverage: u8) -> u256: ...
        def seal_task(self, task_id: u256) -> None: ...
        def set_admission_mode(self, task_id: u256, mode: u8) -> None: ...
        def admit_profile(self, task_id: u256, profile_id: u256) -> None: ...
        def cancel_task_draft(self, task_id: u256) -> None: ...
        def submit_bid(self, task_id: u256, profile_id: u256, price: u256) -> u256: ...
        def withdraw_bid(self, bid_id: u256) -> None: ...
        def close_bidding(self, task_id: u256) -> None: ...
        def resolve_qualification(self, task_id: u256, bid_id: u256, requirement_id: u256) -> u256: ...
        def solve_task(self, task_id: u256) -> None: ...

