import logging
from telethon import events
import database
import models
import utils
import config

logger = logging.getLogger(__name__)

async def show_settings_menu(event, user_id: int):
    """
    Renders the global settings menu.
    """
    user = database.get_user(user_id)
    lang = user.get("language", "en") if user else "en"
    
    # Fetch user wallet balance
    wallet_bal = user.get("wallet_balance", 0.0)
    
    LANG_NAMES = {
        "en": "English 🇬🇧",
        "hi": "Hindi 🇮🇳",
        "ru": "Russian 🇷🇺",
        "ja": "Japanese 🇯🇵",
        "fr": "French 🇫🇷",
        "de": "German 🇩🇪",
        "zh": "Chinese 🇨🇳",
        "ar": "Arabic 🇸🇦"
    }
    lang_display = LANG_NAMES.get(lang, lang.upper())
    
    text = (
        f"<blockquote><b>» ⚙️ User Settings</b>\n\n"
        f"👛 <b>Wallet Balance :</b> <code>₹{wallet_bal:.2f}</code>\n"
        f"🌐 <b>Current Language :</b> <code>{lang_display}</code>\n\n"
        f"⚡ <i>Select an action below to manage your account :</i></blockquote>"
    )
    buttons = [
        [
            utils.styled_button(utils.get_text("btn_change_lang", lang), "settings_change_lang", style="primary"),
            utils.styled_button(utils.get_text("btn_buy_slots", lang), "settings_buy_slots", style="primary")
        ],
        [
            utils.styled_button("🎟️ Redeem Coupon", "settings_redeem_coupon", style="primary"),
            utils.styled_button("👥 Referrals", "settings_referrals", style="primary")
        ],
        [utils.styled_button(utils.get_text("back_to_menu", lang), "menu_start", style="primary")]
    ]
    
    try:
        msg = event.message if hasattr(event, 'message') else event
        if getattr(msg, 'media', None):
            await msg.delete()
            await event.respond(text, buttons=buttons, parse_mode="html")
        else:
            await event.edit(text, buttons=buttons, parse_mode="html")
    except Exception:
        await event.respond(text, buttons=buttons, parse_mode="html")

async def show_purchase_menu(event, user_id: int):
    """
    Renders the paid slot tier menu showing options to purchase slots under admin-defined plans.
    """
    user = database.get_user(user_id)
    lang = user.get("language", "en") if user else "en"
    
    allowed = utils.get_allowed_slots(user_id)
    
    global_settings = database.get_global_settings()
    plans = global_settings.get("subscription_plans", [])
    
    if not plans:
        buttons = [[utils.styled_button("🔙 ʙᴀᴄᴋ", "menu_settings", style="primary")]]
        text = (
            f"> ❌ <b>NO PLANS AVAILABLE</b>\n"
            f"> ━━━━━━━━━━━━━━━━━━━━\n"
            f"> No subscription plans are currently configured by administrators.\n"
            f"> ━━━━━━━━━━━━━━━━━━━━"
        )
        try:
            msg = event.message if hasattr(event, 'message') else event
            if getattr(msg, 'media', None):
                await msg.delete()
                await event.respond(text, buttons=buttons)
            else:
                await event.edit(text, buttons=buttons)
        except Exception:
            await event.respond(text, buttons=buttons)
        return
        
    text = (
        f"<blockquote><b>» 💳 Purchase Slot Upgrades</b>\n\n"
        f"> ━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Current Allowed Slots :</b> <code>{allowed}</code>\n"
        f"⚡ <i>Select a subscription plan below to upgrade:</i></blockquote>"
        f"> ━━━━━━━━━━━━━━━━━━━━"
    )
    
    buttons = []
    for plan in plans:
        plan_id = plan["id"]
        name = plan["button_name"]
        price = plan["price"]
        days = plan["days"]
        slots = plan.get("slots")
        if slots:
            btn_label = f"✨ {name} ({slots} Slots - ₹{price:.0f} / {days} days)"
        else:
            btn_label = f"✨ {name} (₹{price:.0f} / {days} days)"
        buttons.append([
            utils.styled_button(btn_label, f"buy_plan_{plan_id}", style="primary")
        ])
        
    buttons.append([utils.styled_button(utils.get_text("btn_back_to_bots", lang), "menu_settings", style="primary")])
    try:
        msg = event.message if hasattr(event, 'message') else event
        if getattr(msg, 'media', None):
            await msg.delete()
            await event.respond(text, buttons=buttons)
        else:
            await event.edit(text, buttons=buttons)
    except Exception:
        await event.respond(text, buttons=buttons)

def register_handlers(client):
    
    # ------------------ Navigation ------------------
    @client.on(events.CallbackQuery(pattern="^menu_settings$"))
    async def settings_menu_callback(event):
        await show_settings_menu(event, event.sender_id)

    @client.on(events.CallbackQuery(pattern="^settings_change_lang$"))
    async def change_lang_menu_callback(event):
        user_id = event.sender_id
        user = database.get_user(user_id)
        lang = user.get("language", "en") if user else "en"
        
        buttons = [
            [
                utils.styled_button("English 🇬🇧", "set_lang_en", style="primary"),
                utils.styled_button("Hindi 🇮🇳", "set_lang_hi", style="primary"),
                utils.styled_button("Russian 🇷🇺", "set_lang_ru", style="primary")
            ],
            [
                utils.styled_button("Japanese 🇯🇵", "set_lang_ja", style="primary"),
                utils.styled_button("French 🇫🇷", "set_lang_fr", style="primary"),
                utils.styled_button("German 🇩🇪", "set_lang_de", style="primary")
            ],
            [
                utils.styled_button("Chinese 🇨🇳", "set_lang_zh", style="primary"),
                utils.styled_button("Arabic 🇸🇦", "set_lang_ar", style="primary")
            ],
            [utils.styled_button(utils.get_text("back_to_menu", lang), "menu_settings", style="primary")]
        ]
        
        await event.respond(utils.get_text("select_lang", lang), buttons=buttons)

    @client.on(events.CallbackQuery(pattern="^settings_buy_slots$"))
    async def buy_slots_menu_callback(event):
        await show_purchase_menu(event, event.sender_id)
