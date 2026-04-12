# Changelog — fft

All notable changes to this package are documented here.
Format: [Semantic Versioning 2.0.0](https://semver.org/).

---

## [1.0.0] — 2026-04-12

### Added
- Initial release: Cooley-Tukey radix-2 DIT FFT (recursive, pure Python).
- `ifft()` via conjugation identity.
- `magnitude_spectrum()` single-sided helper.
- Full pytest test suite (10 test cases, including Parseval and linearity).
- Canonical documentation with LaTeX math and Mermaid diagrams.
