serve:
	dev_appserver.py .

upload:
	appcfg.py update .

bump:
	vim app.yaml
	vim icw/__init__.py
	vim HISTORY.md

install:
	../bin/pip install --upgrade -r requirements_local.txt
	../bin/pip install --upgrade -t lib -r requirements_gae.txt

clean:
	-rm -r .tox tests/.cache

clean-all: clean
	../bin/pip freeze | xargs ../bin/pip uninstall -y
	find lib -not -name 'README.md' -delete

