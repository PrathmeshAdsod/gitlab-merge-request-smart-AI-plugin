# Changelog

All notable changes to the Smart PR AI Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-19

### 💥 Breaking Changes
- Restructured configuration file format from `.smartpr.json` to `.smartpr.yml`
- Changed API endpoints for custom integrations
- Updated minimum required GitLab version to 15.0+

### ✨ Features
- **Enhanced AI Review Engine**: Upgraded to Gemini 1.5 Flash with context-aware analysis
- **Automated Changelog Generation**: Automatic changelog updates on main branch merges
- **Multi-Language Code Formatting**: Added support for TypeScript, Go, Rust, and CSS
- **Security Vulnerability Scanning**: Built-in detection for secrets, SQL injection, and XSS
- **Intelligent Auto-Tagging**: AI-powered tag suggestions based on code changes
- **Performance Analysis**: Optimization suggestions and performance impact assessment
- **Custom Configuration System**: Extensive customization through `.smartpr.yml`
- **HTML Report Generation**: Visual reports with charts and statistics
- **Batch Processing**: Handle multiple files efficiently with progress tracking

### 🐛 Bug Fixes
- Fixed formatting failures causing pipeline crashes
- Resolved GitLab API rate limiting issues
- Corrected MR comment threading problems
- Fixed changelog generation for merge commits
- Resolved memory leaks in large file processing

### 🔒 Security
- Enhanced secret detection with improved pattern matching
- Added support for custom security rules
- Implemented secure token handling
- Added audit logging for security events

### ⚡ Performance
- Optimized AI API calls with intelligent caching
- Reduced pipeline execution time by 40%
- Implemented parallel processing for multiple files
- Added smart file filtering to skip unnecessary reviews

### 📚 Documentation
- Complete rewrite of documentation with examples
- Added troubleshooting guide and FAQ
- Created configuration reference guide
- Added video tutorials and demos

### 🧪 Tests
- Added comprehensive test suite for all components
- Implemented integration tests with GitLab API
- Added performance benchmarking tests
- Created mock environments for testing

### ⚙️ Configuration
- New YAML-based configuration system
- Environment-specific config support
- Advanced rule customization options
- Backward compatibility mode for legacy configs

## [1.2.1] - 2024-11-15

### 🐛 Bug Fixes
- Fixed issue with Python formatting on special characters
- Resolved GitLab comment permissions error
- Corrected tag color application

### 📚 Documentation
- Updated README with new examples
- Added configuration troubleshooting section

## [1.2.0] - 2024-11-01

### ✨ Features
- Added support for JavaScript and TypeScript formatting
- Introduced basic security scanning
- Enhanced error reporting and logging

### 🔒 Security
- Added basic secret detection patterns
- Implemented secure environment variable handling

### ⚡ Performance
- Optimized file processing for large repositories
- Reduced memory usage during formatting

## [1.1.0] - 2024-10-15

### ✨ Features
- Added AI-powered code review using Gemini API
- Implemented automatic MR commenting
- Added basic tagging functionality

### 🐛 Bug Fixes
- Fixed Python formatting edge cases
- Resolved pipeline artifact issues

### 📚 Documentation
- Added API documentation
- Created setup guide

## [1.0.0] - 2024-10-01

### ✨ Features
- Initial release of Smart PR AI Plugin
- Python code formatting with Black and isort
- Basic GitLab CI/CD integration
- Simple MR detection and processing

### 📚 Documentation
- Basic README and setup instructions
- Initial component specification

---

## Legend

- 💥 Breaking Changes
- ✨ Features  
- 🐛 Bug Fixes
- 🔒 Security
- ⚡ Performance
- 📚 Documentation
- 🧪 Tests
- ⚙️ Configuration
- 🔧 Other Changes