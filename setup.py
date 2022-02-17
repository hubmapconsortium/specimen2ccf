from distutils.core import setup

from setuptools import find_packages

from specimen2ccf import __version__

classifiers = """
Development Status :: 5 - Production/Stable
Environment :: Console
License :: OSI Approved :: BSD License
Intended Audience :: Science/Research
Topic :: Scientific/Engineering
Topic :: Scientific/Engineering :: Bio-Informatics
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Operating System :: POSIX :: Linux
""".strip().split('\n')

setup(name='specimen2ccf',
      version=__version__,
      description='A Python tool to convert HuBMAP specimen data to CCF Specimen Ontology (CCF-SCO) instances',
      author='Josef Hardi',
      author_email='johardi@stanford.edu',
      url='https://github.com/hubmapconsortium/specimen2ccf',
      license='BSD',
      classifiers=classifiers,
      install_requires=[
          'rdflib==5.0.0',
          'requests_file==1.5.1'
      ],
      python_requires='>=3.5, <3.9',
      test_suite='nose.collector',
      tests_require=['nose'],
      packages=find_packages(),
      include_package_data=True,
      scripts=['bin/specimen2ccf'])
