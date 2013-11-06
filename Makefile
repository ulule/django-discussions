pep8:
	flake8 discussions --ignore=E501,E127,E128,E124

test:
	coverage run --branch --source=discussions manage.py test discussions
	coverage report --omit=discussions/test*

release:
	python setup.py sdist register upload -s
