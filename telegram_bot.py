#!/usr/bin/env python3
"""
Telegram Bot for Nextbase Auto
Allows users to report traffic incidents via Telegram by sending photos.
"""

import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(
    PHOTO,
    INCIDENT_TYPE,
    REGISTRATION,
    COLOR,
    INCIDENT_DATE,
    INCIDENT_TIME,
    LOCATION,
    FIRST_NAME,
    LAST_NAME,
    EMAIL,
    PHONE,
    ADDRESS1,
    ADDRESS2,
    COUNTY,
    POSTCODE,
    OCCUPATION,
    DATE_OF_BIRTH,
    PLACE_OF_BIRTH,
    GENDER,
) = range(19)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for photo."""
    await update.message.reply_text(
        "👋 Welcome to Nextbase Auto Bot!\n\n"
        "I'll help you report bad parking to South Yorkshire Police.\n\n"
        "📸 Please send me a photo of the incident.\n\n"
        "You can /cancel at any time to stop."
    )
    return PHOTO


async def photo_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the uploaded photo."""
    user = update.effective_user
    photo_file = await update.message.photo[-1].get_file()
    
    # Download photo
    photo_path = f"/tmp/nextbase_bot_{user.id}.jpg"
    await photo_file.download_to_drive(photo_path)
    
    # Store photo path in context
    context.user_data["photo_path"] = photo_path
    
    await update.message.reply_text(
        "✅ Photo received and saved!\n\n"
        "Now I need some details about the incident."
    )
    
    # Ask for incident type
    keyboard = [["Corner parking", "Pavement parking"]]
    await update.message.reply_text(
        "⚠️ What type of incident is this?\n\n"
        "• Corner parking - Vehicle parked within 10m of junction\n"
        "• Pavement parking - Vehicle parked on pavement/footway",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
    )
    return INCIDENT_TYPE


async def incident_type_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store incident type and ask for registration."""
    text = update.message.text
    if "corner" in text.lower():
        context.user_data["incident_type"] = "corner"
    else:
        context.user_data["incident_type"] = "pavement"
    
    await update.message.reply_text(
        "🚗 What is the vehicle registration number?\n\n"
        "Example: AB12 XYZ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return REGISTRATION


async def registration_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store registration and ask for color."""
    context.user_data["registration"] = update.message.text.upper().strip()
    
    await update.message.reply_text("🎨 What is the vehicle color?\n\nExample: Silver, Blue, Red")
    return COLOR


async def color_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store color and ask for incident date."""
    context.user_data["color"] = update.message.text
    
    await update.message.reply_text(
        "📅 What date did the incident occur?\n\n"
        "Format: DD/MM/YYYY (e.g., 15/02/2026)"
    )
    return INCIDENT_DATE


async def incident_date_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store incident date and ask for time."""
    context.user_data["incident_date"] = update.message.text
    
    await update.message.reply_text(
        "🕐 What time did the incident occur?\n\n"
        "Format: HH:MM (e.g., 14:30)"
    )
    return INCIDENT_TIME


async def incident_time_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store incident time and ask for location."""
    try:
        context.user_data["incident_time"] = update.message.text
        
        await update.message.reply_text(
            "📍 What is the street name where the incident occurred?\n\n"
            "Example: Hunter House Road"
        )
        return LOCATION
    except Exception as e:
        logger.error(f"Error in incident_time_received: {e}", exc_info=True)
        await update.message.reply_text(f"Error: {e}")
        return ConversationHandler.END


async def location_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store location and ask for first name."""
    context.user_data["incident_location"] = update.message.text
    
    await update.message.reply_text(
        "✅ Location saved.\n\n"
        "🔒 **Privacy Notice:**\n"
        "I now need to collect your personal information to complete the report. "
        "This data is NOT stored or shared with anyone. It's only used temporarily "
        "to generate your report, then deleted.\n\n"
        "👤 What is your first name?"
    )
    return FIRST_NAME


async def first_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store first name and ask for last name."""
    context.user_data["first_name"] = update.message.text
    await update.message.reply_text("What is your last name?")
    return LAST_NAME


async def last_name_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store last name and ask for email."""
    context.user_data["last_name"] = update.message.text
    await update.message.reply_text("📧 What is your email address?")
    return EMAIL


async def email_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store email and ask for phone."""
    context.user_data["email"] = update.message.text
    await update.message.reply_text("📱 What is your phone number?")
    return PHONE


async def phone_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store phone and ask for address."""
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("🏠 What is your address (first line)?")
    return ADDRESS1


async def address1_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store address1 and ask for address2."""
    context.user_data["address1"] = update.message.text
    await update.message.reply_text("Address line 2 (or type 'skip' if not applicable):")
    return ADDRESS2


async def address2_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store address2 and ask for county."""
    text = update.message.text
    if text.lower() != "skip":
        context.user_data["address2"] = text
    else:
        context.user_data["address2"] = ""
    
    await update.message.reply_text("Which county do you live in?")
    return COUNTY


async def county_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store county and ask for postcode."""
    context.user_data["county"] = update.message.text
    await update.message.reply_text("📮 What is your postcode?")
    return POSTCODE


async def postcode_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store postcode and ask for occupation."""
    context.user_data["postcode"] = update.message.text
    await update.message.reply_text("💼 What is your occupation?")
    return OCCUPATION


async def occupation_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store occupation and ask for date of birth."""
    context.user_data["occupation"] = update.message.text
    await update.message.reply_text(
        "🎂 What is your date of birth?\n\n"
        "Format: DD/MM/YYYY (e.g., 15/03/1985)"
    )
    return DATE_OF_BIRTH


async def dob_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store DOB and ask for place of birth."""
    context.user_data["date_of_birth"] = update.message.text
    await update.message.reply_text("🏙️ What is your place of birth (city)?")
    return PLACE_OF_BIRTH


async def pob_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store place of birth and ask for gender."""
    context.user_data["place_of_birth"] = update.message.text
    
    keyboard = [["Male", "Female", "Other"]]
    await update.message.reply_text(
        "⚧️ What is your gender?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True),
    )
    return GENDER


async def gender_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store gender and show final summary."""
    context.user_data["gender"] = update.message.text
    
    # Generate summary
    await show_summary(update, context)
    
    return ConversationHandler.END


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show complete summary of all collected data in easy-to-copy format."""
    data = context.user_data
    
    # Load incident template
    incident_type = data.get("incident_type", "corner")
    template = load_incident_template(incident_type)
    
    # Parse date to get day of week
    try:
        from datetime import datetime
        date_str = data.get('incident_date', '')
        if '/' in date_str:
            dt = datetime.strptime(date_str, '%d/%m/%Y')
            day_of_week = dt.strftime('%A')
        else:
            day_of_week = ""
    except:
        day_of_week = ""
    
    await update.message.reply_text(
        "✅ **All information collected!**\n\n"
        "I'll now send you all the details in easy-to-copy sections.\n\n"
        "Simply tap each message to copy and paste into the form.",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    # Send personal information section
    personal_info = (
        "📋 **PERSONAL INFORMATION**\n"
        "Copy each line below:\n\n"
        f"**First Name:**\n{data.get('first_name')}\n\n"
        f"**Last Name:**\n{data.get('last_name')}\n\n"
        f"**Email:**\n{data.get('email')}\n\n"
        f"**Phone:**\n{data.get('phone')}\n\n"
        f"**Address Line 1:**\n{data.get('address1')}\n\n"
        f"**Address Line 2:**\n{data.get('address2', 'N/A')}\n\n"
        f"**County:**\n{data.get('county')}\n\n"
        f"**Postcode:**\n{data.get('postcode')}\n\n"
        f"**Occupation:**\n{data.get('occupation')}\n\n"
        f"**Date of Birth:**\n{data.get('date_of_birth')}\n\n"
        f"**Place of Birth:**\n{data.get('place_of_birth')}\n\n"
        f"**Gender:**\n{data.get('gender')}"
    )
    await update.message.reply_text(personal_info)
    
    # Send incident details section
    incident_info = (
        "🚗 **INCIDENT DETAILS**\n"
        "Copy each line below:\n\n"
        f"**Incident Location:**\n{data.get('incident_location')}\n\n"
        f"**Incident Date:**\n{data.get('incident_date')}\n\n"
    )
    if day_of_week:
        incident_info += f"**Day of Week:**\n{day_of_week}\n\n"
    
    incident_info += (
        f"**Incident Time:**\n{data.get('incident_time')}\n\n"
        f"**Vehicle Registration:**\n{data.get('registration')}\n\n"
        f"**Vehicle Colour:**\n{data.get('color')}\n\n"
        f"**Vehicle Make:**\ncar\n\n"
        f"**Vehicle Model:**\nNot known"
    )
    await update.message.reply_text(incident_info)
    
    # Send incident description (this is the long one)
    description_msg = (
        "📝 **INCIDENT DESCRIPTION**\n"
        "Tap to copy this full description:\n\n"
        f"{template}"
    )
    await update.message.reply_text(description_msg)
    
    # Send form link and instructions
    final_instructions = (
        "🔗 **READY TO SUBMIT**\n\n"
        "1. Open the form here:\n"
        "https://secureform.nextbase.co.uk/?location=SouthYorkshire\n\n"
        "2. Tap each message above to copy\n"
        "3. Paste into the matching fields\n"
        "4. Upload your photo\n"
        "5. Complete reCAPTCHA\n"
        "6. Submit!\n\n"
        "💡 **Tips:**\n"
        "• Long-press a message to copy\n"
        "• Keep Telegram open while filling form\n"
        "• Switch between apps to paste\n\n"
        "Use /start to report another incident."
    )
    await update.message.reply_text(final_instructions)


def load_incident_template(incident_type):
    """Load the incident description template."""
    templates = {
        "corner": (
            "I found the above vehicle parked in a manner that failed to meet the rules laid out in the Highway Code, "
            "creating an unnecessary obstruction of the road and a danger to vulnerable road users.\n\n"
            "Rule 243 of the highway code states DO NOT STOP or park opposite or within 10m (32 feet) of a junction, "
            "opposite a traffic island, or on a bend and \"DO NOT stop or park where the kerb has been lowered to help "
            "wheelchair users and powered mobility vehicles.\"\n\n"
            "The vehicle was obscuring visibility at a junction causing a danger for vulnerable road users such as "
            "motorcyclists, cyclists, and pedestrians who are put at more risk as a result of poor junction visibility. "
            "Rule 242 of the Highway code states \"You MUST NOT leave your vehicle or trailer in a dangerous position "
            "or where it causes an unnecessary obstruction of the road.\". It was also covering a dropped kerb.\n\n"
            "Offence code: Leave a motor vehicle in dangerous position RT88508.\n\n"
            "No notes or badges were displayed in the vehicle. No loading or unloading was taking place."
        ),
        "pavement": (
            "I found the above vehicle parked in a manner that failed to meet the rules laid out in the Highway Code, "
            "creating an unnecessary obstruction of the road and a danger to vulnerable road users.\n\n"
            "The car was parked partly on the footway, which constitutes part of 'the road' making it impossible for "
            "wheelchair users and prams to pass.\n\n"
            "Rule 145 states \"You MUST NOT drive on or over a pavement, footpath or bridleway except to gain lawful "
            "access to property, or in the case of an emergency\".\n\n"
            "Rule 244 states \"You MUST NOT park partially or wholly on the pavement in London, and should not do so "
            "elsewhere unless signs permit it. Parking on the pavement can obstruct and seriously inconvenience pedestrians, "
            "people in wheelchairs or with visual impairments and people with prams or pushchairs\"\n\n"
            "Rule 243 of the highway code states DO NOT STOP or park opposite or within 10m (32 feet) of a junction, "
            "opposite a traffic island, or on a bend and \"DO NOT stop or park where the kerb has been lowered to help "
            "wheelchair users and powered mobility vehicles.\"\n\n"
            "The vehicle was causing a danger for vulnerable road users such as motorcyclists, cyclists, and pedestrians "
            "who are put at more risk as a result of poor junction visibility.\n\n"
            "Rule 242 of the Highway code states \"You MUST NOT leave your vehicle or trailer in a dangerous position "
            "or where it causes an unnecessary obstruction of the road.\"\n\n"
            "Offence code: Leave a motor vehicle in dangerous position RT88508.\n\n"
            "No notes or badges were displayed in the vehicle. No loading or unloading was taking place."
        ),
    }
    return templates.get(incident_type, templates["corner"])


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "❌ Report cancelled. Use /start to begin again.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display help information."""
    help_text = (
        "🤖 **Nextbase Auto Bot Help**\n\n"
        "**Commands:**\n"
        "/start - Start a new incident report\n"
        "/help - Show this help message\n"
        "/cancel - Cancel current report\n\n"
        "**How to use:**\n"
        "1. Send /start\n"
        "2. Upload a photo of the incident\n"
        "3. Answer questions about the incident\n"
        "4. Answer questions about your personal details\n"
        "5. Get a complete summary with incident description\n\n"
        "**Privacy:**\n"
        "Your data is only stored temporarily during the conversation "
        "and is not saved permanently by this bot."
    )
    await update.message.reply_text(help_text)


def main() -> None:
    """Run the bot."""
    # Get bot token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not set in environment")
        print("Please set it in .env file or environment variables")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Define conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHOTO: [MessageHandler(filters.PHOTO, photo_received)],
            INCIDENT_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, incident_type_received)],
            REGISTRATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, registration_received)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, color_received)],
            INCIDENT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, incident_date_received)],
            INCIDENT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, incident_time_received)],
            LOCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, location_received)],
            FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_name_received)],
            LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, last_name_received)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_received)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_received)],
            ADDRESS1: [MessageHandler(filters.TEXT & ~filters.COMMAND, address1_received)],
            ADDRESS2: [MessageHandler(filters.TEXT & ~filters.COMMAND, address2_received)],
            COUNTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, county_received)],
            POSTCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, postcode_received)],
            OCCUPATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, occupation_received)],
            DATE_OF_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, dob_received)],
            PLACE_OF_BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, pob_received)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_received)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    
    # Run the bot
    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
