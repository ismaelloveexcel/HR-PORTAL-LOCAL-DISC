targetScope = 'resourceGroup'

@description('Primary Azure region for resources.')
param location string

@description('App Service plan name for the backend.')
param appServicePlanName string

@description('Backend App Service name.')
param backendAppName string

@description('Static Web App name for the frontend.')
param staticWebAppName string

@description('Static Web App region (must be a supported Static Web Apps location).')
param staticWebAppLocation string

@description('PostgreSQL flexible server name.')
param postgresServerName string

@description('PostgreSQL administrator username.')
param postgresAdminUsername string

@secure()
@description('PostgreSQL administrator password.')
param postgresAdminPassword string

@description('Database name to create.')
param postgresDbName string

@description('Application Insights resource name.')
param appInsightsName string

@secure()
@description('AUTH_SECRET_KEY for backend App Service.')
param authSecretKey string

@secure()
@description('DATABASE_URL connection string for backend App Service.')
param databaseUrl string

@description('Minimum credential length enforced by the backend.')
param minCredentialLength int

@description('Session timeout in minutes for authenticated sessions.')
param sessionTimeoutMinutes int

@description('Allow all Azure services (0.0.0.0) to reach the database in addition to the App Service outbound IPs.')
param allowAzureServices bool = true

@description('Optional list of IP addresses to allow (set allowAzureServices to false to restrict only to these).')
param allowedIpAddresses array = []

var linuxFxVersion = 'PYTHON|3.11'
var backendStartupCommand = 'sh -c "cd backend && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"'

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  kind: 'app'
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true
    perSiteScaling: false
  }
}

resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: backendAppName
  location: location
  kind: 'app,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: linuxFxVersion
      appCommandLine: backendStartupCommand
      alwaysOn: true
      ftpsState: 'Disabled'
      healthCheckPath: '/api/health/ping'
      minTlsVersion: '1.2'
      http20Enabled: true
    }
  }
}

resource webAppSettings 'Microsoft.Web/sites/config@2023-01-01' = {
  name: 'appsettings'
  parent: webApp
  properties: {
    APPLICATIONINSIGHTS_CONNECTION_STRING: appInsights.properties.ConnectionString
    APPLICATIONINSIGHTS_INSTRUMENTATIONKEY: appInsights.properties.InstrumentationKey
    AUTH_SECRET_KEY: authSecretKey
    DATABASE_URL: databaseUrl
    PASSWORD_MIN_LENGTH: string(minCredentialLength)
    SESSION_TIMEOUT_MINUTES: string(sessionTimeoutMinutes)
    WEBSITES_PORT: '8000'
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
    ENABLE_ORYX_BUILD: 'true'
    PYTHONUNBUFFERED: '1'
  }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01' = {
  name: postgresServerName
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    administratorLogin: postgresAdminUsername
    administratorLoginPassword: postgresAdminPassword
    storage: {
      storageSizeGB: 128
      autoGrow: 'Enabled'
    }
    network: {
      publicNetworkAccess: 'Enabled'
    }
    highAvailability: {
      mode: 'Disabled'
    }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
  }
}

resource postgresDb 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2023-06-01' = {
  name: postgresDbName
  parent: postgres
  properties: {}
}

resource postgresFirewall 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-06-01' = [for (ip, index) in allowedIpAddresses: {
  name: 'AllowAppService-${index}'
  parent: postgres
  properties: {
    startIpAddress: ip
    endIpAddress: ip
  }
}]

resource postgresFirewallAzure 'Microsoft.DBforPostgreSQL/flexibleServers/firewallRules@2023-06-01' = if (allowAzureServices) {
  name: 'AllowAzureServices'
  parent: postgres
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: staticWebAppName
  location: staticWebAppLocation
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    buildProperties: {
      appLocation: 'frontend'
      apiLocation: ''
      appArtifactLocation: 'dist'
    }
  }
}

output backendUrl string = 'https://${webApp.properties.defaultHostName}'
output backendHostname string = webApp.properties.defaultHostName
output frontendUrl string = 'https://${staticWebApp.properties.defaultHostname}'
output frontendHostname string = staticWebApp.properties.defaultHostname
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output postgresHost string = postgres.properties.fullyQualifiedDomainName
output postgresConnectionStringTemplate string = 'postgresql://${postgresAdminUsername}:<password>@${postgres.properties.fullyQualifiedDomainName}:5432/${postgresDbName}?sslmode=require'
