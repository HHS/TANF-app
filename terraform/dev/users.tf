resource "cloudfoundry_user" "dev_test_user" {

    name = "test-dummy"
    password = "Passw0rd"

    groups = [ "cloud_controller.admin", "scim.read", "scim.write" ]
}

resource "cloudfoundry_space_users" "dev_space_users" {
  space      = "tanf-dev"
  managers   = [
    "test-dummy"
  ]
  developers = [
    "test-dummy"
  ]
  auditors   = [
    "test-dummy"
  ]
}

resource "cloudfoundry_org_users" "dev_org_users" {
  org              = "hhs-act-prototyping"
  managers         = [
    "test-dummy"
  ]
  billing_managers = [
    "test-dummy"
  ]
  auditors         = [
    "test-dummy"
  ]
}
