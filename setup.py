#from distutils.core import setup, Extension

#module1 = Extension('qx',
                    #sources = ['qx.c'])

#setup (name = 'qx',
       #version = '1.0',
       #description = 'This is a demo package',
       #ext_modules = [module1]) 


#from distutils.core import setup, Extension
 
#module1 = Extension('hello', sources = ['hellomodule.c'])
 
#setup (name = 'PackageName',
        #version = '1.0',
        #description = 'This is a demo package',
        #ext_modules = [module1])
        
        
from distutils.core import setup, Extension
 
module1 = Extension('cBencode', sources = ['cBencode.c'])
 
setup (name = 'PackageName',
        version = '1.0',
        description = 'This is a demo package',
        ext_modules = [module1])