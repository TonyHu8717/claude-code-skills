# code-review

Pull request code review using parallel AI agents for high-signal issue detection.

## 1. When to Use

### 1.1 Trigger Conditions

- User asks to review a PR or pull request
- User asks for code review on current changes
- User says "review this PR", "code review", "check my PR"
- User provides a GitHub PR URL

### 1.2 Prerequisites

- Must be in a git repository with a GitHub remote
- `gh` CLI must be authenticated
- PR must exist on GitHub

## 2. Workflow

### Step 1: Pre-checks (Haiku agent)

Check if any of these are true — if so, stop:
- PR is closed
- PR is a draft
- PR doesn't need review (automated/trivial)
- Claude already commented on this PR

### Step 2: Find CLAUDE.md files (Haiku agent)

Return file paths for all relevant CLAUDE.md files (root + directories containing modified files).

### Step 3: PR Summary (Sonnet agent)

View the PR and return a summary of changes.

### Step 4: Parallel Review (4 agents)

- **Agents 1+2**: CLAUDE.md compliance (Sonnet) — audit changes for rule adherence
- **Agent 3**: Bug detection (Opus) — scan diff for obvious bugs, focus on diff only
- **Agent 4**: Code issues (Opus) — security, incorrect logic in changed code

**Critical: HIGH SIGNAL only.** Flag:
- Syntax/type errors, missing imports
- Clear logic errors producing wrong results
- Unambiguous CLAUDE.md violations

Do NOT flag: style concerns, potential input-dependent issues, subjective suggestions.

### Step 5: Validation (parallel subagents)

For each issue from Step 4, launch a validation agent to confirm the issue is real:
- Opus for bugs/logic issues
- Sonnet for CLAUDE.md violations

### Step 6: Filter

Remove unvalidated issues. Output summary:
- If issues found: list each with description
- If no issues: "No issues found. Checked for bugs and CLAUDE.md compliance."

### Step 7: GitHub Comments (if `--comment` provided)

Post inline comments via `mcp__github_inline_comment__create_inline_comment` with `confirmed: true`:
- Brief description + committable suggestion for small fixes
- Description + suggested fix for larger changes (6+ lines)
- ONE comment per unique issue — no duplicates

## 3. Usage

```
/code-review <PR-number-or-URL>
/code-review <PR-number-or-URL> --comment
```

Without `--comment`: outputs review to terminal only.
With `--comment`: also posts inline comments on GitHub.

## 4. Anti-patterns

Do NOT use this skill for:
- Reviewing code that isn't in a PR
- General code quality discussions
- Non-GitHub repositories
