from typing import Optional
import json
import os
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Записаться на консультацию", callback_data="book_appointment"),
        InlineKeyboardButton(text="💰 Услуги и цены", callback_data="services")
    )
    builder.row(
        InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_question"),
        InlineKeyboardButton(text="📍 Адрес и контакты", callback_data="contacts")
    )
    
    return builder.as_markup()


def get_services_keyboard() -> InlineKeyboardMarkup:
    """Create services keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu"))
    return builder.as_markup()


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Create confirmation keyboard for appointment."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_appointment"),
        InlineKeyboardButton(text="✏️ Изменить", callback_data="edit_appointment"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_appointment")
    )
    
    return builder.as_markup()


def get_admin_keyboard(appointment_id: int, username: Optional[str] = None) -> InlineKeyboardMarkup:
    """Create admin keyboard for appointment management."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_{appointment_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_simple_{appointment_id}")
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Написать причину отказа", callback_data=f"admin_reject_reason_{appointment_id}")
    )
    
    if username:
        builder.row(
            InlineKeyboardButton(text="📞 Позвонить пациенту", url=f"https://t.me/{username}")
        )
    
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Create back to main menu keyboard."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu"))
    return builder.as_markup()


def get_reschedule_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for rescheduling appointment."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📅 Выбрать другое время", callback_data="book_appointment"))
    return builder.as_markup()


def get_main_menu_button_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with main menu button."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🏠 Вернуться в главное меню", callback_data="main_menu"))
    return builder.as_markup()


def get_services_selection_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with services from clinic.json for selection."""
    builder = InlineKeyboardBuilder()
    
    # Get the path to clinic.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    clinic_path = os.path.join(current_dir, '..', 'data', 'clinic.json')
    
    try:
        with open(clinic_path, 'r', encoding='utf-8') as f:
            clinic_data = json.load(f)
        
        services = clinic_data.get('services', [])
        
        for i, service in enumerate(services):
            service_name = service.get('name', '')
            builder.add(
                InlineKeyboardButton(text=service_name, callback_data=f"select_service:{i}")
            )
        
        # Add back button
        builder.row(
            InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")
        )
    except Exception as e:
        # Fallback if clinic.json can't be read
        builder.add(
            InlineKeyboardButton(text="🔙 В главное меню", callback_data="main_menu")
        )
    
    return builder.as_markup()
