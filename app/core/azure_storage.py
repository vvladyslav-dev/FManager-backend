from azure.storage.blob.aio import BlobServiceClient
from app.core.config import settings


class AzureBlobStorageClient:
    def __init__(self):
        self.connection_string = settings.azure_storage_connection_string
        self.container_name = settings.azure_storage_container_name
        self._blob_service_client = None
        self._container_client = None
    
    @property
    async def blob_service_client(self):
        if self._blob_service_client is None:
            self._blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
        return self._blob_service_client
    
    @property
    async def container_client(self):
        if self._container_client is None:
            service_client = await self.blob_service_client
            self._container_client = service_client.get_container_client(
                self.container_name
            )
        return self._container_client
    
    async def upload_file(self, file_content: bytes, blob_name: str) -> str:
        """Upload file to Azure Blob Storage and return blob URL"""
        container = await self.container_client
        blob_client = container.get_blob_client(blob_name)
        await blob_client.upload_blob(file_content, overwrite=True)
        return blob_client.url
    
    async def delete_file(self, blob_name: str) -> None:
        """Delete file from Azure Blob Storage"""
        container = await self.container_client
        blob_client = container.get_blob_client(blob_name)
        await blob_client.delete_blob()
    
    async def get_file_url(self, blob_name: str) -> str:
        """Get URL for a blob"""
        container = await self.container_client
        blob_client = container.get_blob_client(blob_name)
        return blob_client.url
    
    async def download_file(self, blob_name: str) -> bytes:
        """Download file content from Azure Blob Storage"""
        container = await self.container_client
        blob_client = container.get_blob_client(blob_name)
        download_stream = await blob_client.download_blob()
        return await download_stream.readall()
    
    async def close(self):
        """Close connections"""
        if self._container_client:
            await self._container_client.close()
        if self._blob_service_client:
            await self._blob_service_client.close()


# Global instance
azure_storage_client = AzureBlobStorageClient()

