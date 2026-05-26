# Deploying a Windows Template with Packer

This guide explains how to build and deploy a Windows template using Packer.

## Prerequisites

Before starting the build, add the following ISOs:

- Windows Server
- VirtIO Drivers
- Cloudbase-Init

### Download Cloudbase-Init

```bash
wget https://cloudbase.it/downloads/CloudbaseInitSetup_Stable_x64.msi
```

### Create an ISO from the installer

```bash
mkisofs -J -r -o CloudbaseInitSetup_Stable_x64.iso CloudbaseInitSetup_Stable_x64.msi
```

## Configure Variables

Create a `variables.auto.pkrvars.hcl` file.

Copy the values from `variables.pkrvars.hcl` into the newly created file, then update them to match your environment, such as the Proxmox IP address and any other required settings.

## Build the Template

Go to the template directory:

```bash
cd packer/windows-server-2022
```

Run the build:

```bash
packer build .
```

## Useful Build Options

### Keep the VM when an error occurs

Use the following command if you do not want the VM to be deleted when the build fails:

```bash
packer build -on-error=ask .
```

### Enable detailed logs

Use the following command to get more detailed logs during the build:

```bash
PACKER_LOG=1 PACKER_LOG_PATH="packer-debug.log" packer build . 2>&1 | tee /dev/stderr
```

Then read the log file:

```bash
cat packer-debug.log
```

## Build Steps Explained
