# This will create a dist directory containing the executable file, all the data
# directories. All Libraries will be bundled in executable file.
#
# Run the build process by entering 'pygame2exe.py' or
# 'python pygame2exe.py' in a console prompt.
#
# To build exe, python, pygame, and py2exe have to be installed. After
# building exe none of this libraries are needed.
 
try:
    from distutils.core import setup
    import py2exe, pygame
    from modulefinder import Module
    import glob, fnmatch
    import sys, os, shutil
    import operator
    import subprocess
    import struct
    import zipfile
except ImportError, message:
    raise SystemExit,  "Unable to load module. %s" % message
 
#hack which fixes the pygame mixer and pygame font
origIsSystemDLL = py2exe.build_exe.isSystemDLL # save the orginal before we edit it
def isSystemDLL(pathname):
    # checks if the freetype and ogg dll files are being included
    if os.path.basename(pathname).lower() in ("sdl_ttf.dll", "libfreetype-6.dll", "libogg-0.dll"):
            return 0
    return origIsSystemDLL(pathname) # return the orginal function
py2exe.build_exe.isSystemDLL = isSystemDLL # override the default function with this one

class pygame2exe(py2exe.build_exe.py2exe): #This hack make sure that pygame default font is copied: no need to modify code for specifying default font
    def copy_extensions(self, extensions):
        #Get pygame default font
        pygamedir = os.path.split(pygame.base.__file__)[0]
        pygame_default_font = os.path.join(pygamedir, pygame.font.get_default_font())
 
        #Add font to list of extension to be copied
        extensions.append(Module("pygame.font", pygame_default_font))
        py2exe.build_exe.py2exe.copy_extensions(self, extensions)
 
class BuildExe:
    def __init__(self):
        #Name of starting .py
        self.script = "main.py"
 
        #Name of program
        self.project_name = "PyGG2"
 
        #Project url
        self.project_url = "https://github.com/nightcracker/PyGG2"
 
        #Version of program
        self.project_version = "0.0"
 
        #License of the program
        self.license = "GPL v3"
 
        #Auhor of program
        self.author_name = "nightcracker / Orpheon"
        self.author_email = "nightcracker@nclabs.org"
        self.copyright = "Copyright (c) 2011"
 
        #Description
        self.project_description = "Python implementation of Gang Garrison 2"
 
        #Icon file (None will use pygame default icon)
        self.icon_file = None
 
        #Extra files/dirs copied to game
        self.extra_datas = []
 
        #Extra/excludes python modules
        self.extra_modules = []
        self.exclude_modules = []
        
        #DLL Excludes
        self.exclude_dll = ['w9xpopen.exe']
        #python scripts (strings) to be included, seperated by a comma
        self.extra_scripts = []
 
        #Zip file name (None will bundle files in exe instead of zip file)
        self.zipfile_name = "dependencies.dat"
 
        #Dist directory
        self.dist_dir = "dist"
 
    ## Code from DistUtils tutorial at http://wiki.python.org/moin/Distutils/Tutorial
    ## Originally borrowed from wxPython's setup and config files
    def opj(self, *args):
        path = os.path.join(*args)
        return os.path.normpath(path)
 
    def find_data_files(self, srcdir, *wildcards, **kw):
        # get a list of all files under the srcdir matching wildcards,
        # returned in a format to be used for install_data
        def walk_helper(arg, dirname, files):
            if '.svn' in dirname:
                return
            names = []
            lst, wildcards = arg
            for wc in wildcards:
                wc_name = self.opj(dirname, wc)
                for f in files:
                    filename = self.opj(dirname, f)
 
                    if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                        names.append(filename)
            if names:
                lst.append( (dirname, names ) )
 
        file_list = []
        recursive = kw.get('recursive', True)
        if recursive:
            os.path.walk(srcdir, walk_helper, (file_list, wildcards))
        else:
            walk_helper((file_list, wildcards),
                        srcdir,
                        [os.path.basename(f) for f in glob.glob(self.opj(srcdir, '*'))])
        return file_list
 
    def run(self):
        if os.path.isdir(self.dist_dir): #Erase previous destination dir
            shutil.rmtree(self.dist_dir)
        
        #Use the default pygame icon, if none given
        if self.icon_file == None:
            path = os.path.split(pygame.__file__)[0]
            self.icon_file = os.path.join(path, 'pygame.ico')
 
        #List all data files to add
        extra_datas = []
        for data in self.extra_datas:
            if os.path.isdir(data):
                extra_datas.extend(self.find_data_files(data, '*'))
            else:
                extra_datas.append(('.', [data]))
        
        setup(
            cmdclass = {'py2exe': pygame2exe},
            version = self.project_version,
            description = self.project_description,
            name = self.project_name,
            url = self.project_url,
            author = self.author_name,
            author_email = self.author_email,
            license = self.license,
 
            # targets to build
            windows = [{
                'script': self.script,
                'icon_resources': [(0, self.icon_file)],
                'copyright': self.copyright
            }],
            options = {'py2exe': {'optimize': 2, 'bundle_files': 1, 'compressed': True, \
                                  'excludes': self.exclude_modules, 'packages': self.extra_modules, \
                                  'dll_excludes': self.exclude_dll, \
                                  'includes': self.extra_scripts} },
            zipfile = self.zipfile_name,
            data_files = extra_datas,
            dist_dir = self.dist_dir
            )
        
        if os.path.isdir('build'): #Clean up build dir
            shutil.rmtree('build')
    
    def after_building(self):
        # rename main.exe to pygg2.exe
        os.rename("dist/main.exe",  "dist/pygg2.exe")
        
        # zip up sprites
        print("Zip up sprites")
        zip = zipfile.ZipFile("dist/sprites.zip", "w", zipfile.ZIP_DEFLATED)
        for folder, subfolders, files in os.walk("sprites"):
            for file in files:
                path = os.path.join(folder, file)
                print("Zipping %s into dist/sprites.zip" % path)
                zip.write(path, os.path.relpath(path, "sprites"))
        zip.close()
        
        # and also zip up the complete distribution
        print("Creating dist archive ready for distribution")
        zip = zipfile.ZipFile("dist/pygg2.zip", "w", zipfile.ZIP_DEFLATED)
        for folder, subfolders, files in os.walk("dist"):
            for file in files:
                # what are you talking about? it's zipfiles all the way down!
                if file == "pygg2.zip": continue
                
                path = os.path.join(folder, file)
                print("Zipping %s into dist/pygg2.zip" % path)
                zip.write(path, os.path.join("pygg2", os.path.relpath(path, "dist")))
        zip.close()
        

def build():
    sys.argv.append('py2exe')
    build = BuildExe()
    build.run()
    build.after_building()

if __name__ == '__main__':
    print("Don't run directly - run python make.py build")
    