# Contributing

## Tooling Guide


### Poetry
mCodingBot bot uses poetry for package managing. Poetry can be installed [with thier official instructions](https://python-poetry.org/docs/#installation).

Before you start coding you have to activate your env with `poetry shell`.

The bot can be run with `python -m mcodingbot`.


### Linting
these commands can be run to lint your code.

```
# check if your code is properly linted
nox -s lint

# check for typing issues
nox -s mypy

# fix linting errors with black, codespell, and isort.
nox -s apply-lint
```

Your code must pass the `mypy` and `lint` nox pipelines to be merged.


## Style Guide

### Imports
All modules use `import mod`.
The typing module is the only exception where you are allowed to do `from typing import T`.

Code from the bot itself itself is always imported as `from bot.a import b`.
