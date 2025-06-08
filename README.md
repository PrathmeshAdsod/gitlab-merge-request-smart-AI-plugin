# Smart PR AI – GitLab Merge Request Assistant

**Smart PR AI** is a drop-in GitLab CI/CD component that:
- Auto-formats only the files changed in a Merge Request (MR)
- Runs an AI-powered review and posts inline suggestions as MR comments

## Features

- Supports Python, JavaScript, TypeScript, Go, Ruby, and more
- Only scans files changed in the MR (not the whole repo)
- Modular: easily swap in your own linters/formatters
- Posts AI suggestions as inline comments using your own LLM

## Usage

1. **Add to your repo:**
   - Copy `.gitlab-ci.yml`, `component.yaml`, and `scripts/` to your project root.

2. **Set CI/CD variables:**
   - `LLM_API_KEY`: Your LLM provider API key (e.g. OpenAI, Anthropic, etc.)
   - `GITLAB_PAT`: GitLab Personal Access Token with `api` scope

3. **Customize formatters (optional):**
   - Edit `scripts/format_files.sh` to adjust file globs or formatter commands for your stack.

4. **Test locally:**
   - Run `scripts/format_files.sh` to check formatting.
   - Run `python scripts/review_pr.py` (set env vars as needed).

## Example `.gitlab-ci.yml`

See the included `.gitlab-ci.yml` for a ready-to-use pipeline.

## Security

- All secrets are passed via environment variables.
- No secrets are hard-coded.

## Troubleshooting

- Check pipeline logs for clear error messages.
- Ensure your PAT has `api` scope and MR pipelines are enabled.

---

**Questions?**  
Open an issue or PR!
