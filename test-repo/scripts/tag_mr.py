#!/usr/bin/env python3
"""
Intelligent MR Tagging based on AI Review Results
"""

import os
import json
import requests
from typing import List, Dict, Any
import sys

class IntelligentTagger:
    def __init__(self):
        self.gitlab_token = os.environ.get('GITLAB_PAT')
        self.gitlab_url = os.environ.get('CI_SERVER_URL', 'https://gitlab.com')
        self.project_id = os.environ.get('CI_PROJECT_ID')
        self.merge_request_iid = os.environ.get('CI_MERGE_REQUEST_IID')
        
        if not all([self.gitlab_token, self.project_id, self.merge_request_iid]):
            print("❌ Missing required environment variables")
            sys.exit(1)
        
        self.headers = {"PRIVATE-TOKEN": self.gitlab_token}

    def load_ai_tags(self) -> List[str]:
        """Load tags suggested by AI review"""
        try:
            with open('ai_tags.txt', 'r') as f:
                return [tag.strip() for tag in f.readlines() if tag.strip()]
        except FileNotFoundError:
            print("⚠️ No AI tags file found")
            return []

    def load_review_status(self) -> Dict[str, Any]:
        """Load review status"""
        try:
            with open('ai_review_status.txt', 'r') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            print("⚠️ No review status file found")
            return {}

    def get_existing_labels(self) -> List[str]:
        """Get existing labels in the project"""
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/labels"
        
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return [label['name'] for label in response.json()]
            else:
                print(f"⚠️ Failed to get existing labels: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error getting labels: {e}")
            return []

    def create_label_if_needed(self, label_name: str, color: str = "#1f77b4") -> bool:
        """Create label if it doesn't exist"""
        existing_labels = self.get_existing_labels()
        
        if label_name in existing_labels:
            return True
        
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/labels"
        data = {
            "name": label_name,
            "color": color,
            "description": f"Auto-generated label by Smart PR AI"
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            if response.status_code == 201:
                print(f"✅ Created label: {label_name}")
                return True
            else:
                print(f"⚠️ Failed to create label {label_name}: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error creating label {label_name}: {e}")
            return False

    def apply_labels_to_mr(self, labels: List[str]) -> bool:
        """Apply labels to the merge request"""
        url = f"{self.gitlab_url}/api/v4/projects/{self.project_id}/merge_requests/{self.merge_request_iid}"
        
        data = {"labels": ",".join(labels)}
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            if response.status_code == 200:
                print(f"✅ Applied labels: {', '.join(labels)}")
                return True
            else:
                print(f"⚠️ Failed to apply labels: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error applying labels: {e}")
            return False

    def determine_label_colors(self) -> Dict[str, str]:
        """Define colors for different label types"""
        return {
            # Languages
            'python': '#3776ab',
            'javascript': '#f7df1e',
            'typescript': '#3178c6',
            'java': '#ed8b00',
            'go': '#00add8',
            'rust': '#000000',
            
            # Categories
            'frontend': '#61dafb',
            'backend': '#8cc84b',
            'api': '#ff6600',
            'database': '#336791',
            'security': '#dc3545',
            'performance': '#28a745',
            'testing': '#6f42c1',
            'documentation': '#6c757d',
            'config': '#ffc107',
            
            # Severity
            'breaking-change': '#dc3545',
            'security-review-needed': '#fd7e14',
            'needs-testing': '#20c997',
            'ready-for-review': '#28a745',
            
            # Status
            'ai-reviewed': '#17a2b8',
            'high-priority': '#dc3545',
            'low-priority': '#6c757d'
        }

    def enhance_tags_with_context(self, ai_tags: List[str], review_status: Dict[str, Any]) -> List[str]:
        """Enhance AI-suggested tags with additional context"""
        enhanced_tags = ai_tags.copy()
        
        # Add status-based tags
        if review_status.get('security_issues', 0) > 0:
            enhanced_tags.append('security-review-needed')
        
        if review_status.get('high_severity_issues', 0) > 0:
            enhanced_tags.append('high-priority')
        elif review_status.get('total_issues', 0) == 0:
            enhanced_tags.append('ready-for-review')
        
        # Add review status tag
        enhanced_tags.append('ai-reviewed')
        
        # Add priority based on issue count
        total_issues = review_status.get('total_issues', 0)
        if total_issues > 10:
            enhanced_tags.append('needs-attention')
        elif total_issues == 0:
            enhanced_tags.append('clean-code')
        
        return list(set(enhanced_tags))  # Remove duplicates

    def run(self):
        """Main execution method"""
        print("🏷️ Starting Intelligent MR Tagging...")
        
        # Load AI suggestions
        ai_tags = self.load_ai_tags()
        review_status = self.load_review_status()
        
        if not ai_tags:
            print("ℹ️ No AI tags to apply")
            return
        
        print(f"🤖 AI suggested tags: {', '.join(ai_tags)}")
        
        # Enhance tags with context
        final_tags = self.enhance_tags_with_context(ai_tags, review_status)
        print(f"🔄 Enhanced tags: {', '.join(final_tags)}")
        
        # Get label colors
        label_colors = self.determine_label_colors()
        
        # Create labels if needed
        created_labels = []
        for tag in final_tags:
            color = label_colors.get(tag, '#1f77b4')  # Default blue
            if self.create_label_if_needed(tag, color):
                created_labels.append(tag)
        
        # Apply labels to MR
        if created_labels:
            success = self.apply_labels_to_mr(created_labels)
            
            # Save applied tags for reporting
            result = {
                "applied_tags": created_labels,
                "success": success,
                "review_summary": review_status
            }
            
            with open('applied_tags.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            if success:
                print(f"✅ Successfully applied {len(created_labels)} labels")
            else:
                print("❌ Failed to apply some labels")
        else:
            print("⚠️ No labels were created or applied")

if __name__ == "__main__":
    tagger = IntelligentTagger()
    tagger.run()