#!/usr/bin/env python3
"""
update_github_pages.py

One-click-ish updater for GitHub Pages sites.

Two common workflows supported:

A) SIMPLE ("main" mode): your site is served from the 'main' branch (root or /docs).
   -> The script stages changes, commits, and pushes to the current branch (default main).

B) PUBLISH BUILD ("gh-pages" mode): your sources live on main, the built static site is deployed to 'gh-pages'.
   -> The script optionally runs your build command and publishes a given build directory to gh-pages using 'git worktree'.
      This avoids switching branches in your working copy.

Usage examples:
  # A) Simple mode (commit & push current repo to main)
  python update_github_pages.py --mode main --commit "Update site"

  # B) Build then publish to gh-pages (e.g., for Jekyll/Hugo/Vite/React)
  python update_github_pages.py --mode gh-pages \
      --build-cmd "npm run build" \
      --build-dir "dist" \
      --commit "Publish site"

  # B2) Jekyll example
  python update_github_pages.py --mode gh-pages \
      --build-cmd "bundle exec jekyll build" \
      --build-dir "_site" \
      --commit "Publish Jekyll site"

Notes:
- Requires git installed and your repo's 'origin' remote configured.
- If you use a custom domain, ensure a CNAME file exists either in your build dir or at the repo root; see --cname.
"""

from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def run(cmd: str, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=str(cwd) if cwd else None)
    if check and result.returncode != 0:
        raise SystemExit(f"Command failed with exit code {result.returncode}: {cmd}")
    return result


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def ensure_git_repo(path: Path):
    if not is_git_repo(path):
        raise SystemExit(f"Not a git repository: {path}")


def current_branch(path: Path) -> str:
    cp = subprocess.run("git rev-parse --abbrev-ref HEAD", shell=True, cwd=str(path), capture_output=True, text=True)
    if cp.returncode != 0:
        raise SystemExit("Failed to determine current git branch.")
    return cp.stdout.strip()


def has_remote_origin(path: Path) -> bool:
    cp = subprocess.run("git remote", shell=True, cwd=str(path), capture_output=True, text=True)
    if cp.returncode != 0:
        return False
    remotes = [r.strip() for r in cp.stdout.splitlines()]
    return "origin" in remotes


def git_config_user_set(path: Path) -> bool:
    name = subprocess.run("git config user.name", shell=True, cwd=str(path), capture_output=True, text=True)
    email = subprocess.run("git config user.email", shell=True, cwd=str(path), capture_output=True, text=True)
    return bool(name.stdout.strip()) and bool(email.stdout.strip())


def copy_tree(src: Path, dst: Path):
    # Copy contents of src into dst (not the src directory itself)
    for item in src.iterdir():
        s = item
        d = dst / item.name
        if s.is_dir():
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)


@dataclass
class Args:
    mode: str
    repo: Path
    commit: str
    build_cmd: Optional[str]
    build_dir: Optional[Path]
    gh_pages_branch: str
    keep_files: bool
    cname: Optional[str]
    push_remote: str


def parse_args() -> Args:
    parser = argparse.ArgumentParser(description="Update a GitHub Pages site in one click-ish.")
    parser.add_argument("--mode", choices=["main", "gh-pages"], required=True,
                        help="Publishing mode. 'main' = push current branch; 'gh-pages' = publish build output to gh-pages")
    parser.add_argument("--repo", default=".", help="Path to the git repository (default: current directory)")
    parser.add_argument("--commit", default=None, help="Commit message (default: auto with timestamp)")
    parser.add_argument("--build-cmd", default=None, help="Optional build command to run before publishing (gh-pages mode)")
    parser.add_argument("--build-dir", default=None, help="Directory containing built static site (gh-pages mode). E.g., 'dist', '_site'")
    parser.add_argument("--gh-pages-branch", default="gh-pages", help="Name of the publish branch (default: gh-pages)")
    parser.add_argument("--keep-files", action="store_true", help="Do not wipe target branch before copy (gh-pages mode)")
    parser.add_argument("--cname", default=None, help="Custom domain to write into CNAME file (overrides any existing)")
    parser.add_argument("--push-remote", default="origin", help="Remote name to push to (default: origin)")
    ns = parser.parse_args()

    repo = Path(ns.repo).resolve()
    commit = ns.commit or f"Site update {datetime_now_human()}"
    build_dir = Path(ns.build_dir).resolve() if ns.build_dir else None

    return Args(
        mode=ns.mode,
        repo=repo,
        commit=commit,
        build_cmd=ns.build_cmd,
        build_dir=build_dir,
        gh_pages_branch=ns.gh_pages_branch,
        keep_files=ns.keep_files,
        cname=ns.cname,
        push_remote=ns.push_remote,
    )


def datetime_now_human() -> str:
    import datetime as _dt
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_clean_index(repo: Path):
    # Avoid committing unrelated files accidentally; let the user control
    # We won't force a clean tree, but we warn if there are untracked/unstaged changes
    subprocess.run("git status --short", shell=True, cwd=str(repo))


def main_mode(args: Args):
    print("== MODE: main ==")
    ensure_git_repo(args.repo)
    if not has_remote_origin(args.repo):
        raise SystemExit("Remote 'origin' not configured. Add it with: git remote add origin <url>")

    if not git_config_user_set(args.repo):
        print("Warning: git user.name or user.email is not set for this repo.", file=sys.stderr)

    # Optional build in 'main' mode too (some users might want it)
    if args.build_cmd:
        print("Running build command...")
        run(args.build_cmd, cwd=args.repo)

    print("Staging changes...")
    run("git add -A", cwd=args.repo)
    # If there is nothing to commit, skip commit step
    cp = subprocess.run("git diff --cached --quiet || echo CHANGES", shell=True, cwd=str(args.repo), capture_output=True, text=True)
    if "CHANGES" in (cp.stdout or ""):
        run(f'git commit -m "{args.commit}"', cwd=args.repo)
    else:
        print("No staged changes detected; skipping commit.")

    # Push
    branch = current_branch(args.repo)
    print(f"Pushing to {args.push_remote} {branch}...")
    run(f"git push {args.push_remote} {branch}", cwd=args.repo)
    print("\nDone. GitHub Pages will rebuild automatically (if this branch is configured in Settings → Pages).")


def gh_pages_mode(args: Args):
    print("== MODE: gh-pages ==")
    ensure_git_repo(args.repo)
    if not has_remote_origin(args.repo):
        raise SystemExit("Remote 'origin' not configured. Add it with: git remote add origin <url>")
    if not args.build_dir:
        raise SystemExit("--build-dir is required in gh-pages mode (e.g., 'dist', '_site').")

    if args.build_cmd:
        print("Running build command...")
        run(args.build_cmd, cwd=args.repo)

    build_dir = args.build_dir
    if not build_dir.exists() or not any(build_dir.iterdir()):
        raise SystemExit(f"Build dir not found or empty: {build_dir}")

    # Prepare worktree dir
    tmpdir = Path(tempfile.mkdtemp(prefix="publish-gh-pages-")).resolve()
    print(f"Using temporary worktree: {tmpdir}")

    try:
        # Fetch branch and create worktree
        run(f"git fetch {args.push_remote}", cwd=args.repo, check=False)

        # If branch doesn't exist, create an orphan branch:
        # We attempt to add worktree. If it fails, we create an orphan.
        add_worktree_cmd = f"git worktree add --checkout {tmpdir} {args.gh_pages_branch}"
        res = subprocess.run(add_worktree_cmd, shell=True, cwd=str(args.repo))
        if res.returncode != 0:
            print(f"Branch '{args.gh_pages_branch}' not found. Creating orphan branch...")
            # Create orphan in tmpdir
            run(f"git worktree add --no-checkout {tmpdir}", cwd=args.repo)
            run("git checkout --orphan {branch}".format(branch=args.gh_pages_branch), cwd=tmpdir)
            # Clean all files in orphan worktree
            for p in tmpdir.iterdir():
                if p.name == ".git":
                    continue
                if p.is_dir():
                    shutil.rmtree(p)
                else:
                    p.unlink()
            run("git commit --allow-empty -m \"Initialize gh-pages branch\"", cwd=tmpdir)
            run(f"git branch -M {args.gh_pages_branch}", cwd=tmpdir)
            run(f"git push -u {args.push_remote} {args.gh_pages_branch}", cwd=tmpdir)

        # Now tmpdir is checked out to gh-pages
        # Clean (unless keep_files) and copy build output
        if not args.keep_files:
            print("Wiping target branch contents...")
            for item in tmpdir.iterdir():
                if item.name == ".git":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

        print(f"Copying build output from {build_dir} → {tmpdir}")
        copy_tree(build_dir, tmpdir)

        # Handle CNAME if requested
        if args.cname:
            cname_path = tmpdir / "CNAME"
            cname_path.write_text(args.cname.strip() + "\n", encoding="utf-8")
            print(f"Wrote CNAME with domain: {args.cname}")

        # Commit & push
        run("git add -A", cwd=tmpdir)
        cp = subprocess.run("git diff --cached --quiet || echo CHANGES", shell=True, cwd=str(tmpdir), capture_output=True, text=True)
        if "CHANGES" in (cp.stdout or ""):
            run(f'git commit -m "{args.commit}"', cwd=tmpdir)
            run(f"git push {args.push_remote} {args.gh_pages_branch}", cwd=tmpdir)
            print("Publish complete.")
        else:
            print("No changes to publish.")
    finally:
        # Clean up worktree
        try:
            print("Cleaning up worktree...")
            run(f"git worktree remove {tmpdir} --force", cwd=args.repo, check=False)
        except Exception as e:
            print(f"Note: failed to remove worktree {tmpdir}: {e}")
        # Also ensure directory is removed from filesystem
        if tmpdir.exists():
            shutil.rmtree(tmpdir, ignore_errors=True)


def main():
    args = parse_args()
    ensure_git_repo(args.repo)
    ensure_clean_index(args.repo)

    if args.mode == "main":
        main_mode(args)
    elif args.mode == "gh-pages":
        gh_pages_mode(args)
    else:
        raise SystemExit("Unknown mode")

if __name__ == "__main__":
    main()
