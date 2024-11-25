import logging
import os
import redis.asyncio as aioredis
from typing import Set

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)



# Initialize Redis client
redis_client = aioredis.from_url("redis://redis:6379")

# Keep track of active chats
active_chats: Set[int] = set()

# Define a few command handlers. These usually take the two arguments update and
# context.
# Best practice would be to replace context with an underscore,
# since context is an unused local variable.
# This being an example and not having context present confusing beginners,
# we decided to have it present as context.
# Modify start handler to store chat_id
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stores chat_id and sends explanation on how to use the bot."""
    active_chats.add(update.message.chat_id)
    await update.message.reply_text("Hi! Use /set <seconds> to set a timer")


async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)

#REDIS

# Modify listen_for_updates to broadcast to all active chats
async def listen_for_updates(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Listen for updates from Redis and broadcast to all active chats."""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe("message_queue")

    async for message in pubsub.listen():
        try:
            if message["type"] == "message":
                data = message["data"].decode("utf-8")
                logging.info(f"Broadcasting message: {data}")
                
                # Broadcast to all active chats
                for chat_id in active_chats:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=data
                    )
        except Exception as e:
            logging.error(f"Error processing message: {e}")

            
def main() -> None:
    """Run bot."""
    # Get the bot token from the environment variable
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("No BOT_TOKEN environment variable set")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["start", "help"], start))
    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))

    # Add job to listen for updates from Redis
    application.job_queue.run_repeating(listen_for_updates, interval=5)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()