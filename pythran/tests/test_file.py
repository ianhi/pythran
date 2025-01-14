from tempfile import mkstemp
from pythran.tests import TestEnv

import unittest

from pythran.typing import List


class TestFile(TestEnv):

    def __init__(self, *args, **kwargs):
        super(TestFile, self).__init__(*args, **kwargs)
        self.file_content = """azerty\nqwerty\n\n"""

    def tempfile(self):
        filename=mkstemp()[1]
        with open(filename,"w") as f:
            f.write(self.file_content)
        self.filename = filename
        return filename

    def reinit_file(self):
        with open(self.filename,"w") as f:
            f.write(self.file_content)
        return self.filename

    def test_filename_only_constructor(self):
        filename=mkstemp()[1]
        self.run_test("def filename_only_constructor(filename):\n open(filename)", filename, filename_only_constructor=[str])

    def test_open(self):
        filename=mkstemp()[1]
        self.run_test("def _open(filename):\n open(filename)", filename, _open=[str])

    def test_open_write(self):
        filename=mkstemp()[1]
        self.run_test("""def _open_write(filename):\n f=open(filename,"w+")\n f.write("azert")""", filename, _open_write=[str])
        self.assertEqual(open(filename).read(), "azert")

    def test_open_append(self):
        filename=mkstemp()[1]
        self.run_test("""def _open_append(filename):\n f=open(filename,"a")\n f.write("azert")""", filename, _open_append=[str])
        self.assertEqual(open(filename).read(), "azert"*2)

    def test_writing_mode_constructor(self):
        # Expecting file to be erased.
        # But python execution of test will erase it before pythran can :s
        self.tempfile()
        self.run_test("""def writing_mode_constructor(filename):\n f=open(filename, "w")\n f.close()""", self.filename,prelude=self.reinit_file, writing_mode_constructor=[str])
        self.assertEqual(open(self.filename).read(), "")

    #TODO : tester le differents modes du constructeur

    def test_write(self):
        self.filename=mkstemp()[1]
        content="""q2\naze23\n"""
        self.run_test("""def _write(filename):\n f=open(filename,'a+')\n n = f.write("""+str('str("""q2\naze23\n""")')+""")\n f.close()\n return n""", self.filename, _write=[str])
        self.assertEqual(open(self.filename).read(), content*2)

    def test_writelines(self):
        self.filename=mkstemp()[1]
        content=["""azerty""", "qsdfgh", "12345524"]
        self.run_test("""def _writelines(filename,_content):\n f=open(filename,'a+')\n f.writelines(_content)\n f.close()""", self.filename, content, _writelines=[str, List[str]])
        self.assertEqual(open(self.filename).read(), str().join(content)*2)

    def test_close(self):
        filename=mkstemp()[1]
        self.run_test("""
def file_close(filename):
	f=open(filename,'w')
	f.close()
	try:
		f.write("q")
	except:pass""", filename, file_close=[str])

    def test_truncate(self):
        self.tempfile()
        self.run_test("def _truncate(filename):\n f=open(filename)\n f.truncate(3); return f.read()", self.filename, _truncate=[str])

    def test_read(self):
        self.tempfile()
        self.run_test("def _read(filename):\n f=open(filename)\n return f.read()", self.filename, _read=[str])

    def test_read_size(self):
        self.tempfile()
        self.run_test("def _read_size(filename, size):\n f=open(filename)\n return f.read(size)", self.filename, 10, _read_size=[str, int])

    def test_read_oversize(self):
        self.tempfile()
        self.run_test("def _read_oversize(filename, size):\n f=open(filename)\n return f.read(size)", self.filename, len(self.file_content)+5, _read_oversize=[str, int])

    def test_readline(self):
        self.tempfile()
        self.run_test("def _readline(filename):\n f=open(filename)\n return [f.readline(),f.readline(), f.readline(),f.readline(),f.readline()]", self.filename, _readline=[str])

    def test_readline_size(self):
        self.tempfile()
        self.run_test("def _readline_size(filename):\n f=open(filename)\n return [f.readline(7),f.readline(3),f.readline(4),f.readline(),f.readline(10)]", self.filename, _readline_size=[str])

    def test_readline_size_bis(self):
        self.tempfile()
        self.run_test("def _readline_size_bis(filename):\n f=open(filename)\n return [f.readline(4),f.readline(3),f.readline(10),f.readline(),f.readline(5)]", self.filename, _readline_size_bis=[str])

    def test_readlines(self):
        self.tempfile()
        self.run_test("def _readlines(filename):\n f=open(filename)\n return f.readlines()", self.filename, _readlines=[str])

    def test_offset_read(self):
        self.tempfile()
        self.run_test("""def _offset_read(filename):\n f=open(filename)\n f.seek(5)\n return f.read()""", self.filename, _offset_read=[str])

    def test_offset_write(self):
        self.tempfile()
        self.run_test("""def _offset_write(filename):\n f=open(filename, "a")\n f.seek(5)\n f.write("aze")\n f.close()\n return open(filename,"r").read()""", self.filename, prelude = self.reinit_file, _offset_write=[str])

    def test_next(self):
        self.tempfile()
        self.run_test("""def _next(filename):\n f=open(filename)\n return [next(f), next(f)]""", self.filename, _next=[str])

    def test_iter(self):
        self.tempfile()
        self.run_test("""def _iter(filename):\n f=open(filename)\n return [l for l in f]""", self.filename, _iter=[str])

    def test_fileno(self):
        self.tempfile()
        # Useless to check if same fileno, just checking if fct can be called
        self.run_test("""def _fileno(filename):\n f=open(filename)\n a=f.fileno()\n return a!= 0""", self.filename, _fileno=[str])

    def test_isatty(self):
        self.tempfile()
        self.run_test("""def _isatty(filename):\n f=open(filename)\n return f.isatty()""", self.filename, _isatty=[str])

    def test_truncate(self):
        self.tempfile()
        self.run_test("""def _truncate(filename):\n f=open(filename, 'a')\n f.seek(3)\n f.truncate()\n f.close()\n return open(filename).read()""", self.filename, _truncate=[str])

    def test_truncate_size(self):
        self.tempfile()
        self.run_test("""def _truncate_size(filename):\n f=open(filename, 'a')\n f.truncate(4)\n f.close()\n return open(filename).read()""", self.filename, _truncate_size=[str])

    def test_flush(self):
        self.tempfile()
        # Don't know how to check properly, just checking fct call.
        self.run_test("""def _flush(filename):\n f=open(filename, 'a')\n f.flush()""", self.filename, _flush=[str])

    def test_tell(self):
        self.tempfile()
        self.run_test("""def _tell(filename):\n f=open(filename)\n f.read(3)\n return f.tell()""", self.filename, _tell=[str])

    def test_seek(self):
        self.tempfile()
        self.run_test("""def _seek(filename):\n f=open(filename, 'a')\n f.seek(3)\n return f.tell()""", self.filename, _seek=[str])

    def test_attribute_closed(self):
        self.tempfile()
        self.run_test("""def _attribute_closed(filename):\n f=open(filename, 'a')\n return f.closed""", self.filename, _attribute_closed=[str])

    def test_attribute_name(self):
        self.tempfile()
        self.run_test("""def _attribute_name(filename):\n return open(filename, 'a').name""", self.filename, _attribute_name=[str])

    def test_attribute_mode(self):
        self.tempfile()
        self.run_test("""def _attribute_mode(filename):\n return open(filename, 'a').mode""", self.filename, _attribute_mode=[str])

    def test_attribute_newlines(self):
        self.tempfile()
        self.run_test("""def _attribute_newlines(filename):\n return open(filename, 'a').newlines""", self.filename, _attribute_newlines=[str])

    def test_map_iter(self):
        self.tempfile()
        self.run_test("""def _map_iter(filename):\n f=open(filename)\n return list(map(lambda s: len(s), f))""", self.filename, _map_iter=[str])

    # The following tests insures the PROXY compatibility with rvalues
    def test_rvalue_write(self):
        self.filename=mkstemp()[1]
        self.run_test("""def _rvalue_write(filename):\n open(filename,'a+').write("aze")""", self.filename, _rvalue_write=[str])

    def test_rvalue_writelines(self):
        self.filename=mkstemp()[1]
        self.run_test("""def _rvalue_writelines(filename):\n open(filename,'a+').writelines(["azerty", "qsdfgh", "12345524"])""", self.filename, _rvalue_writelines=[str])

    def test_rvalue_close(self):
        filename=mkstemp()[1]
        self.run_test("""
            def _rvalue_close(filename):
                open(filename,'w').close()""", filename, _rvalue_close=[str])

    def test_rvalue_read(self):
        self.tempfile()
        self.run_test("def _rvalue_read(filename):\n return open(filename).read()", self.filename, _rvalue_read=[str])

    def test_rvalue_readline(self):
        self.tempfile()
        self.run_test("def _rvalue_readline(filename):\n return open(filename).readline()", self.filename, _rvalue_readline=[str])

    def test_rvalue_readlines(self):
        self.tempfile()
        self.run_test("def _rvalue_readlines(filename):\n return open(filename).readlines()", self.filename, _rvalue_readlines=[str])

    def test_rvalue_next(self):
        self.tempfile()
        self.run_test("""def _rvalue_next(filename):\n return next(open(filename))""", self.filename, _rvalue_next=[str])

    def test_rvalue_fileno(self):
        self.tempfile()
        # Useless to check if same fileno, just checking if fct can be called
        self.run_test("""def _rvalue_fileno(filename):\n open(filename).fileno()""", self.filename, _rvalue_fileno=[str])

    def test_rvalue_isatty(self):
        self.tempfile()
        self.run_test("""def _rvalue_isatty(filename):\n return open(filename).isatty()""", self.filename, _rvalue_isatty=[str])

    def test_rvalue_truncate(self):
        self.tempfile()
        self.run_test("""def _rvalue_truncate(filename):\n open(filename, 'a').truncate(3)""", self.filename, _rvalue_truncate=[str])

    def test_rvalue_flush(self):
        self.tempfile()
        self.run_test("""def _rvalue_flush(filename):\n open(filename, 'a').flush()""", self.filename, _rvalue_flush=[str])

    def test_rvalue_tell(self):
        self.tempfile()
        self.run_test("""def _rvalue_tell(filename):\n return open(filename, 'a').tell()""", self.filename, _rvalue_tell=[str])

    def test_rvalue_seek(self):
        self.tempfile()
        self.run_test("""def _rvalue_seek(filename):\n open(filename, 'a').seek(3)""", self.filename, _rvalue_seek=[str])
