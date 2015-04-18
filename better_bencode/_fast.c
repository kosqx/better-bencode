#include <Python.h>


struct benc_state {
    int size;
    int offset;
    char* buffer;
    PyObject* file;
};


static void benc_state_init(struct benc_state* bs) {
    bs->size = 256;
    bs->offset = 0;
    bs->buffer = malloc(bs->size);
    bs->file = NULL;
}


static void benc_state_free(struct benc_state* bs) {
    if (bs->buffer != NULL) {
        free(bs->buffer);
    }
}


static void benc_state_flush(struct benc_state* bs) {
    if (bs->offset > 0) {
        PyObject_CallMethod(bs->file, "write", "s#", bs->buffer, bs->offset);
        bs->offset = 0;
    }
}


static void benc_state_write_char(struct benc_state* bs, char c) {
    if (bs->file == NULL) {
        if (bs->offset + 1 >= bs->size) {
            bs->buffer = realloc(bs->buffer, bs->size * 2);
        }
        bs->buffer[bs->offset++] = c;
    } else {
        if (bs->offset + 1 >= bs->size) {
            PyObject_CallMethod(bs->file, "write", "s#", bs->buffer, bs->offset);
            bs->offset = 0;
        }
        bs->buffer[bs->offset++] = c;
    }
}


static void benc_state_write_buffer(struct benc_state* bs, char* buff, int size) {
    if (bs->file == NULL) {
        int new_size;
        for (new_size = bs->size; new_size <= bs->offset + size; new_size *= 2);
        if (new_size > bs->size) {
            bs->buffer = realloc(bs->buffer, new_size);
        }
        memcpy(bs->buffer + bs->offset, buff, size);
        bs->offset += size;
    } else {
        if (bs->offset + size >= bs->size) {
            PyObject_CallMethod(bs->file, "write", "s#", bs->buffer, bs->offset);
            bs->offset = 0;
        }
        if (size >= bs->size) {
            PyObject_CallMethod(bs->file, "write", "s#", buff, size);
        } else {
            memcpy(bs->buffer + bs->offset, buff, size);
            bs->offset += size;
        }
    }
}


static void benc_state_write_format(struct benc_state* bs, const int limit, const void *format, ...) {
    char buffer[limit + 1]; // moze by malloca()?

    va_list ap;
    va_start(ap, format);
    int size = vsnprintf(buffer, limit, format, ap);
    va_end(ap);

    return benc_state_write_buffer(bs, buffer, (size < limit) ? size : (limit - 1));
}


static char benc_state_read_char(struct benc_state* bs) {
    if (bs->file == NULL) {
        return bs->buffer[bs->offset++];
    } else {
        char *buffer;
        char result;
        Py_ssize_t length;
        PyObject *data =  PyObject_CallMethod(bs->file, "read", "i", 1);
        PyString_AsStringAndSize(data, &buffer, &length);
        result = buffer[0];
        Py_DECREF(data);
        return result;
    }
}


static PyObject *benc_state_read_pystring(struct benc_state* bs, int size) {
    if (bs->file == NULL) {
        PyObject *result = PyString_FromStringAndSize(bs->buffer + bs->offset, size);
        bs->offset += size;
        return result;
    } else {
        return PyObject_CallMethod(bs->file, "read", "i", size);
    }
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
    } else if (PyInt_Check(obj) || PyLong_Check(obj)) {
        // long x = PyLong_AsLong(obj);
        // benc_state_write_format(bs, 20, "i%lde", x);
        PyObject *encoded = PyObject_Str(obj);
        char *buff = PyBytes_AS_STRING(encoded);
        int size = PyBytes_GET_SIZE(encoded);
        benc_state_write_char(bs, 'i');
        benc_state_write_buffer(bs, buff, size);
        benc_state_write_char(bs, 'e');
    } else if (PyFloat_Check(obj)) {
        double real_val = PyFloat_AS_DOUBLE(obj);
        printf("REAL (%G)\n", real_val);
    } else if (PyList_CheckExact(obj)) {
        n = PyList_GET_SIZE(obj);
        benc_state_write_char(bs, 'l');
        for (i = 0; i < n; i++) {
            do_dump(bs, PyList_GET_ITEM(obj, i));
        }
        benc_state_write_char(bs, 'e');
    } else if (PyDict_CheckExact(obj)) {
        if (1) {
            Py_ssize_t index = 0;
            PyObject *keys, *key, *value;
            keys = PyDict_Keys(obj);
            PyList_Sort(keys);

            benc_state_write_char(bs, 'd');
            for (index = 0; index < PyList_Size(keys); index++) {
                key = PyList_GetItem(keys, index);
                value = PyDict_GetItem(obj, key);
                do_dump(bs, key);
                do_dump(bs, value);
            }
            benc_state_write_char(bs, 'e');

            Py_DECREF(keys);
        } else {
            Py_ssize_t pos = 0;
            PyObject *key, *value;

            benc_state_write_char(bs, 'd');
            while (PyDict_Next(obj, &pos, &key, &value)) {
                do_dump(bs, key);
                do_dump(bs, value);
            }
            benc_state_write_char(bs, 'e');
        }
    } else {
        printf("WTF??\n");
    }
    return 0;
}

static PyObject* dump(PyObject* self, PyObject* args) {
    PyObject* obj;
    PyObject* write;

    struct benc_state bs;
    benc_state_init(&bs);

    if (!PyArg_ParseTuple(args, "OO", &obj, &write))
        return NULL;

    bs.file = write;
    
    do_dump(&bs, obj);

    benc_state_flush(&bs);
    benc_state_free(&bs);

    return Py_BuildValue("s#", bs.buffer, bs.offset);
}


static PyObject* dumps(PyObject* self, PyObject* args) {
    PyObject* obj;
    PyObject* result;

    struct benc_state bs;
    benc_state_init(&bs);

    if (!PyArg_ParseTuple(args, "O", &obj))
        return NULL;

    do_dump(&bs, obj);

    result = Py_BuildValue("s#", bs.buffer, bs.offset);

    benc_state_free(&bs);

    return result;
}


static PyObject *do_load(struct benc_state *bs) {
    PyObject *retval = NULL;

    char first = benc_state_read_char(bs);
    //printf("%c\n", first);

    switch (first) {
        case 'n':
            Py_INCREF(Py_None);
            retval = Py_None;
            break;
        case 'f':
            Py_INCREF(Py_False);
            retval = Py_False;
            break;
        case 't':
            Py_INCREF(Py_True);
            retval = Py_True;
            break;
        case 'i': {
            int sign = 1;
            long long value = 0;
            char current = benc_state_read_char(bs);
            if (current == '-') {
                sign = -1;
                current = benc_state_read_char(bs);
            }
            // TODO: sprawdzanie przedzialow
            while (('0' <= current) && (current <= '9')) {
                value = value * 10 + (current - '0');
                current = benc_state_read_char(bs);
            }
            value *= sign;
            retval = PyLong_FromLongLong(value);

            } break;

        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9': {
            int size = first - '0';
            char current = benc_state_read_char(bs);
            // TODO: sprawdzanie przedzialow
            while (('0' <= current) && (current <= '9')) {
                size = size * 10 + (current - '0');
                current = benc_state_read_char(bs);
            }
            retval = benc_state_read_pystring(bs, size);
            } break;
        case 'e':
            Py_INCREF(PyExc_StopIteration);
            retval = PyExc_StopIteration;
            break;
        case 'l': {
            PyObject *v = PyList_New(0);
            PyObject *item;

            while (1) {
                item = do_load(bs);
                if (item == PyExc_StopIteration) {
                    Py_DECREF(PyExc_StopIteration);
                    break;
                }


                // if ( v2 == NULL ) {
                //  if (!PyErr_Occurred())
                //      PyErr_SetString(PyExc_TypeError,
                //          "NULL object in marshal data for list");
                //  Py_DECREF(v);
                //  v = NULL;
                //  break;
                // }
                PyList_Append(v, item);
            }

            retval = v;
            } break;
        case 'd': {
            PyObject *v = PyDict_New();
            // R_REF(v);
            // if (v == NULL) {
            //  retval = NULL;
            //  break;
            // }
            while (1) {
                PyObject *key, *val;
                key = do_load(bs);
                if (key == NULL)
                    break;
                if (key == PyExc_StopIteration) {
                    Py_DECREF(PyExc_StopIteration);
                    break;
                }
                val = do_load(bs);
                if (val != NULL)
                    PyDict_SetItem(v, key, val);
                Py_DECREF(key);
                Py_XDECREF(val);
            }
            // if (PyErr_Occurred()) {
            //  Py_DECREF(v);
            //  v = NULL;
            // }
            retval = v;
            } break;

        default:
            /* Bogus data got written, which isn't ideal.
               This will let you keep working and recover. */
            // PyErr_SetString(PyExc_ValueError, "bad input data");
            retval = NULL;
            break;
    }
    return retval;
}


static PyObject* load(PyObject* self, PyObject* args) {
    struct benc_state bs;
    bs.offset = 0;
    bs.file = NULL;

    if (!PyArg_ParseTuple(args, "O", &(bs.file)))
        return NULL;

    PyObject* obj = do_load(&bs);

    return obj;
}


static PyObject* loads(PyObject* self, PyObject* args) {
    struct benc_state bs;
    bs.offset = 0;
    bs.file = NULL;

    if (!PyArg_ParseTuple(args, "s#", &(bs.buffer), &(bs.size)))
        return NULL;

    PyObject* obj = do_load(&bs);

    return obj;
}


static PyMethodDef better_bencode_fastMethods[] = {
    {"load", load, METH_VARARGS, "load"},
    {"loads", loads, METH_VARARGS, "loads"},
    {"dump", dump, METH_VARARGS, "Write the value on the open file."},
    {"dumps", dumps, METH_VARARGS, "Return string with value"},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC

initbetter_bencode_fast(void) {
    (void) Py_InitModule("better_bencode_fast", better_bencode_fastMethods);
}
