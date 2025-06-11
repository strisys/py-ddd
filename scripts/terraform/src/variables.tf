# Variables
variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-ai-research"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "East US 2"
}

variable "cognitive_account_name" {
  description = "Name of the Azure AI Services cognitive account"
  type        = string
  default     = "foundry-resource-20250522"
}

variable "ai_project_name" {
  description = "Name of the AI Foundry project"
  type        = string
  default     = "project-20250522"
}

variable "environment" {
  description = "Environment tag"
  type        = string
  default     = "research"
}

variable "project_tag" {
  description = "Project tag"
  type        = string
  default     = "ai-foundry"
}

locals {
  # Example: EST (UTC-5)
  current_date_est = formatdate("YYYYMMDD", timeadd(timestamp(), "-5h"))
}