# Contributing Guide

## Initial Setup

To begin contributing to mCodingBot, you must first fork the repository. After forking, clone:

```
git clone <url to your fork>
cd mCodingBot
```

Next, you need to set up poetry.

```
curl -sSL https://install.python-poetry.org | python3 -
poetry install
```

See the [installation guide](https://python-poetry.org/docs/#installation) for alternative methods.

## Running the Bot

First, if you're making changes that require the database, you will need to set up Postgres. Once installed, create a user named `mcodingbot`, and then a database called `mcodingbot` that is owned by that user.

To run the bot, you first need to set up your `config.json` file. Look at [config.json.example](https://github.com/mcb-dev/mCodingBot/blob/main/config.json.example) for an example configuration. Make sure to set `no_db_mode: true` if you chose not to set up Postgres. If you did set up Postgres, you only need to put your password (if any) in the `config.json`.

Once the config is set up, you can run the bot with `poetry run python3 -m mcodingbot`.

## Contributing

To create a pull request to mCodingBot, first create a new branch for your changes.

```
git checkout -b <new-branch-name>
```

Then, open the source in your editor of choice, and make changes. After making changes, make sure that they pass the pipelines by running `nox`.

```bash
poetry run nox                # run all pipelines
poetry run nox -s mypy        # check only the mypy pipeline
poetry run nox -s apply-lint  # run black and isort
poetry run nos -s lint        # checks if flake8, black, and isort all pass
```

The `mypy` and `lint` pipelines must pass for any PR to be accepted.

Once the pipelines pass, you can push your changes to your branch. Try to use descriptive commit messages, and it is usually best to split changes into individual commits, if possible.

After pushing changes, create a PR to merge your changes into mCodingBot. This can be done from GitHub.
