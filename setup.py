from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='liveengage_data_app',
      version='0.1',
      description='Unofficial wrapper for LiveEngage data APIs',
      url='https://github.com/LiveEngage-Examples/liveengage_data_app',
      author='WildYorkies',
      author_email='',
      license='MIT',
      packages=['liveengage_data_app'],
      install_requires=[
          'requests',
          'requests_oauthlib',
      ],
      zip_safe=False)
