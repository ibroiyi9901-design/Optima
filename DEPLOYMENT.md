# Deployment — stable Studionet only

OPTIMA targets **Studionet, chain ID 61999**.

RPC: `https://studio.genlayer.com/api`

This repository is intentionally **not** configured for Studio-dev / 61997.

## 1. Clone

`git clone https://github.com/ibroiyi9901-design/Optima.git`

`cd Optima`

## 2. Install the repository-local stable CLI

Ignore any globally installed GenLayer CLI for this repo.

`npm install`

`npx genlayer --version`

Expected: **0.39.1**.

## 3. Run Direct Mode before deployment

Under Linux/macOS/WSL:

`python -m venv .venv`

`source .venv/bin/activate`

`pip install -r requirements-test.txt`

`pytest tests/direct -q`

Do not deploy while the suite is red.

## 4. Select and verify Studionet

`npx genlayer network set studionet`

`npx genlayer network info`

Verify the output corresponds to:

- RPC: `https://studio.genlayer.com/api`
- chain ID: `61999`

If you see `61997`, `studio-dev`, or `studio-dev.genlayer.com`, stop.

## 5. Confirm signer and test GEN

Use the stable CLI account commands to confirm the intended signer and enough test GEN. Never commit private keys or a populated `.env`.

## 6. Deploy

`npx genlayer deploy --contract contracts/optima.py`

Wait for the expected finalized state, then record the contract address, deployment transaction hash, deployed Git commit and signer.

## 7. Execute the reviewer lifecycle

Follow `LIVE_DEMO.md`, then fill `REVIEW_EVIDENCE.md` with real transaction hashes and observed results only.

## Current Studionet deployment — renamed Optima source

This is the only live deployment of the **current** source tree, in which the
project was renamed from `COALITION` to `OPTIMA` (class `Optima`, classifier
`OPTIMA / CAPABILITY QUALIFICATION`, `contracts/optima.py`).

- Network: Studionet, chain ID `61999`
- RPC: `https://studio.genlayer.com/api`
- Source SHA-256 (deployed): `da923cab65c336b98cfaf9df8d320bb889a202ee6ac4bf91ad1700c1ee22b31c`
- Deployed bytes: `56047`
- Source SHA-256 (repository): `3f2b5f4600eb83554e35567400a6a33d8c64f3c092f3a153ba6a1bf2a04fdc02`
- Repository bytes: `56042`
- Contract: `0x10b35C8ea408A98e59822e39134Fc423677fcF8b`
- Deployed via: GenLayer Studio (web `run-debug`), not the pinned CLI flow in step 6
- Explorer: `https://explorer-studio.genlayer.com/address/0x10b35C8ea408A98e59822e39134Fc423677fcF8b`
- Studio: `https://studio.genlayer.com/?import-contract=0x10b35C8ea408A98e59822e39134Fc423677fcF8b`
- Deployment transaction: _not recorded_
- Deployment result: _not verified_

Verified read-only against `https://studio.genlayer.com/api`: `eth_chainId`
returns `0xf22f` = `61999`, and `gen_getContractSchema` for this address returns
a 26-method schema that matches `contracts/optima.py` exactly, with no method
present on only one side. The explorer labels this contract `OPTIMA`, where the
pre-rename address is labelled `COALITION`.

The deployed source is three lines behind the repository source, all of them
prose (`coalition` to `team` at lines 369, 418 and 1193). One sits inside an AI
classifier prompt and one is a `task.reason` string, so the interface and the
selection logic are unaffected, but the two hashes above do not match. Redeploy
from the current tree to make them agree; `scripts/live_evidence.py` blocks until
they do.

Fill the deployment transaction and result above from the explorer before
presenting this address as final evidence, and exercise at least one full
task/qualification/solve lifecycle against it.

The pre-rename Studionet deployments were removed from this document, along with
their transaction hashes, receipts and lifecycle readbacks, so that this file
describes exactly one address: the one matching the source in this tree. Their
records are recoverable from version control history and from
[the explorer](https://explorer-studio.genlayer.com) by contract address.
