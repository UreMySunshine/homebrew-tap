"""Generate a formula from the latest stable Bump release and pinned resources."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile


def gh(*args):
    return subprocess.check_output(['gh', *args], text=True)


def main():
    repository = 'UreMySunshine/bump'
    release = json.loads(gh('api', f'repos/{repository}/releases/latest'))
    tag = release['tag_name']
    if not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+', tag):
        raise ValueError('Unexpected release tag')
    version = tag[1:]
    archive = f'bump-{version}.tar.gz'
    with tempfile.TemporaryDirectory() as directory:
        gh('release', 'download', tag, '--repo', repository, '--dir', directory,
           '--pattern', archive, '--pattern', 'homebrew-resources.json', '--pattern', 'SHA256SUMS')
        root = Path(directory)
        checksums = dict(line.split(maxsplit=1)[::-1] for line in (root / 'SHA256SUMS').read_text().splitlines())
        for name in (archive, 'homebrew-resources.json'):
            actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
            if checksums.get(name) != actual:
                raise ValueError(f'Checksum mismatch: {name}')
        checksum = checksums[archive]
        resources = json.loads((root / 'homebrew-resources.json').read_text())
    blocks = []
    names = set()
    for resource in resources:
        name, url, digest = (resource[key] for key in ('name', 'url', 'sha256'))
        if not re.fullmatch(r'[a-z0-9-]+', name) or name in names:
            raise ValueError('Invalid or duplicate dependency name')
        if not re.fullmatch(r'https://files\.pythonhosted\.org/packages/[A-Za-z0-9/._-]+\.whl', url):
            raise ValueError('Unexpected dependency URL')
        if not re.fullmatch(r'[a-f0-9]{64}', digest):
            raise ValueError('Invalid dependency checksum')
        names.add(name)
        blocks.append(f'  resource "{name}" do\n    url "{url}"\n    sha256 "{digest}"\n  end\n')
    if 'textual' not in names:
        raise ValueError('Missing Textual dependency')
    formula = f'''class Bump < Formula
  include Language::Python::Virtualenv

  desc "Terminal dashboard for Homebrew, npm, and standalone tool updates"
  homepage "https://github.com/{repository}"
  url "https://github.com/{repository}/releases/download/{tag}/{archive}"
  sha256 "{checksum}"
  license "MIT"

  depends_on "python@3.14"

{chr(10).join(blocks)}
  def install
    venv = virtualenv_create(libexec, "python3.14")
    venv.pip_install resources
    inreplace "bump", "#!/usr/bin/env -S uv run --script", "#!#{{libexec}}/bin/python"
    libexec.install "bump"
    bin.install_symlink libexec/"bump"
    pkgshare.install "test_bump.py"
  end

  test do
    assert_match "bump #{{version}}", shell_output("#{{bin}}/bump --version")
    assert_match "--check", shell_output("#{{bin}}/bump --help")
    ENV["BUMP_PATH"] = libexec/"bump"
    system libexec/"bin/python", pkgshare/"test_bump.py"
  end
end
'''
    path = Path('Formula/bump.rb')
    changed = not path.exists() or path.read_text() != formula
    path.parent.mkdir(exist_ok=True)
    path.write_text(formula)
    output = os.environ.get('GITHUB_OUTPUT')
    if output:
        with open(output, 'a') as stream:
            stream.write(f'changed={str(changed).lower()}\nversion={version}\n')
    print(f'Bump {version}: {"updated" if changed else "unchanged"}')


if __name__ == '__main__':
    main()
