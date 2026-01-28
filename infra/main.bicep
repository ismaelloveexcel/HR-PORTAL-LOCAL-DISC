targetScope = 'subscription'

@description('Primary Azure region for the resource group and compute resources.')
param location string = 'uaenorth'

@description('Resource group name to create or reuse.')
param resourceGroupName string = 'rg-hr-portal-new'

@description('App Service plan name for the backend.')
param appServicePlanName string = 'hrportal-plan-new'

@description('Backend App Service name.')
param backendAppName string = 'hrportal-backend-new'

@description('Static Web App name for the frontend.')
param staticWebAppName string = 'hrportal-frontend-new'

@description('Static Web App region (must be a supported Static Web Apps location).')
param staticWebAppLocation string = 'eastus2'

@description('PostgreSQL flexible server name.')
param postgresServerName string = 'hrportal-db-new'

@description('PostgreSQL administrator username.')
param postgresAdminUsername string = 'hradmin'

@secure()
@description('PostgreSQL administrator password.')
param postgresAdminPassword string

@description('Database name to create.')
param postgresDbName string = 'postgres'

@description('Application Insights resource name.')
param appInsightsName string = 'hrportal-backend-new-ai'

@secure()
@description('AUTH_SECRET_KEY for backend App Service.')
param authSecretKey string

@secure()
@description('DATABASE_URL connection string for backend App Service.')
param databaseUrl string

@description('Minimum credential length enforced by the backend.')
param minCredentialLength int = 8

@description('Session timeout in minutes for authenticated sessions.')
param sessionTimeoutMinutes int = 480

@description('Allow all Azure services (0.0.0.0) to reach the database in addition to any explicit IP rules.')
param allowAzureServices bool = true

@description('Optional list of IP addresses to allow to the database.')
param allowedIpAddresses array = []

resource rg 'Microsoft.Resources/resourceGroups@2022-09-01' = {
  name: resourceGroupName
  location: location
}

module stack './resources.bicep' = {
  name: 'hrportal-stack'
  scope: rg
  params: {
    location: location
    appServicePlanName: appServicePlanName
    backendAppName: backendAppName
    staticWebAppName: staticWebAppName
    staticWebAppLocation: staticWebAppLocation
    postgresServerName: postgresServerName
    postgresAdminUsername: postgresAdminUsername
    postgresAdminPassword: postgresAdminPassword
    postgresDbName: postgresDbName
    appInsightsName: appInsightsName
    authSecretKey: authSecretKey
    databaseUrl: databaseUrl
    minCredentialLength: minCredentialLength
    sessionTimeoutMinutes: sessionTimeoutMinutes
    allowAzureServices: allowAzureServices
    allowedIpAddresses: allowedIpAddresses
  }
}

output resourceGroupNameOut string = resourceGroupName
output backendUrl string = stack.outputs.backendUrl
output backendHostname string = stack.outputs.backendHostname
output frontendUrl string = stack.outputs.frontendUrl
output frontendHostname string = stack.outputs.frontendHostname
output appInsightsConnectionString string = stack.outputs.appInsightsConnectionString
output postgresHost string = stack.outputs.postgresHost
output postgresConnectionStringTemplate string = stack.outputs.postgresConnectionStringTemplate
