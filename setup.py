from setuptools import setup
from pythonaction.version import get_version

version = get_version()

setup(name='pythonaction',
      version=version,
      description='Test github actions',
      url='',
      author='Guillaume Witz',
      author_email='',
      license='BSD3',
      packages=['pythonaction'],
      package_data={'pythonaction': ['version.txt']},
      zip_safe=False,
      install_requires=[]
      )
