# Miniconda Setup on LinuxONE (s390x)

This document provides instructions for installing Miniconda on a LinuxONE mainframe architecture (`s390x`). 

## Prerequisites
- Access to a LinuxONE / IBM Z environment running Linux (e.g., Ubuntu, RHEL, SUSE).
- Command-line access and basic privileges.

## Installation Steps

1. **Download the Installer**
   Download the latest Miniconda installer specifically built for the `s390x` architecture from the official Anaconda repository.
   
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-s390x.sh -O miniconda.sh
   ```

2. **Verify the Installer (Optional but recommended)**
   Ensure the integrity of the downloaded file by comparing its SHA-256 checksum with the one provided on the Anaconda website.
   
   ```bash
   sha256sum miniconda.sh
   ```

3. **Run the Installer**
   Execute the installer script. You will need to accept the license agreement and choose an installation directory.
   
   ```bash
   bash miniconda.sh
   ```
   
   - Press `Enter` to review the license agreement.
   - Type `yes` to accept the license terms.
   - Press `Enter` to confirm the default installation location (usually `~/miniconda3`), or specify a custom path.
   - Type `yes` to allow the installer to initialize Miniconda by running `conda init`.

4. **Activate Miniconda**
   For the changes to take effect, either restart your terminal session or source your `.bashrc` (or equivalent shell profile).
   
   ```bash
   source ~/.bashrc
   ```

5. **Verify Installation**
   Check that `conda` is installed and accessible.
   
   ```bash
   conda --version
   ```

## Post-Installation Recommendations

- **Update Conda**: Keep your package manager up to date.
  ```bash
  conda update conda
  ```
- **Create a Virtual Environment**: It is best practice to create an isolated environment for your project.
  ```bash
  conda create -n syn-env python=3.10
  conda activate syn-env
  ```
