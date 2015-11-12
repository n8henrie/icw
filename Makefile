serve:
	dev_appserver.py $$PWD

upload:
	appcfg.py update .

bump:
	vim app.yaml
	vim icw/__init__.py
	vim HISTORY.md
