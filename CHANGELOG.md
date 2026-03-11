# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- README now explains scope boundaries more explicitly (`what it does` / `what it does not do`).
- Added a lightweight architecture flow so the attribution → credibility → narrative pipeline is easier to understand.
- Added an example report shape to make the output style more concrete for first-time readers.

### Fixed
- CI lint regressions (Ruff E501 line-length) in narrative scripts.
- Main branch CI is green again after formatting-safe refactors.

## [0.1.0] - 2026-02-24

### Added
- Launchpad attribution now supports Virtuals, Clanker, Bankr, Flaunch, and Doppler signals.
- Confidence tiers in output: `exact`, `heuristic`, `none`.
- Secondary index hints via `alsoIndexedOn`.
- Rich Bankr attribution fields (deployer, fee recipient, tweet URL, website URL).
- Governance and trust docs:
  - `LICENSE` (MIT)
  - `CONTRIBUTING.md`
  - `SECURITY.md`
  - `docs/data-sources.md`
- CI workflow with lint + tests.
- Unit tests for launchpad classification behavior.

### Changed
- `scripts/check_launchpads.py` refactored with testable `classify_launchpad(...)` function.
- README expanded with trust model, data-source rationale, maintainer info, and versioning guidance.

### Notes
- Project remains early-stage and research-focused.
- Use outputs as decision support, not automatic trading execution.
