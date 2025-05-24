import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from FAISS_loader import FAISSLoader
from PDF_loader import PDFLoader

# ---------------------- Logging setup ----------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------- Load env variables ----------------------
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ---------------------- Lazy loaded globals ----------------------
faiss_loader = None
documents = None


# ---------------------- Command: /start ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "👋 Welcome to the RIF Open Calls Bot!\n\n"
        "I can help you find information about Research and Innovation Foundation's Open Calls.\n\n"
        "Just ask me questions like:\n"
        "- Which programmes suit a company of 4 people?\n"
        "- Which calls are for agritech startups?\n"
        "- Which calls expire in May?\n\n"
        "I'll do my best to help you find the information you need!"
    )
    await update.message.reply_text(welcome_message)


# ---------------------- Command: /help ----------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Here's how to use this bot:\n\n"
        "1. Simply ask your question about RIF Open Calls in natural language\n"
        "2. I'll search through the available documents and provide relevant information\n"
        "3. You can ask in any language (primarily optimized for English)\n\n"
        "Example questions:\n"
        "- What funding is available for startups?\n"
        "- When is the next deadline?\n"
        "- What are the eligibility criteria?\n\n"
    )
    await update.message.reply_text(help_text)


# ---------------------- Handler: text messages ----------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global faiss_loader, documents

    try:
        if faiss_loader is None:
            await update.message.reply_text("⚠️ Модель ещё не готова, попробуйте через пару секунд.")
            return

        question = update.message.text
        await update.message.chat.send_action(action="typing")

        search_results = faiss_loader.search(question, k=3)

        if not search_results:
            await update.message.reply_text(
                "🤔 I couldn't find anything relevant. Try rephrasing your question?"
            )
            return

        response = "📄 Here's what I found:\n\n"
        for idx, result in enumerate(search_results, 1):
            result_text = result[:1000] + "..." if len(result) > 1000 else result
            response += f"{idx}. {result_text}\n\n"

        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        await update.message.reply_text("⚠️ An error occurred while processing your request.")


# ---------------------- Async preload function ----------------------
async def preload():
    global faiss_loader, documents
    logger.info("Preloading documents and FAISS index...")
    pdf_loader = PDFLoader()
    documents = pdf_loader.refresh()
    faiss_loader = FAISSLoader()

    logger.info(f"Preloading completed. Loaded {len(documents)} documents.")


# ---------------------- Entry point ----------------------
def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    async def run():
        await preload() # additional async
        logger.info("Starting bot polling...")
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

    asyncio.run(run())


if __name__ == '__main__':
    main()
