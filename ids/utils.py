from django.conf import settings
from agavepy.agave import Agave


def get_portal_api_client():
    return Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                 token=settings.AGAVE_SUPER_TOKEN)


def get_investigation_type_description(project):
    """Returns full project description, as read from yaml config."""
    investigation_type = project.value['investigation_type'].lower()
    object_descriptions = getattr(settings, 'OBJ_DESCR')
    investigation_types = object_descriptions['investigation_types']
    project_description = investigation_types[investigation_type]
    return project_description


def get_project_description(project):
    """Returns project fields."""
    object_descriptions = getattr(settings, 'OBJ_DESCR')
    project_description = object_descriptions['project']
    return project_description


def get_project_form_fields(project):
    """Returns project fields."""
    project_description = get_project_description(project)
    return project_description['fields']


def get_project_fields(project):
    return get_project_form_fields(project)


def get_process_descriptions(project):
    """Returns full process descriptions, as read from yaml config."""
    investigation_type_description = get_investigation_type_description(project)
    process_description = investigation_type_description['processes']
    return process_description


def get_process_type_keys(project):
    """Returns the types of process for a given project"""
    project_processes = get_process_descriptions(project)
    process_types = project_processes.keys()
    return process_types


def get_process_type_titles(project):
    """Returns the types of process for a given project"""
    project_processes = get_process_descriptions(project)
    process_titles = [x.title() for x in project_processes.keys()]
    return process_titles


def get_process_choices(project):
    """
    Returns a list of tuples containing process types and process type
    titles.  Intended for use in a form (includes 'choose one' tuple).
    """
    project_processes = get_process_descriptions(project)
    process_type_choices = [('', 'Choose one'),] + \
                            [(x,x.title()) for x in project_processes.keys()]
    return process_type_choices


def get_process_description(project, process_type):
    """Returns full process description, as read from yaml config,
    given project and process type."""
    project_processes = get_process_descriptions(project)
    process_description = project_processes[process_type]
    return process_description


def get_process_fields(project, process_type):
    """Returns process fields for a given process type."""
    project_processes = get_process_descriptions(project)
    process_description = project_processes[process_type]
    process_fields = process_description['fields']
    return process_fields


def get_specimen_description(project):
    """Returns full specimen descriptions, as read from yaml config."""
    investigation_type_description = get_investigation_type_description(project)
    specimen_description = investigation_type_description['specimen']
    return specimen_description


def get_specimen_fields(project):
    """Returns specimen fields."""
    specimen_description = get_specimen_description(project)
    specimen_fields = specimen_description['fields']
    return specimen_fields


def get_dataset_description(project):
    """Returns full dataset descriptions, as read from yaml config."""
    investigation_type_description = get_investigation_type_description(project)
    dataset_description = investigation_type_description['dataset']
    return dataset_description


def get_dataset_fields(project):
    """Returns dataset fields."""
    dataset_description = get_dataset_description(project)
    dataset_fields = dataset_description['fields']
    return dataset_fields
