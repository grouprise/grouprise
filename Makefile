# load makefilet
include make.d/makefilet-download-ondemand.mk

# define default target
.PHONY: default-target
default-target: build

# include project makefiles
include make.d/virtualenv.mk
include make.d/app.mk
include make.d/nodejs.mk
include make.d/assets.mk
include make.d/test.mk
include make.d/dist.mk
include make.d/dev.mk
