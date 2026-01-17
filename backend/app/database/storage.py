"""
Storage Service for handling file uploads and analysis persistence
"""
import os
import hashlib
import uuid
import base64
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO
import logging

from .connection import Database

logger = logging.getLogger(__name__)


class StorageService:
    """Service for storing files and analysis data in MongoDB"""
    
    # File storage paths
    UPLOAD_DIR = Path("data/uploads")
    TEMP_DIR = Path("data/temp")
    
    def __init__(self):
        # Ensure directories exist
        (self.UPLOAD_DIR / "images").mkdir(parents=True, exist_ok=True)
        (self.UPLOAD_DIR / "videos").mkdir(parents=True, exist_ok=True)
        (self.UPLOAD_DIR / "audio").mkdir(parents=True, exist_ok=True)
        self.TEMP_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_file_hash(self, file_content: bytes) -> str:
        """Generate SHA256 hash for deduplication"""
        return hashlib.sha256(file_content).hexdigest()
    
    def _get_date_path(self) -> str:
        """Get date-based path like 2026/01/17"""
        now = datetime.now(timezone.utc)
        return f"{now.year}/{now.month:02d}/{now.day:02d}"
    
    def _get_file_type(self, filename: str, content_type: str) -> str:
        """Determine file type from filename or content type"""
        filename_lower = filename.lower()
        
        if any(filename_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
            return "image"
        elif any(filename_lower.endswith(ext) for ext in ['.mp4', '.avi', '.mov', '.webm', '.mkv']):
            return "video"
        elif any(filename_lower.endswith(ext) for ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']):
            return "audio"
        elif content_type:
            if content_type.startswith('image/'):
                return "image"
            elif content_type.startswith('video/'):
                return "video"
            elif content_type.startswith('audio/'):
                return "audio"
        
        return "other"
    
    async def save_upload(
        self,
        file_content: bytes,
        filename: str,
        content_type: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Save uploaded file and create database record.
        
        Returns:
            Upload document dict with id, or None if DB not connected
        """
        if not Database.is_connected():
            logger.warning("Database not connected - skipping upload storage")
            return None
        
        try:
            # Generate IDs and hashes
            upload_id = str(uuid.uuid4())
            file_hash = self._get_file_hash(file_content)
            file_type = self._get_file_type(filename, content_type)
            
            # Create file path
            date_path = self._get_date_path()
            file_ext = Path(filename).suffix.lower()
            stored_filename = f"{upload_id}{file_ext}"
            
            # Full path: data/uploads/images/2026/01/17/{uuid}.jpg
            relative_path = f"{file_type}s/{date_path}/{stored_filename}"
            full_path = self.UPLOAD_DIR / relative_path
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'wb') as f:
                f.write(file_content)
            
            # Create database record
            upload_doc = {
                "_id": upload_id,
                "session_id": session_id,
                "user_id": user_id,
                "original_filename": filename,
                "stored_filename": stored_filename,
                "file_path": str(relative_path),
                "file_type": file_type,
                "mime_type": content_type,
                "file_size_bytes": len(file_content),
                "file_hash": file_hash,
                "uploaded_at": datetime.now(timezone.utc),
                "status": "pending"
            }
            
            # Insert into database
            collection = Database.get_collection(Database.UPLOADS)
            await collection.insert_one(upload_doc)
            
            logger.info(f"Saved upload: {upload_id} ({file_type}, {len(file_content)} bytes)")
            return upload_doc
            
        except Exception as e:
            logger.error(f"Failed to save upload: {e}")
            return None
    
    async def save_analysis_result(
        self,
        upload_id: str,
        result: Dict[str, Any],
        mode: str = "standard"
    ) -> Optional[str]:
        """
        Save analysis result to database.
        
        Returns:
            Result ID or None if failed
        """
        if not Database.is_connected():
            return None
        
        try:
            result_id = str(uuid.uuid4())
            
            analysis_doc = {
                "_id": result_id,
                "upload_id": upload_id,
                "classification": result.get("classification", "UNKNOWN"),
                "risk_score": result.get("risk_score", 50.0),
                "confidence": result.get("confidence", "LOW"),
                "detailed_label": result.get("detailed_label"),
                "visual_result": result.get("signals", {}).get("local_visual"),
                "forensic_result": result.get("signals", {}).get("local_forensic"),
                "temporal_result": result.get("signals", {}).get("local_temporal"),
                "enhanced_result": result.get("signals", {}).get("enhanced_ai"),
                "processing_time_ms": result.get("processing_time_ms"),
                "analysis_mode": mode,
                "analyzed_at": datetime.now(timezone.utc),
                "raw_response": result
            }
            
            collection = Database.get_collection(Database.ANALYSIS_RESULTS)
            await collection.insert_one(analysis_doc)
            
            # Update upload status
            uploads = Database.get_collection(Database.UPLOADS)
            await uploads.update_one(
                {"_id": upload_id},
                {"$set": {"status": "completed"}}
            )
            
            logger.info(f"Saved analysis result: {result_id} for upload {upload_id}")
            return result_id
            
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            return None
    
    async def track_session(
        self,
        session_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[str]:
        """
        Create or update a session record.
        
        Returns:
            Session ID
        """
        if not Database.is_connected():
            return None
        
        try:
            session_id = str(uuid.uuid4())
            
            session_doc = {
                "_id": session_id,
                "session_token": session_token,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "started_at": datetime.now(timezone.utc),
                "is_active": True,
                "page_views": [],
                "event_count": 0
            }
            
            collection = Database.get_collection(Database.SESSIONS)
            await collection.insert_one(session_doc)
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to track session: {e}")
            return None
    
    async def track_event(
        self,
        session_id: str,
        event_type: str,
        event_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track an analytics event.
        
        Event types: 'upload', 'analyze', 'download_report', 'mode_change', 'page_view'
        """
        if not Database.is_connected():
            return False
        
        try:
            event_doc = {
                "_id": str(uuid.uuid4()),
                "session_id": session_id,
                "event_type": event_type,
                "event_data": event_data or {},
                "timestamp": datetime.now(timezone.utc)
            }
            
            collection = Database.get_collection(Database.ANALYTICS)
            await collection.insert_one(event_doc)
            
            # Update session event count
            sessions = Database.get_collection(Database.SESSIONS)
            await sessions.update_one(
                {"_id": session_id},
                {"$inc": {"event_count": 1}}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to track event: {e}")
            return False
    
    async def get_session_analytics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics data for a session"""
        if not Database.is_connected():
            return None
        
        try:
            sessions = Database.get_collection(Database.SESSIONS)
            session = await sessions.find_one({"_id": session_id})
            
            if not session:
                return None
            
            # Get uploads for this session
            uploads = Database.get_collection(Database.UPLOADS)
            upload_count = await uploads.count_documents({"session_id": session_id})
            
            # Get analysis results
            results = Database.get_collection(Database.ANALYSIS_RESULTS)
            pipeline = [
                {"$match": {"upload_id": {"$in": [u["_id"] async for u in uploads.find({"session_id": session_id})]}}},
                {"$group": {
                    "_id": "$classification",
                    "count": {"$sum": 1}
                }}
            ]
            
            return {
                "session_id": session_id,
                "started_at": session["started_at"],
                "upload_count": upload_count,
                "event_count": session.get("event_count", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get session analytics: {e}")
            return None
    
    async def save_biometric_data(
        self,
        service_type: str,  # 'liveness', 'age', 'face_match'
        image_bytes: bytes,
        result: Dict[str, Any],
        filename: str = "capture.jpg",
        session_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Save biometric analysis data with compressed image to MongoDB.
        
        - Compresses image using zlib
        - Stores as base64 in MongoDB
        - Saves full analysis result
        
        Returns: document ID or None
        """
        if not Database.is_connected():
            logger.warning("Database not connected - skipping biometric storage")
            return None
        
        try:
            doc_id = str(uuid.uuid4())
            
            # Compress image bytes with zlib
            compressed = zlib.compress(image_bytes, level=6)
            compressed_b64 = base64.b64encode(compressed).decode('utf-8')
            
            # Calculate hash for deduplication
            image_hash = hashlib.sha256(image_bytes).hexdigest()
            
            # Create document
            biometric_doc = {
                "_id": doc_id,
                "service_type": service_type,
                "session_id": session_id,
                "image_hash": image_hash,
                "image_compressed_b64": compressed_b64,
                "original_size_bytes": len(image_bytes),
                "compressed_size_bytes": len(compressed),
                "compression_ratio": round(len(image_bytes) / len(compressed), 2) if compressed else 1,
                "filename": filename,
                "result": result,
                "created_at": datetime.now(timezone.utc),
                "used_for_training": False
            }
            
            # Insert into biometric_data collection
            collection = Database.get_collection("biometric_data")
            await collection.insert_one(biometric_doc)
            
            logger.info(f"Saved biometric data: {doc_id} ({service_type}, {len(image_bytes)} -> {len(compressed)} bytes)")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to save biometric data: {e}")
            return None


# Singleton instance
storage_service = StorageService()

