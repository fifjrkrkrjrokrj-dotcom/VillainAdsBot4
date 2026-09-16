with open('handlers/my_bots.py', 'r', encoding='utf-8') as f:
    content = f.read()

split_mark = '            success_count = sum(1 for r in results if not isinstance(r, Exception) and r[1])'
parts = content.split(split_mark)
if len(parts) < 2:
    print('Failed to split')
    exit(1)

head = parts[0] + r'''            success_count = sum(1 for r in results if not isinstance(r, Exception) and r[1])
            flash = f"<blockquote><b>» ❌ ᴀʟʟ sʟᴏᴛs : ʟᴇᴀᴠᴇ ɢʀᴏᴜᴘ(s) ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n• <b>sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴇғᴛ ɪɴsᴛᴀɴᴄᴇs :</b> <b>{success_count}</b></blockquote>"
            await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
            return
'''

tail = r'''
        elif action == "WAITING_FOR_ALL_BROADCAST":
            broadcast_msg = event.text
            sessions = get_effective_sessions(user_id)
            for s in sessions:
                s.setdefault("settings", {})["broadcast_msg"] = broadcast_msg
                database.save_session(s)
                if userbot_manager.is_bot_running(s["phone"]):
                    userbot_manager.reload_bot_settings(s["phone"])
            flash = "<blockquote><b>» ✉️ ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ ғᴏʀ ᴀʟʟ ʙᴏᴛs!</b></blockquote>"
            await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
            return
            
        elif action == "WAITING_FOR_ALL_WELCOME":
            welcome_msg = event.text
            sessions = get_effective_sessions(user_id)
            for s in sessions:
                s.setdefault("settings", {})["welcome_msg"] = welcome_msg
                database.save_session(s)
                if userbot_manager.is_bot_running(s["phone"]):
                    userbot_manager.reload_bot_settings(s["phone"])
            flash = "<blockquote><b>» 👋 ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ ғᴏʀ ᴀʟʟ ʙᴏᴛs!</b></blockquote>"
            await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
            return

        elif action == "WAITING_FOR_ALL_MULTI_WELCOME":
            msgs = [x.strip() for x in event.text.split(",") if x.strip()]
            if not msgs:
                await event.reply("<blockquote><b>» ❌ ɪɴᴘᴜᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return
            sessions = get_effective_sessions(user_id)
            for s in sessions:
                s.setdefault("settings", {})["welcome_messages"] = msgs
                database.save_session(s)
                if userbot_manager.is_bot_running(s["phone"]):
                    userbot_manager.reload_bot_settings(s["phone"])
            flash = "<blockquote><b>» 👋 ᴍᴜʟᴛɪᴘʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴜᴘᴅᴀᴛᴇᴅ ғᴏʀ ᴀʟʟ ʙᴏᴛs!</b></blockquote>"
            await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
            return
 
        elif action == "WAITING_FOR_ALL_CLONE_TARGET":
            target = event.text.strip()
            if not target:
                await event.reply("<blockquote><b>» ❌ ᴛᴀʀɢᴇᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ. ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ.</b></blockquote>", parse_mode="html")
                return
                
            clone_type = state.get("clone_type", "complete")
            sessions = get_effective_sessions(user_id)
            running_phones = [s["phone"] for s in sessions if userbot_manager.is_bot_running(s["phone"])]
            if not running_phones:
                await event.reply("<blockquote><b>» ❌ ɴᴏ ᴜsᴇʀʙᴏᴛs ᴀʀᴇ ᴄᴜʀʀᴇɴᴛʟʏ ʀᴜɴɴɪɴɢ. ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ʏᴏᴜʀ ᴜsᴇʀʙᴏᴛs ғɪʀsᴛ.</b></blockquote>", parse_mode="html")
                return
                
            progress_msg = await event.reply(f"<blockquote><b>» ⏳ ᴄʟᴏɴɪɴɢ ᴘʀᴏғɪʟᴇ ᴅᴇᴛᴀɪʟs ᴏɴ {len(running_phones)} ʀᴜɴɴɪɴɢ ᴜsᴇʀʙᴏᴛs...</b></blockquote>", parse_mode="html")
            
            async def _clone_concurrent(phone_num):
                return await userbot_manager.clone_profile(phone_num, target, clone_type=clone_type, fallback_client=client)
                
            results = await asyncio.gather(*[_clone_concurrent(p) for p in running_phones], return_exceptions=True)
            try:
                await progress_msg.delete()
            except Exception:
                pass
            
            success_count = 0
            for res in results:
                if not isinstance(res, Exception) and res[0]:
                    success_count += 1
                    
            flash = f"<blockquote><b>» 👤 ᴘʀᴏғɪʟᴇ ᴄʟᴏɴɪɴɢ ʀᴇsᴜʟᴛs</b>\n• ᴄʟᴏɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴏɴ {success_count}/{len(running_phones)} ᴜsᴇʀʙᴏᴛs!</blockquote>"
            await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
            return
 
        elif action == "WAITING_FOR_ALL_NAME":
            new_name = event.text.strip()
            if not new_name:
                await event.reply("<blockquote><b>» ❌ ɴᴀᴍᴇ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return
                
            sessions = get_effective_sessions(user_id)
            if not sessions:
                await event.reply("<blockquote><b>» ❌ ɴᴏ ᴜsᴇʀʙᴏᴛ sʟᴏᴛs ғᴏᴜɴᴅ.</b></blockquote>", parse_mode="html")
                return
                
            progress_msg = await event.reply(f"<blockquote><b>» ⏳ ᴜᴘᴅᴀᴛɪɴɢ ɴᴀᴍᴇ ᴛᴏ '{new_name}' ᴀᴄʀᴏss ᴀʟʟ sʟᴏᴛs...</b></blockquote>", parse_mode="html")
            
            async def _update_one_name(s):
                return await userbot_manager.set_userbot_name(s["phone"], new_name)
                
            results = await asyncio.gather(*[_update_one_name(s) for s in sessions], return_exceptions=True)
            try:
                await progress_msg.delete()
            except Exception:
                pass
                
            success_count = sum(1 for r in results if not isinstance(r, Exception) and r[0])
            flash = f"<blockquote><b>» ✏️ ᴜᴘᴅᴀᴛᴇᴅ ɴᴀᴍᴇ ᴛᴏ '{new_name}' ғᴏʀ {success_count}/{len(sessions)} ᴜsᴇʀʙᴏᴛs!</b></blockquote>"
            await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
            return
 
        elif action == "WAITING_FOR_ALL_CUSTOM_INTERVAL":
            val_str = event.text.strip()
            if val_str.isdigit() and int(val_str) >= 60:
                val = int(val_str)
                sessions = get_effective_sessions(user_id)
                for s in sessions:
                    s.setdefault("settings", {})["broadcast_interval"] = val
                    database.save_session(s)
                    userbot_manager.reload_bot_settings(s["phone"])
                flash = f"<blockquote><b>» ⏱️ ɪɴᴛᴇʀᴠᴀʟ ᴜᴘᴅᴀᴛᴇᴅ ᴛᴏ {val}s ғᴏʀ ᴀʟʟ ʙᴏᴛs!</b></blockquote>"
                await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
                return
            else:
                await event.reply(utils.get_text("interval_invalid", lang))
                return
 
        elif action == "WAITING_FOR_ALL_CUSTOM_DELAY":
            val_str = event.text.strip()
            if val_str.isdigit() and 2 <= int(val_str) <= 300:
                val = int(val_str)
                sessions = get_effective_sessions(user_id)
                for s in sessions:
                    s.setdefault("settings", {})["inter_group_delay"] = val
                    database.save_session(s)
                    userbot_manager.reload_bot_settings(s["phone"])
                flash = f"<blockquote><b>» ⏱️ ɪɴᴛᴇʀ-ɢʀᴏᴜᴘ ᴅᴇʟᴀʏ ᴜᴘᴅᴀᴛᴇᴅ ᴛᴏ {val}s ғᴏʀ ᴀʟʟ ʙᴏᴛs!</b></blockquote>"
                await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
                return
            else:
                await event.reply(utils.get_text("inter_delay_invalid", lang))
                return
 
        elif action == "WAITING_FOR_ALL_MULTI_MSG":
            raw_text = event.text
            msgs = [m.strip() for m in raw_text.split(",") if m.strip()]
            if msgs:
                sessions = get_effective_sessions(user_id)
                for s in sessions:
                    s.setdefault("settings", {})["broadcast_messages"] = msgs
                    database.save_session(s)
                    if userbot_manager.is_bot_running(s["phone"]):
                        userbot_manager.reload_bot_settings(s["phone"])
                flash = f"<blockquote><b>» ✅ ʀᴀɴᴅᴏᴍɪᴢᴇᴅ ᴍᴇssᴀɢᴇs ᴜᴘᴅᴀᴛᴇᴅ ғᴏʀ ᴀʟʟ ʙᴏᴛs ({len(msgs)} ᴍsɢs)!</b></blockquote>"
                await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
                return
            else:
                await event.reply("<blockquote><b>» ❌ ᴍᴇssᴀɢᴇ ʟɪsᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ. sᴇᴘᴀʀᴀᴛᴇ ᴡɪᴛʜ ᴄᴏᴍᴍᴀs (,).</b></blockquote>", parse_mode="html")
                return

        elif action == "WAITING_FOR_ALL_AUTO_REPLY_SINGLE":
            reply_msg = event.text.strip()
            if reply_msg:
                sessions = get_effective_sessions(user_id)
                for s in sessions:
                    s.setdefault("settings", {})["auto_reply_msg"] = reply_msg
                    s["settings"]["auto_reply"] = True
                    database.save_session(s)
                    if userbot_manager.is_bot_running(s["phone"]):
                        userbot_manager.reload_bot_settings(s["phone"])
                flash = "<blockquote><b>» 💬 sɪɴɢʟᴇ ᴛᴀɢ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ ғᴏʀ ᴀʟʟ ʙᴏᴛs!</b></blockquote>"
                await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
                return
            else:
                await event.reply("<blockquote><b>» ❌ ᴍᴇssᴀɢᴇ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return

        elif action == "WAITING_FOR_ALL_AUTO_REPLY_MSGS":
            raw_text = event.text
            msgs = [m.strip() for m in raw_text.split(",") if m.strip()]
            if msgs:
                sessions = get_effective_sessions(user_id)
                for s in sessions:
                    s.setdefault("settings", {})["auto_reply_messages"] = msgs
                    s["settings"]["auto_reply"] = True
                    database.save_session(s)
                    if userbot_manager.is_bot_running(s["phone"]):
                        userbot_manager.reload_bot_settings(s["phone"])
                flash = f"<blockquote><b>» ✅ ᴛᴀɢ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇs ᴜᴘᴅᴀᴛᴇᴅ ғᴏʀ ᴀʟʟ ʙᴏᴛs ({len(msgs)} ᴍsɢs)!</b></blockquote>"
                await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
                return
            else:
                await event.reply(utils.get_text("auto_reply_invalid", lang))
                return

        elif action == "WAITING_FOR_ALL_RUN_TIMER":
            raw_text = event.text.strip().lower()
            try:
                if raw_text.endswith("m"):
                    minutes = float(raw_text[:-1])
                    seconds = minutes * 60
                else:
                    hours = float(raw_text)
                    seconds = hours * 3600
                    
                if seconds == 0:
                    sessions = get_effective_sessions(user_id)
                    for s in sessions:
                        if "run_expiry" in s:
                            del s["run_expiry"]
                        database.save_session(s)
                    flash = "<blockquote><b>» ✅ ʀᴜɴ ᴛɪᴍᴇʀ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴀʟʟ ʙᴏᴛs!</b></blockquote>"
                else:
                    import time
                    expiry_time = time.time() + seconds
                    sessions = get_effective_sessions(user_id)
                    for s in sessions:
                        s["run_expiry"] = expiry_time
                        database.save_session(s)
                    flash = f"<blockquote><b>» ✅ ʀᴜɴ ᴛɪᴍᴇʀ sᴇᴛ! ᴀʟʟ ʙᴏᴛs ᴡɪʟʟ sᴛᴏᴘ ᴀғᴛᴇʀ {raw_text}.</b></blockquote>"
                
                await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
                return
            except ValueError:
                await event.reply("<blockquote><b>» ❌ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ (ᴇ.ɢ., 2 ғᴏʀ ʜᴏᴜʀs, 30m ғᴏʀ ᴍɪɴᴜᴛᴇs, 0 ᴛᴏ ᴅɪsᴀʙʟᴇ).</b></blockquote>", parse_mode="html")
                return

        elif action == "WAITING_FOR_ALL_SONG":
            # Extract media info using extract_media_info
            media_obj, audio_title, audio_duration = extract_media_info(event.message)
            is_audio_file = False
            local_file_path = None
            
            if media_obj:
                is_audio_file = True
                progress_msg = await event.reply("📥 <b>Downloading uploaded media...</b>\n━━━━━━━━━━━━━━━━━━━━\n📊 Progress: `[░░░░░░░░░░] 0.0%`")
                os.makedirs("downloads", exist_ok=True)
                try:
                    local_file_path = await client.download_media(
                        event.message, 
                        file="downloads/",
                        progress_callback=lambda c, t: download_progress_sync(c, t, progress_msg, "Downloading uploaded media")
                    )
                except Exception as dl_err:
                    logger.error(f"Failed to download media: {dl_err}")
                    await progress_msg.edit(f"❌ <b>Failed to download media:</b> {dl_err}")
                    return
                finally:
                    try:
                        await progress_msg.delete()
                    except Exception:
                        pass
            
            query = None
            if not is_audio_file:
                query = event.text.strip() if event.text else ""
                if not query:
                    await event.reply("<blockquote><b>» ❌ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ sᴏɴɢ ǫᴜᴇʀʏ ᴏʀ sᴇɴᴅ ᴀɴ ᴀᴜᴅɪᴏ ғɪʟᴇ.</b></blockquote>", parse_mode="html")
                    return
                    
            sessions = get_effective_sessions(user_id)
            running_phones = [s["phone"] for s in sessions if userbot_manager.is_bot_running(s["phone"])]
            
            vc_bots = []
            for p in running_phones:
                bot_obj = userbot_manager._running_bots[p]
                if getattr(bot_obj, "current_vc_chat_id", None):
                    vc_bots.append((p, bot_obj))
                    
            if not vc_bots:
                await event.reply("<blockquote><b>» ❌ ɴᴏ ʀᴜɴɴɪɴɢ ᴜsᴇʀʙᴏᴛs ᴀʀᴇ ɪɴ ᴀ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.</b></blockquote>", parse_mode="html")
                return
                
            progress_msg = await event.reply(f"<blockquote><b>» ⏳ sᴛᴀʀᴛɪɴɢ ᴘʟᴀʏ ᴏɴ {len(vc_bots)} ᴜsᴇʀʙᴏᴛs ᴄᴏɴᴄᴜʀʀᴇɴᴛʟʏ...</b></blockquote>", parse_mode="html")
            
            async def _play_one_all_concurrent(p, bot_obj):
                return await bot_obj.play_song(query, play_type="audio", local_file=local_file_path, title=audio_title, duration=audio_duration)
                
            results = await asyncio.gather(*[_play_one_all_concurrent(p, bot) for p, bot in vc_bots], return_exceptions=True)
            try:
                await progress_msg.delete()
            except Exception:
                pass
            
            success_count = 0
            song_info_global = None
            for res in results:
                if not isinstance(res, Exception) and res[0]:
                    success_count += 1
                    song_info_global = res[2]
                    
            if success_count > 0 and song_info_global:
                caption = (
                    f"> 🎵 <b>Now Playing (All Slots)</b>\n"
                    f"> \n"
                    f"> • <b>Title</b>: `{song_info_global['title']}`\n"
                    f"> • <b>Duration</b>: `{song_info_global['duration']}s`\n"
                    f"> • <b>Requested by</b>: [{user.get('name', 'User')}](tg://user?id={user_id})\n"
                    f"> \n"
                    f"> 🎧 _Playing on {success_count} userbot(s) in Voice Chats!_"
                )
                sent_msg = None
                try:
                    sent_msg = await event.reply(caption, file=song_info_global["thumb"])
                except Exception:
                    try:
                        sent_msg = await event.reply(caption)
                    except Exception:
                        pass
                
                if sent_msg:
                    async def auto_delete():
                        await asyncio.sleep(song_info_global["duration"])
                        try:
                            await client.delete_messages(event.chat_id, sent_msg.id)
                        except Exception:
                            pass
                        file_path = song_info_global.get("file_path")
                        if file_path and os.path.exists(file_path) and "silence.mp3" not in file_path:
                            try:
                                os.remove(file_path)
                                logger.info(f"Deleted local song file: {file_path}")
                            except Exception as e:
                                logger.warning(f"Could not delete local file {file_path}: {e}")
                    asyncio.create_task(auto_delete())
                    
                flash = f"<blockquote><b>» ✅ ᴘʟᴀʏɪɴɢ sᴏɴɢ:</b> {song_info_global['title']}</blockquote>"
            else:
                flash = "<blockquote><b>» ❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴘʟᴀʏ sᴏɴɢ ᴏɴ ᴀɴʏ ᴜsᴇʀʙᴏᴛ.</b></blockquote>"
                
            await show_all_slots_dashboard(event, user_id, flash_message=flash)
            return

        # --- All Slots Group / Channel Actions ---
        elif action in ("WAITING_FOR_ALL_VC_GRP_LINK", "WAITING_FOR_ALL_VC_MULTI_GRP_LINK"):
            raw_text = (getattr(event, "raw_text", None) or event.text or "").strip()
            raw_text = re.sub(r'<[^>]+>', '', raw_text).strip()
            if not raw_text:
                await event.reply("<blockquote><b>» ❌ ɢʀᴏᴜᴘ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return
                
            strip_chars = "\'\"`()[]{}<> \t\n\r"
            links = [re.sub(r'<[^>]+>', '', x).strip().strip(strip_chars) for x in re.split(r'[,;\n\r\t]+', raw_text) if x.strip()]
            links = [x for x in links if x]
            if not links:
                await event.reply("<blockquote><b>» ❌ ɴᴏ ᴠᴀʟɪᴅ ʟɪɴᴋs ᴘʀᴏᴠɪᴅᴇᴅ.</b></blockquote>", parse_mode="html")
                return
                
            sessions = get_effective_sessions(user_id)
            if not sessions:
                await event.reply("<blockquote><b>» ❌ ɴᴏ ᴜsᴇʀʙᴏᴛ sᴇssɪᴏɴs ғᴏᴜɴᴅ.</b></blockquote>", parse_mode="html")
                return
                
            # Auto-start stopped bots if needed
            for s in sessions:
                if not userbot_manager.is_bot_running(s["phone"]):
                    try:
                        await userbot_manager.start_userbot(s["phone"], user_id)
                    except Exception as start_err:
                        logger.warning(f"Could not auto-start {s['phone']}: {start_err}")
                        
            running_phones = [s["phone"] for s in sessions if userbot_manager.is_bot_running(s["phone"])]
            if not running_phones:
                await event.reply("<blockquote><b>» ❌ ɴᴏɴᴇ ᴏғ ᴛʜᴇ ᴜsᴇʀʙᴏᴛs ᴀʀᴇ ʀᴜɴɴɪɴɢ.</b></blockquote>", parse_mode="html")
                return
                
            progress_msg = await event.reply(
                f"⏳ <b>ᴊᴏɪɴɪɴɢ {len(links)} ɢʀᴏᴜᴘ(s) ᴀᴄʀᴏss {len(running_phones)} ᴜsᴇʀʙᴏᴛ(s)...</b>",
                parse_mode="html"
            )
            
            total_joins_success = 0
            total_joins_failed = 0
            
            for p_idx, phone_num in enumerate(running_phones, 1):
                bot_obj = userbot_manager._running_bots.get(phone_num)
                if not bot_obj:
                    continue
                for l_idx, link in enumerate(links, 1):
                    try:
                        ok = await join_channel_single(bot_obj.client, link)
                        if ok:
                            total_joins_success += 1
                        else:
                            total_joins_failed += 1
                    except Exception as e:
                        logger.warning(f"Error bot {phone_num} joining {link}: {e}")
                        total_joins_failed += 1
                    if l_idx < len(links):
                        await asyncio.sleep(1.2)
                try:
                    await progress_msg.edit(
                        f"⏳ <b>ᴊᴏɪɴɪɴɢ ɢʀᴏᴜᴘs... (ʙᴏᴛ {p_idx}/{len(running_phones)})</b>\n\n"
                        f"✅ <b>sᴜᴄᴄᴇssғᴜʟ :</b> {total_joins_success} | ❌ <b>ғᴀɪʟᴇᴅ :</b> {total_joins_failed}",
                        parse_mode="html"
                    )
                except Exception:
                    pass
                    
            try:
                await progress_msg.delete()
            except Exception:
                pass
                
            flash = (
                f"<blockquote><b>» 📚 ᴀʟʟ sʟᴏᴛs : ɢʀᴏᴜᴘ ᴊᴏɪɴɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n"
                f"• <b>ᴛᴏᴛᴀʟ ᴜsᴇʀʙᴏᴛs :</b> <b>{len(running_phones)}</b>\n"
                f"• <b>ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘ ʟɪɴᴋs :</b> <b>{len(links)}</b>\n"
                f"• <b>✅ sᴜᴄᴄᴇssғᴜʟ ᴊᴏɪɴs :</b> <b>{total_joins_success}</b>\n"
                f"• <b>❌ ғᴀɪʟᴇᴅ ᴊᴏɪɴs :</b> <b>{total_joins_failed}</b></blockquote>"
            )
            await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
            return

        elif action == "WAITING_FOR_ALL_LEAVE_GRP":
            raw_text = event.text.strip()
            if not raw_text:
                await event.reply("<blockquote><b>» ❌ ɪɴᴘᴜᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return
            strip_chars = "\'\"`()[]{}<> \t\n\r"
            links = [x.strip().strip(strip_chars) for x in re.split(r'[,;\n\r\t]+', raw_text) if x.strip()]
            sessions = get_effective_sessions(user_id)
            running_phones = [s["phone"] for s in sessions if userbot_manager.is_bot_running(s["phone"])]
            if not running_phones:
                await event.reply("<blockquote><b>» ❌ ɴᴏ ʀᴜɴɴɪɴɢ ᴜsᴇʀʙᴏᴛs ғᴏᴜɴᴅ.</b></blockquote>", parse_mode="html")
                return
            progress_msg = await event.reply("⏳ <b>ʟᴇᴀᴠɪɴɢ ɢʀᴏᴜᴘ(s) ᴀᴄʀᴏss ᴀʟʟ ᴜsᴇʀʙᴏᴛs...</b>", parse_mode="html")
            left_count = 0
            for phone_num in running_phones:
                bot_obj = userbot_manager._running_bots.get(phone_num)
                if not bot_obj:
                    continue
                for link in links:
                    try:
                        ok = await leave_chat_single(bot_obj.client, link)
                        if ok:
                            left_count += 1
                    except Exception:
                        pass
            try:
                await progress_msg.delete()
            except Exception:
                pass
            flash = f"<blockquote><b>» ❌ ᴀʟʟ sʟᴏᴛs : ʟᴇᴀᴠᴇ ɢʀᴏᴜᴘ(s) ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n• <b>sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴇғᴛ ɪɴsᴛᴀɴᴄᴇs :</b> <b>{left_count}</b></blockquote>"
            await show_all_slots_dashboard(event, user_id, flash_message=flash, fetch_all=is_system_all_mode(user_id))
            return
            
        # --- Handle Single Bot Actions ---
        if not phone:
            await event.reply("<blockquote><b>» ❌ sᴇssɪᴏɴ ɴᴏᴛ ғᴏᴜɴᴅ.</b></blockquote>", parse_mode="html")
            return
            
        sess = database.get_session(phone)
        if not sess or not is_session_owner_or_admin(sess, user_id):
            await event.reply("<blockquote><b>» ❌ sᴇssɪᴏɴ ᴇʀʀᴏʀ.</b></blockquote>", parse_mode="html")
            return
            
        # 1. Broadcast Message
        if action == "WAITING_FOR_BROADCAST":
            sess["settings"]["broadcast_msg"] = event.text
            database.save_session(sess)
            flash = "<blockquote><b>» ✉️ ʙʀᴏᴀᴅᴄᴀsᴛ ᴍᴇssᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b></blockquote>"
            
        elif action == "WAITING_FOR_RUN_TIMER":
            raw_text = event.text.strip().lower()
            try:
                if raw_text.endswith("m"):
                    minutes = float(raw_text[:-1])
                    seconds = minutes * 60
                else:
                    hours = float(raw_text)
                    seconds = hours * 3600
                    
                if seconds == 0:
                    if "run_expiry" in sess:
                        del sess["run_expiry"]
                    database.save_session(sess)
                    flash = "<blockquote><b>» ✅ ʀᴜɴ ᴛɪᴍᴇʀ ᴅɪsᴀʙʟᴇᴅ!</b></blockquote>"
                else:
                    import time
                    expiry_time = time.time() + seconds
                    sess["run_expiry"] = expiry_time
                    database.save_session(sess)
                    flash = f"<blockquote><b>» ✅ ʀᴜɴ ᴛɪᴍᴇʀ sᴇᴛ! ʙᴏᴛ ᴡɪʟʟ sᴛᴏᴘ ᴀғᴛᴇʀ {raw_text}.</b></blockquote>"
            except ValueError:
                await event.reply("<blockquote><b>» ❌ ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ ɴᴜᴍʙᴇʀ (ᴇ.ɢ., 2 ғᴏʀ ʜᴏᴜʀs, 30m ғᴏʀ ᴍɪɴᴜᴛᴇs, 0 ᴛᴏ ᴅɪsᴀʙʟᴇ).</b></blockquote>", parse_mode="html")
                return
            
        # 2. Welcome Message
        elif action == "WAITING_FOR_WELCOME":
            sess["settings"]["welcome_msg"] = event.text
            database.save_session(sess)
            flash = "<blockquote><b>» 👋 ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b></blockquote>"
            
        # 2.b Multiple Welcome Messages
        elif action == "WAITING_FOR_MULTI_WELCOME":
            msgs = [x.strip() for x in event.text.split(",") if x.strip()]
            if not msgs:
                await event.reply("<blockquote><b>» ❌ ɪɴᴘᴜᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return
            sess["settings"]["welcome_messages"] = msgs
            database.save_session(sess)
            flash = "<blockquote><b>» 👋 ᴍᴜʟᴛɪᴘʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴜᴘᴅᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b></blockquote>"
            
        # 2.5 Join VC Link
        elif action == "WAITING_FOR_VC_LINK":
            link = event.text.strip()
            if not link:
                await event.reply("<blockquote><b>» ❌ ᴄʜᴀᴛ ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ/ʟɪɴᴋ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return
                
            if not userbot_manager.is_bot_running(phone):
                await event.reply("<blockquote><b>» ❌ ᴜsᴇʀʙᴏᴛ ɪs ɴᴏᴛ ʀᴜɴɴɪɴɢ. ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ɪᴛ ғɪʀsᴛ.</b></blockquote>", parse_mode="html")
                return
                
            progress_msg = await event.reply("⏳ <b>ᴊᴏɪɴɪɴɢ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>", parse_mode="html")
            bot_obj = userbot_manager._running_bots[phone]
            success, msg = await bot_obj.join_voice_chat(link)
            try:
                await progress_msg.delete()
            except Exception:
                pass
            
            if success:
                flash = f"<blockquote><b>» ✅ ᴊᴏɪɴᴇᴅ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ!</b>\n{msg}</blockquote>"
            else:
                flash = f"<blockquote><b>» ❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴠᴄ:</b> {msg}</blockquote>"

        # 2.6 Join Group via Link or Multiple Links (Single Bot)
        elif action in ("WAITING_FOR_VC_GRP_LINK", "WAITING_FOR_VC_MULTI_GRP_LINK"):
            raw_text = (getattr(event, "raw_text", None) or event.text or "").strip()
            raw_text = re.sub(r'<[^>]+>', '', raw_text).strip()
            if not raw_text:
                await event.reply("<blockquote><b>» ❌ ɢʀᴏᴜᴘ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return
                
            if not userbot_manager.is_bot_running(phone):
                await event.reply("<blockquote><b>» ❌ ᴜsᴇʀʙᴏᴛ ɪs ɴᴏᴛ ʀᴜɴɴɪɴɢ.</b></blockquote>", parse_mode="html")
                return
                
            strip_chars = "\'\"`()[]{}<> \t\n\r"
            links = [re.sub(r'<[^>]+>', '', x).strip().strip(strip_chars) for x in re.split(r'[,;\n\r\t]+', raw_text) if x.strip()]
            links = [x for x in links if x]
            if not links:
                await event.reply("<blockquote><b>» ❌ ɴᴏ ᴠᴀʟɪᴅ ʟɪɴᴋs ᴘʀᴏᴠɪᴅᴇᴅ.</b></blockquote>", parse_mode="html")
                return
                
            bot_obj = userbot_manager._running_bots[phone]
            
            if len(links) == 1:
                link = links[0]
                progress_msg = await event.reply("⏳ <b>ᴊᴏɪɴɪɴɢ ɢʀᴏᴜᴘ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>", parse_mode="html")
                success = await join_channel_single(bot_obj.client, link)
                try:
                    await progress_msg.delete()
                except Exception:
                    pass
                if success:
                    flash = f"<blockquote><b>» ✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴊᴏɪɴᴇᴅ ɢʀᴏᴜᴘ!</b>\n\n• <b>ᴛᴀʀɢᴇᴛ :</b> <code>{link}</code>\n• <i>ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴄʟɪᴄᴋ '🎙️ ᴊᴏɪɴ ᴠᴄ' ᴛᴏ ᴇɴᴛᴇʀ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.</i></blockquote>"
                else:
                    flash = f"<blockquote><b>» ❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ ɢʀᴏᴜᴘ</b>\n\n• <b>ᴛᴀʀɢᴇᴛ :</b> <code>{link}</code>\n• <i>ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʟɪɴᴋ ɪs ᴠᴀʟɪᴅ ᴏʀ ɴᴏᴛ ᴇxᴘɪʀᴇᴅ.</i></blockquote>"
            else:
                progress_msg = await event.reply(f"⏳ <b>ᴊᴏɪɴɪɴɢ {len(links)} ɢʀᴏᴜᴘs... (0/{len(links)})</b>", parse_mode="html")
                success_count = 0
                failed_count = 0
                for idx, link in enumerate(links, 1):
                    try:
                        ok = await join_channel_single(bot_obj.client, link)
                        if ok:
                            success_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        logger.warning(f"Error joining {link}: {e}")
                        failed_count += 1
                    try:
                        await progress_msg.edit(
                            f"⏳ <b>ᴊᴏɪɴɪɴɢ {len(links)} ɢʀᴏᴜᴘs... ({idx}/{len(links)})</b>\n\n"
                            f"✅ <b>sᴜᴄᴄᴇss :</b> {success_count} | ❌ <b>ғᴀɪʟᴇᴅ :</b> {failed_count}",
                            parse_mode="html"
                        )
                    except Exception:
                        pass
                    if idx < len(links):
                        await asyncio.sleep(1.5)
                        
                try:
                    await progress_msg.delete()
                except Exception:
                    pass
                    
                flash = (
                    f"<blockquote><b>» 📚 ᴍᴜʟᴛɪᴘʟᴇ ɢʀᴏᴜᴘs ᴊᴏɪɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n"
                    f"• <b>ᴛᴏᴛᴀʟ ʟɪɴᴋs :</b> <b>{len(links)}</b>\n"
                    f"• <b>✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴊᴏɪɴᴇᴅ :</b> <b>{success_count}</b>\n"
                    f"• <b>❌ ғᴀɪʟᴇᴅ :</b> <b>{failed_count}</b></blockquote>"
                )
                
            await show_bot_dashboard(event, phone, user_id, flash_message=flash)
            return

        # 2.7 Leave Group via Link/ID (Single Bot)
        elif action == "WAITING_FOR_LEAVE_GRP":
            raw_text = (getattr(event, "raw_text", None) or event.text or "").strip()
            raw_text = re.sub(r'<[^>]+>', '', raw_text).strip()
            if not raw_text:
                await event.reply("<blockquote><b>» ❌ ɪɴᴘᴜᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return
                
            if not userbot_manager.is_bot_running(phone):
                await event.reply("<blockquote><b>» ❌ ᴜsᴇʀʙᴏᴛ ɪs ɴᴏᴛ ʀᴜɴɴɪɴɢ.</b></blockquote>", parse_mode="html")
                return
                
            strip_chars = "\'\"`()[]{}<> \t\n\r"
            links = [re.sub(r'<[^>]+>', '', x).strip().strip(strip_chars) for x in re.split(r'[,;\n\r\t]+', raw_text) if x.strip()]
            links = [x for x in links if x]
            if not links:
                await event.reply("<blockquote><b>» ❌ ɴᴏ ᴠᴀʟɪᴅ ʟɪɴᴋs ᴘʀᴏᴠɪᴅᴇᴅ.</b></blockquote>", parse_mode="html")
                return
                
            progress_msg = await event.reply("⏳ <b>ʟᴇᴀᴠɪɴɢ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>", parse_mode="html")
            bot_obj = userbot_manager._running_bots[phone]
            left_cnt = 0
            for lk in links:
                try:
                    if await leave_chat_single(bot_obj.client, lk):
                        left_cnt += 1
                except Exception:
                    pass
            try:
                await progress_msg.delete()
            except Exception:
                pass
            
            if left_cnt > 0:
                flash = f"<blockquote><b>» ✅ sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴇғᴛ {left_cnt} ɢʀᴏᴜᴘ(s)!</b></blockquote>"
            else:
                flash = "<blockquote><b>» ❌ ғᴀɪʟᴇᴅ ᴛᴏ ʟᴇᴀᴠᴇ ɢʀᴏᴜᴘ(s). ᴄʜᴇᴄᴋ ʟɪɴᴋ/ɪᴅ.</b></blockquote>"
                
            await show_bot_dashboard(event, phone, user_id, flash_message=flash)
            return
                
        # 3. Clone Profile
        elif action == "WAITING_FOR_CLONE_TARGET":
            target = event.text.strip()
            if not target:
                await event.reply("<blockquote><b>» ❌ ᴛᴀʀɢᴇᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ. ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴜsᴇʀɴᴀᴍᴇ/ɪᴅ.</b></blockquote>", parse_mode="html")
                return
                
            clone_type = state.get("clone_type", "complete")
            progress_msg = await event.reply("<blockquote><b>» ⏳ ᴄʟᴏɴɪɴɢ ᴘʀᴏғɪʟᴇ ᴅᴇᴛᴀɪʟs, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b></blockquote>", parse_mode="html")
            success, msg = await userbot_manager.clone_profile(phone, target, clone_type=clone_type, fallback_client=client)
            try:
                await progress_msg.delete()
            except Exception:
                pass
            
            if success:
                flash = f"<blockquote><b>» ✅ ᴘʀᴏғɪʟᴇ sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʟᴏɴᴇᴅ!</b>\n{msg}</blockquote>"
            else:
                flash = f"<blockquote><b>» ❌ ᴄʟᴏɴɪɴɢ ғᴀɪʟᴇᴅ:</b>\n{msg}</blockquote>"

        # 4. Change Name
        elif action == "WAITING_FOR_NAME":
            new_name = event.text.strip()
            if not new_name:
                await event.reply("<blockquote><b>» ❌ ɴᴀᴍᴇ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return
            progress_msg = await event.reply("<blockquote><b>» ⏳ ᴜᴘᴅᴀᴛɪɴɢ ᴀᴄᴄᴏᴜɴᴛ ɴᴀᴍᴇ...</b></blockquote>", parse_mode="html")
            success, msg = await userbot_manager.set_userbot_name(phone, new_name)
            try:
                await progress_msg.delete()
            except Exception:
                pass
            if success:
                flash = f"<blockquote><b>» ✏️ {msg}</b></blockquote>"
            else:
                flash = f"<blockquote><b>» ❌ {msg}</b></blockquote>"
                
        # 5. Custom Interval
        elif action == "WAITING_FOR_CUSTOM_INTERVAL":
            val_str = event.text.strip()
            if val_str.isdigit() and int(val_str) >= 60:
                val = int(val_str)
                sess["settings"]["broadcast_interval"] = val
                database.save_session(sess)
                flash = f"<blockquote><b>» ⏱️ ɪɴᴛᴇʀᴠᴀʟ ᴜᴘᴅᴀᴛᴇᴅ ᴛᴏ {val}s</b></blockquote>"
            else:
                await event.reply(utils.get_text("interval_invalid", lang))
                return

        # 5.5 Custom Delay
        elif action == "WAITING_FOR_CUSTOM_DELAY":
            val_str = event.text.strip()
            if val_str.isdigit() and 2 <= int(val_str) <= 300:
                val = int(val_str)
                sess.setdefault("settings", {})["inter_group_delay"] = val
                database.save_session(sess)
                flash = f"<blockquote><b>» ⏱️ ɪɴᴛᴇʀ-ɢʀᴏᴜᴘ ᴅᴇʟᴀʏ ᴜᴘᴅᴀᴛᴇᴅ ᴛᴏ {val}s</b></blockquote>"
            else:
                await event.reply(utils.get_text("inter_delay_invalid", lang))
                return

        # 5.6 Multiple Messages
        elif action == "WAITING_FOR_MULTI_MSG":
            raw_text = event.text
            msgs = [m.strip() for m in raw_text.split(",") if m.strip()]
            if msgs:
                sess.setdefault("settings", {})["broadcast_messages"] = msgs
                database.save_session(sess)
                flash = f"<blockquote><b>» ✅ sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ {len(msgs)} ᴍᴇssᴀɢᴇs ғᴏʀ ʀᴀɴᴅᴏᴍɪᴢᴇᴅ ʙʀᴏᴀᴅᴄᴀsᴛ!</b></blockquote>"
            else:
                await event.reply("<blockquote><b>» ❌ ᴍᴇssᴀɢᴇ ʟɪsᴛ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ. sᴇᴘᴀʀᴀᴛᴇ ᴡɪᴛʜ ᴄᴏᴍᴍᴀs (,).</b></blockquote>", parse_mode="html")
                return

        # 5.6.4 Single Auto Reply Message
        elif action == "WAITING_FOR_AUTO_REPLY_SINGLE":
            msg_text = event.text.strip()
            if msg_text:
                sess.setdefault("settings", {})["auto_reply_msg"] = msg_text
                sess["settings"]["auto_reply"] = True
                database.save_session(sess)
                userbot_manager.reload_bot_settings(phone)
                flash = "<blockquote><b>» 💬 sɪɴɢʟᴇ ᴛᴀɢ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇ ᴜᴘᴅᴀᴛᴇᴅ!</b></blockquote>"
            else:
                await event.reply("<blockquote><b>» ❌ ᴍᴇssᴀɢᴇ ᴄᴀɴɴᴏᴛ ʙᴇ ᴇᴍᴘᴛʏ.</b></blockquote>", parse_mode="html")
                return

        # 5.6.5 Auto Reply Messages
        elif action == "WAITING_FOR_AUTO_REPLY_MSGS":
            raw_text = event.text
            msgs = [m.strip() for m in raw_text.split(",") if m.strip()]
            if msgs:
                sess.setdefault("settings", {})["auto_reply_messages"] = msgs
                sess["settings"]["auto_reply"] = True  # Auto-enable when messages are set
                database.save_session(sess)
                userbot_manager.reload_bot_settings(phone)
                flash = f"<blockquote><b>» ✅ ᴛᴀɢ ᴀᴜᴛᴏ-ʀᴇᴘʟʏ ᴍᴇssᴀɢᴇs ᴜᴘᴅᴀᴛᴇᴅ ({len(msgs)} ᴍsɢs)!</b></blockquote>"
            else:
                await event.reply(utils.get_text("auto_reply_invalid", lang))
                return
 
        # 5.7 Play Song query
        elif action == "WAITING_FOR_SONG":
            # Extract media info using extract_media_info
            media_obj, audio_title, audio_duration = extract_media_info(event.message)
            is_audio_file = False
            local_file_path = None
            
            if media_obj:
                is_audio_file = True
                progress_msg = await event.reply("📥 <b>Downloading uploaded media...</b>\n━━━━━━━━━━━━━━━━━━━━\n📊 Progress: `[░░░░░░░░░░] 0.0%`")
                os.makedirs("downloads", exist_ok=True)
                try:
                    local_file_path = await client.download_media(
                        event.message, 
                        file="downloads/",
                        progress_callback=lambda c, t: download_progress_sync(c, t, progress_msg, "Downloading uploaded media")
                    )
                except Exception as dl_err:
                    logger.error(f"Failed to download media: {dl_err}")
                    await progress_msg.edit(f"❌ <b>Failed to download media:</b> {dl_err}")
                    return
                finally:
                    try:
                        await progress_msg.delete()
                    except Exception:
                        pass
            
            query = None
            if not is_audio_file:
                query = event.text.strip() if event.text else ""
                if not query:
                    await event.reply("<blockquote><b>» ❌ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ sᴏɴɢ ǫᴜᴇʀʏ ᴏʀ sᴇɴᴅ ᴀɴ ᴀᴜᴅɪᴏ ғɪʟᴇ.</b></blockquote>", parse_mode="html")
                    return
                
            if not userbot_manager.is_bot_running(phone):
                await event.reply("<blockquote><b>» ❌ ᴜsᴇʀʙᴏᴛ ɪs ɴᴏᴛ ʀᴜɴɴɪɴɢ.</b></blockquote>", parse_mode="html")
                return
                
            bot_obj = userbot_manager._running_bots[phone]
            progress_msg = await event.reply("⏳ <b>ᴘʟᴀʏɪɴɢ sᴏɴɢ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>", parse_mode="html")
            success, msg, song_info = await bot_obj.play_song(query, play_type="audio", local_file=local_file_path, title=audio_title, duration=audio_duration)
            try:
                await progress_msg.delete()
            except Exception:
                pass
            
            if success and song_info:
                caption = (
                    f"> 🎵 <b>Now Playing</b>\n"
                    f"> \n"
                    f"> • <b>Title</b>: `{song_info['title']}`\n"
                    f"> • <b>Duration</b>: `{song_info['duration']}s`\n"
                    f"> • <b>Requested by</b>: [{user.get('name', 'User')}](tg://user?id={user_id})\n"
                    f"> \n"
                    f"> 🎧 _Playing in voice chat for userbot `{phone}`_"
                )
                sent_msg = None
                try:
                    sent_msg = await event.reply(caption, file=song_info["thumb"])
                except Exception:
                    try:
                        sent_msg = await event.reply(caption)
                    except Exception:
                        pass
                
                if sent_msg:
                    async def auto_delete():
                        await asyncio.sleep(song_info["duration"])
                        try:
                            await client.delete_messages(event.chat_id, sent_msg.id)
                        except Exception:
                            pass
                        file_path = song_info.get("file_path")
                        if file_path and os.path.exists(file_path) and "silence.mp3" not in file_path:
                            try:
                                os.remove(file_path)
                                logger.info(f"Deleted local song file: {file_path}")
                            except Exception as e:
                                logger.warning(f"Could not delete local file {file_path}: {e}")
                    asyncio.create_task(auto_delete())
                    
                flash = f"<blockquote><b>» ✅ ᴘʟᴀʏɪɴɢ sᴏɴɢ:</b> {song_info['title']}</blockquote>"
            else:
                flash = f"<blockquote><b>» ❌ ғᴀɪʟᴇᴅ ᴛᴏ ᴘʟᴀʏ:</b> {msg}</blockquote>"
                
        # Return to dashboard showing updated stats and flash notification
        userbot_manager.reload_bot_settings(phone)
        await show_bot_dashboard(event, phone, user_id, flash_message=flash)
'''

with open('handlers/my_bots.py', 'w', encoding='utf-8') as f:
    f.write(head + tail)
print('Successfully rewritten handlers/my_bots.py')
