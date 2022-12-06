import nox


@nox.session
def mypy(session: nox.Session) -> None:
    session.install("poetry")
    session.run("poetry", "install", "--with", "typing")
    session.run("mypy", ".")


@nox.session(name="apply-lint")
def apply_lint(session: nox.Session) -> None:
    session.run("poetry", "install", "--only", "linting")
    session.run("black", ".")
    session.run("isort", ".")
    session.run("ruff", ".", "--fix")


@nox.session
def lint(session: nox.Session) -> None:
    session.run("poetry", "install", "--only", "linting")
    session.run("black", ".", "--check")
    session.run("ruff", ".")
    session.run("isort", ".", "--check")
