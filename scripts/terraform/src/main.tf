resource "azurerm_resource_group" "rg_ai_research" {
  provider = azurerm.azure-default

  name     = var.resource_group_name
  location = var.location

  tags = {
    environment = var.environment
    project     = var.project_tag
  }
}