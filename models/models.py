import datetime
from pathlib import Path
from typing import Literal, Optional

from pydantic import field_validator

from models.base import CamelCaseModel


class GlobalSettings(CamelCaseModel):
    max_size_in_mb: int

    def convert_mb_to_bytes(cls, data: int) -> int:
        return data * 1024 * 1024


class LifecyclePolicy(CamelCaseModel):
    enabled: bool = True
    action: Literal['trash', 'delete'] = 'trash'
    days_to_keep: int = 30


class OrderedFile(CamelCaseModel):
    name: str
    ordered_date: datetime.date
    path: str

    rule_name_applied: str


class PathConfig(CamelCaseModel):
    source_path: Path
    destination_path: Path

    @field_validator('source_path')
    def validate_source_path(cls, v):
        if not v.name:
            raise ValueError('Source path cannot be empty')
        return v

    @field_validator('destination_path')
    def validate_destination_path(cls, v):
        if not v.name:
            raise ValueError('Destination path cannot be empty')
        return v


class SortingRule(CamelCaseModel):
    folder_name: str
    match_by: str
    patterns: list[str]

    lifecycle: Optional[LifecyclePolicy] = None


class FolderSortingRule(CamelCaseModel):
    """Defines a folder sorting rule with associated folder name, matching criteria, and patterns."""
    ruleName: str
    matchBy: Literal['glob', 'regex']
    patterns: list[str]
    action: Literal['process_contents', 'move', 'ignore']

    # for 'process_contents' action
    deleteEmptyAfterProcessing: bool = False

    # for 'move' action
    destinationFolder: Optional[str] = None

    lifecycle: Optional[LifecyclePolicy] = None

