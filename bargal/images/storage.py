import os
from pathlib import Path


class ImageFileStore:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)

        # Ensure the directory exists or create it
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise RuntimeError(f"Cannot create or access directory {storage_path}: {e}")

        # Verify it's a directory and we have read/write access
        if not self.storage_path.is_dir():
            raise NotADirectoryError(f"{storage_path} is not a directory")
        if not os.access(self.storage_path, os.R_OK | os.W_OK):
            raise PermissionError(f"Insufficient permissions for directory {storage_path}")

    def save_image(self, image_name: str, image_data: bytes) -> None:
        file_path = self.storage_path / image_name
        with open(file_path, "wb") as image_file:
            image_file.write(image_data)

    def load_image(self, image_name: str) -> bytes:
        file_path = self.storage_path / image_name
        with open(file_path, "rb") as image_file:
            return image_file.read()

    def has_image(self, image_name: str) -> bool:
        file_path = self.storage_path / image_name
        return file_path.is_file()
