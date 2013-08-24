all:
	python setup.py build
	cp build/lib.linux-i686-2.6/cBencode.so .
	python use.py

clean:
	rm -rf build cBencode.so