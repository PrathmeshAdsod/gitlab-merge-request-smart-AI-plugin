#!/usr/bin/env python3
"""
Automated Changelog Generation for Main Branch Merges
"""

import os
import json
import subprocess
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests
import git
from jinja2 import Template

class ChangelogGenerator:
    def __init__(self):
        self.gitlab_token = os.environ.get('GITLAB_PAT')
        self.gitlab_url = os.environ.get('CI_SERVER_URL', 'https://gitlab.com')
        self.project_id = os.environ.get('CI_PROJECT_ID')
        self.commit_sha = os.environ.get('CI_COMMIT_SHA')
        
        self.repo = git.Repo('.')
        self.headers = {"PRIVATE-TOKEN": self.gitlab_token} if self.gitlab_token else {}

    def get_recent_merge_commits(self, days: int = 7) -> List[git.Commit]:
        """Get merge commits from the last N days"""
        try:
            # Get commits from the last N days
            since_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            since_date = since_date.replace(day=since_date.day - days)
            
            commits = list(self.repo.iter_commits(
                'HEAD', 
                since=since_date,
                merges=True
            ))
            
            return commits
        except Exception as e:
            print(f"❌ Error getting merge commits: {e}")
            return []

    def extract_mr_info_from_commit(self, commit: git.Commit) -> Optional[Dict[str, Any]]:
        """Extract MR information from merge commit message"""
        # GitLab merge commit pattern: "Merge branch 'feature-branch' into 'main'"
        # or "Merge request #123 from 'feature-branch'"
        
        message = commit.message
        
        # Extract MR number
        mr_match = re.search(r'Merge (?:request|branch).*?[#!](\d+)', message)
        mr_number = mr_match.group(1) if mr_match else None
        
        # Extract branch name
        branch_match = re.search(r"from '([^']+)'|branch '([^']+)'", message)
        branch_name = None
        if branch_match:
            branch_name = branch_match.group(1) or branch_match.group(2)
        
        # Get commit details
        info = {
            'commit_sha': commit.hexsha,
            'commit_message': message.strip(),
            'author': str(commit.author),
            'author_email': commit.author.email,
            'date': commit.committed_datetime.isoformat(),
            'mr_number': mr_number,
            'branch_name': branch_name,
            'files_changed': [],
            'additions': 0,
            'deletions': 0
        }
        
        # Get changed files (parent[0] is the main branch, parent[1] is the feature branch)
        if len(commit.parents) >= 2:
            try:
                diff = commit.parents[0].diff(commit.parents[1])
                info['files_changed'] = [item.a_path or item.b_path for item in diff]
                
                # Calculate stats
                stats = commit.stats.total
                info['additions'] = stats.get('insertions', 0)
                info['deletions'] = stats.get('deletions', 0)
                
            except Exception as e:
                print(f"⚠️ Error getting diff for commit {commit.hexsha}: {e}")
        
        return info

    def get_mr_details_from_api(self, mr_number: str) -> Optional[Dict[str, Any]]:
        """Get additional MR details from GitLab API"""
        if not self.gitlab_token or not mr_number:
            return None
        
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{mr_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                mr_data = response.json()
                return {
                    'title': mr_data.get('title', 'Unknown'),
                    'description': mr_data.get('description', ''),
                    'labels': mr_data.get('labels', []),
                    'web_url': mr_data.get('web_url', ''),
                    'author': mr_data.get('author', {}).get('name', 'Unknown'),
                    'merged_by': mr_data.get('merged_by', {}).get('name', 'Unknown'),
                    'target_branch': mr_data.get('target_branch', 'main'),
                    'source_branch': mr_data.get('source_branch', 'unknown')
                }
        except Exception as e:
            print(f"⚠️ Error getting MR details for #{mr_number}: {e}")
        
        return None

    def categorize_changes(self, merge_info: Dict[str, Any]) -> str:
        """Categorize the type of change based on files, labels, and commit message"""
        files_changed = merge_info.get('files_changed', [])
        labels = merge_info.get('labels', [])
        commit_message = merge_info.get('commit_message', '').lower()
        title = merge_info.get('title', '').lower()
        
        # Check labels first
        if any(label in ['breaking-change', 'major'] for label in labels):
            return 'breaking'
        if any(label in ['feature', 'enhancement'] for label in labels):
            return 'feature'
        if any(label in ['bugfix', 'fix', 'bug'] for label in labels):
            return 'fix'
        if any(label in ['security'] for label in labels):
            return 'security'
        if any(label in ['performance'] for label in labels):
            return 'performance'
        if any(label in ['documentation', 'docs'] for label in labels):
            return 'docs'
        
        # Check commit message and title
        if any(word in commit_message or word in title for word in ['break', 'breaking', 'major']):
            return 'breaking'
        if any(word in commit_message or word in title for word in ['feat', 'feature', 'add', 'new']):
            return 'feature'
        if any(word in commit_message or word in title for word in ['fix', 'bug', 'patch', 'repair']):
            return 'fix'
        if any(word in commit_message or word in title for word in ['security', 'vulnerability', 'cve']):
            return 'security'
        if any(word in commit_message or word in title for word in ['perf', 'performance', 'optimize']):
            return 'performance'
        if any(word in commit_message or word in title for word in ['doc', 'readme', 'documentation']):
            return 'docs'
        
        # Check file patterns
        if any('test' in f.lower() for f in files_changed):
            return 'test'
        if any(f.endswith('.md') for f in files_changed):
            return 'docs'
        if any(f.startswith('.') or 'config' in f.lower() for f in files_changed):
            return 'config'
        
        return 'other'

    def generate_changelog_entry(self, merge_commits: List[Dict[str, Any]]) -> str:
        """Generate changelog entry for the commits"""
        if not merge_commits:
            return ""
        
        # Group by category
        categories = {
            'breaking': {'title': '💥 Breaking Changes', 'items': []},
            'security': {'title': '🔒 Security', 'items': []},
            'feature': {'title': '✨ Features', 'items': []},
            'fix': {'title': '🐛 Bug Fixes', 'items': []},
            'performance': {'title': '⚡ Performance', 'items': []},
            'docs': {'title': '📚 Documentation', 'items': []},
            'test': {'title': '🧪 Tests', 'items': []},
            'config': {'title': '⚙️ Configuration', 'items': []},
            'other': {'title': '🔧 Other Changes', 'items': []}
        }
        
        for commit_info in merge_commits:
            category = self.categorize_changes(commit_info)
            
            # Create changelog item
            title = commit_info.get('title', commit_info.get('commit_message', 'Unknown change'))
            author = commit_info.get('author', 'Unknown')
            mr_number = commit_info.get('mr_number')
            web_url = commit_info.get('web_url')
            
            item = f"- {title}"
            if author:
                item += f" (by @{author})"
            if mr_number and web_url:
                item += f" ([#{mr_number}]({web_url}))"
            elif mr_number:
                item += f" (#{mr_number})"
            
            categories[category]['items'].append(item)
        
        # Build changelog content
        changelog_content = f"## [{datetime.now().strftime('%Y-%m-%d')}]\n\n"
        
        for category_data in categories.values():
            if category_data['items']:
                changelog_content += f"### {category_data['title']}\n\n"
                for item in category_data['items']:
                    changelog_content += f"{item}\n"
                changelog_content += "\n"
        
        return changelog_content

    def update_changelog_file(self, new_entry: str):
        """Update the CHANGELOG.md file"""
        changelog_path = Path('CHANGELOG.md')
        
        # Read existing changelog or create header
        if changelog_path.exists():
            with open(changelog_path, 'r') as f:
                existing_content = f.read()
        else:
            existing_content = "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
        
        # Insert new entry after the header
        lines = existing_content.split('\n')
        header_end = 0
        
        # Find where to insert (after initial header/description)
        for i, line in enumerate(lines):
            if line.startswith('## '):
                header_end = i
                break
        else:
            # No existing releases, add after header
            header_end = len(lines)
        
        # Insert new entry
        new_lines = lines[:header_end] + new_entry.split('\n') + lines[header_end:]
        
        # Write updated changelog
        with open(changelog_path, 'w') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ Updated {changelog_path}")

    def create_summary_report(self, merge_commits: List[Dict[str, Any]]):
        """Create a summary report of the changelog update"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_commits': len(merge_commits),
            'commits': merge_commits,
            'categories': {},
            'stats': {
                'total_additions': sum(c.get('additions', 0) for c in merge_commits),
                'total_deletions': sum(c.get('deletions', 0) for c in merge_commits),
                'unique_authors': len(set(c.get('author', 'Unknown') for c in merge_commits))
            }
        }
        
        # Count by category
        for commit_info in merge_commits:
            category = self.categorize_changes(commit_info)
            summary['categories'][category] = summary['categories'].get(category, 0) + 1
        
        with open('changelog_update.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Summary: {len(merge_commits)} commits from {summary['stats']['unique_authors']} authors")

    def run(self):
        """Main execution method"""
        print("📝 Starting Changelog Generation...")
        
        # Get recent merge commits
        merge_commits = self.get_recent_merge_commits(days=1)  # Only today's merges
        
        if not merge_commits:
            print("ℹ️ No recent merge commits found")
            return
        
        print(f"🔍 Found {len(merge_commits)} merge commits")
        
        # Process commits and get additional info
        processed_commits = []
        for commit in merge_commits:
            commit_info = self.extract_mr_info_from_commit(commit)
            
            # Enhance with API data if available
            if commit_info and commit_info.get('mr_number'):
                api_info = self.get_mr_details_from_api(commit_info['mr_number'])
                if api_info:
                    commit_info.update(api_info)
            
            if commit_info:
                processed_commits.append(commit_info)
        
        if not processed_commits:
            print("ℹ️ No processable commits found")
            return
        
        # Generate changelog entry
        changelog_entry = self.generate_changelog_entry(processed_commits)
        
        if changelog_entry.strip():
            # Update changelog file
            self.update_changelog_file(changelog_entry)
            
            # Create summary report
            self.create_summary_report(processed_commits)
            
            print(f"✅ Changelog updated with {len(processed_commits)} entries")
        else:
            print("ℹ️ No changelog entries to add")

if __name__ == "__main__":
    generator = ChangelogGenerator()
    generator.run()