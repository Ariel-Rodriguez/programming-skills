# Changelog

All notable changes to the skills collection will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-01-30

### Rebranding
- Added `ps-` prefix to all 12 programming skills (e.g., `ps-functional-core-imperative-shell`) for better branding alignment.

### Benchmarking
- Implemented robust validation schema (`includes`, `excludes`, `regex`, `min_length`, `max_length`) in `evaluator.py`.
- Added support for external file inputs in benchmark scenarios.
- Improved diagnostic output in verbose mode.

### Documentation
- Consolidated Architecture and Design documentation into `docs/architecture.md`.
- Updated `contributing.md` for the v2.2.0 workflow.

### Added
- Initial 12 programming skills with pseudocode examples

### Changed
- Restructured from language-specific examples to pseudocode format

## [1.0.0] - 2026-01-27

### Added
- **Functional Core Imperative Shell** - Separate pure logic from effects
- **Explicit State Invariants** - Design state with clear invariants
- **Single Direction Data Flow** - Unidirectional data flow
- **Explicit Boundaries Adapters** - Isolate frameworks
- **Local Reasoning** - Understandable locally
- **Naming as Design** - Intent-revealing names
- **Error Handling Design** - Model errors explicitly
- **Policy Mechanism Separation** - Separate what from how
- **Explicit Ownership Lifecycle** - Clear resource ownership
- **Minimize Mutation** - Control mutation
- **Composition Over Coordination** - Compose, don't orchestrate
- **Illegal States Unrepresentable** - Prevent misuse structurally

### Architecture
- Simple pseudocode-based format (v1.0.0)
- Single release for all platforms (cursor-antigravity.zip, copilot.zip)
- No build process required
- Language-agnostic approach

---

## Version Format

**Major.Minor.Patch** (e.g., 1.2.3)

- **Major**: Breaking changes to skill format or structure
- **Minor**: New skills added or significant skill improvements
- **Patch**: Bug fixes, typo corrections, minor clarifications

## Change Categories

- **Added**: New skills or features
- **Changed**: Modifications to existing skills
- **Deprecated**: Skills marked for removal
- **Removed**: Skills deleted
- **Fixed**: Bug fixes or corrections
- **Security**: Security-related changes
