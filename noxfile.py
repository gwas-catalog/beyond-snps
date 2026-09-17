#!/usr/bin/env -S uv run
# /// script
# dependencies = ["nox"]
# ///

from __future__ import annotations

import nox

# Use uv for environment creation and package installation
nox.options.default_venv_backend = "uv"
nox.options.sessions = ["lint", "tests"]


@nox.session
def tests(session):
    # Install local workspace packages
    session.install(".")
    session.install("./sumstatlib")

    # manually install pydantic
    session.install("pydantic")

    # Install test tooling
    session.install("pytest", "coverage")

    # Run tests under coverage
    session.run(
        "coverage",
        "run",
        "--source=gwascatalog,sumstatlib/tests",
        "--omit=sumstatlib/tests/integration/*",
        "-m",
        "pytest",
        "--ignore=sumstatlib/tests/integration",
        "sumstatlib",
    )

    # Coverage report (terminal)
    session.run(
        "coverage",
        "report",
        "-m",
        "--fail-under",
        "90",
        "--omit=sumstatlib/tests/conftest.py",
    )

    # Queue integration tests session after this session completes
    session.notify("integration_tests")


@nox.session
def integration_tests(session):
    session.install(".")
    session.install("./sumstatlib")
    # manually install pydantic
    session.install("pydantic")
    session.install("pytest")

    # Run only integration tests (adjust marker/glob as appropriate)
    session.run("pytest", "sumstatlib/tests/integration", "tests/integration")


@nox.session
def lint(session):
    # Install workspace packages (so type checking resolves imports)
    session.install(".")
    session.install("./sumstatlib")
    # manually install pydantic (this is OK, remember the web app)
    session.install("pydantic")

    # Lint + format + typing tools
    session.install("ruff", "ty")

    # Format check (fails if reformatting needed)
    session.run("ruff", "format", "--check", ".")

    # Lint
    session.run("ruff", "check", ".")

    # Type checking
    session.run("ty", "check", "src", "sumstatlib/src")


@nox.session(venv_backend="none")
def build_wheel(session: nox.Session) -> None:
    """Build a wheel for the specified workspace package.

    Usage:  nox -s build_wheel -- <package-name>
    Example: nox -s build_wheel -- gwascatalog.sumstatlib
    """
    if not session.posargs:
        session.error(
            "Specify a package name, e.g.: nox -s build_wheel -- gwascatalog.sumstatlib"
        )
    session.run("uv", "build", "--package", session.posargs[0], external=True)


@nox.session(venv_backend="none")
def publish_pypi(session: nox.Session) -> None:
    """Publish built wheels in dist/ to PyPI using uv trusted publishing."""
    session.run("uv", "publish", external=True)


if __name__ == "__main__":
    nox.main()
