# Development and installation helpers for grouprise
#
# See "make help" for a list of most targets.
#
# The various tasks are grouped into several files below make.d/.
#
# Features:
#     * install python-based dependencies via virtualenv
#     * prepare local django configuration and run the server
#     * build and package nodejs-based dependencies
#     * run tests
#     * publish a release (increase version numbers, create tagged commit, ...)
#     * create release artifacts (tar, deb, ...)

# load makefilet
include make.d/makefilet-download-ondemand.mk

GROUPRISE_MAKEFILES = Makefile $(wildcard make.d/*.mk)

# define default target
.PHONY: default-target
default-target: build

# include project makefiles
include make.d/virtualenv.mk
include make.d/app.mk
include make.d/doc.mk
include make.d/nodejs.mk
include make.d/assets.mk
include make.d/test.mk
include make.d/dist.mk
include make.d/dev.mk
