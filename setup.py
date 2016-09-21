from setuptools import setup

setup(name='gtimer',
      version='1.0.0-beta.4',
      description='A global Python timer',
      long_description='Documentation at: http://gtimer.readthedocs.io',
      url='http://github.com/astooke/gtimer',
      author='Adam Stooke',
      author_email='adam.stooke@gmail.com',
      license='MIT',
      packages=['gtimer',
                'gtimer.disabled',
                'gtimer.local',
                'gtimer.private',
                'gtimer.public'],
      classifiers=['Development Status :: 4 - Beta',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3'],
      zip_safe=False)
