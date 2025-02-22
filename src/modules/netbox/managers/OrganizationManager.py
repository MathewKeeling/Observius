import logging
import requests
from src.modules.yaml.YamlReader import YamlReader


class OrganizationManager:
    def __init__(self, api):
        self.api = api

    def create_organization(self, data):
        return self.api._post("tenancy/tenants/", data)

    def create_organizations_from_yaml(self, yaml_file):
        organizations_data = YamlReader(yaml_file=yaml_file).get_section(
            "organizations"
        )
        if organizations_data:
            for organization in organizations_data:
                try:
                    self.create_organization(organization)
                    logging.debug(f"Organization created: {organization['name']}")
                except requests.exceptions.RequestException as e:
                    logging.debug(
                        f"Error creating organization {organization['name']}: {e}"
                    )
        else:
            logging.debug("No organizations found in the YAML file.")

    def get_organization_id(self, organization_slug):
        response = self.api._get(f"tenancy/tenants/?slug={organization_slug}")
        organizations = response.get("results", [])
        if organizations:
            return organizations[0]["id"]
        else:
            raise ValueError(f"Organization with slug '{organization_slug}' not found.")

    def get_organizations(self, params=None):
        return self.api._get("tenancy/tenants/", params)

    def organization_exists(self, slug):
        slug = slug.lower()
        organizations = self.get_organizations()
        for organization in organizations.get("results", []):
            if organization.get("slug").lower() == slug:
                return True
        return False
