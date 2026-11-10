# Contributing

Thanks for your interest in this project. Bug reports, questions and suggestions
are welcome as [GitHub issues](../../issues). Please do not include credentials,
tokens or private project details in an issue.

Pull requests from outside Sonar are not accepted at this time, so that changes
to the pinned CLI version, checksums and credential handling stay under a single
review. The source is public: you are welcome to fork and experiment.

To report a security vulnerability, follow [SECURITY.md](SECURITY.md) instead of
opening an issue.

## Development

Host tests use Python 3.12 or 3.13 and [uv](https://docs.astral.sh/uv/). There
are no third-party dependencies.

```sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
```

Guidelines for changes in this repository:

- Update `kit/files/home/sonar-kit/versions.json` (release and both checksums)
  together, and verify the checksums against the published binaries.
- Do not weaken credential redaction, the startup readiness gate or the
  sandbox's network and isolation policy.
- Keep the kit version in `kit/spec.yaml` and `pyproject.toml` in sync; a test
  enforces this.
