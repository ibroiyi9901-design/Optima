# Review evidence

Live evidence for OPTIMA on **Studionet chain 61999**. The pre-rename
deployments have been withdrawn from this file; see the final section for the
only address that matches the current source.

## Direct Mode

- CI run: https://github.com/ometere123/optima/actions/runs/36353215840
- tested commit: `7fc99f2a675b99ed5a0de2e3300c200469e7bf3e`
- runner OS: Ubuntu 24.04 GitHub-hosted runner
- Python: 3.12
- local GenLayer CLI: `0.39.1`
- Direct Mode harness: `genlayer-testing-suite@v0.29.2`
- GenVM runner bundle: `v0.3.0-rc7`
- contract runner hash: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
- static preflight: **passed**
- test command: `pytest tests/direct -q`
- passed count: **26**
- failed count: **0**
- CI conclusion: **success**
- runtime: **23.68s**
- notes: the repository includes `scripts/prepare_direct_mode.py` because the stable v0.29.2 harness expects the historical universal-bundle cache name while the official rc7 release now publishes the runner archive as `genvm-runners-all.tar.xz`.

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
- Source SHA-256: `3f2b5f4600eb83554e35567400a6a33d8c64f3c092f3a153ba6a1bf2a04fdc02`
- Source bytes: `56042`
- Deployed via: GenLayer Studio
- Explorer: `https://explorer-studio.genlayer.com/address/0x10b35C8ea408A98e59822e39134Fc423677fcF8b`
- Studio: `https://studio.genlayer.com/?import-contract=0x10b35C8ea408A98e59822e39134Fc423677fcF8b`
- Deployment transaction: _not yet recorded_
- Deployment result: _not yet recorded_
- On-chain task/qualification/solve lifecycle on this address: _not yet recorded_

The Direct Mode figures above (26 passed, commit `7fc99f2a…`) certify the
**pre-rename** source. The renamed source has not yet been re-certified against
the pinned toolchain, and this file no longer carries any receipt, hash or
verdict for `0x10b35C8e…`. Populate the fields above only from finalized 61999
receipts for that address; do not carry prior values forward.
