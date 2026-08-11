import json
import logging
from typing import Optional
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.config import config
from app.states import AppointmentStates, QuestionStates, AdminStates
from app.keyboards import (
    get_main_menu_keyboard,
    get_services_keyboard,
    get_confirmation_keyboard,
    get_admin_keyboard,
    get_back_keyboard,
    get_reschedule_keyboard,
    get_main_menu_button_keyboard,
    get_services_selection_keyboard
)
from app.database import init_db, create_appointment, get_appointment, update_appointment_status, update_appointment_with_rejection
from app.groq_client import groq_client
from app.validators import is_valid_name, is_valid_phone, is_valid_date, is_valid_time, is_valid_text_length

router = Router()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.message(F.text == "/start")
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "👋 Здравствуйте! Добро пожаловать в DentAssist Demo Clinic!\n\n"
        "Я помогу вам:\n"
        "🦷 узнать об услугах и ценах\n"
        "❓ ответить на вопросы о лечении\n"
        "📅 записаться на консультацию\n\n"
        "Выберите, что вас интересует 👇",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery) -> None:
    """Handle main menu callback."""
    await callback.message.edit_text(
        "🦷 DentAssist - Главное меню\n\nВыберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "services")
async def callback_services(callback: CallbackQuery) -> None:
    """Handle services callback."""
    try:
        with open(config.CLINIC_DATA_PATH, "r", encoding="utf-8") as f:
            clinic_data = json.load(f)
        
        services_text = "💰 Услуги и цены:\n\n"
        for service in clinic_data.get("services", []):
            services_text += f"• {service['name']} — {service['price']}\n"
        
        if clinic_data.get("note"):
            services_text += f"\n{clinic_data['note']}"
        
        await callback.message.edit_text(
            services_text,
            reply_markup=get_services_keyboard()
        )
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Error loading services: {e}")
        await callback.message.edit_text(
            "Ошибка загрузки услуг. Попробуйте позже.",
            reply_markup=get_back_keyboard()
        )
        await callback.answer()


@router.callback_query(F.data == "contacts")
async def callback_contacts(callback: CallbackQuery) -> None:
    """Handle contacts callback."""
    try:
        with open(config.CLINIC_DATA_PATH, "r", encoding="utf-8") as f:
            clinic_data = json.load(f)
        
        contacts_text = (
            f"📍 {clinic_data.get('name', 'DentAssist Clinic')}\n\n"
            f"🏠 Адрес: {clinic_data.get('address', 'Не указан')}\n"
            f"📞 Телефон: {clinic_data.get('phone', 'Не указан')}\n"
            f"🕐 Время работы: {clinic_data.get('working_hours', 'Не указано')}"
        )
        
        await callback.message.edit_text(
            contacts_text,
            reply_markup=get_back_keyboard()
        )
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Error loading contacts: {e}")
        await callback.message.edit_text(
            "Ошибка загрузки контактов. Попробуйте позже.",
            reply_markup=get_back_keyboard()
        )
        await callback.answer()


@router.callback_query(F.data == "book_appointment")
async def callback_book_appointment(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle book appointment callback."""
    await state.clear()
    await state.set_state(AppointmentStates.service)
    
    await callback.message.edit_text(
        "📅 Запись на консультацию\n\n"
        "Выберите услугу:",
        reply_markup=get_services_selection_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("select_service:"))
async def callback_select_service(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle service selection callback."""
    import json
    import os
    
    # Get the path to clinic.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    clinic_path = os.path.join(current_dir, '..', 'data', 'clinic.json')
    
    try:
        with open(clinic_path, 'r', encoding='utf-8') as f:
            clinic_data = json.load(f)
        
        services = clinic_data.get('services', [])
        service_index = int(callback.data.split(":")[-1])
        
        if 0 <= service_index < len(services):
            service_name = services[service_index].get('name', '')
            
            await state.update_data(service=service_name)
            await state.set_state(AppointmentStates.date)
            
            await callback.message.edit_text(
                f"✅ Выбрана услуга: {service_name}\n\n"
                "Введите желаемую дату (например: 15.08.2026):"
            )
        else:
            await callback.answer("❌ Ошибка выбора услуги")
            return
    except Exception as e:
        logger.error(f"Error selecting service: {e}")
        await callback.answer("❌ Ошибка загрузки услуг")
        return
    
    await callback.answer()


@router.message(AppointmentStates.date)
async def process_date(message: Message, state: FSMContext) -> None:
    """Process date input."""
    if not is_valid_date(message.text):
        await message.answer(
            "⚠️ Введите дату в формате ДД.ММ.ГГГГ, например 20.08.2026"
        )
        return
    
    await state.update_data(preferred_date=message.text)
    await state.set_state(AppointmentStates.time)
    
    await message.answer(
        "Введите желаемое время (например: 14:00):"
    )


@router.message(AppointmentStates.time)
async def process_time(message: Message, state: FSMContext) -> None:
    """Process time input."""
    if not is_valid_time(message.text):
        await message.answer(
            "⚠️ Введите время в формате ЧЧ:ММ, например 14:30, в рабочие часы клиники (09:00–20:00)"
        )
        return
    
    await state.update_data(preferred_time=message.text)
    await state.set_state(AppointmentStates.name)
    
    await message.answer(
        "Введите ваше имя:"
    )


@router.message(AppointmentStates.name)
async def process_name(message: Message, state: FSMContext) -> None:
    """Process name input."""
    if not is_valid_name(message.text):
        await message.answer(
            "⚠️ Похоже, вы ввели не имя. Пожалуйста, введите имя и фамилию текстом."
        )
        return
    
    await state.update_data(patient_name=message.text)
    await state.set_state(AppointmentStates.phone)
    
    await message.answer(
        "Введите ваш номер телефона:"
    )


@router.message(AppointmentStates.phone)
async def process_phone(message: Message, state: FSMContext) -> None:
    """Process phone input."""
    if not is_valid_phone(message.text):
        await message.answer(
            "⚠️ Неверный формат номера. Введите номер в формате +998901234567"
        )
        return
    
    await state.update_data(phone=message.text)
    await state.set_state(AppointmentStates.comment)
    
    await message.answer(
        "Добавьте комментарий (необязательно) или отправьте /skip для продолжения:"
    )


@router.message(AppointmentStates.comment, F.text == "/skip")
async def process_skip_comment(message: Message, state: FSMContext) -> None:
    """Skip comment input."""
    await state.update_data(comment="")
    await show_confirmation(message, state)


@router.message(AppointmentStates.comment)
async def process_comment(message: Message, state: FSMContext) -> None:
    """Process comment input."""
    await state.update_data(comment=message.text)
    await show_confirmation(message, state)


async def show_confirmation(message: Message, state: FSMContext) -> None:
    """Show appointment confirmation."""
    data = await state.get_data()
    
    confirmation_text = (
        "📋 Проверьте заявку:\n\n"
        f"Услуга: {data.get('service', 'Не указано')}\n"
        f"Дата: {data.get('preferred_date', 'Не указано')}\n"
        f"Время: {data.get('preferred_time', 'Не указано')}\n"
        f"Имя: {data.get('patient_name', 'Не указано')}\n"
        f"Телефон: {data.get('phone', 'Не указано')}\n"
        f"Комментарий: {data.get('comment', 'Нет') or 'Нет'}"
    )
    
    await state.set_state(AppointmentStates.confirmation)
    await message.answer(
        confirmation_text,
        reply_markup=get_confirmation_keyboard()
    )


@router.callback_query(F.data == "edit_appointment")
async def callback_edit_appointment(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle edit appointment callback."""
    await state.set_state(AppointmentStates.service)
    await callback.message.edit_text(
        "📅 Редактирование заявки\n\n"
        "Какую услугу вы хотите?",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "cancel_appointment")
async def callback_cancel_appointment(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle cancel appointment callback."""
    await state.clear()
    await callback.message.edit_text(
        "❌ Заявка отменена.",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_appointment")
async def callback_confirm_appointment(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle confirm appointment callback."""
    data = await state.get_data()
    
    appointment_data = {
        "telegram_user_id": callback.from_user.id,
        "username": callback.from_user.username,
        **data
    }
    
    try:
        appointment_id = create_appointment(appointment_data)
        await state.clear()
        
        await send_admin_notification(appointment_id, appointment_data)
        
        await callback.message.edit_text(
            "✅ Заявка успешно отправлена!\n\n"
            "Мы свяжемся с вами для подтверждения записи.",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
    
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при отправке заявки. Попробуйте позже.",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()


async def send_admin_notification(appointment_id: int, data: dict) -> None:
    """Send notification to admin."""
    from aiogram import Bot
    
    bot = Bot(token=config.BOT_TOKEN)
    
    admin_text = (
        f"🦷 Новая заявка DentAssist\n\n"
        f"Имя: {data.get('patient_name')}\n"
        f"Телефон: {data.get('phone')}\n"
        f"Услуга: {data.get('service')}\n"
        f"Дата: {data.get('preferred_date')}\n"
        f"Время: {data.get('preferred_time')}\n"
        f"Комментарий: {data.get('comment') or 'Нет'}\n"
        f"Telegram ID: {data.get('telegram_user_id')}\n"
        f"Username: @{data.get('username') or 'Не указан'}\n\n"
        f"Статус: новая заявка"
    )
    
    try:
        await bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=admin_text,
            reply_markup=get_admin_keyboard(appointment_id, data.get('username'))
        )
    except Exception as e:
        logger.error(f"Error sending admin notification: {e}")
    
    await bot.session.close()


@router.callback_query(F.data.startswith("admin_confirm_"))
async def callback_admin_confirm(callback: CallbackQuery) -> None:
    """Handle admin confirm callback."""
    appointment_id = int(callback.data.split("_")[-1])
    
    if update_appointment_status(appointment_id, "confirmed"):
        await callback.answer("✅ Заявка подтверждена")
        await callback.message.edit_reply_markup(reply_markup=None)
    else:
        await callback.answer("❌ Ошибка подтверждения")


@router.callback_query(F.data.startswith("admin_reject_simple_"))
async def callback_admin_reject(callback: CallbackQuery) -> None:
    """Handle admin reject callback."""
    appointment_id = int(callback.data.split("_")[-1])
    
    if update_appointment_status(appointment_id, "rejected"):
        await callback.answer("❌ Заявка отклонена")
        
        # Get appointment details to notify patient
        appointment = get_appointment(appointment_id)
        
        if appointment:
            from aiogram import Bot
            bot = Bot(token=config.BOT_TOKEN)
            
            try:
                await bot.send_message(
                    chat_id=appointment["telegram_user_id"],
                    text="😔 К сожалению, выбранное время занято.\nПожалуйста, выберите другое время для записи.",
                    reply_markup=get_reschedule_keyboard()
                )
                logger.info(f"Patient {appointment['telegram_user_id']} notified about rejection")
            except Exception as e:
                logger.error(f"Error sending rejection notification to patient {appointment['telegram_user_id']}: {e}")
            
            await bot.session.close()
        
        await callback.message.edit_text(
            "❌ Заявка отклонена, клиент уведомлён"
        )
    else:
        await callback.answer("❌ Ошибка отклонения")


@router.callback_query(F.data.startswith("admin_reject_reason_"))
async def callback_admin_reject_reason(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle admin reject with reason callback."""
    appointment_id = int(callback.data.split("_")[-1])
    
    await state.set_state(AdminStates.waiting_for_rejection_reason)
    await state.update_data(appointment_id=appointment_id)
    
    await callback.message.answer(
        f"Напишите причину отказа для заявки #{appointment_id}, она будет отправлена клиенту:"
    )
    await callback.answer()


@router.message(AdminStates.waiting_for_rejection_reason)
async def process_admin_rejection_reason(message: Message, state: FSMContext) -> None:
    """Process admin's rejection reason input."""
    data = await state.get_data()
    appointment_id = data.get("appointment_id")
    rejection_reason = message.text
    
    if not appointment_id:
        await message.answer("❌ Ошибка: не найден ID заявки")
        await state.clear()
        return
    
    # Update appointment with rejection reason
    if update_appointment_with_rejection(appointment_id, "rejected", rejection_reason):
        # Get appointment details to notify patient
        appointment = get_appointment(appointment_id)
        
        if appointment:
            from aiogram import Bot
            bot = Bot(token=config.BOT_TOKEN)
            
            try:
                await bot.send_message(
                    chat_id=appointment["telegram_user_id"],
                    text=f"😔 К сожалению, ваша заявка отклонена.\nПричина: {rejection_reason}\n\nПожалуйста, выберите другое время или услугу для записи.",
                    reply_markup=get_reschedule_keyboard()
                )
                logger.info(f"Patient {appointment['telegram_user_id']} notified about rejection with reason")
            except Exception as e:
                logger.error(f"Error sending rejection notification to patient {appointment['telegram_user_id']}: {e}")
            
            await bot.session.close()
        
        await message.answer(f"✅ Заявка #{appointment_id} отклонена. Причина отправлена клиенту.")
    else:
        await message.answer("❌ Ошибка отклонения заявки")
    
    await state.clear()


@router.callback_query(F.data == "ask_question")
async def callback_ask_question(callback: CallbackQuery, state: FSMContext) -> None:
    """Handle ask question callback."""
    await state.set_state(QuestionStates.waiting_for_question)
    
    await callback.message.edit_text(
        "❓ Задайте вопрос о клинике, услугах или записи.\n\n"
        "Я отвечу на основе данных клиники.",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@router.message(QuestionStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext) -> None:
    """Process user question."""
    user_question = message.text
    
    await message.answer("🤔 Думаю...")
    
    try:
        answer = await groq_client.ask_question(user_question)
        await message.answer(answer, reply_markup=get_back_keyboard())
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, запишитесь на консультацию.",
            reply_markup=get_back_keyboard()
        )
    
    await state.clear()


@router.message(F.text == "/cancel")
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    """Handle /cancel command."""
    await state.clear()
    await message.answer(
        "❌ Действие отменено.\n\n",
        reply_markup=get_main_menu_keyboard()
    )
