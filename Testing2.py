import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

BOT_TOKEN = '6222391384:AAEoLLtl8DDzbjiXy4NwpndASWrhDH9Krk0'
CHAT_ID = "-511576030"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [InlineKeyboardButton("Baroque Obama", callback_data="1")],
        [InlineKeyboardButton("Obama dressing up as washington", callback_data="2")],
        [InlineKeyboardButton("Option 3", callback_data="3")],
        [InlineKeyboardButton("Use a hint LOL", callback_data="4")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    # await context.bot.send_message(
    #     chat_id=CHAT_ID,
    #     text="Voting round!"
    # )
    # await context.bot.send_message(
    #     chat_id=CHAT_ID,
    #     text="Pick your option"
    # )
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="Vote for the prompt you think generated Photo 1!",
        reply_markup=reply_markup
    )
    # await update.message.reply_text("Please choose:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays info on how to use the bot."""
    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()