# Sonar integration for Docker Sandboxes
# Copyright (C) SonarSource Sàrl
# mailto:info AT sonarsource DOT com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""Install the exact Sonar artifact into the sandbox, never a floating script."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import tempfile

BASE_URL = "https://binaries.sonarsource.com/Distribution/sonarqube-cli"


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def install(destination=Path("/usr/local/bin/sonar")):
    lock = json.loads(Path(__file__).with_name("versions.json").read_text())
    architecture = {"aarch64": "arm64", "arm64": "arm64",
                    "x86_64": "x86-64"}.get(platform.machine())
    if platform.system() != "Linux" or architecture is None:
        raise RuntimeError("The kit installer runs inside a supported Linux sandbox only.")
    target = "linux-" + architecture
    expected = lock["sha256"][target]
    if destination.is_file() and digest(destination) == expected:
        print("SonarQube CLI already matches the pinned checksum.")
        return
    release = lock["release"]
    if not re.fullmatch(r"\d+(?:\.\d+)+", release):
        raise RuntimeError("versions.json must pin a numeric release version.")
    url = f'{BASE_URL}/{release}/linux/sonarqube-cli-{release}-{target}.bin'
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Stage on the destination filesystem so replacement is atomic.
    fd, filename = tempfile.mkstemp(prefix=".sonar-", dir=destination.parent)
    os.close(fd)
    staged = Path(filename)
    try:
        subprocess.run(["curl", "--fail", "--silent", "--show-error", "--location",
                        "--proto", "=https", "--proto-redir", "=https",
                        "--retry", "2", "--max-time", "180", url, "-o", str(staged)],
                       check=True, timeout=570)
        if digest(staged) != expected:
            raise RuntimeError("Sonar download checksum mismatch; installed binary was preserved.")
        staged.chmod(0o755)
        staged.replace(destination)
    finally:
        staged.unlink(missing_ok=True)
    print(f"Installed SonarQube CLI {release} ({target}).")


if __name__ == "__main__":
    install()
