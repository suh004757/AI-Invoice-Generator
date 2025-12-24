"""
Purchase Order model
"""
from datetime import datetime
from typing import Optional


class PurchaseOrder:
    """Purchase Order model"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        original_filename: str = "",
        file_path: str = "",
        file_type: str = "",
        extracted_text: str = "",
        status: str = "uploaded",
        upload_date: Optional[str] = None
    ):
        self.id = id
        self.original_filename = original_filename
        self.file_path = file_path
        self.file_type = file_type
        self.extracted_text = extracted_text
        self.status = status
        self.upload_date = upload_date or datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "file_path": self.file_path,
            "file_type": self.file_type,
            "extracted_text": self.extracted_text,
            "status": self.status,
            "upload_date": self.upload_date
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PurchaseOrder':
        """Create from dictionary"""
        return cls(
            id=data.get("id"),
            original_filename=data.get("original_filename", ""),
            file_path=data.get("file_path", ""),
            file_type=data.get("file_type", ""),
            extracted_text=data.get("extracted_text", ""),
            status=data.get("status", "uploaded"),
            upload_date=data.get("upload_date")
        )
