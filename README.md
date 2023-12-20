<div align="center">
<h1 align="center">
<img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" />
<br></h1>
<h3>◦ Code United: Shape, Share, Shine with GitHub Project:</h3>
<h3>◦ Developed with the software and tools below.</h3>

<p align="center">
<img src="https://img.shields.io/badge/tqdm-FFC107.svg?style=flat-square&logo=tqdm&logoColor=black" alt="tqdm" />
<img src="https://img.shields.io/badge/Jinja-B41717.svg?style=flat-square&logo=Jinja&logoColor=white" alt="Jinja" />
<img src="https://img.shields.io/badge/OpenSSL-721412.svg?style=flat-square&logo=OpenSSL&logoColor=white" alt="OpenSSL" />
<img src="https://img.shields.io/badge/OpenAI-412991.svg?style=flat-square&logo=OpenAI&logoColor=white" alt="OpenAI" />
<img src="https://img.shields.io/badge/SymPy-3B5526.svg?style=flat-square&logo=SymPy&logoColor=white" alt="SymPy" />
<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python" />

<img src="https://img.shields.io/badge/AIOHTTP-2C5BB4.svg?style=flat-square&logo=AIOHTTP&logoColor=white" alt="AIOHTTP" />
<img src="https://img.shields.io/badge/NumPy-013243.svg?style=flat-square&logo=NumPy&logoColor=white" alt="NumPy" />
<img src="https://img.shields.io/badge/Numba-00A3E0.svg?style=flat-square&logo=Numba&logoColor=white" alt="Numba" />
<img src="https://img.shields.io/badge/SQLite-003B57.svg?style=flat-square&logo=SQLite&logoColor=white" alt="SQLite" />
<img src="https://img.shields.io/badge/JSON-000000.svg?style=flat-square&logo=JSON&logoColor=white" alt="JSON" />
</p>
</div>

---

## 📖 Table of Contents
- [📖 Table of Contents](#-table-of-contents)
- [📍 Overview](#-overview)
- [📦 Features](#-features)
- [📂 repository Structure](#-repository-structure)
- [⚙️ Modules](#modules)
- [🚀 Getting Started](#-getting-started)
    - [🔧 Installation](#-installation)
    - [🤖 Running ](#-running-)
    - [🧪 Tests](#-tests)
- [🛣 Roadmap](#-roadmap)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [👏 Acknowledgments](#-acknowledgments)

---


## 📍 Overview

The repository contains an automated Python application geared towards processing and transcribing audio files from Google Drive. It has capabilities for authentication, file handling, and audio transcription using OpenAI's Whisper model. A user can download specific audio and log files, store them locally, and get them transcribed. The efficacy of the application is heightened with flexible command-line functionalities, and an extensive suite of dependencies, ensuring it fulfills a range of computational tasks relevant to transcription services.

---

## 📦 Features

|    | Feature            | Description                                                                                                        |
|----|--------------------|--------------------------------------------------------------------------------------------------------------------|
| ⚙️ | **Architecture**   | The code base is a procedural Python application with split functionality for handling audio files and authentication with Google Drive. |
| 📄 | **Documentation**  | Comments are provided within the code, however, there's no standalone documentation that details the codebase architecture or usage. |
| 🔗 | **Dependencies**   | The system makes use of numerous libraries including aiohttp for asynchronous HTTP requests, attrs for attribute management, and Google API services. |
| 🧩 | **Modularity**     | The code is well-organized with functions separated into modules handling Google Drive interactions and WSRP transcriptions. |
| 🧪 | **Testing**        | No clear testing strategy or test files are included. The codebase lacks a clear test component which is crucial for development. |
| ⚡️  | **Performance**    | With no observable performance optimizations or benchmarking, it's unclear how efficient the system is during large file handling. |
| 🔐 | **Security**       | OAuth 2.0 authentication is used for secure communication with Google Drive, ensuring secure data transmission.|
| 🔀 | **Version Control**| No specific version control strategy discovered. Ideally, commit history should be available for analysis.|
| 🔌 | **Integrations**   | The system integrates with Google Drive for file fetching and leverages OpenAI's Whisper API for audio transcriptions.|
| 📶 | **Scalability**    | The scalability remains uncertain due to the lack of information about how the system handles a large number of files or concurrent requests. |

---


## 📂 Repository Structure

```sh
└── /
    ├── credentials.json
    ├── main.py
    ├── requirements.txt
    ├── token.json
    └── wspr_transcribe.py

```

---


## ⚙️ Modules

<details closed><summary>Root</summary>

| File                              | Summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ---                               | ---                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| [main.py]({file_path})            | The code is an automated Python-based application to process and handle specific audio files from Google Drive. It authenticates Google Drive, downloads audio and log files based on a given date prefix, creates necessary directories if they don't exist, and stores these files locally. It also offers a transcribe functionality using a user-specified model. The script accepts command-line arguments for date, download, transcribe, upload, and selection of the whisper model version. |
| [requirements.txt]({file_path})   | The provided code is a `requirements.txt` file used to specify Python package dependencies for a project. It allows automatic installation of packages like aiohttp, aiosignal, anyio, attrs, colorama and much more, encompassing libraries for asynchronous HTTP requests, attributes manipulation, cryptography, network analysis, and Google API services among others. The comments illustrate how to create a Conda environment using this file.                                              |
| [wspr_transcribe.py]({file_path}) | The provided Python code leverages the Whisper API to transcribe audio files to text. The script has two primary functions: `translate_audio` and `transcribe`. The `translate_audio` function takes an audio file, transcribes it using the Whisper model and store the results in a JSON file. The `transcribe` function iterates over all the.wav audio files in a specified directory, and applies the `translate_audio` function to each one.                                                  |
| [credentials.json]({file_path})   | The credentials.json file holds configuration details for a Google-based OAuth2.0 authentication process. It contains identifiers like client_id, client_secret, and project_id. It also specifies the authentication, token request URLs, redirect URIs after authentication, and the javascript origins allowed to initiate the authentication process.                                                                                                                                           |
| [token.json]({file_path})         | The provided code is contents of a JSON configuration file that contains OAuth 2.0 credentials. These credentials include access token, refresh token, token URI, client ID, client secret, authorized scopes, and token expiry time. They are particularly used to authenticate and authorize applications, enabling them to access Google Drive services safely using Google's APIs.                                                                                                              |

</details>

---

## 🚀 Getting Started

***Dependencies***

Please ensure you have the following dependencies installed on your system:

`- ℹ️ Dependency 1`

`- ℹ️ Dependency 2`

`- ℹ️ ...`

### 🔧 Installation

1. Clone the  repository:
```sh
git clone ../
```

2. Change to the project directory:
```sh
cd 
```

3. Install the dependencies:
```sh
pip install -r requirements.txt
```

### 🤖 Running 

```sh
python main.py
```

### 🧪 Tests
```sh
pytest
```

---


## 🛣 Project Roadmap

> - [X] `ℹ️  Task 1: Implement X`
> - [ ] `ℹ️  Task 2: Implement Y`
> - [ ] `ℹ️ ...`


---

## 🤝 Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Submit Pull Requests](https://github.com/local//blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github.com/local//discussions)**: Share your insights, provide feedback, or ask questions.
- **[Report Issues](https://github.com/local//issues)**: Submit bugs found or log feature requests for LOCAL.

#### *Contributing Guidelines*

<details closed>
<summary>Click to expand</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a Git client.
   ```sh
   git clone <your-forked-repo-url>
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear and concise message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.

Once your PR is reviewed and approved, it will be merged into the main branch.

</details>

---

## 📄 License


This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

## 👏 Acknowledgments

- List any resources, contributors, inspiration, etc. here.

[**Return**](#Top)

---

