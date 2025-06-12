
resource "azurerm_service_plan" "development" {
  provider            = azurerm.azure-default
  resource_group_name = azurerm_resource_group.rg_ai_research.name
  location            = azurerm_resource_group.rg_ai_research.location
  name                = "asp-development-01"

  os_type  = "Linux"
  sku_name = "P1v3"

  per_site_scaling_enabled        = false
  zone_balancing_enabled          = false
  premium_plan_auto_scale_enabled = true
  worker_count                    = 1
  maximum_elastic_worker_count    = 1
}

resource "azurerm_user_assigned_identity" "acr_pull" {
  provider            = azurerm.azure-default
  resource_group_name = azurerm_resource_group.rg_ai_research.name
  location            = azurerm_service_plan.development.location
  name                = "acr_pull"
}

data "azurerm_container_registry" "existing" {
  provider            = azurerm.azure-default
  name                = "strisys"
  resource_group_name = "rg-shared"
}

resource "azurerm_role_assignment" "acr_pull" {
  provider             = azurerm.azure-default
  principal_id         = azurerm_user_assigned_identity.acr_pull.principal_id
  scope                = data.azurerm_container_registry.existing.id
  role_definition_name = "AcrPull"
}

resource "azurerm_linux_web_app" "web_app" {
  provider            = azurerm.azure-default
  resource_group_name = azurerm_resource_group.rg_ai_research.name
  location            = azurerm_service_plan.development.location
  service_plan_id     = azurerm_service_plan.development.id
  name                = "ai-research-app"

  identity {
    type = "UserAssigned"
    identity_ids = [
      azurerm_user_assigned_identity.acr_pull.id
    ]
  }

  site_config {
    always_on                                     = true
    container_registry_use_managed_identity       = true
    container_registry_managed_identity_client_id = azurerm_user_assigned_identity.acr_pull.client_id
    http2_enabled                                 = true
    minimum_tls_version                           = "1.2"
    scm_minimum_tls_version                       = "1.2"
    ftps_state                                    = "Disabled"
    use_32_bit_worker                             = true
    websockets_enabled                            = false
    vnet_route_all_enabled                        = false

    application_stack {
      docker_image_name   = "airesearch:latest"
      docker_registry_url = "https://${data.azurerm_container_registry.existing.login_server}"
    }

    ip_restriction {
      ip_address = "0.0.0.0/0"
      name       = "Allow all"
      priority   = 2147483647
      action     = "Allow"
    }

    scm_ip_restriction {
      ip_address = "0.0.0.0/0"
      name       = "Allow all"
      priority   = 2147483647
      action     = "Allow"
    }
  }

  # Configure logging settings to match Azure portal
  logs {
    detailed_error_messages = false
    failed_request_tracing  = false

    application_logs {
      file_system_level = "Information"
    }

    http_logs {
      file_system {
        retention_in_days = 5
        retention_in_mb   = 35
      }
    }
  }

  app_settings = {
    DOCKER_ENABLE_CI     = "true"
    AZURE_CLIENT_ID      = var.azure_client_id
    AZURE_CLIENT_SECRET  = var.azure_client_secret
    AZURE_TENANT_ID      = var.azure_tenant_id
    AZURE_REDIRECT_URI   = "https://ai-research-app.azurewebsites.net/signin"
    AZURE_KEY_VAULT_NAME = var.azure_key_vault_name
    IS_CLOUD_ENVIRONMENT = true
    MSAL_DEBUGGING       = false
    IS_AUTH_ENABLED      = true
  }

  https_only                    = true
  client_affinity_enabled       = false
  client_certificate_enabled    = false
  client_certificate_mode       = "Required"
  public_network_access_enabled = true

  tags = {
    # Add your tags here
  }
}