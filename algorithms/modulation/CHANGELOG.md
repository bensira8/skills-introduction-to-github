# Changelog — modulation

All notable changes to this package are documented here.
Format: [Semantic Versioning 2.0.0](https://semver.org/).

---

## [1.0.0] — 2026-04-12

### Added
- Initial release: AM (DSB-SC and DSB-LC) modulation and envelope demodulation.
- FM modulation (cumulative phase integration) and FM discriminator demodulation.
- First-order IIR low-pass filter helper with RC time-constant design.
- Nyquist and frequency-validity guards on all public functions.
- Full pytest test suite (12 test cases).
- Canonical documentation with LaTeX math and Mermaid diagrams.
