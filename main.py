import logging
import csv
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from config import API_TOKEN

# Настройка логирования: в файл bot.log и в консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

class Form(StatesGroup):
    question_index = State()

QUESTIONS = [
    {'key': 'child_name', 'text': '1. ОБЩИЕ ДАННЫЕ:\nФИО ребёнка'},
    {'key': 'child_birth_date', 'text': 'Дата рождения'},
    {'key': 'hand_preference', 'text': 'Правша, левша, амбидекстр'},
    {'key': 'bilingual', 'text': 'Есть ли в семье двуязычие?'},
    {'key': 'birth_details', 'text': 'Перенесённые заболевания, медикаментозное лечение'},
    {'key': 'specialists', 'text': 'Стояли или стоите на учёте у узких специалистов?'},
    {'key': 'speech_therapy', 'text': 'Посещали раньше логопеда или нет?'},
    {'key': 'speech_therapy_exercises', 'text': 'Если да, какие упражнения выполняются'},
    {'key': 'siblings', 'text': 'Есть ли ещё дети в семье, возраст'},
    {'key': 'mother_name', 'text': 'ФИО матери'},
    {'key': 'mother_age', 'text': 'Возраст матери на время рождения ребёнка'},
    {'key': 'hereditary_diseases_mother', 'text': 'Наследственные заболевания у мамы'},
    {'key': 'speech_defects_mother', 'text': 'Дефекты речи, неправильный прикус у мамы (отсутствуют-присутствуют; если есть, какие)'},
    {'key': 'orthodontic_braces_mother', 'text': 'Устанавливались ли ортодонтические брекеты у мамы?'},
    {'key': 'frenectomy_mother', 'text': 'Подрезалась ли уздечка языка или губы у мамы?'},
    {'key': 'father_name', 'text': 'ФИО отца'},
    {'key': 'father_age', 'text': 'Возраст отца на время рождения ребёнка'},
    {'key': 'hereditary_diseases_father', 'text': 'Наследственные заболевания у папы'},
    {'key': 'speech_defects_father', 'text': 'Дефекты речи, неправильный прикус у папы (отсутствуют-присутствуют; если есть, какие)'},
    {'key': 'orthodontic_braces_father', 'text': 'Устанавливались ли ортодонтические брекеты у папы?'},
    {'key': 'frenectomy_father', 'text': 'Подрезалась ли уздечка языка или губы у папы?'},
    {'key': 'pregnancy_details', 'text': '2. БЕРЕМЕННОСТЬ:\nНа каком сроке были роды'},
    {'key': 'complications', 'text': '3. РОДЫ\nДосрочные, срочные, быстрые, обезвоженные'},
    {'key': 'stimulation', 'text': 'Стимуляция'},
    {'key': 'asphyxia', 'text': 'Асфиксия (синяя, красная, белая)'},
    {'key': 'birth_injury', 'text': 'Обвитие, травмы, гематомы'},
    {'key': 'rh_factor', 'text': 'Резус-фактор (мама (+ или -); ребёнок (+ или -))'},
    {'key': 'birth_weight_height', 'text': 'Вес и рост при рождении'},
    {'key': 'breastfeeding', 'text': '4. ВСКАРМЛИВАНИЕ\nАктивное сосание'},
    {'key': 'feeding_issues', 'text': 'Отказ от груди'},
    {'key': 'poppering', 'text': 'Поперхивания во время сосания, чрезмерное срыгивание'},
    {'key': 'nipple_difficulty', 'text': 'Трудности в удерживании соска'},
    {'key': 'pacifier', 'text': 'Сосал ли ребёнок соску, если да, то до какого возраста'},
    {'key': 'early_development', 'text': '5. РАННЕЕ РАЗВИТИЕ:\nДержал голову (в 1,5-2 мес.)?'},
    {'key': 'sitting', 'text': 'Сидел (в 6 мес.)?'},
    {'key': 'crawling', 'text': 'Ползал (в 7-8 мес.)?'},
    {'key': 'walking', 'text': 'Ходил (к 1 году)?'},
    {'key': 'first_teeth', 'text': 'Появление первых зубов (в 6-8 мес.)?'},
    {'key': 'teeth_count', 'text': 'Количество зубов к 1 году (около 8)'},
    {'key': 'psychomotor_status', 'text': '6. СОСТОЯНИЕ РАННЕГО ПСИХОМОТОРНОГО РАЗВИТИЯ:\nДвигательно беспокоен?'},
    {'key': 'psychomotor_status_2', 'text': 'Криклив'},
    {'key': 'psychomotor_status_3', 'text': 'С трудом засыпал'},
    {'key': 'psychomotor_status_4', 'text': 'Беспокойный и короткий сон'},
    {'key': 'psychomotor_status_5', 'text': 'Заторможенный, вялый, не реагировал на окружающих'},
    {'key': 'speech_development', 'text': 'РАННЕЕ РЕЧЕВОЕ РАЗВИТИЕ:\nВремя появления гуления (2-3 мес.)'},
    {'key': 'speech_issues', 'text': 'Время появления лепета (4-6 мес.)'},
    {'key': 'first_words', 'text': 'Время появления первых слов (до 1 года)'},
    {'key': 'first_phrase', 'text': 'Первая фраза (1,5-2 года)'},
    {'key': 'speech_complaints_2', 'text': 'Прерывалось ли речевое развитие:'},
    {'key': 'speech_complaints', 'text': '8. ЗАМЕЧАНИЯ, ЖАЛОБЫ РОДИТЕЛЕЙ НА РЕЧЕВОЕ РАЗВИТИЕ РЕБЁНКА'}
]


# Вопросы с кнопками "Да/Нет"
YES_NO_QUESTIONS = {
    'bilingual': 'Вы билингвальны?',
    'orthodontic_braces_mother': 'Мать носила ортодонтические брекеты?',
    'frenectomy_mother': 'Мать делала подрезание уздечки?',
    'orthodontic_braces_father': 'Отец носил ортодонтические брекеты?',
    'frenectomy_father': 'Отец делал подрезание уздечки?',
    'breastfeeding': 'Грудное вскармливание?',
    'feeding_issues': 'Были ли проблемы с кормлением?',
    'poppering': 'Использовалась ли пустышка?',
    'nipple_difficulty': 'Были ли проблемы с захватом соска?',
    'psychomotor_status_5': 'Проблемы с психомоторным статусом на 5-м этапе?',
    'speech_development': 'Развивалась ли речь нормально?',
    'speech_issues': 'Были ли проблемы с речью?',
    'first_words': 'Первые слова появились вовремя?',
    'first_phrase': 'Первая фраза появилась вовремя?',
    'speech_complaints_2': 'Жалобы на речь (вторая проверка)?',
    'stimulation': 'Были ли стимуляции развития?',
    'early_development_1': 'Раннее развитие - этап 1?',
    'early_development_2': 'Раннее развитие - этап 2?',
    'early_development_3': 'Раннее развитие - этап 3?',
    'early_development_4': 'Раннее развитие - этап 4?',
    'early_teeth': 'Раннее появление зубов?',
    'speech_therapy': 'Посещали раньше логопеда или нет?',
    'early_development': 'Держал голову (в 1,5-2 мес.)?',
    'sitting': 'Сидел (в 6 мес.)?',
    'crawling': 'Ползал (в 7-8 мес.)?',
    'walking': 'Ходил (к 1 году)?',
    'first_teeth': 'Появление первых зубов (в 6-8 мес.)?'
}

# Вопросы с несколькими вариантами ответа
MULTI_OPTION_QUESTIONS = {
    'hand_preference': ['Правша', 'Левша', 'Амбидекстр'],
    'complications': ['Досрочные', 'Срочные', 'Быстрые', 'Обезвоженные'],
    'birth_injury': ['Нет','Обвитие', 'Травмы', 'Гематомы'],
    'asphyxia': ['Нет', 'Синяя', 'Красная', 'Белая']
}

# Функция для создания клавиатуры "Да/Нет"
def yes_no_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        ],
        resize_keyboard=True, one_time_keyboard=True
    )

# Функция для создания клавиатуры с несколькими вариантами ответа
def multi_option_keyboard(options):
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in options],
        resize_keyboard=True, one_time_keyboard=True
    )

INTRO = (
    "Здравствуйте!\n"
    "Перед вами анкета для знакомства с вами и вашим ребёнком.\n"
    "✔️Ответы на вопросы помогут нам лучше понять особенности вашего малыша.\n"
    "✔️Все данные являются сугубо конфиденциальными, и используются только для анализа.\n"
    "☝️Для вашего удобства, вы можете отключить звук на устройстве, чтобы сосредоточиться на ответах.\n"
)

def save_to_csv(user_id, user_data):
    file_name = 'responses.csv'
    file_exists = False
    try:
        with open(file_name, 'r', encoding='utf-8'):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(file_name, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([q['text'] for q in QUESTIONS])
        writer.writerow([user_data.get(q['key'], '') for q in QUESTIONS])

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if message.chat.type != "private":
        return

    await state.set_state(Form.question_index)
    await state.update_data(answers={}, question_index=0)
    await message.answer(INTRO)
    first_key = QUESTIONS[0]['key']
    first_text = QUESTIONS[0]['text']

    if first_key in YES_NO_QUESTIONS:
        await message.answer(first_text, reply_markup=yes_no_keyboard())
    elif first_key in MULTI_OPTION_QUESTIONS:
        await message.answer(first_text, reply_markup=multi_option_keyboard(MULTI_OPTION_QUESTIONS[first_key]))
    else:
        await message.answer(first_text, reply_markup=ReplyKeyboardRemove())

@router.message()
async def handle_input(message: Message, state: FSMContext):
    if message.chat.type != "private":
        return

    data = await state.get_data()
    idx = data.get('question_index', 0)
    answers = data.get('answers', {})

    if idx < len(QUESTIONS):
        key = QUESTIONS[idx]['key']
        user_answer = message.text.strip()

        # Проверка для вопросов с кнопками "Да/Нет"
        if key in YES_NO_QUESTIONS and user_answer not in ["Да", "Нет"]:
            await message.answer("Пожалуйста, выберите ответ с помощью кнопок ниже.", reply_markup=yes_no_keyboard())
            return

        # Проверка для вопросов с несколькими вариантами ответа
        if key in MULTI_OPTION_QUESTIONS and user_answer not in MULTI_OPTION_QUESTIONS[key]:
            await message.answer("Пожалуйста, выберите ответ с помощью кнопок ниже.", reply_markup=multi_option_keyboard(MULTI_OPTION_QUESTIONS[key]))
            return

        # Сохраняем ответ
        answers[key] = user_answer

        # Следующий вопрос
        idx += 1
        if idx < len(QUESTIONS):
            next_key = QUESTIONS[idx]['key']
            next_text = QUESTIONS[idx]['text']
            if next_key in YES_NO_QUESTIONS:
                await state.update_data(question_index=idx, answers=answers)
                await message.answer(next_text, reply_markup=yes_no_keyboard())
            elif next_key in MULTI_OPTION_QUESTIONS:
                await state.update_data(question_index=idx, answers=answers)
                await message.answer(next_text, reply_markup=multi_option_keyboard(MULTI_OPTION_QUESTIONS[next_key]))
            else:
                await state.update_data(question_index=idx, answers=answers)
                await message.answer(next_text, reply_markup=ReplyKeyboardRemove())
        else:
            # Анкета завершена
            await state.update_data(answers=answers)
            await message.answer("Спасибо! Анкета заполнена.", reply_markup=ReplyKeyboardRemove())
            save_to_csv(message.from_user.id, answers)

            # Отправляем файл в группу
            GROUP_ID = -4660017776
            try:
                file_to_send = FSInputFile('responses.csv', filename='responses.csv')
                await bot.send_document(
                    chat_id=GROUP_ID,
                    document=file_to_send,
                    caption="Обновлённые данные анкеты."
                )
                await message.answer("Данные успешно отправлены логопеду.")
            except Exception as e:
                await message.answer("Данные сохранены, но не удалось отправить файл. Попробуйте позже.")
                logging.error(f"Ошибка при отправке файла: {e}")

            await state.clear()
    else:
        await message.answer("Анкета не активна. Введите /start, чтобы начать заново.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
