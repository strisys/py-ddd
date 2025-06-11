# resource "azurerm_storage_account" "storage_account" {
#   provider                        = azurerm.azure-research
#   name                            = "aifoundrystorage${local.current_date_est}"
#   resource_group_name             = azurerm_resource_group.rg_ai_research.name
#   location                        = azurerm_resource_group.rg_ai_research.location
#   account_tier                    = "Standard"
#   account_replication_type        = "LRS"
#   allow_nested_items_to_be_public = false
# }

# resource "azurerm_storage_container" "data" {
#   provider              = azurerm.azure-research
#   storage_account_id    = azurerm_storage_account.storage_account.id
#   name                  = "data"
#   container_access_type = "private"
# }
