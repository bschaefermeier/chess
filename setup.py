from setuptools import setup

setup(name='chess',
      version='0.1',
      description='Chess game',
      url='http://pxll.de',
      author='Guybrush Threepwood',
      author_email='',
      license='MIT',
      packages=['chess'],
      install_requires=[
          'numpy',
          'matplotlib',
      ],
      zip_safe=False)
