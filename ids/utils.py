from django.conf import settings
from agavepy.agave import Agave


def replace_space(func):
    def func_wrapper(project):
        return project.replace(" ", "-")
    return func_wrapper


def get_portal_api_client():
    return Agave(api_server=settings.AGAVE_TENANT_BASEURL,
                 token=settings.AGAVE_SUPER_TOKEN)


def get_investigation_type(project):
    return project.value['investigation_type'].lower()


@replace_space
def get_investigation_type_description(project):
    """Returns full project description, as read from yaml config."""
    investigation_type = project.value['investigation_type'].lower()
    object_descriptions = getattr(settings, 'OBJ_DESCR')
    investigation_types = object_descriptions['investigation_types']
    project_description = investigation_types[investigation_type]
    return project_description


def get_project_description():
    """Returns project fields."""
    object_descriptions = getattr(settings, 'OBJ_DESCR')
    project_description = object_descriptions['project']
    return project_description


def get_project_form_fields():
    """Returns project fields."""
    project_description = get_project_description()
    return project_description['fields']


@replace_space
def get_process_descriptions(project):
    """Returns full process descriptions, as read from yaml config."""
    investigation_type_description = get_investigation_type_description(project)
    process_description = investigation_type_description['processes']
    return process_description


@replace_space
def get_material_descriptions(project):
    """Returns full process descriptions, as read from yaml config."""
    investigation_type_description = get_investigation_type_description(project)
    material_description = investigation_type_description['material']
    return material_description


@replace_space
def get_information_descriptions(project):
    """Returns full process descriptions, as read from yaml config."""
    investigation_type_description = get_investigation_type_description(project)
    information_description = investigation_type_description['information']
    return information_description


@replace_space
def get_process_type_keys(project):
    """Returns the types of process for a given project"""
    project_processes = get_process_descriptions(project)
    process_types = project_processes.keys()    
    return process_types


@replace_space
def get_material_type_keys(project):
    """Returns the types of process for a given project"""
    material_processes = get_process_descriptions(project)
    material_types = material_processes.keys()
    return material_types


@replace_space
def get_information_type_keys(project):
    """Returns the types of process for a given project"""
    information_processes = get_process_descriptions(project)
    information_types = information_processes.keys()
    return information_types


@replace_space
def get_process_type_titles(project):
    """Returns the types of process for a given project"""
    project_processes = get_process_descriptions(project)
    process_titles = [x.title() for x in project_processes.keys()]
    return process_titles


@replace_space
def get_material_type_titles(project):
    """Returns the types of process for a given project"""
    project_material = get_material_descriptions(project)
    material_titles = [x.title() for x in project_material.keys()]
    return material_titles


@replace_space
def get_information_type_titles(project):
    """Returns the types of process for a given project"""
    project_information = get_information_descriptions(project)
    information_titles = [x.title() for x in project_information.keys()]
    return information_titles


@replace_space
def get_process_choices(project):
    """
    Returns a list of tuples containing process types and process type
    titles.  Intended for use in a form (includes 'choose one' tuple).
    """
    project_processes = get_process_descriptions(project)
    process_type_choices = [('', 'Choose one'),] + \
                            [(x,x.title()) for x in project_processes.keys()]
    return process_type_choices


@replace_space
def get_material_choices(project):
    """
    Returns a list of tuples containing process types and process type
    titles.  Intended for use in a form (includes 'choose one' tuple).
    """
    project_material = get_material_descriptions(project)
    material_type_choices = [('', 'Choose one'), ] + \
                            [(x, x.title()) for x in project_material.keys()]
    return material_type_choices


@replace_space
def get_information_choices(project):
    """
    Returns a list of tuples containing process types and process type
    titles.  Intended for use in a form (includes 'choose one' tuple).
    """
    project_information = get_information_descriptions(project)
    information_type_choices = [('', 'Choose one'), ] + \
                               [(x, x.title()) for x in project_information.keys()]
    return information_type_choices


def get_process_description(project, process_type):
    """Returns full process description, as read from yaml config,
    given project and process type."""
    project_processes = get_process_descriptions(project)
    process_description = project_processes[process_type]
    return process_description


def get_material_description(project, material_type):
    """Returns full process description, as read from yaml config,
    given project and process type."""
    project_material = get_process_descriptions(project)
    material_description = project_material[material_type]
    return material_description


def get_process_fields(project, process_type):
    """Returns process fields for a given process type."""
    project_processes = get_process_descriptions(project)
    process_description = project_processes[process_type]
    process_fields = process_description['fields']
    return process_fields


def get_material_fields(project, material_type):
    """Returns process fields for a given process type."""
    project_material = get_material_descriptions(project)
    material_description = project_material[material_type]
    material_fields = material_description['fields']
    return material_fields


@replace_space
def get_information_fields(project, information_type):
    """Returns process fields for a given process type."""
    project_information = get_information_descriptions(project)
    information_description = project_information[information_type]
    information_fields = information_description['fields']
    return information_fields


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


def get_data_description(project):
    """Returns full dataset descriptions, as read from yaml config."""
    investigation_type_description = get_investigation_type_description(project)
    data_description = investigation_type_description['data']
    return data_description


def get_data_fields(project):
    """Returns dataset fields."""
    data_description = get_data_description(project)
    data_fields = data_description['fields']
    return data_fields


# TODO: TO BE TESTED
def get_probe_description(project):
    """Returns full probe descriptions, as read from yaml config."""
    investigation_type_description = get_investigation_type_description(project)
    probe_description = investigation_type_description['probe']
    return probe_description


def get_probe_fields(project):
    """Returns probe fields."""
    probe_description = get_probe_description(project)
    probe_fields = probe_description['fields']
    return probe_fields

