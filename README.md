# UreMySunshine Homebrew Tap

```sh
brew install uremysunshine/tap/bump
bump
```

Bump provides a Textual interface for checking and selectively updating Homebrew,
npm global packages, and standalone tools. Python and pinned application dependencies
are installed in an isolated Homebrew environment; uv is not required to run Bump.

## Updates

```sh
brew update
brew upgrade uremysunshine/tap/bump
```

The Publish formula workflow checks the latest stable
[Bump release](https://github.com/UreMySunshine/bump/releases) hourly and can also be
started manually. It verifies release asset checksums, generates the formula,
installs it on macOS, and runs its tests before pushing the change. GitHub may delay
scheduled jobs; public repository schedules may be disabled after 60 days without
repository activity. Workflow failures are visible in Actions and do not publish
the formula. No cross-repository secret is required.

Dependencies are pinned as checksummed PyPI wheel resources. The tap currently
provides source installs, not prebuilt bottles. Real desktop validation was performed
on Apple Silicon macOS; other platforms are not claimed as verified.

License: MIT.
