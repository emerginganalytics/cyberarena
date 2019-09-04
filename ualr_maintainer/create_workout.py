import create_network, create_vm
import time, calendar

# --------------------------- RUN --------------------------


def create_dos_workout(name_workout, name_subnet_workout, ts):

    create_network.create_ecosystem_workout(name_workout, ts)
    time.sleep(20)

    # create the vm and return the ext IP of the entry lab
    return create_vm.build_dos_vm(name_workout, name_subnet_workout, ts)


def create_cyberattack_workout(name_workout, name_subnet_workout, ts):

    create_network.create_ecosystem_workout(name_workout, ts)
    time.sleep(10)

    # create the vm and return the ext IP of the entry lab
    return create_vm.build_cyberattack_vm(name_workout, name_subnet_workout, ts)


def create_spoof_workout(name_workout, name_subnet_workout, ts):

    create_network.create_ecosystem_workout(name_workout, ts)
    time.sleep(10)

    # create the vm and return the ext IP of the entry lab
    return create_vm.build_spoof_vm(name_workout, name_subnet_workout, ts)


def create_hiddennode_workout(name_workout, name_subnet_workout, ts):

    create_network.create_ecosystem_workout(name_workout, ts)
    time.sleep(10)

    # create the vm and return the ext IP of the entry lab
    return create_vm.build_hiddennode_vm(name_workout, name_subnet_workout, ts)


def create_ids_workout(name_workout, name_subnet_workout, ts):

    create_network.create_ecosystem_workout(name_workout, ts)
    time.sleep(10)

    # create the vm and return the ext IP of the entry lab
    return create_vm.build_ids_vm(name_workout, name_subnet_workout, ts)


def create_phishing(name_workout, name_subnet_workout, ts):

    create_network.create_ecosystem_workout(name_workout, ts)
    time.sleep(10)

    # create the vm and return the ext IP of the entry lab
    return create_vm.build_phishing_vm(name_workout, name_subnet_workout, ts)


def create_theharbor(name_workout, name_subnet_workout, ts):

    create_network.create_ecosystem_workout(name_workout, ts)
    time.sleep(10)

    # create the vm and return the ext IP of the entry lab
    return create_vm.build_theharbor_vm(name_workout, name_subnet_workout, ts)