#

git add --all
git commit -m "update"

git push --prune
git tag 12.0.6 -m ''
git push origin --tags
