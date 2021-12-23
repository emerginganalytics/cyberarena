import os
import sys
import yaml
from common.globals import ds_client, BUILD_STATES, compute, project
from common.prepare_compute import create_instance_custom_image
from common.nuke_workout import nuke_workout
from common.state_transition import state_transition


def create_new_server_in_unit(unit_id, build_server_spec):
    """
    Use this script when a new server is needed for an existing Unit. This is often helpful for semester long labs
    in which you would like to modify the build environment.
    @param unit_id: The unit_id to add the server to
    @type unit_id: String
    @param build_server_spec: The yaml specification file which holds the new server
    @type build_server_spec: String
    @param spec_folder: Folder where the specs are located
    @type spec_folder: String
    @return: None
    @rtype: None
    """
    spec_folder = "..\\build-files\\server-specs"

    # Open and read YAML file
    server_spec = os.path.join(spec_folder, build_server_spec)
    with open(server_spec, "r") as f:
        yaml_spec = yaml.load(f, Loader=yaml.SafeLoader)
    name = yaml_spec['name']
    custom_image = yaml_spec['image']
    tags = yaml_spec['tags'] if 'tags' in yaml_spec else None
    machine_type = yaml_spec['machine_type'] if 'machine_type' in yaml_spec else 'n1-standard-1'
    network_routing = yaml_spec['network_routing'] if 'network_routing' in yaml_spec else False

    query_workouts = ds_client.query(kind='cybergym-workout')
    query_workouts.add_filter('unit_id', '=', unit_id)
    for workout in list(query_workouts.fetch()):
        workout_project = workout.get('build_project_location', project)
        if workout_project == project:
            workout_id = workout.key.name
            nics = []
            for n in yaml_spec['nics']:
                n['external_NAT'] = n['external_NAT'] if 'external_NAT' in n else False
                nic = {
                    "network": f"{workout_id}-{n['network']}",
                    "internal_IP": n['internal_IP'],
                    "subnet": f"{workout_id}-{n['network']}-{n['subnet']}",
                    "external_NAT": n['external_NAT']
                }
                if 'IP_aliases' in n and n['IP_aliases']:
                    alias_ip_ranges = []
                    for ipaddr in n['IP_aliases']:
                        alias_ip_ranges.append({"ipCidrRange": ipaddr})
                    nic['aliasIpRanges'] = alias_ip_ranges
                nics.append(nic)
            create_instance_custom_image(compute=compute, workout=workout_id, name=f"{workout_id}-{name}",
                                         custom_image=custom_image, machine_type=machine_type,
                                         networkRouting=network_routing, networks=nics, tags=tags)


if __name__ == "__main__":
    create_new_server_in_unit()
