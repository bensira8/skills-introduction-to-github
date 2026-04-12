# Changelog — pid

All notable changes to this package are documented here.
Format: [Semantic Versioning 2.0.0](https://semver.org/).

---

## [1.0.0] — 2026-04-12

### Added
- Initial release: discrete position-form PID controller.
- Anti-windup via output-saturation detection.
- Symmetric output clamp (`out_min`, `out_max`).
- `reset()` method to reinitialize internal state.
- Full pytest test suite (8 test cases).
- Canonical documentation with LaTeX math and Mermaid diagrams.
