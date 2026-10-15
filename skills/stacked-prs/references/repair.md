# Repair a stack

Read this when trunk advances, a lower layer changes history, or a parent PR merges. Work bottom to top. Preserve the saved per-layer heads and inherited boundaries until verification finishes.

## Preserve published ancestry

When the user asks to retain both histories or the stack uses additive merges, merge current trunk into the lowest affected open layer, resolve conflicts there, then merge each updated parent into its child. Respect a repository that prohibits merge commits; surface that conflict before changing strategy.

Check each updated layer contains its old head, its updated parent, and any newly integrated trunk. Review conflict resolutions and behavior at overlapping seams. Ancestry alone cannot prove the combined behavior.

## Restack rewritten parents

For an authorized rebase, save each child's old inherited parent boundary before rewriting any layer. The parent's current tip is not necessarily that boundary if the child branched earlier. Confirm the chosen boundary and inspect the commits it excludes and retains.

For a linear topic branch, transplant only its own commits onto the updated parent. The variables below mean the inspected new parent ref, saved old inherited parent SHA, and child branch:

```fish
git rebase --onto "$stack_new_parent" "$stack_old_boundary" "$stack_child"
```

Then repeat for higher descendants using their saved boundaries. Inspect merge-bearing histories before choosing plain rebase, merge-preserving rebase, or the repo's stack tool. Resolve conflicts in the affected layer and continue with the same tool's recovery commands. Keep unrelated work outside the operation.

## After a parent merges

Refresh the PR state and trunk, and identify whether the parent was merge committed, squashed, or rebased. Retarget the lowest remaining PR to trunk and propagate its new head upward.

With a squash or rebase merge, the old parent commits may be absent from trunk. Exclude those old commits using the saved inherited boundary when transplanting the child's own commits. Verify parent changes appear once and the child's diff contains its remaining work. If the inherited boundary cannot be recovered from saved refs, local history, or PR metadata, report the gap before rewriting history.

## Verify before publication

For every active parent-child edge, use Git's existing checks, substituting the inspected refs:

```fish
git merge-base --is-ancestor "$stack_parent" "$stack_child"
git diff --check "$stack_parent...$stack_child"
git diff --stat "$stack_parent...$stack_child"
git log --oneline "$stack_parent..$stack_child"
```

Treat nonzero ancestry or whitespace checks as failures. Read the actual diff, not just its stat. Compare rewritten commit ranges with `git range-diff` and inspect missing or changed patches, then run behavior checks. For additive merges, inspect the merge resolutions and check old-head preservation instead of relying on range-diff.

For authorized rewritten publication, use an explicit expected SHA for each rewritten ref. This single-layer example uses the remote, remote branch name, validated local branch, and previously recorded remote head:

```fish
git push --force-with-lease="refs/heads/$stack_remote_branch:$stack_expected_remote_head" "$stack_remote" "$stack_child:refs/heads/$stack_remote_branch"
```

Prefer one `--atomic` push for all affected refs when supported, with an explicit lease for every rewritten branch. On unsupported atomic push, report it and choose a publication sequence that keeps the stack reviewable. On lease failure, inspect the changed head; refreshing the expected SHA alone does not reconcile somebody else's work.

## Stack tools

Use the repo's installed tool and current `--help` rather than assuming flags. The locally inspected `gh stack` distinguishes `rebase` (local repair), `sync` (fetch, rebase, push, and update remote stack state), `submit` (push and create/update PRs), and `link` (remote stack linking). `link` with branch arguments can push and create PRs. Inspect these side effects before execution; use PR URLs when linking existing PRs, and read back bases and ancestry afterward.

Mechanics: [Git rebase](https://git-scm.com/docs/git-rebase), [Git push](https://git-scm.com/docs/git-push). The installed tool's help remains authoritative for its available operations.
