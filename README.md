# WAP - Windows Artifact Parser

![WAP](https://github.com/user-attachments/assets/c4428f83-a8d7-4acb-be72-522b3bd5b48e)

The Windows Artifact Parser automates the process of parsing Windows artifacts, saving time and effort for forensic investigators. The tool processes the input data, extracts relevant information, and generates comprehensive reports for each artifact type.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

## Table of Contents

- [Introduction](#-introduction)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Usage](#-usage)
- [Support](#coffee-support)

## 📚 Introduction

The Windows Artifact Parser is a command line tool designed to automatically parse various Windows artifacts, providing valuable insights for forensic investigations. The tool supports the parsing of multiple artifact types, including registry hives, event logs, browser data, and more.

## 🚀 Features

- Automatic parsing of multiple Windows artifacts:
  - Amcache
  - Browser data (Chrome, Firefox, Edge)
  - Jumplist
  - MFT
  - UsnJournal and LogFile
  - Prefetch
  - Recent Files
  - Recycle Bin
  - Shellbags (NTUSER and UsrClass.DAT)
  - Registry Hives
  - Windows Event Logs
- Supports input as a zip file of collected data or a directory.

## 📋 Prerequisites

Before proceeding with the execution, make sure you have the following prerequisites:

- .NET Framework (required for Eric Zimmerman's tools)

## 💻 Usage

To execute the tool, follow the steps below:

1. **Open Command Prompt as Administrator:**
   Ensure you have administrative privileges to run the tool effectively.

2. **Run the Tool:**
   Depending on whether you are using a zip file or a directory, use the appropriate command.

   - **If using a ZIP file:**
     - **Basic ZIP file:**
       ```sh
       WAP.exe --zip [Path to ZIP]
       ```
     - **Password-protected ZIP file:**
       ```sh
       WAP.exe --zip [Path to ZIP] --password [ZIP PASSWORD]
       ```

   - **If using a directory:**
     ```sh
     WAP.exe --directory [Path to DIRECTORY]
     ```

3. **Wait for Parsing to Complete:**
   The tool will automatically process the input data and generate the output in the specified format. Once the parsing is complete, the output structure will be as follows:

   - **For ZIP files:**
     - Extracted data will be located in:
       ```
       WAP_Extraction_[ZIP_NAME]\Extracted_Data
       ```
     - Results will be stored in:
       ```
       WAP_Extraction_[ZIP_NAME]\Results
       ```

   - **For Directories:**
     - Results will be stored in:
       ```
       Results_[DIRECTORY_NAME]
       ```

By following these steps, you can efficiently run the Windows Artifact Parser and obtain comprehensive reports on the parsed Windows artifacts. **Download the executable from [Releases](https://github.com/SanketBaraiya/WAP/releases) Page.**

**Note:** Some binaries used to parse the artifacts are unsigned and may be flagged by your AV. So please make sure that the tool is executed in environment where the binaries are not removed by AV, for proper execution.

***Currently tested with following collections:***
- [CyLR](https://github.com/orlikoski/CyLR)
- [Magnet Response](https://www.magnetforensics.com/resources/magnet-response/)
- [artifactcollector](https://github.com/forensicanalysis/artifactcollector)

## :coffee: Support

[![PayPal](https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://www.paypal.me/sanketbaraiya16)
[![Google Pay](https://img.shields.io/badge/GooglePay-%233780F1.svg?style=for-the-badge&logo=Google-Pay&logoColor=white)](https://mega.nz/file/5AgGWYJY#OS2bS3sbPkUai0lE9wW6ymq_Ub1gLHn2XCZVanMWYts)
[![Paytm](https://img.shields.io/badge/Paytm-1C2C94?style=for-the-badge&logo=paytm&logoColor=05BAF3)](https://mega.nz/file/kBwSxKpL#BMColiA74JWw1cXx7Z0LdpEjBRmkc6rp5oWmq23pXNY)
