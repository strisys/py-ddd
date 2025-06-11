resource "azurerm_resource_group" "rg_ai_research" {
  provider = azurerm.azure-research

  name     = var.resource_group_name
  location = var.location

  tags = {
    environment = var.environment
    project     = var.project_tag
  }
}

# module "other-onpremises-simulation" {
#   source = "./sql"
#   config = var.config
# }
