# Contribution Guidelines

## yay! hello there!

Nice to have you on board. Whenever you add new features try not to break any existing tests and add new ones whenever you can. You can use the make targets `lint`, `lint_js`, `lint_py` to lint your code and `test` for testing.

## Release Workflow

To create a new release take the following steps:

1. clean your workspace (the output of `git status` should be empty)
2. checkout the master branch and update it
3. run `make release-major`, `make release-minor` or `make release-patch`
4. push your updated master branch (`git push`) and tags (`git push --tags`)¹
5. done

¹ you might also want to checkout `config --global push.followTags true` ;)  
