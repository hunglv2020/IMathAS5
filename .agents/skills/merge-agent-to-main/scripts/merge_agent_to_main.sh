#!/usr/bin/env bash
set -euo pipefail

commit_message="${1:-Update .agents content}"

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

current_branch="$(git branch --show-current)"
if [[ "$current_branch" == "main" ]]; then
  echo "Current branch is already main. Run this skill from the source branch that contains the .agents changes."
  exit 1
fi

has_working_agent_changes=false
if ! git diff --quiet -- .agents || ! git diff --cached --quiet -- .agents || [[ -n "$(git ls-files --others --exclude-standard -- .agents)" ]]; then
  has_working_agent_changes=true
fi

has_branch_agent_diff=false
if ! git diff --quiet main..HEAD -- .agents; then
  has_branch_agent_diff=true
fi

if [[ "$has_working_agent_changes" == false && "$has_branch_agent_diff" == false ]]; then
  echo "No .agents differences found against main."
  exit 0
fi

# Unstage non-.agents files so only .agents changes land in the commit
mapfile -t other_staged < <(git diff --cached --name-only | grep -v '^\.agents/')
if [[ ${#other_staged[@]} -gt 0 ]]; then
  git restore --staged -- "${other_staged[@]}"
fi

source_commit=""
if [[ "$has_working_agent_changes" == true ]]; then
  git add .agents
  git commit -m "$commit_message"
  source_commit="$(git rev-parse --short HEAD)"
fi

# Re-stage the files we temporarily unstaged
if [[ ${#other_staged[@]} -gt 0 ]]; then
  git add -- "${other_staged[@]}"
fi

worktree_dir="$(mktemp -d /tmp/imathas4-main-XXXXXX)"
cleanup() {
  if git worktree list --porcelain | grep -q "^worktree ${worktree_dir}$"; then
    git worktree remove "$worktree_dir" --force
  fi
  rm -rf "$worktree_dir"
}
trap cleanup EXIT

git worktree add "$worktree_dir" main >/dev/null

if [[ "$has_working_agent_changes" == true ]]; then
  # Abort early if this commit is already on main
  if git -C "$worktree_dir" merge-base --is-ancestor "$source_commit" HEAD 2>/dev/null; then
    echo "Commit $source_commit is already on main. Nothing to do."
    exit 0
  fi

  git -C "$worktree_dir" cherry-pick "$source_commit"
  target_commit="$(git -C "$worktree_dir" rev-parse --short HEAD)"

  echo "Source branch: $current_branch"
  echo "Source commit: $source_commit"
  echo "Main commit:   $target_commit"
else
  git -C "$worktree_dir" checkout "$current_branch" -- .agents

  # checkout above updates the index; compare against HEAD(main), not worktree vs index.
  if git -C "$worktree_dir" diff --cached --quiet -- .agents; then
    echo "No .agents differences to apply on main."
    exit 0
  fi

  git -C "$worktree_dir" add .agents
  git -C "$worktree_dir" commit -m "${commit_message} (sync .agents from ${current_branch})"
  target_commit="$(git -C "$worktree_dir" rev-parse --short HEAD)"

  echo "Source branch: $current_branch"
  echo "Source commit: <none: synced from branch snapshot>"
  echo "Main commit:   $target_commit"
fi
