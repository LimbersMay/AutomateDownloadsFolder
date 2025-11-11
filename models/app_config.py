from typing import List, Literal

from pydantic import Field

from models.base import CamelCaseModel
from models.models import (
    FolderSortingRule,
    GlobalSettings,
    LifecyclePolicy,
    OrderedFile,
    PathConfig,
    SortingRule,
)


class AppConfig(CamelCaseModel):
    """Application configuration model."""

    paths: PathConfig
    settings: GlobalSettings = Field(alias='settings')
    default_lifecycle: LifecyclePolicy = Field(default_factory=LifecyclePolicy)

    # --- Rules for files ---
    sorting_rules: List[SortingRule]
    default_folder: str = "Other"

    # --- Rules for folders ---
    folder_rules: List[FolderSortingRule] = []
    default_folder_action: Literal['process_contents', 'move', 'ignore'] = 'ignore'

    # --- Register of ordered files ---
    ordered_files: List[OrderedFile] = []
