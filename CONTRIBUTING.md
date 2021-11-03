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


## Branch workflow

The git branches of the repository are used according to the [OneFlow](https://www.endoflineblog.com/oneflow-a-git-branching-model-and-workflow) concept.
The [merge of a feature branch](https://www.endoflineblog.com/oneflow-a-git-branching-model-and-workflow#finishing-a-feature-branch) should use *Option 1 (rebase)* or *Option 3 (rebase + merge no-ff)*.

In case of TL;DR:

* There is only one permanent branch (`main`).  Release commits are branched, tagged and merged back into `main`.
* Feature branches are based on the `main` branch.  They are merged back into `main` via *rebase* or *rebase + merge no-fastforward*.
* Hot fixes start at a release tag.  After tagging they are merged back into `main`.

Only the most recent release is supported (for hot fixes).


## Release workflow

To create a new release take the following steps:

1. checkout the `main` branch
2. create a release notes document (below `docs/releases/`) and add it to `docs/releases/index.rst`
3. commit your changes
4. run `make release-major`, `make release-minor` or `make release-patch`
5. push your updated `main` branch (`git push`) and tags (`git push --tags`)¹
6. done

¹ you might also want to apply `git config --global push.followTags true` ;)

## License

The source code of grouprise itself is released under the [AGPLv3](LICENSE),
which is included in the [LICENSE](LICENSE) file.

