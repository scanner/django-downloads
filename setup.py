from distutils.core import setup
import os

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
#
# Cribbed from James Bennett's setup.py because I was lazy
# <james@b-list.org>  -- <http://www.b-list.org/>
#
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('downloads'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[13:] # Strip "downloads/" or "downloads\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name='django-downloads',
      version='0.1',
      description='Access controlled set of downloadable items for Django',
      author='Eric Scanner Luce',
      author_email='scanner@apricot.com',
      url='http://github.com/scanner/django-downloads',
      package_dir={'downloads': 'downloads'},
      packages=packages,
      package_data={'downloads': data_files},
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
      install_requires=['django-guardian>=0.2.2',
      			'South>=0.7.3',
                        'Django>=1.2'],
      )
