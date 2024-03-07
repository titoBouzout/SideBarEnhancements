rem FF PTSD

git add --all
git commit -m "update"

git push --prune
git tag 7.0.0
git push origin --tags
git push --delete origin 6.0.0