.PHONY: dist

clean:
	rm -rf dist

build: dist
	python setup.py sdist
	python setup.py bdist_wheel

register:
	twine register dist/*.whl

upload:
	twine upload dist/*

test-register:
	twine register dist/*.whl -r testpypi

test-upload:
	twine upload dist/* -r testpypi

test:
	tox
