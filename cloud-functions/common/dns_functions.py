import ast
import googleapiclient.discovery
from common.globals import ds_client, dns_suffix, dnszone, log_client, LOG_LEVELS, project, parent_project
from googleapiclient.errors import HttpError


# Create a new DNS record for the server and add the information to the datastore for later management
def add_dns_record(dns_prefix, new_ip):
    service = googleapiclient.discovery.build('dns', 'v1')

    # Use the parent project when modifying the DNS otherwise, if this IS the parent, then use the current project
    target_project = parent_project if parent_project else project

    # First, get the existing workout DNS
    response = service.resourceRecordSets().list(project=target_project, managedZone=dnszone,
                                                 name=dns_prefix + dns_suffix + ".").execute()
    existing_rrset = response['rrsets']
    change_body = {
        "deletions": existing_rrset,
        "additions": [
            {
                "kind": "dns#resourceRecordSet",
                "name": dns_prefix + dns_suffix + ".",
                "rrdatas": [new_ip],
                "type": "A",
                "ttl": 30
            }
        ],
    }
    # Try first to perform the DNS change, but in case the DNS did not previously exist, try again without the deletion change.
    try:
        request = service.changes().create(project=target_project, managedZone=dnszone, body=change_body).execute()
    except HttpError:
        try:
            del change_body["deletions"]
            request = service.changes().create(project=target_project, managedZone=dnszone, body=change_body).execute()
        except HttpError:
            # Finally, it may be the DNS has already been successfully updated, in which case
            # the API call will throw an error. We ignore this case.
            pass


def delete_dns(dns_prefix, ip_address):
    """
    Deletes a DNS record based on the build_id host name and IP address.
    :param build_id: The Datastore entity build_id, which is also the record host name.
    :param ip_address: The IP address of of the record to delete.
    :return: None
    """
    # Use the parent project when modifying the DNS otherwise, if this IS the parent, then use the current project
    target_project = parent_project if parent_project else project
    try:
        service = googleapiclient.discovery.build('dns', 'v1')

        change_body = {"deletions": [
            {
                "kind": "dns#resourceRecordSet",
                "name": dns_prefix + dns_suffix + ".",
                "rrdatas": [ip_address],
                "type": "A",
                "ttl": 30
            },
        ]}
        service.changes().create(project=target_project, managedZone=dnszone, body=change_body).execute()
    except():
        g_logger = log_client.logger(str(dns_prefix))
        g_logger.log_text("Error in deleting DNS record for workout {}".format(dns_prefix), severity=LOG_LEVELS.ERROR)
        return False
    return True


def add_active_directory_dns(build_id, ip_address, network):
    """
    Add a DNS forwarding rule to support an Active Directory server acting as the default DNS server
    @param build_id: The ID of the workout or arena with the DNS server
    @type build_id: String
    @param ip_address: IP address of the active directory server
    @type ip_address: String
    @param network: A list of network names to use for DNS forwarding
    @type network: List
    @return: Status
    @rtype: Boolean
    """
    service = googleapiclient.discovery.build('dns', 'v1')
    g_logger = log_client.logger(build_id)

    managed_zone_body = {
        "kind": "dns#managedZone",
        "name": build_id,
        "dnsName": "cybergym.local.",
        "visibility": "private",
        "description": "",
        "privateVisibilityConfig": {
            "kind": "dns#managedZonePrivateVisibilityConfig",
            "networks": []
        },
        "forwardingConfig": {
            "kind": "dns#managedZoneForwardingConfig",
            "targetNameServers": [
                {
                    "kind": "dns#managedZoneForwardingConfigNameServerTarget",
                    "ipv4Address": ip_address,
                    "forwardingPath": "default"
                }
            ],
        }
    }

    forwarding_network = {
        "kind": "dns#managedZonePrivateVisibilityConfigNetwork",
        "networkUrl": f"https://www.googleapis.com/compute/v1/projects/{project}/global/networks/{network}"
    }
    managed_zone_body["privateVisibilityConfig"]["networks"].append(forwarding_network)

    # Try first to perform the DNS change, but in case the DNS did not previously exist, try again without the deletion change.
    try:
        request = service.managedZones().create(project=project, body=managed_zone_body)
        response = request.execute()
    except HttpError as err:
        error_text = ast.literal_eval(err.content.decode("UTF-8"))['error']['errors'][0]['message']
        g_logger.log_text(f"Error while adding private DNS zone for Active Directory: {error_text}")
        return False
    return True


def delete_active_directory_dns(managed_zone):
    """
    Deletes the given managed zone
    @param managed_zone: Managed zone for deleting
    @type managed_zone: str
    @return: Status
    @rtype: bool
    """
    g_logger = log_client.logger(managed_zone)
    service = googleapiclient.discovery.build('dns', 'v1')
    try:
        request = service.managedZones().delete(project=project, managedZone=managed_zone)
        request.execute()
    except HttpError as err:
        error_text = ast.literal_eval(err.content.decode("UTF-8"))['error']['errors'][0]['message']
        g_logger.log_text(f"Error while adding private DNS zone for Active Directory: {error_text}")
        return False
    return True
