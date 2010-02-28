from setuptools import setup

setup(name='py-amqp-client',
      version='0.1.0',
      author='John Weaver',
      author_email='john@pledge4code.com',
      url='http://github.com/saebyn/py-amqp-client/',
      package_dir={'': 'py-amqp-client'},
      packages=[''],
      install_requires=['amqplib >= 0.6.1'],
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.6',
      ],
      platforms=('Any',),
     )
