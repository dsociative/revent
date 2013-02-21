#!/usr/bin/env python

from setuptools import setup


setup(name='revent',
      description='event queue on libev with dumps to redis',
      author='dsociative',
      author_email='admin@geektech.ru',
      packages=['revent'],
      dependency_links=[
          "http://github.com/dsociative/rmodel/tarball/master#egg=rmodel-0.0.0",
      ],
      install_requires=[
          'redis',
          'pyev',
          'rmodel',
          'unittest2'
      ]
    )