from aiogram.fsm.state import State, StatesGroup


class AppointmentStates(StatesGroup):
    service = State()
    date = State()
    time = State()
    name = State()
    phone = State()
    comment = State()
    confirmation = State()


class QuestionStates(StatesGroup):
    waiting_for_question = State()


class AdminStates(StatesGroup):
    waiting_for_rejection_reason = State()
