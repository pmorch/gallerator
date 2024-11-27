ECHO=@
default:
	@echo No default rule - look in Makefile
	$(ECHO)exit 1


# see https://stackoverflow.com/questions/79232116
# 	$(ECHO) . ./venv/bin/activate ; \
# 		echo $(PWD)/src > $$(python3 -c 'import sysconfig; print(sysconfig.get_path("purelib"))')/pmorch-gallery.pth

venv:
	@echo Making venv
	$(ECHO) python3 -m venv venv
	$(ECHO) ./venv/bin/pip3 install $(PWD)

ost:
	$(ECHO) echo python3 install $(PWD)

lint:
	@echo Running ruff
	$(ECHO)ruff check --select I

lint-fix:
	@echo Running ruff --fix
	$(ECHO) check --select I --fix

test:
	$(ECHO) python3 -m unittest src/pmorch_gallery/tests/*.py