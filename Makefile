ENVS = py27,py36,py37
export PYTHONPATH := $(CURDIR):$(CURDIR)/test

# Collect information to build as sensible package name
name = plugin.video.vtm.go
version = $(shell xmllint --xpath 'string(/addon/@version)' addon.xml)
git_branch = $(shell git rev-parse --abbrev-ref HEAD)
git_hash = $(shell git rev-parse --short HEAD)
zip_name = $(name)-$(version)-$(git_branch)-$(git_hash).zip
include_files = plugin.py service.py addon.xml LICENSE README.md CHANGELOG.md resources/
include_paths = $(patsubst %,$(name)/%,$(include_files))
exclude_files = \*.new \*.orig \*.pyc \*.pyo

all: check test build

check: check-pylint check-tox check-translations

check-pylint:
	@echo ">>> Running pylint checks"
	@pylint *.py resources/ test/

check-tox:
	@echo ">>> Running tox checks"
	@tox -q

check-translations:
	@echo ">>> Running translation checks"
	@msgcmp resources/language/resource.language.nl_nl/strings.po resources/language/resource.language.en_gb/strings.po

check-addon: clean build
	@echo ">>> Running addon checks"
	$(eval TMPDIR := $(shell mktemp -d))
	@unzip ../${zip_name} -d ${TMPDIR}
	cd ${TMPDIR} && kodi-addon-checker --branch=leia
	@rm -rf ${TMPDIR}

test: test-unit

test-unit:
	@echo ">>> Running unit tests"
ifdef TRAVIS_JOB_ID
		@coverage run -m unittest discover
else
		@python -m unittest discover -v -b -f
endif

clean:
	@find . -name '*.pyc' -type f -delete
	@find . -name '*.pyo' -type f -delete
	@find . -name '__pycache__' -type d -delete
	@rm -rf .pytest_cache/ .tox/ test/cdm test/userdata/temp
	@rm -f *.log .coverage

build: clean
	@echo ">>> Building package"
	@rm -f ../$(zip_name)
	cd ..; zip -r $(zip_name) $(include_paths) -x $(exclude_files)
	@echo "Successfully wrote package as: ../$(zip_name)"

release: build
	rm -rf ../repo-plugins/plugin.video.vtm.go/
	unzip ../$(zip_name) -d ../repo-plugins/

run:
	@echo ">>> Run CLI"
	python test/run.py /

.PHONY: check test
