from aiogram import Router
from aiogram.types import CallbackQuery, Message


router = Router()


@router.message()
async def handle_message(message: Message) -> None:
    await message.answer("Сообщение получено.")


@router.callback_query()
async def handle_callback_query(callback_query: CallbackQuery) -> None:
    await callback_query.answer()
