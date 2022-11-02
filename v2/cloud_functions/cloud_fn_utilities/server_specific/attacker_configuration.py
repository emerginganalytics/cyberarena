from cloud_fn_utilities.globals import BuildConstants

__author__ = "Andrew Bomberger"
__copyright__ = "Copyright 2022, UA Little Rock, Emerging Analytics Center"
__credits__ = ["Andrew Bomberger"]
__license__ = "MIT"
__version__ = "1.0.0"
__maintainer__ = "Philip Huff"
__email__ = "pdhuff@ualr.edu"
__status__ = "Testing"


class Agent(object):
    """
    Agents are the red team machines that are injected into the specified network to act as the
    main contact point in an emulated botnet.

    agent_build_obj = {
        parent_id,
        parent_build_type,
        build_id => workout or workspace id that the agent is associated with
        agent_topic,
        agent_telemetry
    }
    """
    def __init__(self, build_id):
        self.build_id = build_id
        self.server_name = f'{self.build_id}-agent'

    def prepare_agent(self):
        return {
            'name': self.server_name,
            'image': BuildConstants.MachineImages.AGENT,
            'machine_type': BuildConstants.MachineTypes.SMALL,
            'tags': {'items': ['allow-all-local-external']},
            'metadata': '',
            'nics': [
                {
                    'network': 'enterprise',
                    'internal_ip': BuildConstants.Networks.Reservations.AGENT_SERVER,
                    'subnet_name': 'default',
                    'external_nat': False
                }
            ],
            'build_type': BuildConstants.BuildType.AGENT_SERVER,
        }

    class AgentStartup:
        agent_start_env = \
            '#! /bin/bash\n' \
            'cat >> /etc/environment << EOF\n' \
            'AGENT_TOPIC={agent_topic}\n' \
            'AGENT_TELEMETRY={agent_telemetry}\n' \
            'BUILD_ID={build_id}\n' \
            'EOF'

# [ eof ]
