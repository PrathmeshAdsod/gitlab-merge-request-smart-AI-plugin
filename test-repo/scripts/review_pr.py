#!/usr/bin/env python3
"""
Enhanced AI-Powered Code Review using Gemini API
Provides intelligent code review with context-aware suggestions
"""

import os
import sys
import json
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
import google.generativeai as genai
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import yaml

console = Console()

class SmartCodeReviewer:
    def __init__(self):
        self.gemini_api_key = os.environ.get('LLM_API_KEY')
        self.gitlab_token = os.environ.get('GITLAB_PAT')
        self.gitlab_url = os.environ.get('CI_SERVER_URL', 'https://gitlab.com')
        self.project_id = os.environ.get('CI_PROJECT_ID')
        self.merge_request_iid = os.environ.get('CI_MERGE_REQUEST_IID')
        self.target_branch = os.environ.get('CI_MERGE_REQUEST_TARGET_BRANCH_NAME', 'main')
        
        if not self.gemini_api_key:
            console.print("❌ LLM_API_KEY environment variable not set", style="red")
            sys.exit(1)
            
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.review_results = []
        self.security_issues = []
        self.suggested_tags = set()
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from .smartpr.yml if exists"""
        config_path = Path('.smartpr.yml')
        default_config = {
            'max_file_size': 50000,  # 50KB
            'ignore_patterns': ['.git/*', 'node_modules/*', '*.min.js', '*.bundle.js'],
            'review_focus': ['security', 'performance', 'maintainability', 'best_practices'],
            'language_configs': {
                'python': {'max_complexity': 10, 'enable_security_scan': True},
                'javascript': {'enable_eslint_suggestions': True},
                'typescript': {'strict_mode_suggestions': True}
            }
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                    default_config.update(user_config or {})
            except Exception as e:
                console.print(f"⚠️ Error loading config: {e}", style="yellow")
        
        return default_config

    def get_changed_files(self) -> List[str]:
        """Get list of changed files in the MR"""
        try:
            if self.merge_request_iid:
                cmd = f"git diff --name-only origin/{self.target_branch}...HEAD"
            else:
                cmd = "git diff --name-only HEAD~1 HEAD"
                
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            # Filter files based on config
            filtered_files = []
            for file in files:
                if self.should_review_file(file):
                    filtered_files.append(file)
            
            return filtered_files
        except Exception as e:
            console.print(f"❌ Error getting changed files: {e}", style="red")
            return []

    def should_review_file(self, file_path: str) -> bool:
        """Check if file should be reviewed based on config"""
        # Check ignore patterns
        for pattern in self.config.get('ignore_patterns', []):
            if re.match(pattern.replace('*', '.*'), file_path):
                return False
        
        # Check file size
        if Path(file_path).exists():
            file_size = Path(file_path).stat().st_size
            if file_size > self.config.get('max_file_size', 50000):
                return False
        
        # Check if it's a code file
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs', 
                          '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.swift', '.kt'}
        return Path(file_path).suffix.lower() in code_extensions

    def get_file_content(self, file_path: str) -> Optional[str]:
        """Get file content safely"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            console.print(f"⚠️ Could not read {file_path}: {e}", style="yellow")
            return None

    def get_file_diff(self, file_path: str) -> Optional[str]:
        """Get diff for a specific file"""
        try:
            if self.merge_request_iid:
                cmd = f"git diff origin/{self.target_branch}...HEAD -- {file_path}"
            else:
                cmd = f"git diff HEAD~1 HEAD -- {file_path}"
                
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            return result.stdout if result.stdout else None
        except Exception as e:
            console.print(f"❌ Error getting diff for {file_path}: {e}", style="red")
            return None

    def analyze_security_issues(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        """Basic security analysis"""
        issues = []
        
        # Common security patterns
        security_patterns = {
            'hardcoded_secrets': [
                r'(password|pwd|pass)\s*=\s*["\'][^"\']+["\']',
                r'(api_key|apikey|secret|token)\s*=\s*["\'][^"\']+["\']',
                r'(SECRET_KEY|API_KEY)\s*=\s*["\'][^"\']+["\']'
            ],
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%s.*["\']',
                r'cursor\.execute\s*\(\s*["\'].*\+.*["\']'
            ],
            'xss_vulnerability': [
                r'innerHTML\s*=\s*.*\+',
                r'document\.write\s*\('
            ]
        }
        
        for category, patterns in security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    issues.append({
                        'file': file_path,
                        'line': line_num,
                        'category': category,
                        'description': f"Potential {category.replace('_', ' ')} detected",
                        'severity': 'high' if category == 'hardcoded_secrets' else 'medium'
                    })
        
        return issues

    def determine_tags(self, file_changes: List[Dict[str, Any]]) -> List[str]:
        """Determine appropriate tags based on file changes"""
        tags = set()
        
        for change in file_changes:
            file_path = change['file']
            
            # Language-based tags
            if file_path.endswith(('.py', '.pyi')):
                tags.add('python')
            elif file_path.endswith(('.js', '.jsx', '.ts', '.tsx')):
                tags.add('javascript')
            elif file_path.endswith('.java'):
                tags.add('java')
            elif file_path.endswith(('.html', '.css')):
                tags.add('frontend')
            elif file_path.endswith(('.yml', '.yaml')):
                tags.add('config')
            elif file_path.endswith('.md'):
                tags.add('documentation')
            
            # Function-based tags
            if 'test' in file_path.lower():
                tags.add('testing')
            if 'api' in file_path.lower():
                tags.add('api')
            if any(word in file_path.lower() for word in ['security', 'auth', 'login']):
                tags.add('security')
            if any(word in file_path.lower() for word in ['db', 'model', 'migration']):
                tags.add('database')
        
        # Determine change type based on review results
        if any(r.get('has_breaking_changes') for r in self.review_results):
            tags.add('breaking-change')
        if any(r.get('performance_impact') for r in self.review_results):
            tags.add('performance')
        if self.security_issues:
            tags.add('security-review-needed')
        
        return sorted(list(tags))

    def create_review_prompt(self, file_path: str, diff: str, content: str) -> str:
        """Create detailed prompt for AI review"""
        language = Path(file_path).suffix.lstrip('.')
        
        prompt = f"""
As an expert code reviewer, analyze this {language} code change and provide constructive feedback.

FILE: {file_path}
LANGUAGE: {language}

DIFF:
```diff
{diff}
```

FULL FILE CONTENT (for context):
```{language}
{content[:3000]}{'...' if len(content) > 3000 else ''}
```

Please analyze and provide feedback on:
1. **Code Quality**: Style, readability, maintainability
2. **Security**: Potential vulnerabilities or security concerns
3. **Performance**: Efficiency and optimization opportunities
4. **Best Practices**: Language-specific conventions and patterns
5. **Error Handling**: Robustness and edge case handling
6. **Testing**: Testability and test coverage considerations

For each issue found, provide:
- Specific line numbers if applicable
- Clear description of the issue
- Suggested improvement
- Severity (high/medium/low)

Also identify:
- Whether this introduces breaking changes
- Performance impact (positive/negative/neutral)
- Required follow-up actions

Respond in JSON format:
{{
  "summary": "Overall assessment summary",
  "issues": [
    {{
      "line": 123,
      "severity": "medium",
      "category": "performance",
      "description": "Issue description",
      "suggestion": "Specific improvement suggestion"
    }}
  ],
  "positive_aspects": ["List of good practices found"],
  "has_breaking_changes": false,
  "performance_impact": "neutral",
  "follow_up_actions": ["List of recommended actions"]
}}
"""
        return prompt

    def review_file(self, file_path: str) -> Dict[str, Any]:
        """Review a single file using AI"""
        console.print(f"🔍 Reviewing: {file_path}")
        
        content = self.get_file_content(file_path)
        if not content:
            return {"file": file_path, "error": "Could not read file"}
        
        diff = self.get_file_diff(file_path)
        if not diff:
            return {"file": file_path, "error": "No changes detected"}
        
        # Security analysis
        security_issues = self.analyze_security_issues(file_path, content)
        self.security_issues.extend(security_issues)
        
        try:
            prompt = self.create_review_prompt(file_path, diff, content)
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            review_data = json.loads(response.text)
            review_data["file"] = file_path
            review_data["security_issues"] = security_issues
            
            return review_data
            
        except json.JSONDecodeError as e:
            console.print(f"⚠️ Failed to parse AI response for {file_path}: {e}", style="yellow")
            return {
                "file": file_path,
                "error": "Failed to parse AI response",
                "raw_response": response.text if 'response' in locals() else "No response"
            }
        except Exception as e:
            console.print(f"❌ Error reviewing {file_path}: {e}", style="red")
            return {"file": file_path, "error": str(e)}

    def post_review_comment(self, review: Dict[str, Any]):
        """Post review comments to GitLab MR"""
        if not self.gitlab_token or not self.merge_request_iid:
            console.print("⚠️ Cannot post comments: Missing GitLab token or MR IID", style="yellow")
            return
        
        headers = {"PRIVATE-TOKEN": self.gitlab_token}
        
        # Create summary comment
        summary = self.create_summary_comment(review)
        
        comment_data = {
            "body": summary
        }
        
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.merge_request_iid}/notes"
        
        try:
            response = requests.post(url, headers=headers, json=comment_data)
            if response.status_code == 201:
                console.print("✅ Posted review comment", style="green")
            else:
                console.print(f"⚠️ Failed to post comment: {response.status_code}", style="yellow")
        except Exception as e:
            console.print(f"❌ Error posting comment: {e}", style="red")

    def create_summary_comment(self, reviews: List[Dict[str, Any]]) -> str:
        """Create a comprehensive summary comment"""
        total_files = len(reviews)
        total_issues = sum(len(r.get('issues', [])) for r in reviews)
        high_severity = sum(1 for r in reviews for issue in r.get('issues', []) if issue.get('severity') == 'high')
        
        comment = f"""## 🤖 Gemini AI Code Review Summary

**Files Reviewed:** {total_files}  
**Issues Found:** {total_issues}  
**High Severity:** {high_severity}  
**Security Issues:** {len(self.security_issues)}

---

"""
        
        for review in reviews:
            if 'error' in review:
                comment += f"### ❌ {review['file']}\n**Error:** {review['error']}\n\n"
                continue
                
            file_name = review['file']
            issues = review.get('issues', [])
            
            comment += f"### 📁 `{file_name}`\n"
            comment += f"**Summary:** {review.get('summary', 'No summary available')}\n\n"
            
            if issues:
                comment += "**Issues Found:**\n"
                for issue in issues[:5]:  # Limit to 5 issues per file
                    severity_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.get('severity', 'low'), '⚪')
                    comment += f"- {severity_emoji} **Line {issue.get('line', 'N/A')}**: {issue.get('description', 'No description')}\n"
                    comment += f"  *Suggestion:* {issue.get('suggestion', 'No suggestion')}\n"
                
                if len(issues) > 5:
                    comment += f"- ... and {len(issues) - 5} more issues\n"
                comment += "\n"
            
            positive_aspects = review.get('positive_aspects', [])
            if positive_aspects:
                comment += "**Positive Aspects:**\n"
                for aspect in positive_aspects[:3]:
                    comment += f"- ✅ {aspect}\n"
                comment += "\n"
        
        if self.security_issues:
            comment += "### 🔒 Security Issues\n"
            for issue in self.security_issues[:3]:
                comment += f"- **{issue['file']}** (Line {issue['line']}): {issue['description']}\n"
            comment += "\n"
        
        # Recommendations
        comment += "### 📋 Recommendations\n"
        comment += "- Review all high-severity issues before merging\n"
        if self.security_issues:
            comment += "- Address security concerns immediately\n"
        comment += "- Consider adding tests for new functionality\n"
        comment += "- Update documentation if needed\n\n"
        
        comment += "*Generated by Smart PR AI Plugin with Gemini*"
        
        return comment

    def save_results(self):
        """Save review results to files"""
        # Save review status
        status = {
            "total_files": len(self.review_results),
            "total_issues": sum(len(r.get('issues', [])) for r in self.review_results),
            "high_severity_issues": sum(1 for r in self.review_results for issue in r.get('issues', []) if issue.get('severity') == 'high'),
            "security_issues": len(self.security_issues),
            "overall_status": "needs_attention" if self.security_issues or any(r.get('has_breaking_changes') for r in self.review_results) else "approved"
        }
        
        with open('ai_review_status.txt', 'w') as f:
            f.write(json.dumps(status, indent=2))
        
        # Save detailed results
        with open('review_summary.json', 'w') as f:
            json.dump(self.review_results, f, indent=2)
        
        # Save security issues
        with open('security_issues.json', 'w') as f:
            json.dump(self.security_issues, f, indent=2)
        
        # Save suggested tags
        tags = self.determine_tags(self.review_results)
        with open('ai_tags.txt', 'w') as f:
            f.write('\n'.join(tags))

    def run(self):
        """Main execution method"""
        console.print("🚀 Starting Smart AI Code Review...", style="bold blue")
        
        changed_files = self.get_changed_files()
        if not changed_files:
            console.print("ℹ️ No files to review", style="blue")
            return
        
        console.print(f"📁 Found {len(changed_files)} files to review")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Reviewing files...", total=len(changed_files))
            
            for file_path in changed_files:
                progress.update(task, description=f"Reviewing {file_path}")
                review_result = self.review_file(file_path)
                self.review_results.append(review_result)
                progress.advance(task)
        
        # Post comments to GitLab
        if self.review_results:
            self.post_review_comment(self.review_results)
        
        # Save results
        self.save_results()
        
        # Summary
        console.print("\n📊 Review Summary:", style="bold")
        console.print(f"  Files reviewed: {len(self.review_results)}")
        console.print(f"  Total issues: {sum(len(r.get('issues', [])) for r in self.review_results)}")
        console.print(f"  Security issues: {len(self.security_issues)}")
        
        if self.security_issues:
            console.print("⚠️ Security issues found - please review carefully!", style="bold red")
        
        console.print("✅ Review completed!", style="bold green")

if __name__ == "__main__":
    reviewer = SmartCodeReviewer()
    reviewer.run()