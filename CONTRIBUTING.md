# Contributing to GOAT SDK Python

First off, thank you for considering contributing to GOAT SDK Python! It's people like you that make GOAT SDK Python such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include any error messages or stack traces

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fork the repo and create your branch from `main`
* If you've added code that should be tested, add tests
* If you've changed APIs, update the documentation
* Ensure the test suite passes
* Make sure your code lints
* Issue that pull request!

## Development Process

1. Fork the repository
2. Create a new branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run the tests: `poetry run pytest`
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature/my-feature`
7. Submit a pull request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/GOAT-sdk-py.git
cd GOAT-sdk-py

# Install poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Run tests
poetry run pytest
```

### Code Style

* Use [Black](https://github.com/psf/black) for code formatting
* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
* Write docstrings for all public modules, functions, classes, and methods
* Use type hints for all function arguments and return values

## Documentation

* Keep README.md and all other documentation up to date
* Use clear and consistent terminology
* Include examples for new features
* Update the CHANGELOG.md file

## Questions?

Feel free to contact the project maintainers if you have any questions. 