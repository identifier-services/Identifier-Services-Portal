from django import forms
from .base import DynamicForm
from ..models import Dataset
import six, logging

logger = logging.getLogger(__name__)


class DatasetForm(DynamicForm):
    metadata_model = Dataset
