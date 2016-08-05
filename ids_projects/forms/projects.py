from .base import DynamicForm
from ..models import Project
import logging

logger = logging.getLogger(__name__)


class ProjectForm(DynamicForm):
    metadata_model = Project
