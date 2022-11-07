from main_app_utilities.globals import BuildConstants

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
    def __init__(self, agent_build_obj):
        self.agent_build_obj = agent_build_obj
        self.build_id = self.agent_build_obj.get('build_id', None)
        self.server_name = f'{self.build_id}-agent'
        self.parent_build_type = self.agent_build_obj.get('parent_build_type', None)
        self.parent_id = self.agent_build_obj.get('parent_id', None)
        self.startup_script = '#! /bin/bash\n' \
                              'cat >> /etc/environment << EOF\n' \
                              'AGENT_TOPIC={' + self.agent_build_obj["agent_topic"] + '}\n' \
                              'AGENT_TELEMETRY={' + self.agent_build_obj['agent_telemetry'] + '}\n' \
                              'EOF'

    def get(self):
        return {
            'parent_id': self.build_id,
            'parent_build_type': self.parent_build_type,
            'fixed_arena_class_id': self.parent_id,
            'name': self.server_name,
            'image': BuildConstants.MachineImages.AGENT,
            'machine_type': BuildConstants.MachineTypes.SMALL,
            'tags': {'items': ['allow-all-local-external']},
            'metadata': self.startup_script,
            'nics': [
                {
                    'network': 'enterprise',
                    'internal_ip': BuildConstants.Networks.Reservations.AGENT_MACHINE,
                    'subnet_name': 'default',
                    'external_nat': False
                }
            ],
            'build_type': BuildConstants.BuildType.AGENT_MACHINE,
        }

# [ eof ]
