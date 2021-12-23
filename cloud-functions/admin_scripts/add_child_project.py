from common.globals import ds_client, AdminInfoEntity


def add_child_project(child_project):
    """
    Add a child project to this parent project. This function gets called by the main application when
    a new child project has been provisioned.
    @param child_project: Name of the child project
    @type child_project: String
    @return: None
    """
    admin_info = ds_client.get(ds_client.key(AdminInfoEntity.KIND, 'cybergym'))
    if AdminInfoEntity.Entities.CHILD_PROJECTS in admin_info:
        admin_info[AdminInfoEntity.Entities.CHILD_PROJECTS].append(child_project)
    else:
        admin_info[AdminInfoEntity.Entities.CHILD_PROJECTS] = [child_project]
    ds_client.put(admin_info)
    return True
