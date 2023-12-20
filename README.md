# drive-file-downloader

Credentials are required from google in order to use drive APIs (Drive API V3). If you do not know how to do this, please see https://developers.google.com/identity/protocols/oauth2 or speak to developer. Please store these credentials in the top level domain as credentials.json. 

Upon running this program, you will be asked to authorize it, and a token will be downloaded to token.json. This token would need to be passed intact to the HPC in order to allow it to access the files via the API (I dont think that the HPC has browsers!).

Files that are downloaded

- Audio Files (Files Starting with YYYYMMDD)
- Log Files (File names that start with export_YYYY_MM_DD)

Parameters:
