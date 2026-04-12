# Algorithms — SemVer Technical Artifacts

This directory holds **independently versioned algorithm packages**, each treated as a
first-class technical artifact compatible with GitHub Copilot's context engine.

## Convention

Every algorithm lives under `algorithms/<name>/` and **must** contain:

| Path | Purpose |
|------|---------|
| `src/<name>.py` | Executable implementation (typed, documented) |
| `tests/test_<name>.py` | Reproducible pytest tests |
| `docs/README.md` | Canonical documentation (LaTeX math + Mermaid diagrams) |
| `CHANGELOG.md` | SemVer history (`MAJOR.MINOR.PATCH`) |
| `pyproject.toml` | Package metadata & declared version |

## Versioning rules (SemVer)

- **PATCH** — bug fix, no API change, no math change.
- **MINOR** — new optional parameter / new variant, backwards-compatible.
- **MAJOR** — breaking API change **or** change in the mathematical definition.

## Algorithms

| Package | Version | Description |
|---------|---------|-------------|
| [`pid`](pid/) | 1.0.0 | Discrete PID controller (position form) |
| [`fft`](fft/) | 1.0.0 | Cooley-Tukey radix-2 DIT FFT |
| [`modulation`](modulation/) | 1.0.0 | AM & FM modulation / demodulation |
| [`rlc`](rlc/) | 1.0.0 | RLC analogue filter (low-pass, high-pass, band-pass) + bilinear-transform discrete equivalents |

## Running all tests

```bash
pip install pytest
pytest algorithms/ -v
```

## Copilot context hints

Each `src/*.py` file begins with a structured docstring block (`# ALGO-META`) so
Copilot can identify the algorithm, its version, and its mathematical contract
without reading the full source.
