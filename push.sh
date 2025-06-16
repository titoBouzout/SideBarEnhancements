#

git add --all
git commit -m "update"

git push --prune
git tag 12.0.5
git push origin --tags
