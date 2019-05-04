# Billardtrainer (V`0.1.1`)
A snooker and pool training system in development with Python on Raspberry-Pi and Android.

Using libraries:  
```
Python 3.7.3 (3.5.3 @raspberrypi)
OpenCV 4.1.0.25 opencv-python && opencv-contrib-python (3.4.4 @raspberrypi)
Numpy 1.16.3 (1.12.1 @raspberrypi)
GitPython 2.1.11
imutils 0.5.2
```

### Development

##### Updating this branch:

1. get current branch from origin:  
`git fetch origin`
2. create your local copy:  
  option 1: new branch  
  `git checkout -b myfeature origin/0.1.0`  
  option 2: rebase your current branch onto 0.1.0    
  `git rebase origin/0.1.0`
3. make your edits and commit.  
for commit tips review links.md ([for example](https://dev.to/2nit/how-to-better-organize-your-git-commits-bkb))
4. push your edits to your new branch in origin:  
`git push -u origin HEAD`
5. open pull request for code review, using 0.1.0 as base. 
6. if changes are discussed and accepted, merge pull request (probieren wir dann mal...)
7. delete feature branch in repository  
`git push origin -d myfeature`
