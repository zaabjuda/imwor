# coding=utf-8
__author__ = "Dmitry Zhiltsov"
__copyright__ = "Copyright 2015, Dmitry Zhiltsov"

from setuptools import setup


with open('README.rst') as f:
    readme = f.read()


setup(name='imwor',
      version='0.4.3',
      description='Imwor is an image processing application server',
      long_description=readme,
      url='http://',
      author='Dmitry Zhiltsov',
      author_email='dzhiltsov@me.com',
      license='GPLv3',
      include_package_data=True,
      packages=['imwor'],
      package_data={
          'imwor': ['frontalface.xml'],
      },
      install_requires=[
          'Pillow==3.0.0',
          'pycurl==7.19.5.3',
          'sphinx-me==0.3',
          'tornado==4.3',
      ],
      extras_require={
          'Facial Recognition': ['cv']
      },
      zip_safe=True,
      entry_points={'console_scripts': ['imwor = imwor.app:main']}
      )
