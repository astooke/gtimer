from setuptools import setup

long_description = 'TBD'

setup(name='gtimer',
      version='0.1.0-b',
      description='A global Python timer',
      long_description=long_description,
      url='http://github.com/astooke/gtimer',
      author='Adam Stooke',
      author_email='adam.stooke@gmail.com',
      license='MIT',
      packages=['gtimer',
                'gtimer.disabled',
                'gtimer.local',
                'gtimer.private',
                'gtimer.public'],
      zip_safe=False)
