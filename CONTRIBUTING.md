# Contributing to Ecommerce-Django-REST-APIs (RadinGalleryAPI)

We appreciate your interest in contributing to this project! Whether you are fixing bugs, adding features, or improving the documentation, your contributions are welcome and valuable.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Setting Up the Project](#setting-up-the-project)
4. [Pull Request Guidelines](#pull-request-guidelines)
5. [Reporting Issues](#reporting-issues)
6. [Coding Standards](#coding-standards)

---

## Code of Conduct

By participating in this project, you agree to follow our [Code of Conduct](./CODE_OF_CONDUCT.md). Please ensure that all interactions are respectful, professional, and constructive.

---

## How to Contribute

You can contribute in the following ways:

1. **Report Bugs**: If you find a bug, open an issue and provide details.
2. **Fix Bugs**: Fork the repository, create a branch, fix the bug, and submit a pull request.
3. **Add Features**: Suggest or implement new features with clear explanations.
4. **Improve Documentation**: Update documentation to make it clearer or add missing sections.
5. **Write Tests**: Add or improve test cases to increase code reliability.

---

## Setting Up the Project

Follow these steps to set up the project locally:

1. **Fork and Clone**  
   Fork the repository and clone it to your local machine:
   ```bash
   git clone https://github.com/<your-username>/Ecommerce-Django-REST-APIs.git
   cd Ecommerce-Django-REST-APIs
   ```

2. **Create a Virtual Environment**  
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install Dependencies**  
   Install all required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**  
   Copy `.env.example` to `.env` and configure necessary variables.

5. **Run Docker Containers**  
   Build and run the application using Docker:
   ```bash
   docker-compose up --build
   ```

6. **Run Tests**  
   Run the tests to verify everything is working:
   ```bash
   pytest
   ```

---

## Pull Request Guidelines

To submit a Pull Request (PR), please follow these steps:

1. **Create a Branch**  
   Make a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write Clear Commit Messages**  
   Use descriptive and clear commit messages:
   ```bash
   git commit -m "Add: description of your changes"
   ```

3. **Test Your Changes**  
   Ensure that all tests pass:
   ```bash
   pytest
   ```

4. **Push to Your Fork**  
   Push your changes to your forked repository:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**  
   Open a PR on GitHub and describe your changes clearly.

---

## Reporting Issues

If you encounter any bugs or have feature requests, please open an issue on GitHub. When reporting issues, include:
- A clear and descriptive title.
- Steps to reproduce the issue.
- Expected and actual behavior.
- Screenshots or logs if applicable.

---

## Coding Standards

To ensure consistency and quality, please follow these coding standards:

1. **PEP8 Guidelines**  
   Follow Python's PEP8 style guide for code formatting.

2. **Format Code with Black**  
   Use `black` for automatic code formatting:
   ```bash
   pip install black
   black .
   ```

3. **Lint with Flake8**  
   Use `flake8` to check for coding errors and lint issues:
   ```bash
   pip install flake8
   flake8 .
   ```

4. **Add Docstrings**  
   Include meaningful docstrings for functions, classes, and modules.

5. **Write Tests**  
   Ensure any new functionality is covered with tests using `pytest`.

---

## Thank You 🎉

We appreciate your contributions to this project! Every bug fix, feature addition, or documentation improvement helps make this project better for everyone. If you have any questions, feel free to reach out or open an issue for further discussion.
