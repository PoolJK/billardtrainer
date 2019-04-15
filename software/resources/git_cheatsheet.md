git log of current branch (as in pycharm->version control->log) (also see better git log below):  
`git log --graph --decorate --oneline`

git reflog of HEAD position (use before git reset HEAD@{...})  
`git reflog`

reset HEAD position to previous commit after messing up:  
`git reset HEAD@{x}`  
(where x = number of HEAD from reflog)

what's going on?  
`git status`  
`git branch`

what's going on in remote repo?  
`git fetch origin`  
`git branch -r`  
`git status`

save current unsaved changes and clear them:    
`git stash`  
reapply saved changes:  
`git pop`

switch to other branch:  
`git checkout branch_name`

update current local branch from remote tracking branch:  
`git stash`  
`git fetch origin`  
`git rebase origin/remote_branch_name`  
`git stash pop`

add all changes:  
`git add .`  
commit:  
`git commit -m 'commit_message'`  
commit to previous commit and edit last commit message (keeping working tree clean):  
`git commit --amend`  
commit to previous commit without editing the message:  
`git commit --amend --no-edit`  

clean up working tree:  

##### example 1: rebase to remove commit
- step 1: show log to read the commit hashes:  
`git lg`  
- step 2: start rebase;  
    commit-2 is first from bottom to be kept; commit-1 is first from top to be kept. Commits in between will get removed. This is also possible via `git rebase -i`  
`git rebase --onto commit-2 commit-1 branch_name`  
- step 3: follow rebase instructions from git;  
use -Xtheirs to accept theirs by default;  
resolving conflicts is simpler in pycharm;

push current branch to origin (after cleaning up working tree):  
`git push origin HEAD:remote_branch_name`

better git log:  
`git config --global alias.lg "log --color --graph --pretty=format:'%C(yellow)%h%Creset - %C(red)%<(20,trunc)%d%Creset %<(50,trunc)%s %Cgreen%ar%Creset %C(bold blue)<%an>%Creset' --abbrev-commit"`  
(usage: git lg)

see all aliases:  
`git config --get-regexp alias`
