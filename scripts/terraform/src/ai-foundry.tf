

resource "azapi_resource" "cognitive_services_account" {
  provider                  = azapi.azure-research
  type                      = "Microsoft.CognitiveServices/accounts@2025-04-01-preview"
  name                      = var.cognitive_account_name
  location                  = azurerm_resource_group.rg_ai_research.location
  parent_id                 = azurerm_resource_group.rg_ai_research.id
  schema_validation_enabled = false

  identity {
    type = "SystemAssigned"
  }

  body = {
    properties = {
      customSubDomainName    = var.cognitive_account_name
      allowProjectManagement = true
      networkAcls = {
        defaultAction = "Allow"
      }
    }
    sku = {
      name = "S0"
    }
    kind = "AIServices"
  }
}


resource "azapi_resource" "cognitive_services_project" {
  provider                  = azapi.azure-research
  type                      = "Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview"
  name                      = var.ai_project_name
  location                  = azurerm_resource_group.rg_ai_research.location
  parent_id                 = azapi_resource.cognitive_services_account.id
  schema_validation_enabled = false

  depends_on = [azapi_resource.cognitive_services_account]

  identity {
    type = "SystemAssigned"
  }

  body = {
    properties = {}
    kind       = "AIServices"
  }
}

# Use the following command to get the model parameters:
# az cognitiveservices account list-models --name "foundry-resource-20250523-2" --resource-group "rg-ai-research" --output table
# If still having problems, create in portal and then got to the ARM JSON for the resource of type 'Azure AI foundry'
resource "azapi_resource" "gpt_4_1_deployment" {
  provider                  = azapi.azure-research
  type                      = "Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview"
  name                      = "gpt-4.1-2"
  parent_id                 = azapi_resource.cognitive_services_account.id
  location                  = azurerm_resource_group.rg_ai_research.location
  schema_validation_enabled = false

  body = {
    properties = {
      model = {
        format  = "OpenAI"
        name    = "gpt-4.1"
        version = "2025-04-14"
      }
      versionUpgradeOption = "OnceNewDefaultVersionAvailable"
      raiPolicyName        = "Microsoft.DefaultV2"
    }
    sku = {
      name     = "GlobalStandard"
      capacity = 140
    }
  }
}


resource "azapi_resource" "gpt_ada_deployment" {
  provider                  = azapi.azure-research
  type                      = "Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview"
  name                      = "text-embedding-ada-002-2"
  parent_id                 = azapi_resource.cognitive_services_account.id
  location                  = azurerm_resource_group.rg_ai_research.location
  schema_validation_enabled = false

  body = {
    properties = {
      model = {
        format  = "OpenAI"
        name    = "text-embedding-ada-002"
        version = "2"
      }
      versionUpgradeOption = "NoAutoUpgrade"
      currentCapacity : 150,
      raiPolicyName = "Microsoft.DefaultV2"
    }
    sku = {
      name     = "GlobalStandard"
      capacity = 150
    }
  }

  depends_on = [azapi_resource.gpt_4_1_deployment]
}

# Read the Python script and generate a hash
data "local_file" "create_agents_script" {
  filename = "${path.module}/scripts/create_agents.py"
}

locals {
  scripts_hash = md5(join("", [
    for file in fileset("${path.module}/scripts", "**/*") :
    filemd5("${path.module}/scripts/${file}")
  ]))
  project_endpoint = "https://${var.cognitive_account_name}.services.ai.azure.com/api/projects/${var.ai_project_name}"
}

resource "null_resource" "create_agents" {
  triggers = {
    scripts_hash = local.scripts_hash
  }

  provisioner "local-exec" {
    command = <<EOT
      python3 scripts/create_agents.py \
        --account-name ${azapi_resource.cognitive_services_account.name} \
        --project-name ${azapi_resource.cognitive_services_project.name} \
        --default-deployment ${azapi_resource.gpt_4_1_deployment.name} \
        --default-embedding-deployment ${azapi_resource.gpt_ada_deployment.name} 
    EOT
  }

  depends_on = [azapi_resource.gpt_4_1_deployment, azapi_resource.gpt_ada_deployment, azapi_resource.cognitive_services_account]
}
