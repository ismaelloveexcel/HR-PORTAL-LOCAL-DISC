
// infra/bicep/appservice.bicep
// Creates an App Service Plan (Linux), a Web App, and a staging slot
param location string = resourceGroup().location
@description('App Service Plan (Linux) name')
param planName string = 'plan-employee-leave'
@description('Web App name')
param webAppName string = 'employee-leave-web'
@allowed([ 'F1' 'B1' 'B2' 'S1' 'S2' 'P1v3' ])
param sku string = 'B1'

resource plan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: planName
  location: location
  sku: {
    name: sku
    tier: sku == 'F1' ? 'Free' : (sku startsWith 'B' ? 'Basic' : (sku startsWith 'S' ? 'Standard' : 'PremiumV3'))
    size: sku
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource site 'Microsoft.Web/sites@2023-12-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts' // change to your runtime
      appSettings: [
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
      ]
    }
  }
}

resource slot 'Microsoft.Web/sites/slots@2023-12-01' = {
  name: '${webAppName}/staging'
  location: location
  properties: {
    serverFarmId: plan.id
  }
}

output webAppUrl string = 'https://${webAppName}.azurewebsites.net'
output stagingUrl string = 'https://${webAppName}-staging.azurewebsites.net'
