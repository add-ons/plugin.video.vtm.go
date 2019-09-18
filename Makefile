ENVS = flake8,py27,py37
export PYTHONPATH := $(CURDIR):$(CURDIR)/test

# Collect information to build as sensible package name
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
reset = \e[0;39m

all: check test build

check: check-pylint check-tox check-translations

check-pylint:
	@echo -e "$(blue)>>> Starting pylint checks$(reset)"
	@pylint *.py resources/ resources/lib/ test/

check-tox:
	@echo "$(blue)>>> Starting tox checks$(reset)"
	@tox -q -e $(ENVS)

check-translations:
	@echo "$(blue)>>> Starting translation checks$(reset)"
	@msgcmp resources/language/resource.language.nl_nl/strings.po resources/language/resource.language.en_gb/strings.po

check-addon: # disabled by default
	@echo "$(blue)>>> Starting addon checks$(reset)"
	@kodi-addon-checker . --branch=leia

test: test-unit

test-unit:
    env
	@echo "$(white)=$(blue) Starting tests$(reset)"
	@python -m unittest discover

clean:
	@find . -name '*.pyc' -type f -delete
	@find . -name '__pycache__' -type d -delete
	@rm -rf .pytest_cache/ .tox/
	@rm -f *.log

build:
	@echo -e "$(white)=$(blue) Building package$(reset)"
	@rm -f ../$(zip_name)
	cd ..; zip -r $(zip_name) $(include_paths) -x $(exclude_files)
	@echo -e "$(white)=$(blue) Successfully wrote package as: $(white)../$(zip_name)$(reset)"

run:
	@echo -e "$(white)=$(blue) Run CLI$(reset)"
	python test/run.py /

.PHONY: check test
