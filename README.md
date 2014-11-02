GIP lab - The Drone Project
========
 - Master branch is the development branch, in general, commits should go to the master branch.
 - Release branch is the branch that will be deployed on the drone/ground station - Only verified code will be merged to this branch.
 - Add directories/branches as you see fit and give them proper names ('flight_controll' and not 'your_name').
 - Add external documentation, explain what you are doing, why you are doing it and how you are doing it.
 - Use branches when possible instead of working on the master branch, in particular when adding new features/fixing bugs.
 - Report bugs/todo items on the issue tracker.

Repository usage (Windows)
======
 - Setup your git client (http://git-scm.com/book/en/v1/Getting-Started), to cache your password type:
```
git config --global credential.helper wincred  
```
 - Start GIT Bash and go to the directory you want to clone the project in (Using Dropbox is recommended).
```
cd /c/Dropbox/
```
 - Clone the repository:
```
git clone https://github.com/fselius/GIPdrone.git
```
 - Add new code/branch/commit/push/merge.
 - To fetch updates from the repository (Good habit to do so every time you start working):
```
git fetch
```
