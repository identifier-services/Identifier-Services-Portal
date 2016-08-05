from .base import DynamicForm
from ..models import Dataset
import logging

logger = logging.getLogger(__name__)


class DatasetForm(DynamicForm):
    metadata_model = Dataset
