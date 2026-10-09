
# Development and Testing

## Development dependencies

Install the project and its development dependencies:

```bash
pip install -e ".[dev]"
```

## Automated tests

Run the complete test suite:

```bash
python -m pytest -v
```

Run tests that do not require the real dataset:

```bash
python -m pytest -m "not integration"
```

Integration tests requiring `anime.csv` are skipped when the dataset is unavailable, according to the project's pytest configuration.

## Code quality

Run Ruff linting:

```bash
ruff check .
```

Check formatting:

```bash
ruff format --check .
```

Run static type checking:

```bash
mypy src/
```

## Continuous integration

GitHub Actions runs the configured CI workflow for pushes to `main` and pull requests targeting `main`.

The workflow installs the project, runs the tests and executes Ruff lint checks.

[View CI workflow runs](https://github.com/sunilnarayan419-ui/Anime-Analytics-API/actions)

## Making changes

1. Create a branch for your change.
2. Implement the change and add or update tests.
3. Run the test suite and quality checks.
4. Review the changes with `git diff`.
5. Commit and push your branch.
6. Review the CI result before merging.

## Documentation maintenance

When API behavior changes, update the relevant documentation and examples alongside the implementation.

Run `mkdocs build --strict` before publishing the documentation site.
