---
name: stacked-prs
description: Stacked PRs. Use to create a stack, restack after a lower layer or trunk changes, repair a broken stack, or merge a stack in order.
---

# Stacked PRs

A **stack** is an ordered dependency chain: trunk → bottom PR → higher PRs. Each PR targets its immediate parent and carries one reviewable change relative to it. Independent changes get independent PRs.

This skill grants no authority by itself. Commits, pushes, PR edits, issue updates and merges stay within the task's existing authorization.

## 1. Map the stack

Inspect the checkout, worktrees, dirty files, repository instructions and installed stack tool; unrelated work stays untouched. Read the applicable GitHub procedure before service calls.

Fetch refs and inspect every affected PR, lower dependencies and higher descendants included. Record in task notes per layer: order, branch and worktree, base branch and SHA, local and remote head SHAs, PR URL and state, required checks. For existing branches, record each child's **inherited boundary** (the parent commit it was built on) before changing refs. Unexpected remote changes get reconciled before anything else.

Settle the intended behavior at overlapping **seams**: a clean text merge leaves conflicting exit codes, schemas, APIs or accounting rules unresolved. Material behavior choices go to the user.

**Done when:** every layer has a recorded parent, boundary and purpose, and every seam decision is settled.

## 2. Build or update

- **New stack:** branch each layer from the current tip of the layer below. Shared prerequisites live in the lowest layer that owns them; dependent behavior and tests sit above.
- **Existing stack:** keep its established merge or rebase strategy and the user's history constraints. Resolve a shared conflict at the lowest responsible layer, then propagate bottom to top through every affected descendant. When trunk advanced or a parent was rewritten or merged, read [repair.md](references/repair.md) before changing ancestry.

**Done when:** each active parent is an ancestor of its child, and each parent-to-child diff holds exactly that layer's change.

## 3. Validate and publish

Run the repo's checks at **every** changed layer, scaled to its behavior, and exercise the interactions at the top of the stack; a green top branch says nothing about lower layers alone. Checks that share processes, ports or databases run in isolated worktrees or one at a time. Failures get fixed with assertions intact.

Use the installed stack tool after reading its `--help`. Keep local repair and validation separate from commands that push, open PRs or change bases. With plain Git, push only the intended refs, atomically where supported, leasing each rewritten branch against its recorded SHA. A rejected push means inspect the remote change, then decide.

Read back: remote heads equal validated local heads, each PR targets its parent, and each parent-relative diff and description is right. Describe each layer's problem, behavior and validation, plus merge order when the stack UI hides it; follow the repo's PR template.

In T3, register every PR with `link_pull_request` and confirm with `list_thread_pull_requests`; elsewhere, report the URLs.

**Done when:** every published head matches its validated local head and every PR targets its correct parent.

## 4. Merge and report

Match CI runs to the published heads and current bases. Report each check as passing, pending, failed, missing or unknown. With duplicate runs, judge a complete run with all its required jobs. Cancel a redundant run only when authorized and its complete replacement is confirmed.

To monitor in T3, `watch_pull_request` and yield for notifications, then unwatch at hand-back; elsewhere, use the harness's completion mechanism.

Merge only on request: bottom to top, with the repo's merge method and required checks. After each merge, refresh refs and repair the remaining stack before the next. Branches stay unless deletion is requested.

**Done when:** live state is rechecked and the report gives stack order, URLs, verified heads, local checks and CI status, each layer labelled prepared, published, passing or merged.
