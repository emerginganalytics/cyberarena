"""
In testing! This is not ready for production. Originally, this was set up to allow a redteam network to attack other
students. However, many servers such as firewalls and active directory controls require their IP address to remain
static. Therefore, dynamic address assignment for distinct student networks does not work. But, there may still be
other uses for this class in the future.

This class takes an existing set of workout specifications and further specifies:
 1) Subnets for network build specifications
 2) IP addresses for each server
 3) Firewall rules to ensure all networks can communicate with each other
"""

from netaddr import IPAddress, IPNetwork


__author__ = "Philip Huff"
__copyright__ = "Copyright 2021, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Philip Huff"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class StudentNetworkCombiner:
    def __init__(self, cloud_ready_specs, combine_student_networks):
        self.cloud_ready_specs = cloud_ready_specs
        self.combine_network = combine_student_networks.get('combine_network', None)
        self.available_subnet = IPNetwork(combine_student_networks.get('subnet', '10.1.0.0/16'))

    def allocate_networks(self):
        """
        Loop through the cloud ready specs and assign IP networks and IP addresses to components
        @return: None
        """
        subnets = list(self.available_subnet.subnet(24))
        for i, spec in enumerate(self.cloud_ready_specs):
            # Define the available subnet for this workout and the available list of IP addresses.
            allocated_subnet = str(subnets[i])
            ip_addresses = subnets[i].iter_hosts()[2:]  # Skip .1 and .2 for the gateway address and student_entry
            spec['combine_network'] = True
            for network in spec['networks']:
                if network['name'] == self.combine_network:
                    network['subnets'][0]['ip_subnet'] = allocated_subnet

            for j, server in enumerate(spec['servers']):
                for nic in server['nics']:
                    if nic['network'] == self.combine_network:
                        existing_address = nic.get('internal_IP', None)
                        if existing_address:
                            nic['internal_IP'] = str(ip_addresses[j])
                        else:
                            pass

