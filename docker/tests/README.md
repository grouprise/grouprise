# Local container environment for running tests

The container environment can be used for running tests in an isolated environment.


# Usage

```shell
make test-python-in-container
```


# Features

* local configuration customizations are discarded
    * better isolation of test environment
* mixture of Debian packages and pip-installed python packages is properly tested
    * even for non-stable or non-Debian test environments

# Known issues

* The docker image is *always* rebuild, since the build context encompasses the complete project
  directory.
    * This takes only a few seconds as long as no local files were changed (due to the local image
      layer cache).
* The `npm ci` and `pip install` build steps are executed from scratch, if any `Makefile` snippets
  or dependency files were changed.
