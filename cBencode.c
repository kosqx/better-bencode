#include <Python.h>
 
// static PyObject* say_hello(PyObject* self, PyObject* args)
// {
//     const char* name;
 
//     if (!PyArg_ParseTuple(args, "s", &name))
//         return NULL;
 
//     printf("Hello %s!\n", name);
 
//     Py_RETURN_NONE;
// }

struct benc_state {
	int size;
	int offset;
	char buffer[1024];
	PyObject* fout;
};

static int benc_state_flush(struct benc_state* bs) {
	if (bs->offset >= bs->size) {
		PyObject* s = Py_BuildValue("s#", bs->buffer, bs->offset);
		_PyObject_CallMethodId(bs->fout, &PyId_write, "O", s);
		Py_DECREF(s);
	}
}

static int benc_state_write_char(struct benc_state* bs, char c) {
	bs->buffer[bs->offset++] = c;

}

static int benc_state_write_string(struct benc_state* bs, char* str) {
	while (*str) {
		bs->buffer[bs->offset++] = *str++;
	}
}

static int benc_state_write_buffer(struct benc_state* bs, char* buff, int size) {
	int i;
	for (i = 0; i < size; i++) {
		bs->buffer[bs->offset++] = buff[i];
	}
}

int benc_state_write_format(struct benc_state* bs, const int limit, const void *format, ...) {
	char buffer[limit + 1]; // moze by malloca()?

	va_list ap;
	va_start(ap, format);
	int size = vsnprintf(buffer, limit, format, ap);
	va_end(ap);

	return benc_state_write_buffer(bs, buffer, (size < limit) ? size : (limit - 1));
}


static int do_dump(struct benc_state *bs, PyObject* obj);

static int do_dump(struct benc_state *bs, PyObject* obj) {
	int i = 0, n = 0;
	if (obj == Py_None) {
		benc_state_write_char(bs, 'n');
	} else if (obj == Py_True) {
		benc_state_write_char(bs, 't');
	} else if (obj == Py_False) {
		benc_state_write_char(bs, 'f');
	} else if (PyBytes_CheckExact(obj)) {
		char *buff = PyBytes_AS_STRING(obj);
		int size = PyBytes_GET_SIZE(obj);

		benc_state_write_format(bs, 12, "%d:", size);
		benc_state_write_buffer(bs, buff, size);
	// }  else if () {
	// 	printf("INT\n");
	// 	// PyObject *encoded = PyObject_Str(obj);
	// 	// if (encoded == NULL)
	// 	// 	return -1;
	// 	// return _steal_list_append(rval, encoded);
	} else if (PyInt_Check(obj) || PyLong_Check(obj)) {
		// long x = PyLong_AsLong(obj);
		// benc_state_write_format(bs, 20, "i%lde", x);
		PyObject *encoded = PyObject_Str(obj);
		char *buff = PyBytes_AS_STRING(encoded);
		int size = PyBytes_GET_SIZE(encoded);
		benc_state_write_char(bs, 'i');
		benc_state_write_buffer(bs, buff, size);
		benc_state_write_char(bs, 'e');



	// } else if (PyInt_Check(obj) || PyLong_Check(obj)) {
	// 	long x = PyLong_AsLong(obj);
	// 	benc_state_write_format(bs, 20, "i%lde", x);
	// } else if (PyLong_CheckExact(obj)) {
	// 	long x = PyLong_AsLong(obj);
	// 	benc_state_write_format(bs, 20, "i%lde", x);
	} else if (PyFloat_Check(obj)) {
		double real_val = PyFloat_AS_DOUBLE(obj);
		
		printf("REAL (%G)\n", real_val);
		
		// PyObject *encoded = encoder_encode_float(s, obj);
		// if (encoded == NULL)
		// 	return -1;
		// return _steal_list_append(rval, encoded);

	} else if (PyList_CheckExact(obj)) {
		benc_state_write_char(bs, 'l');
		n = PyList_GET_SIZE(obj);
		for (i = 0; i < n; i++) {
			do_dump(bs, PyList_GET_ITEM(obj, i));
		}
		benc_state_write_char(bs, 'e');
	} else if (PyDict_CheckExact(obj)) {
		Py_ssize_t pos = 0;
		PyObject *key, *value;

		benc_state_write_char(bs, 'd');
		while (PyDict_Next(obj, &pos, &key, &value)) {
			do_dump(bs, key);
			do_dump(bs, value);
		}
		benc_state_write_char(bs, 'e');
	} else {
		printf("WTF??\n");
	}
}
 
static PyObject* dump(PyObject* self, PyObject* args)
{
	PyObject* obj;
	PyObject* f;
	struct benc_state bs;
	bs.size = 10;
	bs.offset = 0;
	bs.fout = f;
 
	if (!PyArg_ParseTuple(args, "OO", &obj, &f))
		return NULL;
	
	do_dump(&bs, obj);
 
	return Py_BuildValue("s#", bs.buffer, bs.offset);
}
 
static PyMethodDef cBencodeMethods[] =
{
	 // {"say_hello", say_hello, METH_VARARGS, "Greet somebody."},
	 {"dump", dump, METH_VARARGS, "Greet somebody."},
	 {NULL, NULL, 0, NULL}
};
 
PyMODINIT_FUNC
 
initcBencode(void)
{
	 (void) Py_InitModule("cBencode", cBencodeMethods);
}