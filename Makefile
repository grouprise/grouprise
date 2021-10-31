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

# specify DESTDIR before makefilet sets its default
DESTDIR ?= /
# we need access to the site packages in order to use "xapian"
VIRTUALENV_CREATE_ARGUMENTS ?= --system-site-packages
SHELL_FILES_ALL ?= $(shell find debian/ -type f -perm /a+x | grep -vE "^debian/tests/" | xargs grep -lI '^\#!/bin/.*sh')

# load makefilet
include make.d/makefilet-download-ondemand.mk

GROUPRISE_MAKEFILES = Makefile $(wildcard make.d/*.mk)

# define default target
.PHONY: default-target
default-target: build

# include project makefiles
include make.d/app.mk
include make.d/ci.mk
include make.d/doc.mk
include make.d/nodejs.mk
include make.d/assets.mk
include make.d/test.mk
include make.d/dist.mk
include make.d/dev.mk
