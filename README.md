# qualdocs
A python library for supporting open qualitative coding of text data in Google Docs comments.

## Motivation

Open qualitative coding (also called inductive qualitative coding) is a methodology common among social scientists who deal with heterogeneous, unstructured text data, such as interviews. Text is annotated with tags, called codes, which can be further categorized into a hierarchical structure. In contrast to closed qualitative coding, there is no pre-set list or typology of tags, as the researchers are supposed to inductively generate a typology. 

Existing offerings for open qualitative coding are closed source and expensive (MaxQDA, nVivo, Dedoose). Google Docs provides a relatively easy-to-use and free collaborative platform for document annotation, but there is not an easy way to aggregate, synthesize, or search through codes -- particularly across documents. This is where qualdocs comes in.

## How to code text in Google Docs
This approach to qualitative coding is based on comments made in Google Docs files. Leave one set of codes per comment, in any of the following formats:
```
topcode1
topcode1, topcode2
topcode2: subcode1
topcode1: subcode1: subsubcode1
topcode2: subcode1, subcode2, subcode3
topcode1: subcode2: subsubcode1, subsubcode2, subsubcode3
```
You can see a sample of docs coded in [this public folder](https://drive.google.com/open?id=1EtYEx9U9KRfAOAh9LaSsmIQyDqiJ392qZJom1Jmv5MI) on Google Drive.

## Setup

### Install the library

`pip install qualdocs`

### Turn on the Drive API for your account

(Instructions from [Google API quickstart](https://developers.google.com/drive/v3/web/quickstart/python)

1. Use [this wizard](https://console.developers.google.com/start/api?id=drive) to create or select a project in the Google Developers Console and automatically turn on the API. Click Continue, then Go to credentials.
1. On the Add credentials to your project page, click the Cancel button.
1. At the top of the page, select the OAuth consent screen tab. Select an Email address, enter a Product name if not already set, and click the Save button.
1. Select the Credentials tab, click the Create credentials button and select OAuth client ID.
1. Select the application type Other, enter the name "Drive API Quickstart", and click the Create button.
1. Click OK to dismiss the resulting dialog.
1. Click the file_download (Download JSON) button to the right of the client ID.
1. Move this file to your working directory and rename it client_secret.json.

### Do the OAuth dance

Run `python qualdocs/get_credentials.py`, which will open up a browser window for you to authenticate. After you complete it, close the window and a file will be created in `[your home directory].credentials/`

## Usage

Alternatively, see [this Jupyter notebook](https://github.com/qualdocs/qualdocs/blob/master/qualdocs-example.ipynb) for a demo.

```
import qualdocs
import pandas as pd

credentials = qualdocs.get_credentials()
service = qualdocs.get_service()

ids = qualdocs.get_file_ids(service, search="docathon")

json_dict = qualdocs.get_json_dict(service, ids)

df = qualdocs.json_to_df(json_dict)
```

## Dependencies

Requires pandas, httplib2, apiclient, oauth2client, numpy, PyDrive
