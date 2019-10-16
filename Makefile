ENVS = py27,py36,py37
export PYTHONPATH := $(CURDIR):$(CURDIR)/test

# Collect information to build as sensible package name
ADDONDIR = $(shell pwd)
name = $(shell xmllint --xpath 'string(/addon/@id)' addon.xml)
version = $(shell xmllint --xpath 'string(/addon/@version)' addon.xml)
git_branch = $(shell git rev-parse --abbrev-ref HEAD)
git_hash = $(shell git rev-parse --short HEAD)
zip_name = $(name)-$(version)-$(git_branch)-$(git_hash).zip
include_files = main.py addon.xml LICENSE README.md resources/
include_paths = $(patsubst %,$(name)/%,$(include_files))
exclude_files = \*.new \*.orig \*.pyc \*.pyo
zip_dir = $(name)/

blue = \e[1;34m
white = \e[1;37m
reset = \e[0;39m\n

all: check test build

check: check-pylint check-tox check-translations

check-pylint:
	@printf "${blue}>>> Running pylint checks$(reset)"
	@pylint *.py resources/ test/

check-tox:
	@printf "${blue}>>> Running tox checks$(reset)"
	@tox -q

check-translations:
	@printf "${blue}>>> Running translation checks$(reset)"
	@msgcmp resources/language/resource.language.nl_nl/strings.po resources/language/resource.language.en_gb/strings.po

check-addon: clean
	@printf "${blue}>>> Running addon checks$(reset)"
	cd /tmp && kodi-addon-checker $(ADDONDIR) --branch=leia

test: test-unit

test-unit:
	@printf "${blue}>>> Running unit tests$(reset)"
ifdef TRAVIS_JOB_ID
		@coverage run -m unittest discover -v -b
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
	@printf "${blue}>>> Building package$(reset)"
	@rm -f ../$(zip_name)
	cd ..; zip -r $(zip_name) $(include_paths) -x $(exclude_files)
	@echo "Successfully wrote package as: $(white)../$(zip_name)$(reset)"

run:
	@printf "${blue}>>> Run CLI$(reset)"
	python test/run.py /

.PHONY: check test
