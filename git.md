## Local Repo Connect to a Remote Repository
- `git init`
- `git remote add origin <liink.git>`
- `git remote -v`

## .gitignore
- (wins) `New-Item -Path . -Name ".gitignore" -ItemType "File" -Force`
- (linux) `nano .gitignore`

``` bash
# .gitignore
*.tsv
*.geojson
```

## add, commit, push
- `git add .`
- `git commit -m '<message>'`
- first push. Check current branch name: `git branch`
- first push: `git push -u origin [branch name]`
- `git push`

## branch
- check current branch name: `git branch`
- rename current branch locally: `git branch -M pu_building`
- delete old branch: `git push origin --delete master`
- verify everthing: `git branch -a`
