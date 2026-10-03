from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..errors import conflict, not_found
from ..models import Reader
from ..schemas import IssueBookRequest, ReaderCreate, ReaderResponse, ReaderUpdate

router = APIRouter(prefix="/readers", tags=["readers"])


async def locked_reader(reader_id: int, session: AsyncSession) -> Reader:
    reader = await session.scalar(select(Reader).where(Reader.id == reader_id).with_for_update())
    if reader is None:
        raise not_found()
    return reader


@router.post("", response_model=ReaderResponse, status_code=status.HTTP_201_CREATED)
async def create_reader(payload: ReaderCreate, session: AsyncSession = Depends(get_session)) -> Reader:
    reader = Reader(**payload.model_dump())
    session.add(reader)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise conflict("card_number is already in use") from None
    await session.refresh(reader)
    return reader


@router.get("", response_model=list[ReaderResponse])
async def list_readers(session: AsyncSession = Depends(get_session)) -> list[Reader]:
    result = await session.scalars(select(Reader).order_by(Reader.id))
    return list(result)


@router.get("/{reader_id}", response_model=ReaderResponse)
async def get_reader(reader_id: int, session: AsyncSession = Depends(get_session)) -> Reader:
    reader = await session.get(Reader, reader_id)
    if reader is None:
        raise not_found()
    return reader


@router.patch("/{reader_id}", response_model=ReaderResponse)
async def update_reader(
    payload: ReaderUpdate,
    reader_id: int = Path(ge=1),
    session: AsyncSession = Depends(get_session),
) -> Reader:
    reader = await locked_reader(reader_id, session)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(reader, key, value)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise conflict("card_number is already in use") from None
    await session.refresh(reader)
    return reader


@router.delete("/{reader_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reader(reader_id: int, session: AsyncSession = Depends(get_session)) -> Response:
    reader = await locked_reader(reader_id, session)
    if reader.book_title is not None:
        await session.rollback()
        raise conflict("reader must return the outstanding book before deletion")
    await session.delete(reader)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{reader_id}/revoke-card", response_model=ReaderResponse)
async def revoke_card(reader_id: int, session: AsyncSession = Depends(get_session)) -> Reader:
    reader = await locked_reader(reader_id, session)
    if reader.book_title is not None:
        await session.rollback()
        raise conflict("card cannot be revoked while a book is outstanding")
    reader.card_active = False
    await session.commit()
    await session.refresh(reader)
    return reader


@router.post("/{reader_id}/issue-book", response_model=ReaderResponse)
async def issue_book(
    payload: IssueBookRequest,
    reader_id: int,
    session: AsyncSession = Depends(get_session),
) -> Reader:
    reader = await locked_reader(reader_id, session)
    if not reader.card_active:
        await session.rollback()
        raise conflict("book cannot be issued to an inactive card")
    if reader.book_title is not None:
        await session.rollback()
        raise conflict("reader already has an outstanding book")
    reader.book_title = payload.book_title
    await session.commit()
    await session.refresh(reader)
    return reader


@router.post("/{reader_id}/return-book", response_model=ReaderResponse)
async def return_book(reader_id: int, session: AsyncSession = Depends(get_session)) -> Reader:
    reader = await locked_reader(reader_id, session)
    if reader.book_title is None:
        await session.rollback()
        raise conflict("reader has no outstanding book")
    reader.book_title = None
    await session.commit()
    await session.refresh(reader)
    return reader
