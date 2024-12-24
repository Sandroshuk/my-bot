import csv
import re

# Функция для проверки корректности строки
def is_valid_row(row):
    """
    Проверяет, что строка содержит осмысленные данные:
    - Не состоит из бессмысленных символов или повторов букв.
    - Учитываются короткие ответы "да" и "нет".
    """
    if not row:
        return False

    # Условие: если строка слишком короткая, считаем её тестовой
    if len(row) < 5:
        return False

    # Условие: проверяем на наличие строк из повторяющихся символов
    for field in row:
        # Игнорируем пустые поля
        if not field.strip():
            continue

        # Допускаем "да" и "нет" как валидные ответы
        if field.strip().lower() in ["да", "нет"]:
            continue

        # Проверяем, состоит ли поле из одинаковых символов (например, "ТТТТ", "ООО")
        if re.fullmatch(r'(\w)\1+', field):
            return False
        
        # Проверка на бессмысленный текст (смешение букв и символов)
        if re.fullmatch(r'[^\w\s]+', field):  # Строки типа "?!@#$"
            return False

        # Проверка на слишком короткие слова из букв (меньше 3 символов)
        if re.fullmatch(r'[А-Яа-яA-Za-z]{1,2}', field):
            return False

    return True

# Пути к файлам
input_file = "responses.csv"
output_file = "responses_cleaned.csv"

# Очистка таблицы
def clean_csv():
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        headers = next(reader)  # Чтение заголовков
        writer.writerow(headers)  # Запись заголовков

        for row in reader:
            if is_valid_row(row):
                writer.writerow(row)

    print("Таблица очищена. Файл сохранен как 'responses_cleaned.csv'.")

if __name__ == "__main__":
    clean_csv()
