variable "aws_region" {
  type        = string
  description = "region output by cloud foundry service-key command"
  default     = "us-gov-west-1"
}

variable "cf_api_url" {
  type        = string
  description = "cloud.gov api url"
  default     = "https://api.fr.cloud.gov"
}

variable "cf_org_name" {
  type        = string
  description = "cloud.gov organization name"
  default     = "hhs-acf-ofa"
}

variable "cf_space_name" {
  type        = string
  description = "cloud.gov space name"
  default     = "tanf-prod"
}

variable "cf_user" {
  type        = string
  description = "secret; cloud.gov deployer account user"
}

variable "cf_password" {
  type        = string
  description = "secret; cloud.gov deployer account password"
}

variable "cf_app_name" {
  type        = string
  description = "name of app"
}
