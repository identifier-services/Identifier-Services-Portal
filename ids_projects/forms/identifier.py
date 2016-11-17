from .base import DynamicForm
from ..models import Identifier
import logging

logger = logging.getLogger(__name__)


class IdentifierForm(DynamicForm):
    metadata_model = Identifier
