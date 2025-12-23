# mdtodocu - Markdown to Docusaurus Converter

## Table of Contents

- [mdtodocu - Markdown to Docusaurus Converter](#mdtodocu---markdown-to-docusaurus-converter)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Features](#features)
  - [Installation](#installation)
    - [Using Makefile](#using-makefile)
  - [Usage](#usage)
    - [1. Convert mdbook to Docusaurus](#1-convert-mdbook-to-docusaurus)
    - [2. Command-Line Arguments](#2-command-line-arguments)
      - [Example:](#example)
  - [How It Works](#how-it-works)
  - [Notes](#notes)
  - [Contributing](#contributing)
  - [License](#license)

---

## Introduction

**mdtodocu** is a Python script designed to convert markdown files structured for **mdbook** into a format compatible with **Docusaurus**. It automates the process of reorganizing files, adding frontmatter, creating directory structures, and handling images required by Docusaurus. This tool is ideal for developers migrating documentation from mdbook to Docusaurus.

---

## Features

- Converts mdbook `SUMMARY.md` hierarchy into Docusaurus-compatible directory structures.
- Automatically generates `_category_.json` files for Docusaurus sidebar categories.
- Adds frontmatter (title and sidebar position) to markdown files.
- Recursively searches for and organizes markdown files.
- Handles image references in markdown files:
  - Updates image paths to use `./img/` prefix.
  - Copies images to the appropriate `./img/` directory.
  - Verifies and logs missing images.
- Processes `!!wiki.include` statements to include external markdown content.
- Preserves the original content while adapting it for Docusaurus.

---

## Installation

### Using Makefile

The repository includes a **Makefile** to simplify installation, rebuilding, and uninstallation of the script.

1. Clone the repository:
   ```bash
   git clone https://github.com/ucli-tools/mdtodocu.git
   cd mdtodocu
   ```

2. Install the script system-wide using the Makefile:
   ```bash
   make build
   ```

   This will:
   - Copy the script to `/usr/local/bin/`.
   - Make the script executable.
   - If necessary, you will be prompted for your password to complete the installation.

3. To rebuild the installation (e.g., after updating the script):
   ```bash
   make rebuild
   ```

4. To uninstall the script:
   ```bash
   make delete
   ```

---

## Usage

### 1. Convert mdbook to Docusaurus

Run the script with the following command:
```bash
mdtodocu <userinput>
```

Replace `<userinput>` with the name of the mdbook directory you want to convert. The script will look for a `SUMMARY.md` file in `../books/<userinput>/SUMMARY.md` and process the markdown files accordingly.

### 2. Command-Line Arguments

- `<userinput>`: The name of the mdbook directory to convert. This is a required argument.

#### Example:
```bash
mdtodocu my-mdbook
```

This will:
1. Parse the `SUMMARY.md` file in `../books/my-mdbook/SUMMARY.md`.
2. Create a Docusaurus-compatible directory structure in `docu_books/my-mdbook`.
3. Add frontmatter to markdown files and generate `_category_.json` files.
4. Update image paths and copy images to the `./img/` directory.
5. Process `!!wiki.include` statements to include external markdown content.

---

## How It Works

1. **Parsing `SUMMARY.md`**: The script reads the `SUMMARY.md` file to extract the hierarchy of markdown files, including titles, indentation levels, and positions.
2. **Directory Structure**: It creates a directory structure in the output folder (`docu_books/<userinput>`) based on the hierarchy.
3. **Frontmatter**: Adds Docusaurus-compatible frontmatter (title and sidebar position) to each markdown file.
4. **Category Files**: Generates `_category_.json` files for directories to define sidebar categories in Docusaurus.
5. **Image Handling**:
   - Updates image paths in markdown files to use `./img/`.
   - Copies images to the appropriate `./img/` directory.
   - Logs missing images in `mdtodocu.log`.
6. **Include Statements**: Processes `!!wiki.include` statements to include external markdown content.
7. **File Copying**: Copies and updates markdown files while preserving their content.

---

## Notes

- Ensure the `SUMMARY.md` file follows the standard mdbook format.
- The script assumes markdown files are located in the current directory or its subdirectories.
- Binary files and non-markdown files are ignored.
- If a file or image is not found in the source directory, a warning is displayed, and the file is skipped.
- The script logs missing images in `mdtodocu.log`.

---

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/mik-tf/mdtodocu/issues) or submit a pull request.

---

## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

