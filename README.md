# RIF Open Calls Telegram Bot

A Telegram bot that helps users find information about Research and Innovation Foundation's (RIF) Open Calls using natural language queries. The bot uses FAISS for semantic search across PDF documents and supports multilingual queries.

Deploy: Railway.com
TelegramBotID = @AbasisNikitabot


## Features

- 🔍 Semantic search across RIF Open Calls documents
- 🌐 Supports multilingual queries
- 📄 Automatic PDF document fetching and processing
- 💡 Natural language understanding
- 🤖 Easy-to-use Telegram interface

## Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))
- Internet connection for downloading PDFs

## Installation

1. Clone the repository:
```bash
git clone [your-repo-url]
cd rif-opencalls-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your Telegram bot token:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

## Project Structure

- `bot.py` - Main Telegram bot implementation
- `FAISS_loader.py` - FAISS vector store implementation for semantic search
- `PDF_loader.py` - PDF document downloader and processor
- `pdfs/` - Directory where PDF documents are stored
- `requirements.txt` - Python dependencies

## Usage

1. Start the bot:
```bash
python bot.py
```

2. Open Telegram and search for your bot using the username you set up with BotFather

3. Start interacting with the bot:
   - Send `/start` to get a welcome message
   - Send `/help` to see available commands
   - Ask questions in natural language about RIF Open Calls

Example questions:
- "Which programmes suit a company of 4 people?"
- "Which calls are for agritech startups?"
- "Which calls expire in May?"

## How It Works

1. The bot automatically downloads PDF documents from the RIF website
2. Documents are processed and split into chunks
3. Text chunks are embedded using a multilingual model
4. FAISS is used to create a searchable vector store
5. When a user asks a question, it's converted to an embedding and searched against the vector store
6. The most relevant document chunks are returned as answers

## Environment Variables

- `TELEGRAM_BOT_TOKEN`: Your Telegram Bot API token
