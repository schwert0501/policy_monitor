import os
import uuid
from datetime import datetime
from minio import Minio
from minio.error import S3Error
from werkzeug.utils import secure_filename
from flask import current_app

class StorageManager:
    """
    Storage manager that can use either local file system or MinIO for file storage
    """
    
    def __init__(self, app=None):
        self.app = app
        self.storage_type = None
        self.minio_client = None
        self.upload_folder = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.storage_type = app.config.get('STORAGE_TYPE', 'local')
        self.upload_folder = app.config.get('UPLOAD_FOLDER')
        
        # Ensure upload folder exists if using local storage
        if self.storage_type == 'local' and not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder, exist_ok=True)
        
        # Initialize MinIO client if using MinIO
        if self.storage_type == 'minio':
            self.minio_client = Minio(
                app.config.get('MINIO_ENDPOINT'),
                access_key=app.config.get('MINIO_ACCESS_KEY'),
                secret_key=app.config.get('MINIO_SECRET_KEY'),
                secure=app.config.get('MINIO_SECURE', False)
            )
            
            # Create bucket if it doesn't exist
            bucket_name = app.config.get('MINIO_BUCKET')
            try:
                if not self.minio_client.bucket_exists(bucket_name):
                    self.minio_client.make_bucket(bucket_name)
            except S3Error as e:
                app.logger.error(f"Error initializing MinIO: {e}")
    
    def _generate_unique_filename(self, filename):
        """Generate a unique filename to prevent overwriting"""
        ext = os.path.splitext(filename)[1]
        date_prefix = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())
        return f"{date_prefix}_{unique_id}{ext}"
    
    def save_file(self, file, folder=''):
        """
        Save a file to the configured storage system
        
        Args:
            file: The file object to save
            folder: Optional subfolder within the storage
            
        Returns:
            str: The file path or URL
        """
        if not file:
            return None
            
        filename = secure_filename(file.filename)
        unique_filename = self._generate_unique_filename(filename)
        
        if folder:
            unique_filename = f"{folder}/{unique_filename}"
        
        if self.storage_type == 'local':
            # Save to local file system
            file_path = os.path.join(self.upload_folder, unique_filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)
            return unique_filename
        
        elif self.storage_type == 'minio':
            # Save to MinIO
            bucket_name = current_app.config.get('MINIO_BUCKET')
            content_type = file.content_type or 'application/octet-stream'
            
            try:
                file.seek(0)
                self.minio_client.put_object(
                    bucket_name,
                    unique_filename,
                    file,
                    length=file.content_length if hasattr(file, 'content_length') else -1,
                    content_type=content_type
                )
                return unique_filename
            except S3Error as e:
                current_app.logger.error(f"Error saving to MinIO: {e}")
                return None
        
        return None
    
    def get_file_url(self, file_path):
        """
        Get the URL or path for a stored file
        
        Args:
            file_path: The stored file path
            
        Returns:
            str: The URL or path to access the file
        """
        if not file_path:
            return None
            
        if self.storage_type == 'local':
            return f"/uploads/{file_path}"
        
        elif self.storage_type == 'minio':
            bucket_name = current_app.config.get('MINIO_BUCKET')
            try:
                # Generate a presigned URL that's valid for 1 hour
                return self.minio_client.presigned_get_object(
                    bucket_name, file_path, expires=3600
                )
            except S3Error as e:
                current_app.logger.error(f"Error generating presigned URL: {e}")
                return None
        
        return None
    
    def delete_file(self, file_path):
        """
        Delete a file from storage
        
        Args:
            file_path: The stored file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not file_path:
            return False
            
        if self.storage_type == 'local':
            full_path = os.path.join(self.upload_folder, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        
        elif self.storage_type == 'minio':
            bucket_name = current_app.config.get('MINIO_BUCKET')
            try:
                self.minio_client.remove_object(bucket_name, file_path)
                return True
            except S3Error as e:
                current_app.logger.error(f"Error deleting from MinIO: {e}")
                return False
        
        return False

# Create a singleton instance
storage = StorageManager() 