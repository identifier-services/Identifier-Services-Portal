from .base import DynamicForm
from ..models import Specimen
import logging

logger = logging.getLogger(__name__)


class SpecimenForm(DynamicForm):
    metadata_model = Specimen