# Contributing to Causal Media/Marketing App

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:
- A clear, descriptive title
- Detailed steps to reproduce the bug
- Expected vs. actual behavior
- Your environment (Python version, OS, browser)
- Screenshots if applicable
- Minimal code example that demonstrates the issue

### Suggesting Enhancements

Enhancement suggestions are welcome! Please create an issue with:
- A clear, descriptive title
- Detailed explanation of the proposed feature
- Use cases and benefits
- Any relevant examples or mockups

### Pull Requests

1. **Fork the repository** and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Set up your development environment**:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Make your changes**:
   - Write clear, readable code
   - Follow existing code style and conventions
   - Add comments for complex logic
   - Update documentation as needed

4. **Test your changes**:
   - Run the app locally: `streamlit run app.py`
   - Test all affected functionality
   - Try with different data sources
   - Verify estimators still work correctly

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```
   
   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for improvements to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring
   - `Test:` for test additions/changes

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** with:
   - Clear title describing the change
   - Detailed description of what changed and why
   - Reference to any related issues
   - Screenshots/examples if applicable

## 📋 Development Guidelines

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use type hints where appropriate
- Keep functions focused and modular
- Aim for clear, self-documenting code
- Add docstrings for functions and classes

Example:
```python
def calculate_effect(
    treatment: pd.Series,
    outcome: pd.Series,
    confounders: List[str]
) -> float:
    """Calculate the causal effect of treatment on outcome.
    
    Args:
        treatment: Treatment variable values
        outcome: Outcome variable values
        confounders: List of confounder variable names
        
    Returns:
        Estimated average treatment effect (ATE)
    """
    # Implementation
```

### Project Structure

```
causalapp/
├── app.py                  # Main Streamlit application
├── utils/
│   └── synthetic.py        # Synthetic data generation
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── LICENSE                # MIT License
├── CONTRIBUTING.md        # This file
└── CHANGELOG.md           # Version history
```

### Adding New Features

When adding new features, consider:

1. **Modularity**: Keep code modular and reusable
2. **Error Handling**: Add appropriate try-catch blocks
3. **User Feedback**: Provide clear feedback/progress indicators
4. **Documentation**: Update README and add inline comments
5. **Backward Compatibility**: Don't break existing functionality

### Testing

While we don't have formal unit tests yet, please:
- Test manually with various datasets
- Try edge cases (small data, missing values, extreme values)
- Test all data sources (CSV, Google Sheets, synthetic)
- Verify all tabs and features work
- Check browser console for errors

## 🎯 Priority Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- [ ] Unit tests and integration tests
- [ ] Time-series and lagged effects support
- [ ] Instrumental variables estimation
- [ ] Export functionality (PDF reports, publication-ready plots)
- [ ] Performance optimization for large datasets

### Medium Priority
- [ ] Additional estimation methods
- [ ] More refutation tests
- [ ] Automated confounder detection
- [ ] Database connectivity
- [ ] Docker containerization
- [ ] CI/CD pipeline

### Nice to Have
- [ ] Multi-language support (i18n)
- [ ] Dark mode toggle
- [ ] Mobile-responsive design improvements
- [ ] Video tutorials
- [ ] Interactive demos

## 📝 Documentation

When contributing, please update relevant documentation:

- **README.md**: For user-facing features
- **CHANGELOG.md**: For all changes
- **Code comments**: For complex logic
- **Docstrings**: For functions and classes
- **This file**: For contribution process changes

## 🐛 Bug Fix Process

1. Create an issue describing the bug
2. Fork and create a branch: `bugfix/issue-number-description`
3. Fix the bug with minimal changes
4. Test thoroughly
5. Submit PR referencing the issue

## ⚖️ Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Assume good intentions
- Keep discussions professional

## 📞 Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Check existing issues for similar questions
- Reach out via email (see README for contact info)

## 🙏 Recognition

All contributors will be:
- Listed in the project's contributors
- Credited in release notes
- Appreciated for their time and effort!

Thank you for helping improve this project! 🎉

