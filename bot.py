import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from faiss_loader import FAISSLoader
from pdf_loader import PDFLoader

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Initialize loaders
pdf_loader = PDFLoader()
logger.info("Downloading and processing PDFs...")
documents = pdf_loader.refresh()  # This will download PDFs if needed
logger.info(f"Loaded {len(documents)} documents")

logger.info("Building FAISS index...")
faiss_loader = FAISSLoader()  # This will process the PDFs and build the index

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "Here's how to use this bot:\n\n"
        "1. Simply ask your question about RIF Open Calls in natural language\n"
        "2. I'll search through the available documents and provide relevant information\n"
        "3. You can ask in any language (primarily optimized for English)\n\n"
        "Example questions:\n"
        "- What funding is available for startups?\n"
        "- When is the next deadline?\n"
        "- What are the eligibility criteria?\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/refresh - Refresh PDF documents and rebuild index"
    )
    await update.message.reply_text(help_text)

async def refresh_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Refresh PDFs and rebuild index."""
    try:
        await update.message.reply_text("Starting refresh... This may take a few minutes.")
        
        # Download and process new PDFs
        global documents
        documents = pdf_loader.refresh()
        await update.message.reply_text(f"Downloaded and processed {len(documents)} documents.")
        
        # Rebuild FAISS index
        global faiss_loader
        faiss_loader = FAISSLoader()
        
        await update.message.reply_text("✅ Refresh complete! You can now ask questions about the latest documents.")
    except Exception as e:
        logger.error(f"Error during refresh: {str(e)}")
        await update.message.reply_text("❌ Sorry, there was an error during refresh. Please try again later.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages and respond with relevant information."""
    try:
        # Get user's question
        question = update.message.text
        
        # Send typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Search for relevant information using FAISS
        search_results = faiss_loader.search(question, k=3)
        
        if not search_results:
            await update.message.reply_text(
                "I couldn't find specific information about that. Could you please rephrase your question "
                "or ask something else about the RIF Open Calls?"
            )
            return
        
        # Format the response
        response = "Here's what I found:\n\n"
        for idx, result in enumerate(search_results, 1):
            # Truncate long results
            result_text = result[:1000] + "..." if len(result) > 1000 else result
            response += f"{idx}. {result_text}\n\n"
        
        response += "\nIs there anything specific you'd like to know more about?"
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        await update.message.reply_text(
            "Sorry, I encountered an error while processing your request. Please try again later."
        )

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("refresh", refresh_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    logger.info("Starting bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
