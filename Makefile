all:
	python setup.py build
	cp build/lib.linux-x86_64-2.7/cBencode.so .
	python use.py

clean:
	rm -rf build cBencode.so
