
<div  align="center">

<h1  align="center">

<img  src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg"  width="100" />

<br></h1>

<h3>◦ Developed with the software and tools below.</h3>

  

<p  align="center">

<img  src="https://img.shields.io/badge/tqdm-FFC107.svg?style=flat-square&logo=tqdm&logoColor=black"  alt="tqdm" />

<img  src="https://img.shields.io/badge/OpenAI-412991.svg?style=flat-square&logo=OpenAI&logoColor=white"  alt="OpenAI" />

<img  src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white"  alt="Python" />

<img  src="https://img.shields.io/badge/JSON-000000.svg?style=flat-square&logo=JSON&logoColor=white"  alt="JSON" />

</p>

</div>

  

---

  

##  📖 Table of Contents

-  [📖 Table of Contents](#-table-of-contents)

-  [📍 Overview](#-overview)

-  [📦 Features](#-features)

-  [📂 repository Structure](#-repository-structure)

-  [⚙️ Modules](#modules)

-  [🚀 Getting Started](#-getting-started)

-  [🔧 Installation](#-installation)

-  [🤖 Running ](#-running-)

-  [📄 License](#-license)

-  [👏 Acknowledgments](#-acknowledgments)

  

---

  
  

##  📍 Overview

  

The repository powers an application that enables automatic transcription of audio files. By leveraging the Whisper API and Google services, the application can extract audio files from Google Drive based on a specified date, transcribe them into text, and then upload the transcriptions back to Drive. This end-to-end automation makes the application valuable to users who handle large volumes of audio data, such as journalists or researchers. It optimizes their workflow by reducing the time and effort needed to manually transcribe audio content.

  

---

  

##  📦 Features

  
|    | Feature            | Description                                                                                                        |
|----|--------------------|--------------------------------------------------------------------------------------------------------------------|

| ⚙️ |  **Architecture**  | The repository is constructed from five main components, `main.py`, `requirements.txt`, `wspr_transcribe.py`, `credentials.json`, `token.json`. The system uses Google Drive API, OpenAI's Whisper ASR API.   |

| 🔗 |  **Dependencies**  | The `requirements.txt` file lists quite a broad range of dependencies, including those for HTTP communication, cryptography, Google service interaction, and Open AI's whisper API. |

| 🔐 |  **Security**  | The system uses OAuth 2.0 via `credentials.json` and `token.json` for secure access to Google's Drive and Whisper APIs. However, storing these files in the code repository might expose sensitive information, potentially compromising security. |


---

  
  

##  📂 Repository Structure

  
Note that `credentials.json` will need to  be provided by the user. To do this please read  https://developers.google.com/workspace/guides/create-credentials and set up an OAuth2 crediential with access to the Google Drive API V3. Once ran, it will download a `token.json` which will need to be periodically refreshed. 
```sh

└──  /

├──  credentials.json

├──  main.py

├──  requirements.txt

├──  token.json

└──  wspr_transcribe.py

  

```

  

---

  
  

##  ⚙️ Modules

  

<details  closed><summary>Root</summary>

  

| File | Summary |

|  ---  |  ---  |

|  [main.py]({file_path})  | The script downloads audio files from Google Drive based on a specific date, transcribes them using a given version of the Whisper model and uploads them back to Drive. The user can control these actions through command line arguments (download, transcribe, upload, date and Whisper model). Main functions include Google Drive authentication, date validation, creating directories, and handling file downloads. |

|  [requirements.txt]({file_path})  | The given requirements.txt file specifies various package dependencies and their versions required to run an application.|

|  [wspr_transcribe.py]({file_path})  | The code in wspr_transcribe.py transcribes audio files to text using the Whisper API. It iterates through.wav files in a specified date directory, transcribes each file's audio content into text, and saves the resulting transcriptions as.json files in a corresponding Text directory. The transcription model used can be selected based on size (base, medium, large), with base as the default size. |

|  [credentials.json]({file_path})  | The credentials.json file contains configuration settings necessary for OAuth 2.0 authentication with Google's API. The file includes the client id & secret, project id, auth & token URIs, certificate URL, and various redirect URIs and JavaScript origins for handling authorized requests and responses. |

|  [token.json]({file_path})  | The token.json file holds authentication and authorization details for the Google Drive API, including tokens (main and refresh), token URI, client ID and secret, required scopes, and the token's expiry date. This information enables secure access to the Drive API's functionalities for programmatic data manipulation on Google Drive. |

  

</details>

  

---

  

##  🚀 Getting Started

  

***Dependencies***

  

Please ensure you have the following dependencies installed on your system:

  
  

###  🔧 Installation

  

1. Clone the repository:

```sh

git  clone https://github.com/afletcher53/drive-file-downloader

```

  

2. Change to the project directory:

```sh

cd drive-file-downloader

```

  

3. Install the dependencies:

```sh

pip  install  -r  requirements.txt

```

  

###  🤖 Running

  

```sh

python  main.py --date=18/12/2023 --download --transcribe --whispermodel=medium

```



  
</details>

  

---

  

##  📄 License

  
  

This project is protected under the [Mozilla Public License 2.0](https://choosealicense.com/licenses/mpl-2.0/) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/mpl-2.0/) file.

  

---

  
[**Return**](#Top)

  

---
