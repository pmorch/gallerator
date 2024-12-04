ECHO=@
default:
	@echo No default rule - look in Makefile
	$(ECHO)exit 1


venv:
	@echo Making venv
	$(ECHO) python3 -m venv venv
	$(ECHO) ./venv/bin/pip3 install $(PWD)

ost:
	$(ECHO) echo python3 install $(PWD)

lint:
	@echo Running ruff
	$(ECHO) ruff check --select I

lint-fix:
	@echo Running ruff --fix
	$(ECHO) ruff check --select I --fix

test:
	$(ECHO) python3 -m unittest src/pmorch_gallery/tests/*.py

# If you want to use nanogallery2, you'll need to download the distribution
# files. Do that with
# make download-nanogallery2
download-nanogallery2:
	$(ECHO) ./src/pmorch_gallery/renderers/nanogallery2/download.sh

# If you want to remove these files again
remove-download-nanogallery2:
	$(ECHO) ./src/pmorch_gallery/renderers/nanogallery2/removeDownloaded.sh

update-readme-usage:
	@echo Updating README.md
	$(ECHO) mv README.md orig.README.md
	$(ECHO) cat orig.README.md | \
		python3 ./release-tools/replace-section.py usage \
		"$$(echo '```' ; gallerator --help ; echo '```')" > README.md

update-docs: update-readme-usage
