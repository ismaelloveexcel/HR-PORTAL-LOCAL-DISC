# Azure Deployment Reference Guide

> 📖 **Comprehensive reference for deploying applications from GitHub to Microsoft Azure**

This guide provides a complete overview of all Microsoft Azure repositories and GitHub Actions available for deploying applications from GitHub to Azure. It covers authentication, deployment actions, workflow samples, and best practices.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Azure GitHub Actions](#key-azure-github-actions)
  - [Authentication](#1-authentication)
  - [Web Application Deployment](#2-web-application-deployment)
  - [Container Deployment](#3-container-deployment)
  - [Serverless Deployment](#4-serverless-deployment)
  - [Infrastructure as Code](#5-infrastructure-as-code)
  - [Database Deployment](#6-database-deployment)
- [Workflow Samples Repository](#workflow-samples-repository)
- [Complete Deployment Examples](#complete-deployment-examples)
- [Recommended Deployment Patterns](#recommended-deployment-patterns)
- [Security Best Practices](#security-best-practices)
- [Quick Reference Table](#quick-reference-table)

---

## Overview

Microsoft Azure provides a comprehensive set of GitHub Actions to enable CI/CD workflows for deploying applications to Azure services. These actions are maintained in the [Azure GitHub organization](https://github.com/Azure) and are designed to work seamlessly with GitHub Actions workflows.

**Key Repository:** [Azure/actions-workflow-samples](https://github.com/Azure/actions-workflow-samples) - Contains starter templates for all common deployment scenarios.

---

## HR Portal Repository Structure for Azure Deployment

Azure App Service uses the **Oryx build system** which expects a specific file structure at the repository root. This HR Portal repository includes the following root-level files specifically for Azure deployment:

### Required Root-Level Files

```
AZURE-DEPLOYMENT-HR-PORTAL/
├── requirements.txt          # ✅ Azure Oryx expects this at root
├── app/                      # ✅ Azure expects app entry point here
│   ├── __init__.py
│   └── main.py               # Re-exports FastAPI app from backend
├── backend/                  # Actual application code
│   ├── app/
│   │   └── main.py           # Real FastAPI application
│   ├── requirements.txt      # Backend-specific dependencies
│   └── ...
└── frontend/
    └── ...
```

### Why This Structure Exists

1. **`/requirements.txt`** (root level)
   - Azure Oryx automatically detects Python projects by looking for `requirements.txt` at the repository root
   - This is a copy of `backend/requirements.txt` to satisfy Oryx build requirements
   - Contains all dependencies: `fastapi`, `uvicorn[standard]`, `gunicorn`, `sqlalchemy`, etc.

2. **`/app/main.py`** (root level)
   - Azure's default startup command looks for `app.main:app`
   - This entry point re-exports the FastAPI app from `backend/app/main.py`
   - Enables simpler startup command without path navigation:
   
   ```bash
   # Simple startup command (uses root app/main.py)
   gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --workers=2
   ```

3. **`/backend/app/main.py`** (actual application)
   - Contains the real FastAPI application code
   - All business logic, routers, and database connections
   - This is where development work happens

### How the Re-Export Works

The root-level `app/main.py` adds the `backend/` directory to Python's path and imports the app:

```python
import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import and re-export the FastAPI app
from app.main import app

__all__ = ["app"]
```

### Critical Startup Settings

For Azure App Service deployments, these settings are **required**:

| Setting | Value | Purpose |
|---------|-------|---------|
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Triggers Oryx build to install dependencies |
| `PYTHONUNBUFFERED` | `1` | Ensures proper logging and prevents buffering issues |
| Startup Command | `gunicorn app.main:app -k uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000 --workers=2` | Explicit binding prevents 502 errors |

### Deployment Methods

This repository supports two deployment approaches:

1. **GitHub Actions (deploy.yml)** - Uses zip deployment with `backend/azure_startup.sh`
2. **Manual CLI (deploy_to_azure.sh)** - Uses GitHub source deployment with root-level `app/main.py`

Both methods work correctly with this dual-location structure.

---

## Key Azure GitHub Actions

### 1. Authentication

#### Azure Login Action

**Repository:** [Azure/login](https://github.com/Azure/login)

**Description:** The foundational action for authenticating with Azure. All other Azure actions depend on this for authentication.

**Authentication Methods:**
1. **OpenID Connect (OIDC)** - Recommended for security
2. **Service Principal with Secret** - Traditional approach
3. **System-assigned Managed Identity** - For self-hosted runners on Azure VMs
4. **User-assigned Managed Identity** - For specific identity requirements

**Example - OIDC Authentication (Recommended):**
```yaml
name: Azure Login with OIDC

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Azure Login
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

**Example - Service Principal Secret:**
```yaml
- name: Azure Login
  uses: azure/login@v2
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}
```

**Required Secrets:**
- `AZURE_CLIENT_ID` - Service principal or managed identity client ID
- `AZURE_TENANT_ID` - Azure AD tenant ID
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_CREDENTIALS` (alternative) - JSON object with all credentials

---

### 2. Web Application Deployment

#### Azure Web Apps Deploy

**Repository:** [Azure/webapps-deploy](https://github.com/Azure/webapps-deploy)

**Description:** Deploy to Azure App Service (Web Apps) for Windows or Linux. Supports deploying folders, JAR, WAR, and ZIP files.

**Supported Runtimes:**
- .NET / ASP.NET Core
- Node.js
- Python
- Java (JAR/WAR)
- PHP
- Go
- Docker containers

**Example - Web App Deployment:**
```yaml
- name: Deploy to Azure Web App
  uses: azure/webapps-deploy@v3
  with:
    app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
    publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
    package: './dist'
```

**Example - With Slot Deployment:**
```yaml
- name: Deploy to Staging Slot
  uses: azure/webapps-deploy@v3
  with:
    app-name: my-webapp
    slot-name: staging
    publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
    package: './dist'
```

#### Azure Static Web Apps Deploy

**Repository:** [Azure/static-web-apps-deploy](https://github.com/Azure/static-web-apps-deploy)

**Description:** Deploy static websites and single-page applications (SPAs) to Azure Static Web Apps. Automatically builds the application using [Oryx](https://github.com/microsoft/Oryx).

**Features:**
- Automatic build detection
- Preview environments for pull requests
- Integrated Azure Functions API
- Global CDN distribution

**Example - Static Web App Deployment:**
```yaml
- name: Build and Deploy Static Web App
  uses: Azure/static-web-apps-deploy@v1
  with:
    azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
    repo_token: ${{ secrets.GITHUB_TOKEN }}
    action: "upload"
    app_location: "frontend"
    output_location: "frontend/dist"
    api_location: "backend/app"
```

---

### 3. Container Deployment

#### Docker Login

**Repository:** [Azure/docker-login](https://github.com/Azure/docker-login)

**Description:** Log in to Azure Container Registry (ACR) or any private container registry.

**Example:**
```yaml
- name: Login to ACR
  uses: azure/docker-login@v1
  with:
    login-server: myregistry.azurecr.io
    username: ${{ secrets.ACR_USERNAME }}
    password: ${{ secrets.ACR_PASSWORD }}
```

#### Azure Container Apps Deploy

**Repository:** [Azure/container-apps-deploy-action](https://github.com/Azure/container-apps-deploy-action)

**Description:** Build and deploy containerized applications to Azure Container Apps.

**Example:**
```yaml
- name: Deploy to Container Apps
  uses: azure/container-apps-deploy-action@v1
  with:
    appSourcePath: ${{ github.workspace }}
    acrName: myregistry
    containerAppName: my-container-app
    resourceGroup: my-resource-group
```

#### Azure Container Instances Deploy

**Repository:** [Azure/aci-deploy](https://github.com/Azure/aci-deploy)

**Description:** Deploy containers to Azure Container Instances for quick, serverless container execution.

**Example:**
```yaml
- name: Deploy to ACI
  uses: azure/aci-deploy@v1
  with:
    resource-group: my-resource-group
    dns-name-label: my-container
    image: myregistry.azurecr.io/myimage:latest
    name: my-container-instance
    location: eastus
```

#### Kubernetes Deploy

**Repository:** [Azure/k8s-deploy](https://github.com/Azure/k8s-deploy)

**Description:** Deploy to any Kubernetes cluster, including Azure Kubernetes Service (AKS).

**Related Actions:**
- [Azure/k8s-set-context](https://github.com/Azure/k8s-set-context) - Set Kubernetes context
- [Azure/aks-set-context](https://github.com/Azure/aks-set-context) - Set AKS-specific context

**Example:**
```yaml
- name: Set K8s Context
  uses: azure/k8s-set-context@v4
  with:
    kubeconfig: ${{ secrets.KUBE_CONFIG }}

- name: Deploy to Kubernetes
  uses: azure/k8s-deploy@v5
  with:
    manifests: |
      manifests/deployment.yaml
      manifests/service.yaml
    images: |
      myregistry.azurecr.io/myapp:${{ github.sha }}
```

#### Web Apps Container Deploy

**Repository:** [Azure/webapps-container-deploy](https://github.com/Azure/webapps-container-deploy) (archived)

**Description:** Deploy containerized apps to Azure Web App for Containers. Now integrated into `azure/webapps-deploy`.

---

### 4. Serverless Deployment

#### Azure Functions Action

**Repository:** [Azure/functions-action](https://github.com/Azure/functions-action)

**Description:** Deploy serverless functions to Azure Functions.

**Example:**
```yaml
- name: Deploy Azure Function
  uses: azure/functions-action@v1
  with:
    app-name: my-function-app
    package: './function-app'
    publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
```

#### Azure Functions Container Action

**Repository:** [Azure/functions-container-action](https://github.com/Azure/functions-container-action)

**Description:** Deploy containerized Azure Functions.

**Example:**
```yaml
- name: Deploy Function Container
  uses: azure/functions-container-action@v1
  with:
    app-name: my-function-app
    image: myregistry.azurecr.io/myfunc:latest
```

---

### 5. Infrastructure as Code

#### Bicep Deploy

**Repository:** [Azure/bicep-deploy](https://github.com/Azure/bicep-deploy)

**Description:** Deploy Azure infrastructure using Bicep or ARM templates.

**Example:**
```yaml
- name: Deploy Bicep
  uses: azure/bicep-deploy@v1
  with:
    scope: resourcegroup
    resourceGroupName: my-resource-group
    template: ./main.bicep
    parameters: ./parameters.json
```

#### Deployment What-If Action

**Repository:** [Azure/deployment-what-if-action](https://github.com/Azure/deployment-what-if-action)

**Description:** Preview Azure infrastructure changes before deployment.

**Example:**
```yaml
- name: What-If Analysis
  uses: azure/deployment-what-if-action@v1
  with:
    scope: resourcegroup
    resourceGroupName: my-resource-group
    template: ./main.bicep
```

---

### 6. Database Deployment

#### SQL Action

**Repository:** [Azure/sql-action](https://github.com/Azure/sql-action)

**Description:** Deploy SQL scripts or DACPAC packages to Azure SQL Database or SQL Server.

**Example:**
```yaml
- name: Deploy SQL Database
  uses: azure/sql-action@v2
  with:
    connection-string: ${{ secrets.AZURE_SQL_CONNECTION_STRING }}
    path: './database/deploy.sql'
```

---

## Workflow Samples Repository

**Repository:** [Azure/actions-workflow-samples](https://github.com/Azure/actions-workflow-samples)

This repository contains ready-to-use workflow templates organized by Azure service:

| Folder | Description |
|--------|-------------|
| `/AppService` | Web Apps deployment (Node.js, Python, Java, .NET, PHP, Go, Docker) |
| `/FunctionApp` | Azure Functions deployment |
| `/Kubernetes` | AKS and Kubernetes deployment |
| `/Database` | Azure SQL and MySQL deployment |
| `/ARM` | ARM template deployment |
| `/Terraform` | Terraform infrastructure deployment |
| `/MachineLearning` | Azure Machine Learning workflows |
| `/AzureCLI` | Azure CLI script execution |
| `/AzurePolicy` | Azure Policy compliance |
| `/End-to-End` | Complete application architectures |

### Sample Workflow Templates

#### Python Web App
**File:** `AppService/python-webapp-on-azure.yml`

```yaml
name: Deploy Python Web App

on: [push]

env:
  AZURE_WEBAPP_NAME: my-app
  PYTHON_VERSION: '3.11'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          python -m venv antenv
          source antenv/bin/activate
          pip install -r requirements.txt

      - uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          package: '.'
```

#### Node.js Web App
**File:** `AppService/node.js-webapp-on-azure.yml`

```yaml
name: Deploy Node.js Web App

on: [push]

env:
  AZURE_WEBAPP_NAME: my-node-app
  NODE_VERSION: '20'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}

      - name: Install and Build
        run: |
          npm install
          npm run build --if-present

      - uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
          package: '.'
```

#### Docker Container Web App
**File:** `AppService/docker-webapp-container-on-azure.yml`

```yaml
name: Deploy Docker Container

on: [push]

env:
  AZURE_WEBAPP_NAME: my-container-app
  ACR_NAME: myregistry

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: azure/docker-login@v1
        with:
          login-server: ${{ env.ACR_NAME }}.azurecr.io
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and Push Image
        run: |
          docker build . -t ${{ env.ACR_NAME }}.azurecr.io/myapp:${{ github.sha }}
          docker push ${{ env.ACR_NAME }}.azurecr.io/myapp:${{ github.sha }}

      - uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          images: ${{ env.ACR_NAME }}.azurecr.io/myapp:${{ github.sha }}
```

---

## Complete Deployment Examples

### Full Stack Application (FastAPI + React)

This example shows how to deploy a full-stack application with a FastAPI backend and React frontend to Azure.

```yaml
name: Deploy Full Stack App to Azure

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

env:
  AZURE_WEBAPP_NAME: hr-portal-backend
  AZURE_STATIC_WEB_APP_NAME: hr-portal-frontend

jobs:
  deploy-backend:
    name: Deploy Backend to Azure App Service
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install uv
          cd backend && uv sync

      - name: Azure Login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          package: backend

  deploy-frontend:
    name: Deploy Frontend to Static Web Apps
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build and Deploy Static Web App
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: upload
          app_location: frontend
          output_location: dist
```

---

## Recommended Deployment Patterns

### Pattern 1: App Service with Publish Profile (Simple)

**Best for:** Simple web apps, quick setup

```yaml
- uses: azure/webapps-deploy@v3
  with:
    app-name: my-app
    publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
    package: './dist'
```

### Pattern 2: OIDC Authentication (Secure)

**Best for:** Production deployments, enterprise security

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    steps:
      - uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - uses: azure/webapps-deploy@v3
        with:
          app-name: my-app
```

### Pattern 3: Container Deployment

**Best for:** Consistent environments, microservices

```yaml
jobs:
  deploy:
    steps:
      - uses: azure/docker-login@v1
        with:
          login-server: myacr.azurecr.io
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - run: |
          docker build -t myacr.azurecr.io/app:${{ github.sha }} .
          docker push myacr.azurecr.io/app:${{ github.sha }}

      - uses: azure/webapps-deploy@v3
        with:
          app-name: my-container-app
          images: myacr.azurecr.io/app:${{ github.sha }}
```

### Pattern 4: Slot Deployment with Swap

**Best for:** Zero-downtime deployments

```yaml
jobs:
  deploy:
    steps:
      - uses: azure/webapps-deploy@v3
        with:
          app-name: my-app
          slot-name: staging
          package: './dist'

      - name: Swap Slots
        uses: azure/cli@v2
        with:
          inlineScript: |
            az webapp deployment slot swap \
              --name my-app \
              --resource-group my-rg \
              --slot staging
```

---

## Security Best Practices

### 1. Use OIDC Authentication

OIDC (OpenID Connect) is the recommended authentication method as it eliminates the need to store long-lived credentials:

```yaml
permissions:
  id-token: write
  contents: read
```

### 2. Limit Secret Scope

Store secrets at the repository level and use environment protection rules:

```yaml
jobs:
  deploy:
    environment: production
    # Requires approval before deployment
```

### 3. Enable Run from Package

For Azure App Service, enable "Run from Package" for faster, more secure deployments:

```yaml
- name: Configure App Settings
  uses: azure/appservice-settings@v1
  with:
    app-name: my-app
    app-settings-json: |
      [
        { "name": "WEBSITE_RUN_FROM_PACKAGE", "value": "1" }
      ]
```

### 4. Use Managed Identities

For self-hosted runners on Azure VMs, use managed identities instead of service principals.

### 5. Implement Least Privilege

When creating service principals, scope permissions to specific resources:

```bash
az ad sp create-for-rbac --name "github-deploy" \
  --role contributor \
  --scopes /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Web/sites/{app}
```

---

## Quick Reference Table

| Use Case | Action | Repository |
|----------|--------|------------|
| **Authentication** | `azure/login@v2` | [Azure/login](https://github.com/Azure/login) |
| **Web App Deployment** | `azure/webapps-deploy@v3` | [Azure/webapps-deploy](https://github.com/Azure/webapps-deploy) |
| **Static Web Apps** | `Azure/static-web-apps-deploy@v1` | [Azure/static-web-apps-deploy](https://github.com/Azure/static-web-apps-deploy) |
| **Azure Functions** | `azure/functions-action@v1` | [Azure/functions-action](https://github.com/Azure/functions-action) |
| **Container Apps** | `azure/container-apps-deploy-action@v1` | [Azure/container-apps-deploy-action](https://github.com/Azure/container-apps-deploy-action) |
| **Container Instances** | `azure/aci-deploy@v1` | [Azure/aci-deploy](https://github.com/Azure/aci-deploy) |
| **Kubernetes/AKS** | `azure/k8s-deploy@v5` | [Azure/k8s-deploy](https://github.com/Azure/k8s-deploy) |
| **Docker Registry** | `azure/docker-login@v1` | [Azure/docker-login](https://github.com/Azure/docker-login) |
| **SQL Database** | `azure/sql-action@v2` | [Azure/sql-action](https://github.com/Azure/sql-action) |
| **Bicep/ARM** | `azure/bicep-deploy@v1` | [Azure/bicep-deploy](https://github.com/Azure/bicep-deploy) |
| **Azure CLI** | `azure/cli@v2` | [Azure/cli](https://github.com/Azure/cli) |
| **Workflow Samples** | Templates | [Azure/actions-workflow-samples](https://github.com/Azure/actions-workflow-samples) |

---

## Additional Resources

- 📖 [GitHub Actions for Azure Documentation](https://github.com/Azure/actions)
- 📖 [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- 📖 [GitHub Actions Workflow Syntax](https://docs.github.com/actions/reference/workflow-syntax-for-github-actions)
- 📖 [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)

---

## Related Repository Documentation

- [GitHub Deployment Options](GITHUB_DEPLOYMENT_OPTIONS.md) - Local, Codespaces, and self-hosted options
- [VSCode Deployment Guide](VSCODE_DEPLOYMENT_GUIDE.md) - Development and deployment in VSCode
- [Contributing Guide](../CONTRIBUTING.md) - Development setup and best practices

---

<p align="center">
  <strong>Secure Renewals HR Portal</strong><br>
  Built with ❤️ for HR teams
</p>
