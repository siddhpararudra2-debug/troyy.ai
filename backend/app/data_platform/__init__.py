"""
Data Platform Module
Provides object storage, data catalog, and archival capabilities
"""
from app.data_platform.object_storage import ObjectStorage
from app.data_platform.data_catalog import DataCatalog
from app.data_platform.archive_manager import ArchiveManager
from app.data_platform.backup_manager import BackupManager

__all__ = [
    "ObjectStorage",
    "DataCatalog",
    "ArchiveManager",
    "BackupManager",
]
