import asyncio
import logging
from aiogram import Bot, Dispatcher, F, html
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiogram.client.default import DefaultBotProperties

from state import Friend, Work, Employee, Teacher, Student
from db import init_db, save_application
from config import TOKEN, ADMIN_ID, GROUP_ID

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


def show_username(u) -> str:
    return f"@{u.username}" if getattr(u, "username", None) else f"id:{u.id}"


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    btn = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Sherik kerak"), KeyboardButton(text="Ish joyi kerak")],
            [KeyboardButton(text="Hodim kerak"), KeyboardButton(text="Ustoz kerak")],
            [KeyboardButton(text="Shogirt kerak")],
        ],
        resize_keyboard=True,
    )
    await message.answer(
        f"""
Assalomu alaykum, {html.bold(message.from_user.full_name)}!
UstozShogird kanalining botiga xush kelibsiz!
/help yordam buyrugi orqali nimalarga qodir ekanligimni bilib oling!
""",
        reply_markup=btn,
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        """
Bu yerda Programmalash bo`yicha   
  #Ustoz,  
  #Shogird,
  #OquvKursi,
  #Sherik,  
  #Xodim  
  #IshJoyi 
topishingiz mumkin."""
    )


async def start_form(message: Message, state: FSMContext, form, category: str):
    await state.set_state(form.name)
    await state.update_data(category=category, user_id=message.from_user.id, username=show_username(message.from_user))
    await message.answer("Ism, familiyangizni kiriting?")


async def form_handler(message: Message, state: FSMContext, form, field, next_field, question: str):
    await state.update_data(**{field: message.text})
    await state.set_state(getattr(form, next_field))
    await message.answer(question)


async def finish_form(message: Message, state: FSMContext, form, category: str):
    await state.update_data(purpose=message.text)
    data = await state.get_data()

    text = f"""
📥 Sizning so‘rovingiz: {category.title()}

👤 Foydalanuvchi: {data['username']}
🏅 Ismi: {data['name']}
📚 Texnologiya: {data['technology']}
📞 Aloqa: {data['phone_number']}
🌐 Hudud: {data['region']}
💰 Narxi: {data['cost']}
👨 Kasbi: {data['work_or_study']}
🕰 Vaqti: {data['time']}
🔎 Maqsad: {data['purpose']}
"""

    btn = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Ha ✅", callback_data=f"user_confirm_{category}"),
            InlineKeyboardButton(text="Yo‘q ❌", callback_data=f"user_reject_{category}")
        ]]
    )

    await message.answer("Quyidagi ma’lumotlaringizni yubormoqchimisiz?\n" + text, reply_markup=btn)
    await state.update_data(preview_text=text)
    await state.set_state(None)


@dp.callback_query(F.data.startswith("user_confirm_"))
async def user_confirm(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_", 2)[2]
    data = await state.get_data()
    text = data.get("preview_text")

    btn = InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(text="Ha ✅", callback_data=f"approve_{category}"),
            InlineKeyboardButton(text="Yo‘q ❌", callback_data=f"reject_{category}")
        ]]
    )

    bot: Bot = callback.bot
    await bot.send_message(ADMIN_ID, text, reply_markup=btn)
    await callback.message.answer("So‘rovingiz adminga yuborildi, tasdiqlash kutilmoqda ✅")
    await callback.message.delete()
    await state.update_data(text=text)


@dp.callback_query(F.data.startswith("user_reject_"))
async def user_reject(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("So‘rovingiz bekor qilindi ❌")
    await state.clear()


@dp.callback_query(F.data.startswith("approve_"))
async def approve_request(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_", 1)[1]
    text = callback.message.text

    bot: Bot = callback.bot
    try:
        await bot.send_message(GROUP_ID, text)
        save_application(
            user_id=str(callback.from_user.id),
            username=show_username(callback.from_user),
            category=category,
            data={"text": text}
        )
        await callback.message.edit_reply_markup()
        await callback.message.answer("So‘rov tasdiqlandi va guruhga yuborildi ✅")
    except Exception as e:
        logging.error(f"Guruhga yuborilmadi: {e}")


@dp.callback_query(F.data.startswith("reject_"))
async def reject_request(callback: CallbackQuery):
    await callback.message.edit_reply_markup()
    await callback.message.answer("So‘rov rad etildi ❌")

# -------- FRIEND --------
@dp.message(F.text == "Sherik kerak")
async def state_friend(message: Message, state: FSMContext):
    await start_form(message, state, Friend, "friend")


@dp.message(Friend.name)
async def friend_name(message: Message, state: FSMContext):
    await form_handler(message, state, Friend, "name", "technology", "Qaysi texnologiyalarni bilasiz?")


@dp.message(Friend.technology)
async def friend_tech(message: Message, state: FSMContext):
    await form_handler(message, state, Friend, "technology", "phone_number", "Telefon raqamingizni kiriting:")


@dp.message(Friend.phone_number)
async def friend_phone(message: Message, state: FSMContext):
    await form_handler(message, state, Friend, "phone_number", "region", "Qaysi hududdansiz?")


@dp.message(Friend.region)
async def friend_region(message: Message, state: FSMContext):
    await form_handler(message, state, Friend, "region", "cost", "Narxi (tekin yoki summa)?")


@dp.message(Friend.cost)
async def friend_cost(message: Message, state: FSMContext):
    await form_handler(message, state, Friend, "cost", "work_or_study", "Kasbi (ishlaydi yoki o‘qiydi)?")


@dp.message(Friend.work_or_study)
async def friend_work(message: Message, state: FSMContext):
    await form_handler(message, state, Friend, "work_or_study", "time", "Qachon murojaat qilish mumkin?")


@dp.message(Friend.time)
async def friend_time(message: Message, state: FSMContext):
    await form_handler(message, state, Friend, "time", "purpose", "Maqsadingiz?")


@dp.message(Friend.purpose)
async def friend_purpose(message: Message, state: FSMContext):
    await finish_form(message, state, Friend, "friend")


# -------- WORK --------
@dp.message(F.text == "Ish joyi kerak")
async def state_work(message: Message, state: FSMContext):
    await start_form(message, state, Work, "work")


@dp.message(Work.name)
async def work_name(message: Message, state: FSMContext):
    await form_handler(message, state, Work, "name", "technology", "Qaysi texnologiyalarni bilasiz?")


@dp.message(Work.technology)
async def work_tech(message: Message, state: FSMContext):
    await form_handler(message, state, Work, "technology", "phone_number", "Telefon raqamingizni kiriting:")


@dp.message(Work.phone_number)
async def work_phone(message: Message, state: FSMContext):
    await form_handler(message, state, Work, "phone_number", "region", "Qaysi hududdansiz?")


@dp.message(Work.region)
async def work_region(message: Message, state: FSMContext):
    await form_handler(message, state, Work, "region", "cost", "Narxi (o‘rtacha oylik maosh)?")


@dp.message(Work.cost)
async def work_cost(message: Message, state: FSMContext):
    await form_handler(message, state, Work, "cost", "work_or_study", "Kasbi?")


@dp.message(Work.work_or_study)
async def work_job(message: Message, state: FSMContext):
    await form_handler(message, state, Work, "work_or_study", "time", "Qachon murojaat qilish mumkin?")


@dp.message(Work.time)
async def work_time(message: Message, state: FSMContext):
    await form_handler(message, state, Work, "time", "purpose", "Maqsadingiz?")


@dp.message(Work.purpose)
async def work_purpose(message: Message, state: FSMContext):
    await finish_form(message, state, Work, "work")


# -------- EMPLOYEE --------
@dp.message(F.text == "Hodim kerak")
async def state_employee(message: Message, state: FSMContext):
    await start_form(message, state, Employee, "employee")


@dp.message(Employee.name)
async def employee_name(message: Message, state: FSMContext):
    await form_handler(message, state, Employee, "name", "technology", "Qaysi texnologiyalarni bilishi kerak?")


@dp.message(Employee.technology)
async def employee_tech(message: Message, state: FSMContext):
    await form_handler(message, state, Employee, "technology", "phone_number", "Telefon raqam:")


@dp.message(Employee.phone_number)
async def employee_phone(message: Message, state: FSMContext):
    await form_handler(message, state, Employee, "phone_number", "region", "Hudud?")


@dp.message(Employee.region)
async def employee_region(message: Message, state: FSMContext):
    await form_handler(message, state, Employee, "region", "cost", "Maosh:")


@dp.message(Employee.cost)
async def employee_cost(message: Message, state: FSMContext):
    await form_handler(message, state, Employee, "cost", "work_or_study", "Lavozimi?")


@dp.message(Employee.work_or_study)
async def employee_job(message: Message, state: FSMContext):
    await form_handler(message, state, Employee, "work_or_study", "time", "Qachon murojaat qilish mumkin?")


@dp.message(Employee.time)
async def employee_time(message: Message, state: FSMContext):
    await form_handler(message, state, Employee, "time", "purpose", "Maqsad:")


@dp.message(Employee.purpose)
async def employee_purpose(message: Message, state: FSMContext):
    await finish_form(message, state, Employee, "employee")


# -------- TEACHER --------
@dp.message(F.text == "Ustoz kerak")
async def state_teacher(message: Message, state: FSMContext):
    await start_form(message, state, Teacher, "teacher")


@dp.message(Teacher.name)
async def teacher_name(message: Message, state: FSMContext):
    await form_handler(message, state, Teacher, "name", "technology", "Qaysi texnologiyalarni o‘rgatadi?")


@dp.message(Teacher.technology)
async def teacher_tech(message: Message, state: FSMContext):
    await form_handler(message, state, Teacher, "technology", "phone_number", "Telefon raqam:")


@dp.message(Teacher.phone_number)
async def teacher_phone(message: Message, state: FSMContext):
    await form_handler(message, state, Teacher, "phone_number", "region", "Hudud?")


@dp.message(Teacher.region)
async def teacher_region(message: Message, state: FSMContext):
    await form_handler(message, state, Teacher, "region", "cost", "Narxi (kurs uchun)?")


@dp.message(Teacher.cost)
async def teacher_cost(message: Message, state: FSMContext):
    await form_handler(message, state, Teacher, "cost", "work_or_study", "Kasbi?")


@dp.message(Teacher.work_or_study)
async def teacher_job(message: Message, state: FSMContext):
    await form_handler(message, state, Teacher, "work_or_study", "time", "Qachon murojaat qilish mumkin?")


@dp.message(Teacher.time)
async def teacher_time(message: Message, state: FSMContext):
    await form_handler(message, state, Teacher, "time", "purpose", "Maqsad:")


@dp.message(Teacher.purpose)
async def teacher_purpose(message: Message, state: FSMContext):
    await finish_form(message, state, Teacher, "teacher")


# -------- STUDENT --------
@dp.message(F.text == "Shogirt kerak")
async def state_student(message: Message, state: FSMContext):
    await start_form(message, state, Student, "student")


@dp.message(Student.name)
async def student_name(message: Message, state: FSMContext):
    await form_handler(message, state, Student, "name", "technology", "Qaysi texnologiyalarni o‘rganmoqchi?")


@dp.message(Student.technology)
async def student_tech(message: Message, state: FSMContext):
    await form_handler(message, state, Student, "technology", "phone_number", "Telefon raqam:")


@dp.message(Student.phone_number)
async def student_phone(message: Message, state: FSMContext):
    await form_handler(message, state, Student, "phone_number", "region", "Hudud?")


@dp.message(Student.region)
async def student_region(message: Message, state: FSMContext):
    await form_handler(message, state, Student, "region", "cost", "Narxi (agar to‘lov qilsa)?")


@dp.message(Student.cost)
async def student_cost(message: Message, state: FSMContext):
    await form_handler(message, state, Student, "cost", "work_or_study", "Kasbi yoki o‘qishi?")


@dp.message(Student.work_or_study)
async def student_job(message: Message, state: FSMContext):
    await form_handler(message, state, Student, "work_or_study", "time", "Qachon murojaat qilish mumkin?")


@dp.message(Student.time)
async def student_time(message: Message, state: FSMContext):
    await form_handler(message, state, Student, "time", "purpose", "Maqsad:")


@dp.message(Student.purpose)
async def student_purpose(message: Message, state: FSMContext):
    await finish_form(message, state, Student, "student")

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
