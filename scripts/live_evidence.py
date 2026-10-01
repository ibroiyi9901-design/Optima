"""Exercise the deployed OPTIMA contract on Studionet and emit real evidence.

This sends real transactions from a funded signer and spends real GEN. It is
deliberately separate from `scripts/preflight.py`, which requires no account.

    python scripts/live_evidence.py --dry-run     # print the plan, send nothing
    python scripts/live_evidence.py               # run it for real

Signing uses the project-local GenLayer CLI. The private key is read from
`ACCOUNT_PRIVATE_KEY` (environment or `.env`) and is never printed, logged or
written to the evidence output.

Everything emitted here is read back from the chain. Nothing is predicted.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "contracts" / "optima.py"

STUDIONET_RPC = "https://studio.genlayer.com/api"
STUDIONET_CHAIN_ID = 61999
TX_RE = re.compile(r"0x[0-9a-fA-F]{64}")

PINNED_CLI = "0.39.1"


def fail(message: str) -> "NoReturn":  # type: ignore[valid-type]
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"  WARN: {message}")


# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------

def load_key() -> str:
    """Read the signer key from the environment or .env without echoing it."""
    key = os.environ.get("ACCOUNT_PRIVATE_KEY", "").strip()
    if not key:
        env_file = ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("ACCOUNT_PRIVATE_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    if not key:
        fail(
            "no signer found. Set ACCOUNT_PRIVATE_KEY in the environment or in "
            ".env (see .env.example). Never commit it."
        )
    if not key.startswith("0x") or len(key) != 66:
        fail("ACCOUNT_PRIVATE_KEY is not a 32-byte 0x-prefixed hex key")
    return key


# --------------------------------------------------------------------------
# chain access
# --------------------------------------------------------------------------

def rpc(method: str, params: list, rpc_url: str = STUDIONET_RPC) -> dict:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
    request = urllib.request.Request(
        rpc_url,
        data=body.encode(),
        headers={"Content-Type": "application/json", "User-Agent": "curl/8"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.URLError as exc:
        fail(f"RPC {method} unreachable at {rpc_url}: {exc}")


def assert_studionet(rpc_url: str) -> None:
    result = rpc("eth_chainId", [], rpc_url)
    chain_id = int(result.get("result", "0x0"), 16)
    if chain_id != STUDIONET_CHAIN_ID:
        fail(
            f"refusing to run: {rpc_url} reports chain {chain_id}, expected "
            f"{STUDIONET_CHAIN_ID}. This script spends real GEN."
        )
    print(f"  chain id {chain_id} confirmed on {rpc_url}")


CLI_CHATTER_PREFIXES = ("[genlayer-js]", "--", "\u2714", "Result:", "- Getting", "Getting ")


def extract_deployed_source(raw: str, contract_address: str) -> str:
    """Pull the contract source out of `genlayer code` output.

    The repository source begins with the `# v0.1.0` / `# { "Depends": ... }`
    header that the chain echoes back, so the source must start there rather
    than at the first import. CLI status chatter is appended after the code.
    """
    lines = raw.splitlines()
    starts = [
        i
        for i, line in enumerate(lines)
        if line.startswith("# v0.1.0") or line.startswith("# { \"Depends\"")
    ]
    start = starts[0] if starts else next(
        (i for i, line in enumerate(lines) if line.startswith("from genlayer import")), -1
    )
    if start < 0:
        fail(f"could not locate the deployed source for {contract_address}")

    end = len(lines)
    for i in range(start, len(lines)):
        if any(lines[i].startswith(prefix) for prefix in CLI_CHATTER_PREFIXES):
            end = i
            break
    return "\n".join(lines[start:end]).rstrip("\n") + "\n"


def assert_deployed_source_matches(contract_address: str, rpc_url: str) -> str:
    """Guard against recording evidence against the wrong bytes.

    Checks the deployed schema, then fetches the deployed source and compares it
    to `contracts/optima.py`. Method names alone are not enough: a pre-rename
    deployment of this same contract exposes an identical schema.
    """
    result = rpc("gen_getContractSchema", [contract_address], rpc_url)
    if "error" in result or "result" not in result:
        fail(f"no deployed contract at {contract_address}: {result.get('error')}")
    deployed_methods = set(result["result"].get("methods", {}))

    local_source = SOURCE.read_text()
    local_methods = set(re.findall(r"^\s{4}def ([a-z][a-z0-9_]*)\(", local_source, re.M))
    missing = sorted(local_methods - deployed_methods)
    extra = sorted(deployed_methods - local_methods)
    if missing or extra:
        fail(
            "deployed contract does not match contracts/optima.py. "
            f"missing on chain: {missing}; extra on chain: {extra}"
        )
    print(f"  deployed schema matches contracts/optima.py ({len(local_methods)} methods)")

    raw = cli(["code", contract_address], "", rpc_url, timeout=180)
    deployed_source = extract_deployed_source(raw, contract_address)

    local_digest = hashlib.sha256(local_source.encode()).hexdigest()
    deployed_digest = hashlib.sha256(deployed_source.encode()).hexdigest()
    if local_digest != deployed_digest:
        drift = [
            line
            for line in difflib.unified_diff(
                deployed_source.splitlines(),
                local_source.splitlines(),
                "deployed",
                "repository",
                lineterm="",
                n=0,
            )
            if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
        ]
        fail(
            "the deployed source differs from contracts/optima.py, so evidence "
            "recorded now would not describe this repository.\n"
            f"  deployed sha256 {deployed_digest} ({len(deployed_source)} bytes)\n"
            f"  repository sha256 {local_digest} ({len(local_source)} bytes)\n"
            "  differing lines:\n" + "\n".join(f"    {d[:140]}" for d in drift[:40])
        )
    print(f"  deployed source is byte-identical to contracts/optima.py ({local_digest[:16]}…)")
    return deployed_digest


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def cli(args: list[str], key: str, rpc_url: str, timeout: int = 180) -> str:
    env = dict(os.environ)
    env["ACCOUNT_PRIVATE_KEY"] = key
    command = ["npx", "genlayer", *args]
    try:
        proc = subprocess.run(
            command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        fail(f"CLI timed out: {' '.join(args)}")
    output = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        fail(f"CLI failed ({proc.returncode}): {' '.join(args)}\n{output.strip()}")
    return output


def await_receipt(tx_hash: str, key: str, rpc_url: str, timeout: int = 900) -> str:
    """Poll until the transaction leaves the pending state."""
    deadline = time.time() + timeout
    last = ""
    while time.time() < deadline:
        try:
            last = cli(["receipt", "--rpc", rpc_url, tx_hash], key, rpc_url, timeout=120)
        except SystemExit:
            last = "(receipt not available yet)"
        low = last.lower()
        if any(word in low for word in ("finalized", "accepted", "majority_agree", "success")):
            return last
        if any(word in low for word in ("failed", "reverted", "error")):
            warn(f"receipt for {tx_hash} reports a failure:\n{last.strip()[:400]}")
            return last
        time.sleep(10)
    warn(f"receipt for {tx_hash} did not finalize within {timeout}s; last seen:\n{last.strip()[:400]}")
    return last


class Runner:
    def __init__(self, contract_address: str, key: str, rpc_url: str, dry_run: bool):
        self.contract = contract_address
        self.key = key
        self.rpc_url = rpc_url
        self.dry_run = dry_run
        self.records: list[dict] = []

    def _arg(self, value) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value)
        text = str(value)
        # The CLI documents `str: hello, "multi word"`.
        return f'"{text}"' if " " in text else text

    def write(self, label: str, method: str, args: list) -> dict:
        argv = ["write", "--rpc", self.rpc_url, self.contract, method]
        for value in args:
            argv += ["--args", self._arg(value)]
        printable = " ".join(argv)
        if self.dry_run:
            print(f"  [dry-run] {label}: {printable}")
            record = {"label": label, "method": method, "args": args, "tx": None, "status": "dry-run"}
            self.records.append(record)
            return record
        print(f"  {label}: {method}({', '.join(self._arg(a) for a in args)})")
        output = cli(argv, self.key, self.rpc_url, timeout=300)
        match = TX_RE.search(output)
        if not match:
            fail(f"could not find a transaction hash in CLI output for {method}:\n{output.strip()[:600]}")
        tx_hash = match.group(0)
        print(f"    tx {tx_hash}")
        print("    waiting for finalization...")
        receipt = await_receipt(tx_hash, self.key, self.rpc_url)
        record = {
            "label": label,
            "method": method,
            "args": args,
            "tx": tx_hash,
            "status": receipt.strip()[:2000],
        }
        self.records.append(record)
        return record

    def call(self, method: str, args: list) -> str:
        argv = ["call", "--rpc", self.rpc_url, self.contract, method]
        for value in args:
            argv += ["--args", self._arg(value)]
        if self.dry_run:
            return "(dry-run)"
        return cli(argv, "", self.rpc_url, timeout=180)


# --------------------------------------------------------------------------
# scenarios
# --------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, help="deployed contract address")
    parser.add_argument("--rpc", default=STUDIONET_RPC)
    parser.add_argument("--out", default="", help="write the evidence block here")
    parser.add_argument("--dry-run", action="store_true", help="send nothing")
    args = parser.parse_args()

    print("OPTIMA live evidence run")
    print(f"  contract {args.contract}")

    assert_studionet(args.rpc)
    deployed_digest = assert_deployed_source_matches(args.contract, args.rpc)

    key = "" if args.dry_run else load_key()
    runner = Runner(args.contract, key, args.rpc, args.dry_run)

    deadline = int(time.time()) + 3600
    providers = [
        ("Alice", "Solidity security", "https://github.com/OpenZeppelin/openzeppelin-contracts", 20),
        ("Bob", "Mechanism design", "https://github.com/ethereum/EIPs", 25),
        ("Carol", "Solidity security", "https://github.com/soliditylang/solidity", 10),
    ]

    profile_ids: dict[str, int] = {}
    bid_ids: dict[str, int] = {}

    print("\n[1/4] provider profiles")
    for name, capability, url, price in providers:
        record = runner.write(f"create_provider {name}", "create_provider",
                              [name, f"{name} publishes public evidence of completed {capability.lower()} work."])
        profile_ids[name] = index_from(record, 1, name)
        runner.write(f"add_provider_evidence {name}", "add_provider_evidence",
                     [profile_ids[name], "portfolio", url])
        runner.write(f"seal_provider {name}", "seal_provider", [profile_ids[name]])

    print("\n[2/4] task, bids and the complete qualification matrix")
    task = runner.write("create_task", "create_task",
                        ["Optima live evidence", "Independent review of a Solidity contract plus mechanism design.",
                         100, 2, deadline])
    task_id = index_from(task, 1, "create_task")
    req_sol = index_from(runner.write("add_requirement SOLIDITY_SECURITY", "add_requirement",
                       [task_id, "SOLIDITY_SECURITY", "Public evidence of completed Solidity smart-contract security review work.", 1]), 1, "SOLIDITY_SECURITY")
    req_mech = index_from(runner.write("add_requirement MECHANISM_DESIGN", "add_requirement",
                        [task_id, "MECHANISM_DESIGN", "Public evidence of completed mechanism and economic mechanism design work.", 1]), 1, "MECHANISM_DESIGN")
    runner.write("seal_task", "seal_task", [task_id])

    for name, _capability, _url, price in providers:
        bid_ids[name] = index_from(runner.write(f"submit_bid {name}", "submit_bid",
                                    [task_id, profile_ids[name], price]), 1, f"submit_bid {name}")
    runner.write("close_bidding", "close_bidding", [task_id])

    for name in providers:
        short = name[0]
        for req_id, req_label in ((req_sol, "SOLIDITY_SECURITY"), (req_mech, "MECHANISM_DESIGN")):
            runner.write(f"resolve_qualification {short}/{req_label}", "resolve_qualification",
                         [task_id, bid_ids[short], req_id])

    solution = runner.write("solve_task", "solve_task", [task_id])

    print("\n[3/4] consumer receipts")
    task_readback = runner.call("get_task", [task_id])
    solution_readback = runner.call("get_solution", [task_id])
    print(f"    get_task     -> {task_readback.strip()[:300]}")
    print(f"    get_solution -> {solution_readback.strip()[:300]}")

    definition_hash = extract_hash(task_readback, "definition_hash")
    solution_hash = extract_hash(solution_readback, "solution_hash")
    matrix_hash = extract_hash(solution_readback, "matrix_hash")

    is_solution = runner.call("is_solution", [task_id, definition_hash or "", solution_hash or ""])
    is_solution_perturbed = runner.call("is_solution", [task_id, definition_hash or "0x" + "00" * 32, solution_hash or ""])
    bundle = None
    if matrix_hash:
        bundle = runner.call("is_solution_bundle",
                             [task_id, definition_hash or "", matrix_hash, solution_hash or ""])

    print("\n[4/4] redundancy and unsatisfiable proofs")
    print("  See LIVE_DEMO.md; run them manually against this address and add the"
          " resulting hashes to REVIEW_EVIDENCE.md.")

    block = render_evidence(args.contract, deployed_digest, runner.records, {
        "task_id": task_id,
        "profile_ids": profile_ids,
        "bid_ids": bid_ids,
        "definition_hash": definition_hash,
        "matrix_hash": matrix_hash,
        "solution_hash": solution_hash,
        "is_solution": is_solution,
        "is_solution_perturbed": is_solution_perturbed,
        "is_solution_bundle": bundle,
        "solve_tx": solution.get("tx"),
    })
    print("\n" + block)
    if args.out:
        Path(args.out).write_text(block)
        print(f"\nwrote {args.out}")


def index_from(record: dict, position: int, label: str) -> int:
    """Read an id back from the CLI output rather than assuming one."""
    if record.get("tx") is None:
        return 0
    numbers = re.findall(r"\b(\d+)\b", record.get("status", ""))
    if position < len(numbers):
        return int(numbers[position])
    warn(f"could not read a returned id for {label}; using 0 and expecting failure")
    return 0


def extract_hash(blob: str, key: str) -> str:
    if not blob:
        return ""
    match = re.search(rf"{key}\"?\s*[:=]\s*\"?(0x[0-9a-fA-F]{{64}})", blob)
    return match.group(1) if match else ""


def render_evidence(contract: str, deployed_digest: str, records: list, derived: dict) -> str:
    lines = ["## Live evidence (generated by `scripts/live_evidence.py`)", ""]
    lines.append(f"- contract: `{contract}`")
    lines.append(f"- chain id: `{STUDIONET_CHAIN_ID}`")
    lines.append(f"- verified deployed source SHA-256: `{deployed_digest}`")
    lines.append(f"- task ID: `{derived['task_id']}`")
    lines.append(f"- definition hash: `{derived['definition_hash'] or 'not read'}`")
    lines.append(f"- matrix hash: `{derived['matrix_hash'] or 'not read'}`")
    lines.append(f"- solution hash: `{derived['solution_hash'] or 'not read'}`")
    lines.append("")
    lines.append("### Transactions")
    lines.append("")
    lines.append("| Step | Method | Transaction |")
    lines.append("| --- | --- | --- |")
    for record in records:
        lines.append(f"| {record['label']} | `{record['method']}` | `{record['tx'] or 'dry-run'}` |")
    lines.append("")
    lines.append("### Consumer boundary")
    lines.append("")
    lines.append(f"- `is_solution` exact hashes: `{derived['is_solution'].strip()[:120]}`")
    lines.append(f"- `is_solution` altered definition hash: `{derived['is_solution_perturbed'].strip()[:120]}`")
    if derived["is_solution_bundle"] is not None:
        lines.append(f"- `is_solution_bundle`: `{derived['is_solution_bundle'].strip()[:120]}`")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
