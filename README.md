# 🤖 UstozShogird Bot

Телеграм-бот для канала **UstozShogird**, который помогает найти:
- 👥 Sherik (напарника)
- 💼 Ish joyi (работу)
- 👨‍💻 Hodim (сотрудника)
- 👨‍🏫 Ustoz (наставника)
- 🧑‍🎓 Shogird (ученика)

Бот ведёт диалог с пользователем, собирает анкету и отправляет её админу на подтверждение. После модерации объявление публикуется в группе.

---

## 🚀 Возможности
- Интерфейс на узбекском языке  
- Формы для 5 категорий (Sherik, Ish joyi, Hodim, Ustoz, Shogird)  
- FSM (Finite State Machine) для пошагового заполнения анкеты  
- Подтверждение заявки пользователем перед отправкой  
- Модерация администратором (Approve / Reject)  
- Сохранение заявок в базу данных  

---

## 🛠️ Технологии
- [Python 3.11+](https://www.python.org/)  
- [Aiogram 3](https://docs.aiogram.dev/)  
- SQLite (через `aiosqlite`)  
- FSM (Finite State Machine)  
- Асинхронная архитектура (`asyncio`)  

---

## 📦 Установка и запуск

1. Клонировать репозиторий:
   ```bash
   git clone https://github.com/username/ustozshogird-bot.git
   cd ustozshogird-bot
