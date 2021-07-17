# Releases

The following steps are recommended for releases:

1. write or update the release notes with notable changes below `docs/releases/`
1. reference these release notes in `docs/releases/index.rst`
1. commit the above changes
1. verify that the latest [CI pipeline](https://git.hack-hro.de/grouprise/grouprise/-/pipelines/) finished successfully
1. run `make release-(major|minor|patch` (depending on the included changes)
1. push the changes: `git push && git push --tags`
1. announce the changes (e.g. in [#grouprise-dev:systemausfall.org](matrix:r/grouprise-dev:systemausfall.org))
