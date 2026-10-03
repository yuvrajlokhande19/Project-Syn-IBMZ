# Miniconda Setup on IBM LinuxONE (s390x)

This guide provides step-by-step instructions for installing Miniconda on IBM LinuxONE (s390x architecture), which provides a stable Python environment for running the Mainframe Core services.

## 1. Prerequisites

Ensure your system is up to date and has basic utilities like `wget` and `tar` installed.

```bash
sudo apt-get update
sudo apt-get install -y wget bzip2 ca-certificates libglib2.0-0 libxext6 libsm6 libxrender1
```

*(Note: Package names above are for Debian/Ubuntu based distributions. For RHEL/SLES use `yum` or `zypper` accordingly).*

## 2. Download the Installer

Download the official Miniconda installer for the `s390x` architecture from the Anaconda repository.

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-s390x.sh -O miniconda.sh
```

## 3. Verify the Installer (Optional but Recommended)

It's a good practice to verify the SHA-256 hash of the downloaded installer.

```bash
sha256sum miniconda.sh
```
Compare the output with the hash provided on the [Miniconda download page](https://docs.conda.io/en/latest/miniconda.html).

## 4. Install Miniconda

Run the installer script:

```bash
bash miniconda.sh -b -p $HOME/miniconda3
```
- `-b` runs the installation in batch mode (no manual intervention).
- `-p` specifies the installation directory.

## 5. Initialize Conda

Initialize conda for your shell (e.g., bash or zsh):

```bash
$HOME/miniconda3/bin/conda init bash
```
*(If you are using zsh, replace `bash` with `zsh`).*

After initialization, reload your shell or source your `.bashrc`:

```bash
source ~/.bashrc
```

## 6. Verify Installation

Check the installed conda and python versions:

```bash
conda --version
python --version
```

## 7. Creating an Environment for Mainframe Core

Create and activate a new environment for the Project Syn backend:

```bash
conda create -n syn-backend python=3.10 -y
conda activate syn-backend
```

You can now proceed to install the required Python packages (e.g., `fastapi`, `uvicorn`, `httpx`) using `pip` or `conda` within this environment.
