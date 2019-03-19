# TODO: remove compatibility for manual operations after the next release (3.0)
#     The real operations are provided by makefilet.

.PHONY: virtualenv_check
virtualenv_check: virtualenv-check
	$(info "'$@' is deprecated - please use '$<' instead.")

.PHONY: virtualenv_update
virtualenv_update: virtualenv-update
	$(info "'$@' is deprecated - please use '$<' instead.")
