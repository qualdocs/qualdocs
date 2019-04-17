from setuptools import setup

setup(name='qualdocs',
      version='0.1.0',
      description='Qualitative data analysis based on Google Docs comments',
      url='http://github.com/qualdocs/qualdocs',
      author='Stuart Geiger',
      author_email='stuart@stuartgeiger.com',
      long_description='A python library for supporting open qualitative coding of text data in Google Docs comments. Integrates with the Google Docs API via PyDrive to create pandas dataframes for each code/tag and the highlighted text in a set of documents.',
      license='MIT',
      packages=['qualdocs'],
      install_requires=[
          'httplib2', 'apiclient', 'oauth2client', 'pandas', 'numpy', 'PyDrive', 'google-api-python-client'],
      zip_safe=False)
