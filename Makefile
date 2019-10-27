test:
	python3 setup.py test

deploy:
	python3 -m twine upload dist/*

build_package:
	python3 setup.py sdist bdist_wheel

setup:
	python3 -m pip install --user --upgrade setuptools wheel
	python3 -m pip install --user --upgrade twine

clean:
	rm -rf build dist nested_csv.egg-info
