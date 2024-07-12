###
# Terraform settings and backend
###

terraform {
  required_providers {
    cloudfoundry = {
      source  = "cloudfoundry-community/cloudfoundry"
      version = "0.14.2"
    }
  }

  backend "s3" {
    key     = "terraform.tfstate.staging"
    prefix  = var.cf_app_name
    encrypt = true
    region  = "us-gov-west-1"
  }
}

provider "cloudfoundry" {
  api_url      = var.cf_api_url
  user         = var.cf_user
  password     = var.cf_password
  app_logs_max = 30

}

provider "aws" {
  region = var.aws_region
}

###
# Target space/org
###

data "cloudfoundry_space" "space" {
  org_name = var.cf_org_name
  name     = var.cf_space_name
}

###
# Provision RDS instance
###

data "cloudfoundry_service" "rds" {
  name = "aws-rds"
}

resource "cloudfoundry_service_instance" "database" {
  name             = "tdp-db-staging"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.rds.service_plans["micro-psql"]
  json_params      = "{\"version\": \"15\"}"
  recursive_delete = true
  timeouts {
    create = "60m"
    update = "60m"
    delete = "2h"
  }
}

###
# Provision S3 buckets
###

data "cloudfoundry_service" "s3" {
  name = "s3"
}

resource "cloudfoundry_service_instance" "staticfiles" {
  name             = "tdp-staticfiles-staging"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.s3.service_plans["basic-public-sandbox"]
  recursive_delete = true
}

resource "cloudfoundry_service_instance" "datafiles" {
  name             = "tdp-datafiles-staging"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.s3.service_plans["basic-sandbox"]
  recursive_delete = true
}

data "cloudfoundry_service" "elasticsearch" {
  name = "aws-elasticsearch"
}

resource "cloudfoundry_service_instance" "elasticsearch" {
  name         = "es-staging"
  space        = data.cloudfoundry_space.space.id
  service_plan = data.cloudfoundry_service.elasticsearch.service_plans["es-dev"]
}
