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
        'dictionary/ovpn_dictionary'
        'dictionary/*'
    ]
}


setup(name='txradius',
      version=version,
      author='jamiesun',
      author_email='jamiesun.net@gmail.com',
      url='https://github.com/talkincode/txradius',
      license='LGPL',
      description='RADIUS tools',
      long_description=open('README.md').read(),
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
              'radtest = txradius.radtest:cli',
              'txovpn_auth = txradius.openvpn.user_pass_verify:cli',
              'txovpn_connect = txradius.openvpn.client_connect:cli',
              'txovpn_disconnect = txradius.openvpn.client_disconnect:cli',
              'txovpn_config = txradius.openvpn.setup_config:echo',
              'txovpn_initdb = txradius.openvpn.statusdb:cli',
              'txovpn_list = txradius.openvpn.statusdb:list',
              'txovpn_daemon = txradius.openvpn.daemon:main',
              'txovpn_kill = txradius.openvpn.client_kill:cli',
          ]
      }
)