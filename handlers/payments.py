import logging
from telethon import events
import database
import config
import utils

logger = logging.getLogger(__name__)

def register_handlers(client):
    
    @client.on(events.CallbackQuery(pattern=r"^(approve|reject)_payment_(.+)$"))
    async def process_payment_decision(event):
        decision = event.pattern_match.group(1)
        payment_id = event.pattern_match.group(2)
        admin_id = event.sender_id
        
        # 1. Verify clicker is an administrator
        global_settings = database.get_global_settings()
        admins = global_settings.get("admins", [])
        
        # Fallback check: also check if user is a chat administrator in the group where clicked
        is_chat_admin = False
        try:
            permissions = await event.client.get_permissions(event.chat_id, admin_id)
            if permissions.is_admin or permissions.is_creator:
                is_chat_admin = True
        except Exception:
            pass
            
        if admin_id not in admins and admin_id not in config.ORIGINAL_ADMIN_IDS and not is_chat_admin:
            await event.answer(utils.get_text("error_not_admin", "en"), alert=True)
            return
            
        # 2. Retrieve payment request
        payment_req = database.get_payment_request(payment_id)
        if not payment_req:
            await event.answer("❌ Payment request not found in database.", alert=True)
            return
            
        if payment_req.get("status") != "pending":
            await event.answer("⚠️ This request has already been processed.", alert=True)
            return
            
        user_id = payment_req["user_id"]
        qty = payment_req["count"]
        user_record = database.get_user(user_id)
        user_lang = user_record.get("language", "en") if user_record else "en"
        
        # 3. Apply decision
        try:
            admin_user = await event.get_sender()
            admin_username = f"@{admin_user.username}" if admin_user and admin_user.username else f"[{admin_id}](tg://user?id={admin_id})"
        except Exception:
            admin_username = f"[{admin_id}](tg://user?id={admin_id})"
        
        import time
        
        if decision == "approve":
            payment_req["status"] = "approved"
            payment_req["processed_by"] = admin_username
            payment_req["processed_at"] = time.time()
            database.save_payment_request(payment_req)
            
            # Update user slot limit with subscription duration
            expires_at = 0.0
            if user_record:
                days = payment_req.get("days", 30)
                plan_name = payment_req.get("plan_name", "Slot Upgrade")
                expires_at = utils.allocate_slots_subscription(
                    user_id, qty, days, plan_name, payment_id
                )
                
            try:
                await event.answer("✅ Request approved!", alert=False)
            except Exception:
                pass
            
            # Edit the log message to confirm approval and update buttons
            try:
                msg = await event.get_message()
                original_text = msg.message or "Payment Verification Request"
                if "Approved by" not in original_text and "Rejected by" not in original_text:
                    status_text = f"\n\n✅ <b>Approved by {admin_username}</b>"
                    updated_text = f"{original_text}{status_text}"
                else:
                    updated_text = original_text
                
                buttons = [[utils.styled_button("✅ ᴄᴏɴғɪʀᴍᴇᴅ", f"payment_info_{payment_id}", style="success")]]
                await event.client.edit_message(event.chat_id, msg.id, updated_text, buttons=buttons)
            except Exception as e:
                logger.error(f"Failed to edit approval log message: {e}")
                
            # Notify User with formatted expiry date
            try:
                import datetime
                expiry_str = datetime.datetime.fromtimestamp(expires_at).strftime('%d %b %Y %H:%M') if expires_at else "N/A"
                notify_text = (
                    f"✅ <b>Your subscription upgrade of {qty} slot(s) has been approved!</b>\n"
                    f"Plan: <b>{payment_req.get('plan_name', 'Upgrade')}</b>\n"
                    f"Expires at: <b>{expiry_str}</b>"
                )
                await client.send_message(user_id, notify_text)
            except Exception as e:
                logger.warning(f"Failed to notify user {user_id} of payment approval: {e}")
                
        elif decision == "reject":
            payment_req["status"] = "rejected"
            payment_req["processed_by"] = admin_username
            payment_req["processed_at"] = time.time()
            database.save_payment_request(payment_req)
            
            try:
                await event.answer("❌ Request rejected.", alert=False)
            except Exception:
                pass
            
            # Edit the log message to confirm rejection and update buttons
            try:
                msg = await event.get_message()
                original_text = msg.message or "Payment Verification Request"
                if "Approved by" not in original_text and "Rejected by" not in original_text:
                    status_text = f"\n\n❌ <b>Rejected by {admin_username}</b>"
                    updated_text = f"{original_text}{status_text}"
                else:
                    updated_text = original_text
                
                buttons = [[utils.styled_button("❌ ʀᴇᴊᴇᴄᴛᴇᴅ", f"payment_info_{payment_id}", style="danger")]]
                await event.client.edit_message(event.chat_id, msg.id, updated_text, buttons=buttons)
            except Exception as e:
                logger.error(f"Failed to edit rejection log message: {e}")
                
            # Notify User
            try:
                notify_text = utils.get_text("payment_rejected_user", user_lang)
                await client.send_message(user_id, notify_text)
            except Exception as e:
                logger.warning(f"Failed to notify user {user_id} of payment rejection: {e}")

    @client.on(events.CallbackQuery(pattern=r"^payment_info_(.+)$"))
    async def view_payment_info_callback(event):
        payment_id = event.pattern_match.group(1)
        admin_id = event.sender_id
        
        # Verify clicker is an administrator
        global_settings = database.get_global_settings()
        admins = global_settings.get("admins", [])
        
        is_chat_admin = False
        try:
            permissions = await event.client.get_permissions(event.chat_id, admin_id)
            if permissions.is_admin or permissions.is_creator:
                is_chat_admin = True
        except Exception:
            pass
            
        if admin_id not in admins and admin_id not in config.ORIGINAL_ADMIN_IDS and not is_chat_admin:
            await event.answer(utils.get_text("error_not_admin", "en"), alert=True)
            return
            
        payment_req = database.get_payment_request(payment_id)
        if not payment_req:
            await event.answer("❌ Payment request details not found.", alert=True)
            return
            
        status = payment_req.get("status", "unknown").capitalize()
        amount = payment_req.get("amount", 0.0)
        qty = payment_req.get("count", 1)
        utr = payment_req.get("utr_code", "N/A")
        user_id = payment_req.get("user_id", "N/A")
        processed_by = payment_req.get("processed_by", "N/A")
        processed_at = payment_req.get("processed_at")
        
        import datetime
        if processed_at:
            if isinstance(processed_at, (int, float)):
                time_str = datetime.datetime.fromtimestamp(processed_at).strftime('%Y-%m-%d %H:%M:%S')
            else:
                time_str = str(processed_at)
        else:
            time_str = "N/A"
            
        details = (
            f"ℹ️ Payment Details\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"ID: {payment_id}\n"
            f"Status: {status}\n"
            f"User ID: {user_id}\n"
            f"Amount: ₹{amount:.2f} (qty: {qty})\n"
            f"UTR: {utr}\n"
            f"Processed By: {processed_by}\n"
            f"Time: {time_str}"
        )
        await event.answer(details, alert=True)
