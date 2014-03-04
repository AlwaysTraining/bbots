from distutils.core import setup
from os import  path
from glob import glob

def get_modules():
    objdir = path.join(path.dirname(__file__),'bbots/*.py')
    mods=[]
    for file in glob(objdir):
        name = path.splitext(path.basename(file))[0]
        if name == '__init__':
            continue
        mods.append("bbots." + name)
    return mods

setup(name="bbots",
      version="0.1",
      packages = ['bbots'],
      py_modules = get_modules(),
      scripts = ['bin/bbots-cli.py'],
      author = ['Derrick Karimi'],
      author_email = [ 'derrick.karimi@gmail.com' ],
      maintainer = ['Derrick Karimi'],
      maintainer_email = ['derrick.karimi@gmail.com'],
      description = ['bbots'],
      url = ['https://github.com/AlwaysTraining/bbots'],
      download_url = ['https://github.com/AlwaysTraining/bbots'],
      install_requires=['pexpect <= 2.4'])
