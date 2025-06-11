
terraform {
  required_version = ">= 1.10.3"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.27.0"
    }
    azapi = {
      source  = "Azure/azapi"
      version = ">=2.4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.6.2"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.2.3"
    }
    time = {
      source  = "hashicorp/time"
      version = ">= 0.13.0"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.2.3"
    }
  }
}

provider "azurerm" {
  features {}
  alias           = "azure-default"
  subscription_id = var.subscription_id
}

provider "azapi" {
  alias = "azure-default"
}

data "azurerm_client_config" "current" {
  provider = azurerm.azure-default
}
