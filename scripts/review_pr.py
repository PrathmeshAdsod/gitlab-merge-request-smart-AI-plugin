#!/usr/bin/env python3
"""
AI Review Script for GitLab Merge Requests

- Fetches changed files in the MR
- Gets their diffs and MR description
- Sends to LLM for review
- Posts inline comments via GitLab API

Environment variables:
  - LLM_API_KEY: Your LLM provider API key
  - GITLAB_PAT: GitLab Personal Access Token (api scope)
  - CI_PROJECT_ID, CI_MERGE_REQUEST_IID, CI_API_V4_URL, etc. (from GitLab CI)
"""

import os
import sys
import requests
import json

# --- Config ---
LLM_API_KEY = os.getenv("LLM_API_KEY")
GITLAB_PAT = os.getenv("GITLAB_PAT")
CI_PROJECT_ID = os.getenv("CI_PROJECT_ID")
CI_MERGE_REQUEST_IID = os.getenv("CI_MERGE_REQUEST_IID")
CI_API_V4_URL = os.getenv("CI_API_V4_URL", "https://gitlab.com/api/v4")

if not all([LLM_API_KEY, GITLAB_PAT, CI_PROJECT_ID, CI_MERGE_REQUEST_IID]):
    print("Missing required environment variables.", file=sys.stderr)
    sys.exit(1)

HEADERS = {"PRIVATE-TOKEN": GITLAB_PAT}

def get_mr_changes():
    url = f"{CI_API_V4_URL}/projects/{CI_PROJECT_ID}/merge_requests/{CI_MERGE_REQUEST_IID}/changes"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["changes"]

def get_mr_description():
    url = f"{CI_API_V4_URL}/projects/{CI_PROJECT_ID}/merge_requests/{CI_MERGE_REQUEST_IID}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("description", "")

def build_prompt(changes, description):
    prompt = {
        "issue_description": description,
        "diffs": [],
        "instructions": (
            "Review the following code diffs. For each, identify bugs, code smells, or missing edge cases. "
            "Suggest better variable/function/class names. Propose docstring or README updates if needed. "
            "Draft a 1-sentence PR summary and a changelog entry. "
            "Respond in JSON: [{file, line, issue, suggestion}], plus 'pr_summary' and 'changelog_entry'."
        )
    }
    for change in changes:
        if any(change["new_path"].endswith(ext) for ext in [".py", ".js", ".ts", ".go", ".rb"]):
            prompt["diffs"].append({
                "file": change["new_path"],
                "diff": change["diff"]
            })
    return prompt

def call_llm(prompt):
    """
    Calls Gemini API for code review suggestions.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key=" + LLM_API_KEY
    headers = {"Content-Type": "application/json"}
    gemini_prompt = {
        "contents": [
            {"role": "user", "parts": [
                {"text": (
                    "You are an AI code reviewer. Based on the provided PR diff and issue context, return helpful suggestions to improve code quality, clarity, and documentation — without changing logic. "
                    "For each suggestion, explain why it's being made, and return structured JSON with file, line, and type. Do not propose changes outside the modified lines.\n"
                    "Types of suggestions:\n"
                    "- Variable/function renaming (for clarity)\n"
                    "- Comment enhancement (for readability)\n"
                    "- Docstring updates\n"
                    "- Code style improvements\n"
                    "- README or documentation notice (summary only)\n"
                    "Always return suggestions in a way that a developer can manually apply them after review. Do not make changes automatically.\n"
                    f"\nPR DIFFS AND CONTEXT:\n{json.dumps(prompt)}"
                )}
            ]}
        ]
    }
    resp = requests.post(url, headers=headers, json=gemini_prompt)
    resp.raise_for_status()
    # Gemini returns suggestions in the 'candidates' field
    content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    try:
        return json.loads(content)
    except Exception:
        print("Gemini response not valid JSON:", content, file=sys.stderr)
        sys.exit(1)

def post_inline_comment(file, line, suggestion):
    # Posts suggestion as an inline comment with Accept/Reject instructions
    url = f"{CI_API_V4_URL}/projects/{CI_PROJECT_ID}/merge_requests/{CI_MERGE_REQUEST_IID}/discussions"
    body = (
        f"**Gemini AI Suggestion**\n\n"
        f"**File:** `{file}`  \n"
        f"**Line:** {line}  \n"
        f"**Type:** {suggestion.get('suggestion_type', 'suggestion')}  \n"
        f"**Suggestion:** {suggestion.get('suggested_change', '')}  \n"
        f"**Why:** {suggestion.get('explanation', '')}  \n"
        f"**Confidence:** {suggestion.get('confidence', 'n/a')}\n\n"
        f"---\n"
        f"To apply this suggestion, click **Accept** below or copy the change manually.\n"
        f"[Accept] | [Reject]"
    )
    payload = {
        "body": body,
        "position": {
            "position_type": "text",
            "new_path": file,
            "new_line": line
        }
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if not resp.ok:
        print(f"Failed to post comment on {file}:{line}: {resp.text}", file=sys.stderr)

def main():
    try:
        changes = get_mr_changes()
        description = get_mr_description()
        prompt = build_prompt(changes, description)
        ai_response = call_llm(prompt)

        # Post inline suggestions with Accept/Reject
        for suggestion in ai_response:
            if not isinstance(suggestion, dict):
                continue
            file = suggestion.get("file")
            line = suggestion.get("line")
            if file and line:
                post_inline_comment(file, line, suggestion)

        # Optionally, post a summary comment with Accept All/Reject All instructions
        url = f"{CI_API_V4_URL}/projects/{CI_PROJECT_ID}/merge_requests/{CI_MERGE_REQUEST_IID}/notes"
        summary_body = (
            "**Gemini AI Review Complete**\n\n"
            "You can Accept/Reject suggestions individually in the MR comments above, or use the following instructions to apply all at once.\n\n"
            "- To **Accept All**, apply all suggested changes manually or with a script.\n"
            "- To **Reject All**, ignore the suggestions.\n"
            "\n---\n"
            "*No changes are made automatically. You are in control!*"
        )
        requests.post(url, headers=HEADERS, json={"body": summary_body})

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
