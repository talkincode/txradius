#!/usr/bin/python


from setuptools import setup, find_packages
import txradius

version = txradius.__version__

install_requires = [
    'six>=1.8.0',
    'Twisted>=15.0.0',
    'Click'
]
install_requires_empty = []

package_data={
    'txradius': [
        'dictionary/*'
    ]
}


setup(name='txradius',
      version=version,
      author='jamiesun',
      author_email='jamiesun.net@gmail.com',
      url='https://github.com/talkincode/txradius',
      license='GPL',
      description='RADIUS tools',
      long_description="radius tools based twisted",
      classifiers=[
       'Development Status :: 6 - Mature',
       'Intended Audience :: Developers',
       'Programming Language :: Python :: 2.6',
       'Programming Language :: Python :: 2.7',
       'Topic :: Software Development :: Libraries :: Python Modules',
       'Topic :: System :: Systems Administration :: Authentication/Directory',
       ],
      packages=find_packages(),
      package_data=package_data,
      keywords=['radius', 'AAA','authentication','accounting','authorization','toughradius'],
      zip_safe=True,
      include_package_data=True,
      eager_resources=['txradius'],
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
              'radtest = txradius.radtest:cli'
          ]
      }
)