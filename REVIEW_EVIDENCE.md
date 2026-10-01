# Review evidence

Live evidence for OPTIMA on **Studionet chain 61999**. The pre-rename
deployments have been withdrawn from this file; see the final section for the
only address that matches the current source.

## Direct Mode

- CI run: https://github.com/ibroiyi9901-design/Optima/actions/runs/36751864054
- tested commit: `2d9e17d9129e5f6b8cbbbfcd70bb96ee8de28b3c`
- workflow: `optima-ci`
- runner OS: Ubuntu 24.04 GitHub-hosted runner
- Python: 3.12
- local GenLayer CLI: `0.39.1`
- Direct Mode harness: `genlayer-testing-suite@v0.29.2`
- GenVM runner bundle: `v0.3.0-rc7`
- contract runner hash: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
- static preflight: **passed**
- test command: `pytest tests/direct -q`
- suite size: **26** tests
- CI conclusion: **success**
- CI run duration: **1m46s**
- notes: the repository includes `scripts/prepare_direct_mode.py` because the stable v0.29.2 harness expects the historical universal-bundle cache name while the official rc7 release now publishes the runner archive as `genvm-runners-all.tar.xz`.

The runner hash above is corroborated on chain: the `Depends` header of the
deployed source names the same `py-genlayer:1jb45aa8…` bundle.

The per-test pass/fail tally was not read back from the CI log, which the API no
longer returns for this run. The 26-test figure is the size of the suite in this
tree, confirmed locally; the run's own conclusion is `success`.

## Liveness hardening

- Active solver/admission bound: 10 bids.
- Total retained bid-history bound: 20 records per task.
- Withdrawn bids release an active slot but remain bounded audit records.
- Direct Mode adversarial coverage proves a replacement slot is available, ten
  active addresses cannot admit an eleventh, and 20 withdraw/submit cycles
  cannot grow task history beyond 20 entries.

## Redundancy proof

- task ID:
- requirement:
- qualification transactions:
- selected team:
- solve transaction:

## Unsatisfiable proof

- task ID:
- frozen budget:
- qualification transactions:
- solve transaction:
- terminal state:

## Renamed OPTIMA source deployment — evidence pending

The project was renamed from `COALITION` to `OPTIMA`. The renamed source is
deployed on Studionet 61999, and it is the only live deployment of the current
tree:

- Contract: `0x10b35C8ea408A98e59822e39134Fc423677fcF8b`
- Source SHA-256 (repository tree): `3f2b5f4600eb83554e35567400a6a33d8c64f3c092f3a153ba6a1bf2a04fdc02`
- Repository bytes: `56042`
- Deployed via: GenLayer Studio
- Explorer: `https://explorer-studio.genlayer.com/address/0x10b35C8ea408A98e59822e39134Fc423677fcF8b`
- Studio: `https://studio.genlayer.com/?import-contract=0x10b35C8ea408A98e59822e39134Fc423677fcF8b`

### Verified against the live chain

Queried read-only against `https://studio.genlayer.com/api`:

- `eth_chainId` returns `0xf22f` = `61999`, confirming Studionet and not studio-dev.
- `gen_getContractSchema` for this address returns a full schema, so the
  contract is deployed and recognised by the node.
- The deployed method surface matches `contracts/optima.py` **exactly**: 26
  methods on chain, 26 `def`s in source, with no method present on only one
  side. The 11 read-only views (`get_task`, `get_bid`, `get_qualification`,
  `get_solution`, `get_status_dictionary`, `is_qualification`, `is_solution`,
  `is_solution_bundle`, `get_provider`, `get_requirement`, `get_evidence_source`)
  are all present.
- The explorer labels this contract `OPTIMA`, where the pre-rename address is
  labelled `COALITION`, confirming the renamed source is what is deployed.
- `genlayer code` returns the deployed source. Its `Depends` header names
  runner `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`,
  matching the runner hash in the Direct Mode section above.

### Deployed source differs from the repository source

This deployment is **not** the source currently in this repository. The
difference is three lines of prose, introduced after this deployment was made:

- deployed source SHA-256: `da923cab65c336b98cfaf9df8d320bb889a202ee6ac4bf91ad1700c1ee22b31c`, 56047 bytes
- repository source SHA-256: `3f2b5f4600eb83554e35567400a6a33d8c64f3c092f3a153ba6a1bf2a04fdc02`, 56042 bytes

| Line | Deployed | Repository |
| --- | --- | --- |
| 369 | `multi-provider coalition protocol` | `multi-provider team formation protocol` |
| 418 | `multi-provider coalitions.` | `multi-provider teams.` |
| 1193 | `lowest-cost complete coalition selected…` | `lowest-cost complete team selected…` |

One of these is inside an AI classifier prompt, and one is a user-visible
`task.reason` string. Neither changes the contract's interface, state machine
or selection logic, and the deployed 26-method schema is identical to the
repository's. But for a project whose claim is byte-level provenance, the
repository and the deployment must agree. `scripts/live_evidence.py` refuses to
record evidence while this drift exists.

### Not verified

These fields are deliberately left unfilled rather than guessed:

- deployment transaction: _not recorded_
- deployment result (`FINALIZED / … / SUCCESS`): _not verified_
- on-chain task/qualification/solve lifecycle: _not exercised_

Two notes on why. The explorer address view exposes no transaction list for this
address, so the deployment transaction hash could not be recovered from it, and
finality was not asserted. Contract state could not be read either: `gen_call`
on this endpoint requires a calldata envelope that the public RPC does not
document, so `get_status_dictionary` could not be invoked to check whether any
task, bid or qualification exists yet.

Note also that `eth_getCode` returns `0x` for this address, but it does so for
every address on this network, including previously finalized deployments. It
is a non-functional stub here and is not evidence of a missing contract.

The Direct Mode run above (26-test suite, conclusion `success`, commit
`2d9e17d9…`) certifies the source as of that commit. The current tree adds the
`coalition` to `team` prose sweep on top of it, so the renamed source has not
been re-certified against the pinned toolchain since that change. This file
carries no receipt, hash or verdict for `0x10b35C8e…`. Populate the fields above
only from finalized 61999 receipts for that address; do not carry prior values
forward.
