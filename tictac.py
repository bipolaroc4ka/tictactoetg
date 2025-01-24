from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import random

# Создание пустого игрового поля
def create_board():
    return [[" " for _ in range(3)] for _ in range(3)]

# Проверка победы
def check_winner(board, symbol):
    # Проверяем строки, столбцы и диагонали
    for row in board:
        if all(cell == symbol for cell in row):
            return True
    for col in range(3):
        if all(board[row][col] == symbol for row in range(3)):
            return True
    if all(board[i][i] == symbol for i in range(3)) or all(board[i][2 - i] == symbol for i in range(3)):
        return True
    return False

# Проверка на ничью
def check_draw(board):
    return all(cell != " " for row in board for cell in row)

# Генерация клавиатуры
def generate_keyboard(board):
    keyboard = []
    for i, row in enumerate(board):
        buttons = [
            InlineKeyboardButton(f"{cell if cell != ' ' else ' '}", callback_data=f"{i}-{j}")
            if cell == " " else InlineKeyboardButton(f"{cell}", callback_data="taken")
            for j, cell in enumerate(row)
        ]
        keyboard.append(buttons)
    return InlineKeyboardMarkup(keyboard)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = create_board()
    context.user_data["board"] = board
    context.user_data["player"] = "X"
    await update.message.reply_text("Игра началась! Вы играете за X.", reply_markup=generate_keyboard(board))

# Обработка нажатия кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    board = context.user_data["board"]
    player = context.user_data["player"]

    if data == "taken":
        await query.edit_message_text("Эта клетка уже занята!", reply_markup=generate_keyboard(board))
        return

    # Разбор координат
    x, y = map(int, data.split("-"))

    # Ход игрока
    if board[x][y] == " ":
        board[x][y] = player
        if check_winner(board, player):
            await query.edit_message_text(f"Вы выиграли! 🎉", reply_markup=generate_keyboard(board))
            return
        if check_draw(board):
            await query.edit_message_text("Ничья! 🤝", reply_markup=generate_keyboard(board))
            return

        # Ход бота
        bot_move(board, "O")
        if check_winner(board, "O"):
            await query.edit_message_text(f"Бот выиграл! 🤖", reply_markup=generate_keyboard(board))
            return
        if check_draw(board):
            await query.edit_message_text("Ничья! 🤝", reply_markup=generate_keyboard(board))
            return

    await query.edit_message_text("Ваш ход!", reply_markup=generate_keyboard(board))

# Ход бота
def bot_move(board, symbol):
    empty_cells = [(i, j) for i, row in enumerate(board) for j, cell in enumerate(row) if cell == " "]
    if empty_cells:
        x, y = random.choice(empty_cells)
        board[x][y] = symbol

# Основная функция
def main():
    # Замените YOUR_TOKEN на ваш токен
    application = Application.builder().token("Your Token").build()

    # Регистрируем команду /start
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    # Запускаем бота
    application.run_polling()

if __name__ == "__main__":
    main()
