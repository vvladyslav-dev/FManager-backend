from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.models import File
from app.domain.repositories.file_repository import IFileRepository


class FileRepository(IFileRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, file: File) -> File:
        self.session.add(file)
        await self.session.flush()
        await self.session.refresh(file)
        return file
    
    async def get_by_id(self, file_id):
        result = await self.session.execute(
            select(File).where(File.id == file_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_submission_id(self, submission_id):
        result = await self.session.execute(
            select(File).where(File.submission_id == submission_id)
        )
        return list(result.scalars().all())

