# Contribution Guidelines

## yay! hello there!

Nice to have you on board. Whenever you add new features try not to break any existing tests and add new ones whenever you can.  You can use `make lint` to lint your code and `make test` for testing.


## Build system

A set of makefiles and the external helper library [makefilet](https://notabug.org/sumpfralle/makefilet) are responsible for building the necessary components.  Just try `make help` in order to get the list of available targets.

The following `make` targets are probably of most interest:

* `assets`: build the static assets (CSS, Javascript and media)
* `app_run`: run a local instance from the current directory
* `build`: build all relevant components
* `clean`: remove all built components
* `lint`: check the code for style violations and other issues
* `test`: run the automated test suite


## Release Workflow

To create a new release take the following steps:

1. clean your workspace (the output of `git status` should be empty)
2. checkout the master branch and update it
3. run `make release-major`, `make release-minor` or `make release-patch`
4. push your updated master branch (`git push`) and tags (`git push --tags`)¹
5. done

¹ you might also want to checkout `config --global push.followTags true` ;)  
