export KODI_HOME := $(CURDIR)/tests/home
export KODI_INTERACTIVE := 0
PYTHON := python

languages = $(filter-out en_gb, $(patsubst resources/language/resource.language.%, %, $(wildcard resources/language/*)))

all: check test build
zip: build
multizip: build

check: check-pylint check-translations

check-pylint:
	@printf ">>> Running pylint checks\n"
	@$(PYTHON) -m pylint *.py resources/lib/ tests/

check-translations:
	@printf ">>> Running translation checks\n"
	@$(foreach lang,$(languages), \
		msgcmp --use-untranslated resources/language/resource.language.$(lang)/strings.po resources/language/resource.language.en_gb/strings.po; \
	)
	@scripts/check_for_unused_translations.py

check-addon: build
	@printf ">>> Running addon checks\n"
	$(eval TMPDIR := $(shell mktemp -d))
	@unzip dist/plugin.video.vtm.go-*+matrix.1.zip -d ${TMPDIR}
	cd ${TMPDIR} && kodi-addon-checker --branch=matrix
	@rm -rf ${TMPDIR}

codefix:
	@isort -l 160 .

test:
	@printf ">>> Running unit tests\n"
	@$(PYTHON) -m pytest -v tests

clean:
	@printf ">>> Cleaning up\n"
	@find . -name '*.py[cod]' -type f -delete
	@find . -name '__pycache__' -type d -delete
	@rm -rf .pytest_cache/ tests/cdm tests/userdata/temp
	@rm -f *.log .coverage
	@rm dist/*.zip

build: clean
	@printf ">>> Building add-on\n"
	@scripts/build.py
	@ls -lah dist/*.zip

release:
ifneq ($(release),)
	docker run -it --rm --env CHANGELOG_GITHUB_TOKEN=$(GH_TOKEN) -v "$(shell pwd)":/usr/local/src/your-app githubchangeloggenerator/github-changelog-generator -u add-ons -p plugin.video.vtm.go --no-issues --exclude-labels duplicate,question,invalid,wontfix,release,testing --future-release v$(release)

	@printf "cd /addon/@version\nset $$release\nsave\nbye\n" | xmllint --shell addon.xml; \
	date=$(shell date '+%Y-%m-%d'); \
	printf "cd /addon/extension[@point='xbmc.addon.metadata']/news\nset v$$release ($$date)\nsave\nbye\n" | xmllint --shell addon.xml; \

	# Next steps to release:
	# - Modify the news-section of addons.xml
	# - git add . && git commit -m "Prepare for v$(release)" && git push
	# - git tag v$(release) && git push --tags
else
	@printf "Usage: make release release=1.0.0\n"
endif

.PHONY: check codefix test clean build release
