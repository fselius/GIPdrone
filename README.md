The GIP lab, drone project
========
 - Master branch is the development branch, in general, commits should go to the master branch.
 - Release branch is the branch that will be deployed on the drone/ground station - Only verified code will be merged to this branch.
 - Add directories/branches as you see fit.
 - In your staging area, use branches when possible instead of working on the master branch.
 - Report bugs/todo items on the issue tracker.

Repository usage (Windows)
========
 - Setup your git client (http://git-scm.com/book/en/v1/Getting-Started), to cache your password type:
```
git config --global credential.helper wincred  
```
 - Start GIT Bash and go to the directory you want to clone the project in (Using Dropbox is recommended).
 ```bash
cd /c/Dropbox/
```
 - Clone the repository:
```
git clone https://github.com/fselius/GIPdrone.git
```
 - Add new code/commit/push/merge.
 - To fetch updates from the repository (It is a good habit to fetch every time you start working):
```
git fetch
```