from .base import DynamicForm
from ..models import Probe
import logging

logger = logging.getLogger(__name__)


class ProbeForm(DynamicForm):
    metadata_model = Probe
