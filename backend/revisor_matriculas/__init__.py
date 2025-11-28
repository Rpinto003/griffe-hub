# -*- coding: utf-8 -*-
"""
Backend - Revisor de Matrículas
"""

from .excel_reader import ExcelReader
from .field_mapping import (
    FORM_MATRICULA_SECTIONS,
    FORM_INICIAL_SECTIONS,
    FORM_MEDICO_SECTIONS,
    UNIFIED_SECTIONS,
    get_field_label
)

__all__ = [
    'ExcelReader',
    'FORM_MATRICULA_SECTIONS',
    'FORM_INICIAL_SECTIONS',
    'FORM_MEDICO_SECTIONS',
    'UNIFIED_SECTIONS',
    'get_field_label'
]