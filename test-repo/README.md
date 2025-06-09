# 🤖 Smart PR AI Plugin - Enhanced Edition

An intelligent GitLab CI/CD plugin that provides comprehensive AI-powered code review, automated formatting, intelligent tagging, and changelog generation using Google's Gemini AI.

## ✨ Features

### 🔧 **Multi-Language Code Formatting**
- **Python**: Black, isort, autopep8, flake8
- **JavaScript/TypeScript**: Prettier, ESLint
- **JSON/YAML**: Prettier formatting
- **CSS/SCSS**: Prettier formatting
- Automatic backup and rollback on formatting failures
- Detailed formatting reports with statistics

### 🧠 **AI-Powered Code Review**
- Context-aware code analysis using Gemini 1.5 Flash
- Security vulnerability detection
- Performance optimization suggestions
- Best practices enforcement
- Maintainability assessment
- Inline MR comments with specific suggestions

### 🏷️ **Intelligent Auto-Tagging**
- Language-based tags (python, javascript, java, etc.)
- Category tags (frontend, backend, api, security, etc.)
- Severity tags (breaking-change, high-priority, etc.)
- Custom tag rules based on file patterns
- Color-coded labels for easy identification

### 📝 **Automated Changelog Generation**
- Automatic changelog updates on main branch merges
- Categorized entries (Features, Bug Fixes, Security, etc.)
- Author attribution and MR links
- Semantic versioning support
- Customizable changelog format

### 🔒 **Security Analysis**
- Hardcoded secrets detection
- SQL injection vulnerability scanning
- XSS vulnerability detection
- Configurable security severity levels
- Integration with security scanning tools

## 🚀 Quick Start

### 1. Setup Environment Variables

Add these variables to your GitLab project settings (Settings > CI/CD > Variables):

```bash
LLM_API_KEY=your_gemini_api_key_here
GITLAB_PAT=your_gitlab_personal_access_token
```

### 2. Include the Plugin

Add to your `.gitlab-ci.yml`:

```yaml
include:
  - remote: 'https://raw.githubusercontent.com/your-org/smart-pr-ai/main/.gitlab-ci.yml'
```

### 3. Configure (Optional)

Create `.smartpr.yml` in your project root:

```yaml
# Smart PR AI Configuration
max_file_size: 100000
review_focus:
  - security
  - performance
  - maintainability
  - best_practices

language_configs:
  python:
    max_complexity: 10
    enable_security_scan: true
  javascript:
    enable_eslint_suggestions: true

security:
  enable_secret_detection: true
  severity_threshold: "medium"

changelog:
  enabled: true
  group_by_category: true
  include_author: true
```

## 📋 Pipeline Stages

### 1. **Format Stage**
- Automatically formats code files
- Supports multiple languages and tools
- Creates backup files before formatting
- Generates detailed formatting reports
- Fails gracefully with proper error handling

### 2. **Review Stage**
- AI-powered code analysis using Gemini
- Context-aware suggestions and improvements
- Security vulnerability detection
- Performance analysis
- Generates comprehensive review reports

### 3. **Tag Stage**
- Intelligent label application based on AI analysis
- Language and category-based tagging
- Custom tag rules and patterns
- Color-coded labels for easy identification

### 4. **Changelog Stage** (Main Branch Only)
- Automatic changelog generation
- Categorized entries with proper formatting
- Author attribution and MR links
- Integration with semantic versioning

## 🎯 Advanced Features

### Custom Configuration

The plugin supports extensive customization through `.smartpr.yml`:

```yaml
# File processing
max_file_size: 100000
max_files_per_review: 20

# Ignore patterns
ignore_patterns:
  - 'node_modules/*'
  - '*.min.js'
  - 'dist/*'

# AI settings
ai_settings:
  model: "gemini-1.5-flash"
  temperature: 0.3
  focus_on_changes_only: true

# Custom tagging rules
tagging:
  custom_tags:
    - name: "hotfix"
      pattern: "hotfix|urgent|critical"
      color: "#dc3545"
```

### Security Scanning

Built-in security analysis includes:
- **Secret Detection**: API keys, passwords, tokens
- **SQL Injection**: Unsafe database queries
- **XSS Vulnerabilities**: Unsafe DOM manipulation
- **Configurable Thresholds**: Low, medium, high severity

### Language Support

Currently supported languages with specialized handling:
- **Python** (Black, isort, flake8, security scanning)
- **JavaScript/TypeScript** (Prettier, ESLint, security analysis)
- **Java** (Google style guide, security scanning)
- **Go** (gofmt, security analysis)
- **CSS/SCSS** (Prettier formatting)
- **JSON/YAML** (Prettier formatting)

## 📊 Reports and Analytics

The plugin generates comprehensive reports:

### Format Report
- Files processed and success rate
- Detailed formatting statistics
- Error logs and troubleshooting info

### Review Report
- AI analysis summary
- Issue categorization and severity
- Performance impact assessment
- Security vulnerability details

### Tag Report
- Applied labels and categories
- Tagging logic and reasoning
- Custom rule matching results

### Changelog Report
- Generated entries and categories
- Commit statistics and author info
- Semantic versioning recommendations

## 🛠️ Development and Testing

### Test Repository

This repository includes a test environment:

1. **index.html**: Interactive test page with animations
2. **Sample configurations**: Example `.smartpr.yml` files
3. **Mock data**: Test scenarios for different code types

### Local Testing

```bash
# Install dependencies
pip install -r scripts/requirements.txt
npm install -g prettier eslint

# Run individual scripts
python scripts/review_pr.py
python scripts/generate_changelog.py
./scripts/format_files.sh
```

## 🔧 Troubleshooting

### Common Issues

1. **API Rate Limits**: Gemini API has rate limits. Consider caching or batching requests.
2. **Large Files**: Files over 100KB are skipped by default. Adjust `max_file_size` if needed.
3. **Token Permissions**: Ensure GitLab PAT has `api` scope.
4. **Merge Conflicts**: Plugin works best with clean MRs without conflicts.

### Debug Mode

Enable verbose logging by setting:
```bash
DEBUG_MODE=true
```

### Support

- **Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides and examples
- **Community**: Join discussions and share configurations

## 📈 Roadmap

### Upcoming Features
- **Multi-model Support**: Claude, GPT-4 integration
- **Advanced Analytics**: Code quality metrics over time
- **Team Insights**: Developer productivity analytics
- **Custom Rules Engine**: Advanced rule configuration
- **Integration Plugins**: Slack, Teams, email notifications

### Version History

- **v2.0.0**: Enhanced AI review, changelog generation, improved security
- **v1.0.0**: Initial release with basic formatting and review

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests for any improvements.

## 📄 License

MIT License - see LICENSE file for details.

---

**Smart PR AI Plugin** - Making code review intelligent, automated, and efficient.

For support and updates, visit our [GitLab repository](https://gitlab.com/smart-pr-ai/plugin).