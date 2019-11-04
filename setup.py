from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='liveengage_data_app',
      version='0.1',
      description='Unofficial wrapper for LiveEngage data APIs',
      url='https://github.com/LiveEngage-Examples/liveengage_data_app',
      author='',
      author_email='',
      license='MIT',
      packages=['liveengage_data_app'],
      install_requires=[
          'requests',
          'requests_oauthlib',
      ],
      classifiers=[
          # How mature is this project? Common values are
          #   3 - Alpha
          #   4 - Beta
          #   5 - Production/Stable
          'Development Status :: 3 - Alpha',

          # Indicate who your project is intended for
          'Intended Audience :: Developers',

          # Pick your license as you wish (should match "license" above)
          'License :: OSI Approved :: MIT License',

          # Specify the Python versions you support here. In particular, ensure
          # that you indicate whether you support Python 2, Python 3 or both.
          'Programming Language :: Python :: 3.5',
      ],
      zip_safe=False)
