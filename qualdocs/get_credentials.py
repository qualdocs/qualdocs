def get_credentials(client_secret=None):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """

    import sys
    sys.argv=['']


    SCOPES = 'https://www.googleapis.com/auth/drive.readonly'

    if client_secret:
        CLIENT_SECRET_FILE = client_secret
    else:
        CLIENT_SECRET_FILE = 'client_secret.json'
    APPLICATION_NAME = 'Qualdocs'

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-api-qualdocs.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:

        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

