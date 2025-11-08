# Contributing to Federated AI

Thank you for your interest in contributing to the Federated AI project! This document provides guidelines for contributing.

## 🔧 Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/federated-ai.git
   cd federated-ai
   ```

2. **Set up development environment**
   ```bash
   # Using Docker (recommended)
   cd docker
   docker compose up -d
   
   # Or manual setup
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements/server.txt
   ```

3. **Create a branch for your feature**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Coding Standards

### Python Code
- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for all functions/classes
- Keep functions small and focused (<50 lines)
- Use meaningful variable names

### Kotlin/Java (Android)
- Follow official Kotlin coding conventions
- Use Jetpack Compose for UI
- Implement MVVM architecture
- Use Hilt for dependency injection
- Write unit tests for ViewModels and Use Cases

### Git Commits
- Use conventional commit messages:
  - `feat:` for new features
  - `fix:` for bug fixes
  - `docs:` for documentation
  - `refactor:` for code refactoring
  - `test:` for adding tests
  - `chore:` for maintenance

Example:
```
feat: add model versioning system

- Implement SHA256 verification
- Add automatic rollback on failure
- Update API endpoints
```

## 🧪 Testing

### Run Tests
```bash
# Python tests
pytest

# With coverage
pytest --cov=server --cov-report=html

# Android tests
cd android-mobo
./gradlew test
./gradlew connectedAndroidTest
```

### Writing Tests
- Write tests for new features
- Maintain >80% code coverage
- Use descriptive test names
- Mock external dependencies

## 📦 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** with your changes
5. **Create pull request** with clear description

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No merge conflicts
- [ ] Descriptive commit messages
- [ ] Screenshots included (for UI changes)

## 🐛 Reporting Bugs

Use GitHub Issues with the bug template:
- **Description**: Clear description of the bug
- **Steps to reproduce**: Detailed steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, etc.
- **Logs**: Relevant error messages

## 💡 Suggesting Features

Use GitHub Issues with the feature template:
- **Problem**: What problem does this solve?
- **Solution**: Proposed solution
- **Alternatives**: Other approaches considered
- **Additional context**: Screenshots, mockups, etc.

## 📖 Documentation

- Keep README.md up to date
- Document API changes
- Add inline code comments
- Update guides in `docs/`

## 🤝 Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Give constructive feedback
- Focus on what's best for the project

## 📧 Questions?

- Create a GitHub Discussion
- Join our community chat
- Email: your-email@example.com

---

Thank you for contributing! 🎉
