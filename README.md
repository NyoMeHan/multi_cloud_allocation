# 📦 Project Setup Guide

> A step-by-step guide to setting up the project solution on **Windows OS**.

---

## 📋 Table of Contents

- [Dependencies](#-dependencies)
- [Installation Guide](#-installation-guide)
  - [1. Docker Desktop](#1-docker-desktop)
  - [2. Kubernetes](#2-kubernetes)
  - [3. Kubectl](#3-kubectl)
  - [4. Minikube](#4-minikube)
  - [5. Kubernetes Metrics](#5-kubernetes-metrics)
  - [6. Python](#6-python)
  - [7. PyCharm Community Edition](#7-pycharm-community-edition)
- [Running the Project](#-running-the-project)

---

## 🧰 Dependencies

- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)
- Kubernetes
- Kubectl
- Minikube
- Kubernetes Metrics
- Python
- PyCharm Community Edition

---

## 🛠 Installation Guide

### 1. Docker Desktop

1. Go to [https://docs.docker.com/desktop/setup/install/windows-install/](https://docs.docker.com/desktop/setup/install/windows-install/)
2. Download **Docker Desktop for Windows**
3. Run `Docker Desktop Installer.exe`
4. Open Docker Desktop

---

### 2. Kubernetes

1. Go to **Settings** in Docker Desktop and enable **"Kubernetes"**
2. Under **Cluster settings**, select **"kind"** to create a cluster with one or more nodes
3. Ensure the configuration matches the required settings (refer to figure in documentation)
4. Verify installation using PowerShell:

```powershell
kubectl version
```

**Expected Output:**
```
Client Version: v1.32.2
Kustomize Version: v5.5.0
Server Version: v1.32.0
```

---

### 3. Kubectl

- Check if `kubectl` is already included in your Docker Desktop installation
- If not, install it via PowerShell:

```powershell
curl.exe -LO https://dl.k8s.io/release/v1.33.0/bin/windows/amd64/kubectl.exe
```

- Move `kubectl.exe` to the Docker Desktop installation path:
  ```
  C:\Program Files\Docker\Docker\resources\bin
  ```

---

### 4. Minikube

1. Download Minikube from [https://minikube.sigs.k8s.io/docs/start/](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fwindows%2Fx86-64%2Fstable%2F.exe+download)
   - Select **Windows** → **.exe installer** → click the latest release link
2. Run `minikube-installer.exe`
3. Add the Minikube application path to **Environment Variables**
4. Verify installation:

```powershell
minikube version
```

**Expected Output:**
```
minikube version: v1.35.0
```

#### 🔧 Create AWS & GCP Simulated Clusters

```powershell
# Start default minikube
minikube start

# Set contexts
kubectl config set-context aws-cluster --cluster=aws-cluster --user=aws-cluster
kubectl config set-context gcp-cluster --cluster=gcp-cluster --user=gcp-cluster

# Start both clusters
minikube start --profile aws-cluster
minikube start --profile gcp-cluster
```

#### ✅ Verify Clusters

```powershell
# List minikube profiles
minikube profile list

# Check Kubernetes contexts
kubectl config get-contexts
```

**Expected Output:**
```
CURRENT   NAME             CLUSTER          AUTHINFO         NAMESPACE
*         aws-cluster      aws-cluster      aws-cluster      default
          docker-desktop   docker-desktop   docker-desktop
          gcp-cluster      gcp-cluster      gcp-cluster      default
          minikube         minikube         minikube         default
```

> `*` indicates the currently active cluster.

---

### 5. Kubernetes Metrics

> ⚠️ Must be installed on **both** `aws-cluster` and `gcp-cluster`.

#### Switch Between Clusters

```powershell
# Switch to aws-cluster
kubectl config use-context aws-cluster
# Output: Switched to context "aws-cluster"

# Switch to gcp-cluster
kubectl config use-context gcp-cluster
# Output: Switched to context "gcp-cluster"
```

#### Install Metrics Server

```powershell
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

#### Patch for Local Clusters

```powershell
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

#### Verify Installation

```powershell
kubectl get pods -n kube-system | Select-String "metrics-server"
```

**Expected Output:**
```
metrics-server-744bb9fbcf-wxqdt   1/1   Running   3 (40h ago)   45h
```

```powershell
kubectl top nodes
```

**Expected Output:**
```
NAME          CPU(cores)   CPU(%)   MEMORY(bytes)   MEMORY(%)
aws-cluster   182m         0%       1721Mi          10%
```

---

### 6. Python

1. Go to [https://www.python.org/downloads/release/python-3126/](https://www.python.org/downloads/release/python-3126/)
2. Download and run the Python installer
3. Add Python to **Environment Variables**

---

### 7. PyCharm Community Edition

1. Go to [https://www.jetbrains.com/pycharm/download/?section=windows](https://www.jetbrains.com/pycharm/download/?section=windows)
2. Download the **Community** version
3. Run the installer

---

## ▶️ Running the Project

1. Place the project solution folder on your local drive
2. Open **PyCharm**
3. Go to **File → Open** and select the project folder
4. Set the Python interpreter:
   - **File → Settings → Project Name → Python Interpreter**
   - Select the correct Python version
5. If import errors appear (red underlines), click the **red bulb** in the editor and install the missing libraries
   > These are built-in Python libraries that may need to be resolved by the IDE automatically.
