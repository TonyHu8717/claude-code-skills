# commit-commands

Git workflow automation: commit, push, PR creation, and branch cleanup.

## 1. When to Use

### 1.1 Trigger Conditions

- User says "commit", "commit my changes", "create a commit"
- User says "commit and push", "push and create PR", "submit a PR"
- User says "clean up branches", "remove stale branches", "clean gone branches"

### 1.2 Prerequisites

- Must be in a git repository
- For PR creation: `gh` CLI must be authenticated
- For branch cleanup: branches must be marked `[gone]`

## 2. Commands

### 2.1 `/commit` — Create a Git Commit

Stages all changes and creates a commit with an auto-generated message.

**Workflow:**
1. Read `git status` and `git diff HEAD` to understand changes
2. Read recent `git log --oneline -10` for commit style
3. Stage relevant files with `git add`
4. Create commit with descriptive message

**Rules:**
- Generate a concise, meaningful commit message
- Match the repository's commit style
- Do NOT commit sensitive files (.env, credentials)
- Single message, single commit — no extra commentary

### 2.2 `/commit-push-pr` — Full PR Workflow

Creates branch, commits, pushes, and opens a PR in one step.

**Workflow:**
1. If on `main`/`master`, create a new feature branch
2. Stage and commit all changes
3. Push branch to origin with `-u` flag
4. Create PR via `gh pr create` with:
   - Short title (under 70 chars)
   - Body with summary of changes
5. Return the PR URL

**Rules:**
- All steps must happen in a single message (parallel tool calls)
- Branch name should be descriptive (e.g., `fix/login-redirect`, `feat/user-profiles`)
- PR body should explain what changed and why

### 2.3 `/clean-gone` — Clean Up Stale Branches

Removes local branches that have been deleted on the remote.

**Workflow:**
1. Run `git branch -v` to find `[gone]` branches
2. Run `git worktree list` to find associated worktrees
3. For each `[gone]` branch:
   - Remove associated worktree if exists (`git worktree remove --force`)
   - Delete the branch (`git branch -D`)
4. Report what was cleaned up

**Rules:**
- Branches with `+` prefix have worktrees — remove worktree first
- Never delete the current branch
- Report each deletion for transparency

## 3. Usage

```
/commit              — stage and commit changes
/commit-push-pr      — commit, push, and create PR
/clean-gone          — remove stale local branches
```

## 4. Anti-patterns

Do NOT use this skill for:
- Interactive rebase (use git directly)
- Force pushing (always ask user first)
- Deleting remote branches (separate operation)
- Amending existing commits (create new commits instead)
