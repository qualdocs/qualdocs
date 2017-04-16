from setuptools import setup

setup(name='qualdocs',
      version='0.0.1',
      description='Qualitative data analysis based on Google Docs comments',
      url='http://github.com/qualdocs/qualdocs',
      author='Stuart Geiger',
      author_email='stuart@stuartgeiger.com',
      license='MIT',
      packages=['qualdocs'],
      install_requires=[
          'httplib2', 'apiclient', 'oauth2client', 'pandas', 'numpy', 'PyDrive', 'google-api-python-client'],
      zip_safe=False)
