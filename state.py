from aiogram.fsm.state import StatesGroup, State

class BaseForm(StatesGroup):
    name = State()
    technology = State()
    phone_number = State()
    region = State()
    cost = State()
    work_or_study = State()
    time = State()
    purpose = State()
    confirm = State()

class Friend(BaseForm): pass
class Work(BaseForm): pass
class Employee(BaseForm): pass
class Teacher(BaseForm): pass
class Student(BaseForm): pass
