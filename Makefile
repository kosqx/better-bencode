all:
	python setup.py build
	cp build/lib.linux-i686-2.6/cBencode.so .
	# python -c 'import cBencode; print "%r" % cBencode.dump([1,2,3])'
	# python -c 'import cBencode; print "%r" % cBencode.dump([None, True, False, "foo"])'
	# python -c 'import cBencode; print "%r" % cBencode.dump({"a": False, "b": True})'
	# python -c 'import cBencode; print "%r" % cBencode.dump({"a": 1, "b": 123456789123456789123456789})'
	# python -c 'import cBencode, sys; cBencode.dump({"a": 1, "b": 123456789123456789123456789}, sys.stdout); print'
	python use.py
