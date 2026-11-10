# Sonar integration for Docker Sandboxes

Run Claude Code in a Docker Sandbox with Sonar guidance and agentic analysis
configured before the agent starts. The kit installs a checksum-pinned SonarQube
CLI and checks authentication, project integration and agent hooks at startup.
It supports SonarQube Cloud EU and US.

This is a reference integration, provided as is and without warranty. It is not
affiliated with or endorsed by Docker, Inc. or Anthropic. Docker, Docker
Sandboxes and Claude Code are trademarks of their respective owners.

## Prerequisites

- Docker Sandboxes `sbx` with schema-v2 kit support (reference version: 0.45.1).
- A platform supported by [Docker Sandboxes](https://docs.docker.com/ai/sandboxes/install/).
- Docker and Claude Code access through Docker's built-in Claude agent.
- An existing SonarQube Cloud project with Vortex enabled and a Sonar user token.
- A source workspace for the agent to work in.

## Configure credentials

Sign in and store the Sonar user token through Docker's hidden prompt:

```sh
sbx login
sbx secret set sonar-cloud
```

Configure Claude using its supported sign-in flow, or store an API key with
`sbx secret set anthropic`. Never put credentials in source files, kit arguments
or command-line values. Docker's credential proxy injects the Sonar token into
approved outbound requests.

## Validate and run

Clone this repository and run these commands from its root. Replace `YOUR_ORG`
and `YOUR_PROJECT` with your SonarQube Cloud keys, and `../your-project` with
the workspace you want to mount:

```sh
sbx kit validate ./kit \
  --kit-arg organization=YOUR_ORG \
  --kit-arg project=YOUR_PROJECT \
  --kit-arg cloud-domain=sonarcloud.io

sbx run --name sonar-claude-project ./kit ../your-project \
  --kit-arg organization=YOUR_ORG \
  --kit-arg project=YOUR_PROJECT \
  --kit-arg cloud-domain=sonarcloud.io
```

For the US region, use `cloud-domain=sonarqube.us` in both commands. Approve the
regional credential binding if Docker prompts for it. The kit inherits Docker's
Claude image and network policy and adds the required Sonar endpoints.

The startup gate verifies the pinned CLI version, authentication, project
integration, required features and Claude hook references. A `configured`
readiness result means setup passed; it does not mean a live analysis succeeded.

Inside the agent workspace, use Sonar's generated instructions and hooks. To
request a file analysis directly, replace `path/to/file.py` and `YOUR_PROJECT`:

```sh
sonar analyze agentic --depth DEEP --file path/to/file.py --project YOUR_PROJECT
```

Keep any analysis errors, skipped-file reports or context warnings. A recent
conventional CI analysis supplies richer project context; zero findings on one
file are not a full-project security assessment.

Stop the sandbox with `sbx stop sonar-claude-project`. To resume, rerun the same
`sbx run` command and use the same workspace and sandbox name.

## Troubleshooting

- **Credentials missing:** store `sonar-cloud` and approve its regional binding.
- **Startup gate fails:** verify the selected region, project permissions and
  Vortex entitlement. Do not disable hooks or isolation to bypass the check.
- **Version or checksum mismatch:** review the pins in
  `kit/files/home/sonar-kit/versions.json`; do not bypass checksum verification.
- **Connection or daemon failure:** inspect `sbx policy log` and `sbx diagnose`.

The kit depends on the pinned CLI's integration-state schema. Revalidate the
startup checks when upgrading the CLI or Docker runtime.

## Develop and package

Host tests use Python 3.12 or 3.13 and `uv`; no third-party Python dependencies
are required. The sandbox runtime uses its image's `python3`.

```sh
uv sync --locked
uv run --locked python -m unittest discover -s tests -v
mkdir -p dist
sbx kit pack ./kit -o dist/sonar-claude-0.1.0.zip
```

Only the `kit/` directory is packaged. The archive contains the kit definition
and runtime files. Signing and registry distribution use Docker's native tools.

## Contributing, security and license

See [CONTRIBUTING.md](CONTRIBUTING.md). Report vulnerabilities as described in
[SECURITY.md](SECURITY.md), not in public issues. This project is licensed under
the [GNU Lesser General Public License v3.0 or later](LICENSE), which supplements
the [GNU General Public License v3.0](COPYING).

## References

- [Docker kit reference](https://docs.docker.com/ai/sandboxes/customize/kit-reference/)
- [Docker kit usage](https://docs.docker.com/ai/sandboxes/customize/kits/)
- [Docker credential bindings](https://docs.docker.com/ai/sandboxes/configuration/credentials/)
- [Sonar Claude Code integration](https://docs.sonarsource.com/sonarqube-cli/integrations/claude-code)
