# Changelog — rlc

All notable changes to this package are documented here.
Format: [Semantic Versioning 2.0.0](https://semver.org/).

---

## [1.0.0] — 2026-04-12

### Added
- Initial release: 2nd-order series RLC filter discretised via the Bilinear Transform.
- Low-pass, high-pass, and band-pass variants.
- Convenience constructors `rlc_lowpass`, `rlc_highpass`, `rlc_bandpass`.
- Direct Form II stateful implementation with `reset()` support.
- `resonant_frequency_hz` property.
- Full pytest test suite (12 test cases).
- Canonical documentation with LaTeX transfer functions and Mermaid block diagrams.
