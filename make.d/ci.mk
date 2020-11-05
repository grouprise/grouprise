# This Makefile contains make targets for generating and uploading the docker image
# which is used to build the grouprise application deb packages in GitLab CI.
#
# If you’ve changed the Build-Depends section of the debian/control file you should run
#     make ci_image_build ci_docker_login ci_image_push
# to update the docker image for the build process.

DOCKER_REGISTRY = git-registry.hack-hro.de:443/stadtgestalten/stadtgestalten
CI_BUILD_IMAGE_PATH = docker/build/Dockerfile
CI_BUILD_IMAGE_NAME = build:buster
CI_BUILD_IMAGE = $(DOCKER_REGISTRY)/$(CI_BUILD_IMAGE_NAME)
CI_BUILD_IMAGE_LOCALES = de_DE.UTF-8 en_US.UTF-8

.PHONY: ci_image_build
ci_image_build:
	docker build \
		--tag "$(CI_BUILD_IMAGE)" \
		--file "$(CI_BUILD_IMAGE_PATH)" \
		--build-arg 'LOCALES=$(CI_BUILD_IMAGE_LOCALES)' \
		.

.PHONY: ci_image_push
ci_image_push:
	docker push "$(CI_BUILD_IMAGE)"

.PHONY: ci_docker_login
ci_docker_login:
	@echo "Login credentials correspond to those of your GitLab account"
	docker login "$(DOCKER_REGISTRY)"

.PHONY: ci_docker_logout
ci_docker_logout:
	docker logout "$(DOCKER_REGISTRY)"
