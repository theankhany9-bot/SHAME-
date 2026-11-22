import json
import os
import re
import sys
import telebot
from telebot import types

# ================= ការកំណត់សំខាន់ៗ =================
BOT_TOKEN = "9151654935:AAFvM0iNx-BfP15pOMicxtARi4YB1F9TXZs"
ADMIN_ID = 6214336913  # ដាក់ Telegram User ID របស់អ្នក (ជាលេខ)
ADMIN_USERNAME = "PUVIN009"  # ដាក់ Username ដោយមិនបាច់មាន @
ABA_GROUP_ID =  -1003803639749  # ដាក់ Group ID របស់ ABA AUTO PAY (ជាលេខអវិជ្ជមាន ឧ. -1003803639749) ឬទុក 0
DATA_FILE = os.path.expanduser("~/bedastore/data.json")
FILES_DIR = os.path.expanduser("~/bedastore/files")
# =================================================

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("❌ ERROR: អ្នកមិនទាន់បានដាក់ BOT_TOKEN ពិតប្រាកដទេ!")
    print("👉 សូមវាយ: nano ~/bedastore/bot.py ហើយប្តូរ YOUR_BOT_TOKEN_HERE ទៅជា Token ពី @BotFather")
    sys.exit(1)

os.makedirs(FILES_DIR, exist_ok=True)
bot = telebot.TeleBot(BOT_TOKEN)
admin_states = {}
user_states = {}


def make_btn(text, callback_data=None, url=None, style=None, custom_emoji_id=None):
    """បង្កើត InlineKeyboardButton ដែលគាំទ្រ style (បៃតង/ខៀវ) និង custom_emoji_id"""
    kwargs = {"text": text}
    if callback_data is not None:
        kwargs["callback_data"] = callback_data
    if url is not None:
        kwargs["url"] = url

    extra = {}
    if style is not None:
        extra["style"] = style
    if custom_emoji_id:
        extra["icon_custom_emoji_id"] = str(custom_emoji_id).strip()

    try:
        return types.InlineKeyboardButton(**kwargs, **extra)
    except TypeError:
        pass

    btn = types.InlineKeyboardButton(**kwargs)
    for k, v in extra.items():
        try:
            setattr(btn, k, v)
        except Exception:
            pass
    return btn


DEFAULT_DATA = {
    "admins": [],
    "balances": {},
    "orders": {},
    "qr_photo_id": None,
    "aba_txns": {},
    "pending_claims": {},
    "home_buttons": {
        "shop": {"label": "🛒 Buy Now / ទិញឥឡូវនេះ", "emoji_id": None, "style": "success"},
        "orders": {"label": "📝 My Order / ការបញ្ជាទិញរបស់ខ្ញុំ", "emoji_id": None, "style": "primary"},
        "balance": {"label": "💰 Balance / តុល្យភាព", "emoji_id": None, "style": "primary"},
        "topup": {"label": "⚡ Top Up Auto / បញ្ចូលទឹកប្រាក់អូតូ", "emoji_id": None, "style": "primary"},
        "contact": {"label": "💬 Contact Admin / ទាក់ទងអ្នកគ្រប់គ្រង", "emoji_id": None, "style": "success"},
    },
    "categories": {
        "esign": {
            "name": "😉𝙀-𝙎𝙄𝙂𝙉-𝘾𝙚𝙧𝙩𝙞𝙛𝙞𝙘𝙖𝙩𝙚 (𝙞𝙋𝘼)",
            "emoji_id": None,
            "products": [
                {"id": "es_1y", "name": "ESing 1Y ធានា 2ខែ", "price": 3.50, "stock": 0, "emoji_id": None, "items": []}
            ],
        },
        "vpn": {
            "name": "😊𝗩𝗣𝗡 𝗣𝗥𝗢𝗫𝗬.𝗩𝗜𝗣 (មានខ្សែរ)",
            "emoji_id": None,
            "products": [
                {"id": "vpn_1h", "name": "1ម៉ោង", "price": 0.18, "stock": 0, "emoji_id": None, "items": []},
                {"id": "vpn_2h", "name": "2ម៉ោង", "price": 0.25, "stock": 0, "emoji_id": None, "items": []},
                {"id": "vpn_1d", "name": "1ថ្ងៃ", "price": 0.90, "stock": 0, "emoji_id": None, "items": []},
            ],
        },
        "fileza": {
            "name": "FILEZA MOD (ប្រើe-sign)",
            "emoji_id": None,
            "products": [
                {"id": "fz_1h", "name": "1ម៉ោង", "price": 0.25, "stock": 0, "emoji_id": None, "items": []}
            ],
        },
        "airlift": {
            "name": "AIRLIFT MOD IPA (ប្រើ e-sign)",
            "emoji_id": None,
            "products": [
                {"id": "al_1h", "name": "1ម៉ោង", "price": 0.25, "stock": 0, "emoji_id": None, "items": []},
                {"id": "al_6h", "name": "6ម៉ោង", "price": 0.70, "stock": 0, "emoji_id": None, "items": []},
                {"id": "al_12h", "name": "12ម៉ោង", "price": 0.90, "stock": 0, "emoji_id": None, "items": []},
            ],
        },
        "innova": {
            "name": "INNOVA CHEAT (មិនប្រើ e-sign)",
            "emoji_id": None,
            "products": [
                {"id": "in_1h", "name": "1ម៉ោង", "price": 0.20, "stock": 0, "emoji_id": None, "items": []},
                {"id": "in_3h", "name": "3ម៉ោង", "price": 0.30, "stock": 0, "emoji_id": None, "items": []},
                {"id": "in_6h", "name": "6ម៉ោង", "price": 0.40, "stock": 0, "emoji_id": None, "items": []},
            ],
        },
        "proxythis": {
            "name": "PROXY THIS.VIP (មិនប្រើ e-sign)",
            "emoji_id": None,
            "products": [
                {"id": "pt_2h", "name": "2ម៉ោង", "price": 0.40, "stock": 0, "emoji_id": None, "items": []},
                {"id": "pt_6h", "name": "6ម៉ោង", "price": 0.70, "stock": 0, "emoji_id": None, "items": []},
                {"id": "pt_12h", "name": "12ម៉ោង", "price": 1.20, "stock": 0, "emoji_id": None, "items": []},
                {"id": "pt_24h", "name": "24ម៉ោង", "price": 1.50, "stock": 0, "emoji_id": None, "items": []},
            ],
        },
        "rezz": {
            "name": "REZZ PANEL (ios & android)",
            "emoji_id": None,
            "products": [
                {"id": "rz_1h", "name": "1ម៉ោង", "price": 1.00, "stock": 0, "emoji_id": None, "items": []}
            ],
        },
        "drip": {
            "name": "DRIP WIRE (ios & android)",
            "emoji_id": None,
            "products": [
                {"id": "dw_1h", "name": "1ម៉ោង", "price": 1.00, "stock": 0, "emoji_id": None, "items": []}
            ],
        },
        "phantom": {
            "name": "PHANTOM (ios & android)",
            "emoji_id": None,
            "products": [
                {"id": "ph_1h", "name": "1ម៉ោង", "price": 1.00, "stock": 0, "emoji_id": None, "items": []}
            ],
        },
        "primeko": {
            "name": "PRIMEKO (ios & android)",
            "emoji_id": None,
            "products": [
                {"id": "pr_1h", "name": "1ម៉ោង", "price": 1.00, "stock": 0, "emoji_id": None, "items": []}
            ],
        },
    },
}


def load_data():
    if not os.path.exists(DATA_FILE):
        save_data(DEFAULT_DATA)
        return json.loads(json.dumps(DEFAULT_DATA))
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        d = json.load(f)
    d.setdefault("admins", [])
    d.setdefault("balances", {})
    d.setdefault("orders", {})
    d.setdefault("qr_photo_id", None)
    d.setdefault("aba_txns", {})
    d.setdefault("pending_claims", {})
    d.setdefault("home_buttons", json.loads(json.dumps(DEFAULT_DATA["home_buttons"])))
    for k, v in DEFAULT_DATA["home_buttons"].items():
        d["home_buttons"].setdefault(k, json.loads(json.dumps(v)))
    for cat in d.get("categories", {}).values():
        cat.setdefault("emoji_id", None)
        for p in cat.get("products", []):
            p.setdefault("items", [])
            p.setdefault("emoji_id", None)
    return d


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_admin(user_id):
    if int(user_id) == int(ADMIN_ID):
        return True
    data = load_data()
    return int(user_id) in [int(x) for x in data.get("admins", [])]


def parse_aba_notification(text):
    if not text:
        return None, None
    amt_match = re.search(r"\$\s*([0-9]+(?:\.[0-9]{1,2})?)", text)
    trx_match = re.search(
        r"(?:Trx\.?\s*ID|លេខប្រតិបត្តិការ)\s*[:：]?\s*([A-Za-z0-9\-]+)",
        text,
        re.IGNORECASE,
    )
    amount = float(amt_match.group(1)) if amt_match else None
    trx_id = trx_match.group(1).strip() if trx_match else None
    return amount, trx_id


def credit_user_for_trx(data, trx_id, uid_str):
    txn = data["aba_txns"].get(trx_id)
    if not txn:
        data["pending_claims"].setdefault(trx_id, [])
        if uid_str not in data["pending_claims"][trx_id]:
            data["pending_claims"][trx_id].append(uid_str)
        save_data(data)
        return "pending", None

    if txn.get("claimed_by"):
        return "already_claimed", txn.get("amount")

    amt = float(txn["amount"])
    txn["claimed_by"] = uid_str
    data["balances"][uid_str] = round(data["balances"].get(uid_str, 0.0) + amt, 2)
    save_data(data)
    return "credited", data["balances"][uid_str]


def main_inline_keyboard():
    data = load_data()
    hb = data["home_buttons"]
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        make_btn(hb["shop"]["label"], callback_data="menu:shop", style=hb["shop"].get("style", "success"), custom_emoji_id=hb["shop"].get("emoji_id")),
        make_btn(hb["orders"]["label"], callback_data="menu:orders", style=hb["orders"].get("style", "primary"), custom_emoji_id=hb["orders"].get("emoji_id")),
        make_btn(hb["balance"]["label"], callback_data="menu:balance", style=hb["balance"].get("style", "primary"), custom_emoji_id=hb["balance"].get("emoji_id")),
        make_btn(hb["topup"]["label"], callback_data="menu:topup", style=hb["topup"].get("style", "primary"), custom_emoji_id=hb["topup"].get("emoji_id")),
        make_btn(hb["contact"]["label"], url=f"https://t.me/{ADMIN_USERNAME}", style=hb["contact"].get("style", "success"), custom_emoji_id=hb["contact"].get("emoji_id")),
    )
    return kb


def categories_keyboard():
    data = load_data()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for cat_key, cat_info in data["categories"].items():
        kb.add(
            make_btn(
                cat_info["name"],
                callback_data=f"cat:{cat_key}",
                style="primary",
                custom_emoji_id=cat_info.get("emoji_id"),
            )
        )
    kb.add(make_btn("⬅️ Back", callback_data="menu:home", style="success"))
    return kb


def products_keyboard(cat_key):
    data = load_data()
    cat_info = data["categories"][cat_key]
    kb = types.InlineKeyboardMarkup(row_width=1)
    for prod in cat_info["products"]:
        label = f"{prod['name']} - ${prod['price']:.2f} [ស្ដុក {prod['stock']}]"
        style = "success" if prod["stock"] > 0 else "primary"
        kb.add(
            make_btn(
                label,
                callback_data=f"buy:{cat_key}:{prod['id']}",
                style=style,
                custom_emoji_id=prod.get("emoji_id"),
            )
        )
    kb.add(make_btn("⬅️ Back", callback_data="menu:shop", style="primary"))
    return kb


def admin_main_keyboard():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        make_btn("📦 ដាក់ស្ដុក / KEY / ហ្វាល់ (ទាំង 10)", callback_data="adm:stock_cats", style="success"),
        make_btn("🗑️ លុបស្ដុកទាំងអស់ (ទាំង 10 → 0)", callback_data="adm:clear_cats", style="primary"),
        make_btn("✨ ដាក់ Premium Emoji (custom_emoji_id)", callback_data="adm:emoji_menu", style="success"),
        make_btn("✏️ កែឈ្មោះប៊ូតុង All", callback_data="adm:rename_menu", style="primary"),
        make_btn("❎ លុបប៊ូតុងផ្សេងៗ (ទាំង 10)", callback_data="adm:del_btn_cats", style="primary"),
        make_btn("👑 Add /Admin តាម ID", callback_data="adm:add_admin", style="success"),
        make_btn("🖼️ កំណត់ QR បង់ប្រាក់", callback_data="adm:set_qr", style="primary"),
        make_btn("💲 កែតម្លៃ / បន្ថែមកញ្ចប់ម៉ោង-Esing", callback_data="adm:price_cats", style="primary"),
        make_btn("💰 បញ្ចូលលុយឱ្យភ្ញៀវ (/addbal)", callback_data="adm:topup_help", style="primary"),
    )
    return kb


def admin_cats_keyboard(mode):
    data = load_data()
    kb = types.InlineKeyboardMarkup(row_width=1)
    for cat_key, cat_info in data["categories"].items():
        total_stock = sum(p.get("stock", 0) for p in cat_info["products"])
        suffix = f" [សរុប: {total_stock}]" if mode == "clear" else ""
        kb.add(
            make_btn(
                f"{cat_info['name']}{suffix}",
                callback_data=f"adm_cat:{mode}:{cat_key}",
                style="primary",
                custom_emoji_id=cat_info.get("emoji_id"),
            )
        )
    kb.add(make_btn("⬅️ Back", callback_data="adm:home", style="success"))
    return kb


def admin_prods_keyboard(mode, cat_key):
    data = load_data()
    cat_info = data["categories"][cat_key]
    kb = types.InlineKeyboardMarkup(row_width=1)

    if mode == "clear":
        kb.add(
            make_btn("🗑️ លុបស្ដុកទាំងអស់ (ចុចម្ដងសល់ 0 ស្ដុក)", callback_data=f"adm_clear_all:{cat_key}", style="success")
        )

    for prod in cat_info["products"]:
        label = f"{prod['name']} - ${prod['price']:.2f} [ស្ដុក {prod['stock']}]"
        if mode == "clear":
            kb.add(make_btn(f"➖ លុបស្ដុកមួយ (-1): {label}", callback_data=f"adm_del_one:{cat_key}:{prod['id']}", style="primary"))
        elif mode == "del_btn":
            kb.add(make_btn(f"❎ {label}", callback_data=f"adm_confirm_del_btn:{cat_key}:{prod['id']}", style="primary"))
        else:
            kb.add(
                make_btn(
                    label,
                    callback_data=f"adm_prod:{mode}:{cat_key}:{prod['id']}",
                    style="success",
                    custom_emoji_id=prod.get("emoji_id"),
                )
            )

    if mode in ("stock", "price"):
        kb.add(make_btn("➕ បន្ថែមកញ្ចប់ម៉ោង / Esing ថ្មី", callback_data=f"adm_addprod:{cat_key}", style="primary"))

    back_cb = "adm:del_btn_cats" if mode == "del_btn" else f"adm:{mode}_cats"
    kb.add(make_btn("⬅️ Back", callback_data=back_cb, style="primary"))
    return kb


def send_home(chat_id, message_id=None):
    text = (
        "✨ <b>BEDA STORE សូមស្វាគមន៍!</b>\n"
        "💎 <i>សេវាកម្មរហ័ស ទំនុកចិត្ត ស្ដុកពិត</i>\n"
        "Please select: / សូមជ្រើសរើស៖"
    )
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, parse_mode="HTML", reply_markup=main_inline_keyboard())
    else:
        bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=main_inline_keyboard())


@bot.message_handler(func=lambda m: m.chat.type in ("group", "supergroup"), content_types=["text"])
def handle_aba_group_message(message):
    if ABA_GROUP_ID != 0 and message.chat.id != ABA_GROUP_ID:
        return
    amount, trx_id = parse_aba_notification(message.text)
    if amount is None or not trx_id:
        return

    data = load_data()
    if trx_id not in data["aba_txns"]:
        data["aba_txns"][trx_id] = {
            "amount": round(amount, 2),
            "claimed_by": None,
            "raw": message.text,
        }
        save_data(data)

    waiting_uids = data["pending_claims"].get(trx_id, [])
    for uid_str in list(waiting_uids):
        status, new_bal = credit_user_for_trx(data, trx_id, uid_str)
        if status == "credited":
            data["pending_claims"][trx_id].remove(uid_str)
            save_data(data)
            try:
                bot.send_message(
                    int(uid_str),
                    f"⚡ <b>AUTO TOP UP ជោគជ័យ!</b>\n\n"
                    f"លេខប្រតិបត្តិការ (Trx. ID)៖ <code>{trx_id}</code>\n"
                    f"ទឹកប្រាក់បានចូល៖ <b>+${amount:.2f}</b>\n"
                    f"សមតុល្យបច្ចុប្បន្ន៖ <b>${new_bal:.2f}</b>",
                    parse_mode="HTML",
                )
            except Exception:
                pass
            break


@bot.message_handler(commands=["start"])
def cmd_start(message):
    data = load_data()
    uid = str(message.from_user.id)
    data["balances"].setdefault(uid, 0.0)
    data["orders"].setdefault(uid, [])
    save_data(data)
    send_home(message.chat.id)


@bot.message_handler(commands=["my_order"])
def cmd_my_order(message):
    data = load_data()
    uid = str(message.from_user.id)
    orders = data["orders"].get(uid, [])
    txt = "📝 <b>My Order / ការបញ្ជាទិញរបស់ខ្ញុំ</b>\n\n" + (
        "\n".join(f"• {o}" for o in orders) if orders else "អ្នកមិនទាន់មានប្រវត្តិបញ្ជាទិញនៅឡើយទេ។"
    )
    kb = types.InlineKeyboardMarkup()
    kb.add(make_btn("⬅️ Back", callback_data="menu:home", style="primary"))
    bot.send_message(message.chat.id, txt, parse_mode="HTML", reply_markup=kb)


@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "⛔ អ្នកមិនមានសិទ្ធិប្រើមុខងារ Admin ទេ។")
        return
    admin_states.pop(message.from_user.id, None)
    bot.send_message(
        message.chat.id,
        "⚡ <b>ADMIN CONTROL CENTER - BEDA STORE</b>\n"
        "✨ <i>គ្រប់គ្រងស្ដុក Emoji ឈ្មោះប៊ូតុង និង Admin យ៉ាងងាយស្រួល</i>",
        parse_mode="HTML",
        reply_markup=admin_main_keyboard(),
    )


@bot.message_handler(commands=["addadmin"])
def cmd_addadmin(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 2:
        bot.reply_to(message, "ប្រើទម្រង់៖ <code>/addadmin USER_ID</code>", parse_mode="HTML")
        return
    try:
        new_aid = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ USER_ID ត្រូវតែជាលេខ។")
        return
    data = load_data()
    if new_aid not in data["admins"]:
        data["admins"].append(new_aid)
        save_data(data)
    bot.reply_to(message, f"👑 បានបន្ថែម Admin ថ្មី៖ <code>{new_aid}</code> រួចរាល់!", parse_mode="HTML")


@bot.message_handler(commands=["addbal"])
def cmd_addbal(message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) != 3:
        bot.reply_to(message, "ប្រើទម្រង់៖ <code>/addbal USER_ID 5.00</code>", parse_mode="HTML")
        return
    try:
        target_uid = str(int(parts[1]))
        amount = float(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ USER_ID ឬ AMOUNT មិនត្រឹមត្រូវទេ។")
        return
    data = load_data()
    data["balances"][target_uid] = round(data["balances"].get(target_uid, 0.0) + amount, 2)
    save_data(data)
    bot.reply_to(
        message,
        f"✅ បានបញ្ចូល <b>${amount:.2f}</b> ទៅកាន់ <code>{target_uid}</code>។ សមតុល្យថ្មី៖ <b>${data['balances'][target_uid]:.2f}</b>",
        parse_mode="HTML",
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = load_data()
    uid = str(call.from_user.id)
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    cb = call.data

    if cb == "menu:home":
        user_states.pop(call.from_user.id, None)
        send_home(chat_id, msg_id)

    elif cb == "menu:shop":
        bot.edit_message_text("🛒 <b>Choose a category:</b>", chat_id, msg_id, parse_mode="HTML", reply_markup=categories_keyboard())

    elif cb == "menu:orders":
        orders = data["orders"].get(uid, [])
        txt = "📝 <b>My Order / ការបញ្ជាទិញរបស់ខ្ញុំ</b>\n\n" + (
            "\n".join(f"• {o}" for o in orders) if orders else "អ្នកមិនទាន់មានប្រវត្តិបញ្ជាទិញនៅឡើយទេ។"
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(make_btn("⬅️ Back", callback_data="menu:home", style="primary"))
        bot.edit_message_text(txt, chat_id, msg_id, parse_mode="HTML", reply_markup=kb)

    elif cb == "menu:balance":
        bal = data["balances"].get(uid, 0.0)
        txt = f"💰 <b>Balance / សមតុល្យ</b>\n\nUser ID: <code>{uid}</code>\nសមតុល្យបច្ចុប្បន្ន៖ <b>${bal:.2f}</b>"
        kb = types.InlineKeyboardMarkup()
        kb.add(make_btn("⬅️ Back", callback_data="menu:home", style="primary"))
        bot.edit_message_text(txt, chat_id, msg_id, parse_mode="HTML", reply_markup=kb)

    elif cb == "menu:topup":
        user_states[call.from_user.id] = {"step": "wait_trx"}
        caption = (
            f"⚡ <b>TOP UP AUTO (ABA AUTO PAY)</b>\n\n"
            f"1️⃣ ស្កេន QR បង់ប្រាក់ទៅកាន់ ABA របស់ហាង\n"
            f"2️⃣ បន្ទាប់ពីវេររួច សូមផ្ញើ <b>លេខប្រតិបត្តិការ (Trx. ID)</b> មកកាន់ Bot នេះ "
            f"ដើម្បីទទួលលុយចូលសមតុល្យដោយស្វ័យប្រវត្តិ!\n\n"
            f"User ID របស់អ្នក៖ <code>{uid}</code>"
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(
            make_btn("💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}", style="success"),
            make_btn("⬅️ Back", callback_data="menu:home", style="primary"),
        )
        if data.get("qr_photo_id"):
            bot.send_photo(chat_id, data["qr_photo_id"], caption=caption, parse_mode="HTML", reply_markup=kb)
        else:
            bot.send_message(chat_id, caption, parse_mode="HTML", reply_markup=kb)

    elif cb.startswith("cat:"):
        cat_key = cb.split(":")[1]
        cat_info = data["categories"][cat_key]
        txt = f"📦 <b>{cat_info['name']}</b>\n\nSelect a product:"
        bot.edit_message_text(txt, chat_id, msg_id, parse_mode="HTML", reply_markup=products_keyboard(cat_key))

    elif cb.startswith("buy:"):
        _, cat_key, prod_id = cb.split(":")
        cat_info = data["categories"][cat_key]
        prod = next((p for p in cat_info["products"] if p["id"] == prod_id), None)
        if not prod:
            return
        if prod["stock"] <= 0:
            bot.answer_callback_query(call.id, "❌ អស់ស្ដុកហើយ! (ស្ដុក 0)", show_alert=True)
            return
        bal = data["balances"].get(uid, 0.0)
        if bal < prod["price"]:
            bot.answer_callback_query(
                call.id,
                f"❌ សមតុល្យមិនគ្រប់គ្រាន់! ត្រូវការ ${prod['price']:.2f} (អ្នកមាន ${bal:.2f})",
                show_alert=True,
            )
            return

        data["balances"][uid] = round(bal - prod["price"], 2)
        prod["stock"] -= 1

        delivered_payload = None
        if prod.get("items"):
            delivered_payload = prod["items"].pop(0)

        order_record = f"{cat_info['name']} - {prod['name']} (${prod['price']:.2f})"
        data["orders"].setdefault(uid, []).append(order_record)
        save_data(data)

        bot.answer_callback_query(call.id, "✅ ទិញបានជោគជ័យ!", show_alert=True)
        bot.send_message(
            chat_id,
            f"✅ <b>ការបញ្ជាទិញជោគជ័យ!</b>\n\n"
            f"ទំនិញ៖ <b>{order_record}</b>\n"
            f"សមតុល្យនៅសល់៖ <b>${data['balances'][uid]:.2f}</b>",
            parse_mode="HTML",
        )

        if delivered_payload:
            if delivered_payload.get("type") == "key":
                bot.send_message(
                    chat_id,
                    f"🔑 <b>KEY របស់អ្នក៖</b>\n<code>{delivered_payload['value']}</code>",
                    parse_mode="HTML",
                )
            elif delivered_payload.get("type") == "file" and os.path.exists(delivered_payload["path"]):
                with open(delivered_payload["path"], "rb") as f_doc:
                    bot.send_document(
                        chat_id,
                        f_doc,
                        caption=f"📦 ហ្វាល់សម្រាប់ <b>{order_record}</b>",
                        parse_mode="HTML",
                    )
        else:
            bot.send_message(
                chat_id,
                f"📩 សូមទាក់ទង @{ADMIN_USERNAME} ជាមួយ User ID: <code>{uid}</code> ដើម្បីទទួលទំនិញ។",
                parse_mode="HTML",
            )

        try:
            bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=products_keyboard(cat_key))
        except Exception:
            pass

    # ================= ADMIN CALLBACKS =================
    elif is_admin(call.from_user.id):
        if cb == "adm:home":
            admin_states.pop(call.from_user.id, None)
            bot.edit_message_text(
                "⚡ <b>ADMIN CONTROL CENTER - BEDA STORE</b>\n"
                "✨ <i>គ្រប់គ្រងស្ដុក Emoji ឈ្មោះប៊ូតុង និង Admin យ៉ាងងាយស្រួល</i>",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=admin_main_keyboard(),
            )

        elif cb == "adm:add_admin":
            admin_states[call.from_user.id] = {"step": "wait_add_admin"}
            current_admins = ", ".join(str(x) for x in ([ADMIN_ID] + data.get("admins", [])))
            bot.send_message(
                chat_id,
                f"👑 <b>ADD ADMIN តាម ID</b>\n\n"
                f"បញ្ជី Admin បច្ចុប្បន្ន៖ <code>{current_admins}</code>\n"
                f"👉 សូមវាយ <b>User ID (ជាលេខ)</b> របស់ Admin ថ្មីដែលអ្នកចង់បន្ថែម៖",
                parse_mode="HTML",
            )

        elif cb == "adm:emoji_menu":
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(
                make_btn("🏠 ដាក់ Premium Emoji លើប៊ូតុងមុខដើម", callback_data="adm_emo_home", style="success"),
                make_btn("📦 ដាក់ Premium Emoji លើមុខងារទាំង 10", callback_data="adm_emo_cats", style="primary"),
                make_btn("⬅️ Back", callback_data="adm:home", style="primary"),
            )
            bot.edit_message_text(
                "✨ <b>ដាក់ PREMIUM EMOJI (custom_emoji_id)</b>\n"
                "ជ្រើសរើសប្រភេទប៊ូតុងដែលអ្នកចង់ដាក់៖",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=kb,
            )

        elif cb == "adm_emo_home":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for h_key, h_info in data["home_buttons"].items():
                kb.add(make_btn(h_info["label"], callback_data=f"adm_set_emo_home:{h_key}", style="primary"))
            kb.add(make_btn("⬅️ Back", callback_data="adm:emoji_menu", style="primary"))
            bot.edit_message_text("🏠 <b>ជ្រើសរើសប៊ូតុងមុខដើម៖</b>", chat_id, msg_id, parse_mode="HTML", reply_markup=kb)

        elif cb.startswith("adm_set_emo_home:"):
            h_key = cb.split(":")[1]
            admin_states[call.from_user.id] = {"step": "wait_emo_home", "h_key": h_key}
            bot.send_message(
                chat_id,
                "✨ <b>ដាក់ Premium Emoji លើប៊ូតុងមុខដើម</b>\n\n"
                "សូមវាយតាមទម្រង់៖\n<code>ឈ្មោះប៊ូតុង | custom_emoji_id</code>\n"
                "ឧទាហរណ៍៖ <code>🛒 ទិញឥឡូវនេះ | 5368324170671202286</code>",
                parse_mode="HTML",
            )

        elif cb == "adm_emo_cats":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for cat_key, cat_info in data["categories"].items():
                kb.add(make_btn(cat_info["name"], callback_data=f"adm_set_emo_cat:{cat_key}", style="primary"))
            kb.add(make_btn("⬅️ Back", callback_data="adm:emoji_menu", style="primary"))
            bot.edit_message_text("📦 <b>ជ្រើសរើសមុខងារ (ទាំង 10) ដើម្បីដាក់ Premium Emoji៖</b>", chat_id, msg_id, parse_mode="HTML", reply_markup=kb)

        elif cb.startswith("adm_set_emo_cat:"):
            cat_key = cb.split(":")[1]
            admin_states[call.from_user.id] = {"step": "wait_emo_cat", "cat_key": cat_key}
            bot.send_message(
                chat_id,
                "✨ <b>ដាក់ Premium Emoji លើមុខងារ</b>\n\n"
                "សូមវាយតាមទម្រង់៖\n<code>ឈ្មោះមុខងារ | custom_emoji_id</code>\n"
                "ឧទាហរណ៍៖ <code>PHANTOM (ios & android) | 5368324170671202286</code>",
                parse_mode="HTML",
            )

        elif cb == "adm:rename_menu":
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(
                make_btn("🏠 កែឈ្មោះប៊ូតុងមុខដើម All", callback_data="adm_ren_home_list", style="success"),
                make_btn("📦 កែឈ្មោះមុខងារទាំង 10 All", callback_data="adm_ren_cat_list", style="primary"),
                make_btn("⬅️ Back", callback_data="adm:home", style="primary"),
            )
            bot.edit_message_text("✏️ <b>កែឈ្មោះប៊ូតុង ALL</b>\nជ្រើសរើសប្រភេទប៊ូតុង៖", chat_id, msg_id, parse_mode="HTML", reply_markup=kb)

        elif cb == "adm_ren_home_list":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for h_key, h_info in data["home_buttons"].items():
                kb.add(make_btn(h_info["label"], callback_data=f"adm_ren_home:{h_key}", style="primary"))
            kb.add(make_btn("⬅️ Back", callback_data="adm:rename_menu", style="primary"))
            bot.edit_message_text("🏠 <b>ចុចលើប៊ូតុងមុខដើមដើម្បីកែឈ្មោះ៖</b>", chat_id, msg_id, parse_mode="HTML", reply_markup=kb)

        elif cb.startswith("adm_ren_home:"):
            h_key = cb.split(":")[1]
            admin_states[call.from_user.id] = {"step": "wait_ren_home", "h_key": h_key}
            bot.send_message(chat_id, "✏️ <b>សូមវាយឈ្មោះថ្មីសម្រាប់ប៊ូតុងនេះ៖</b>", parse_mode="HTML")

        elif cb == "adm_ren_cat_list":
            kb = types.InlineKeyboardMarkup(row_width=1)
            for cat_key, cat_info in data["categories"].items():
                kb.add(make_btn(cat_info["name"], callback_data=f"adm_ren_cat:{cat_key}", style="primary"))
            kb.add(make_btn("⬅️ Back", callback_data="adm:rename_menu", style="primary"))
            bot.edit_message_text("📦 <b>ចុចលើមុខងារ (ទាំង 10) ដើម្បីកែឈ្មោះ៖</b>", chat_id, msg_id, parse_mode="HTML", reply_markup=kb)

        elif cb.startswith("adm_ren_cat:"):
            cat_key = cb.split(":")[1]
            admin_states[call.from_user.id] = {"step": "wait_ren_cat", "cat_key": cat_key}
            bot.send_message(chat_id, "✏️ <b>សូមវាយឈ្មោះថ្មីសម្រាប់មុខងារនេះ៖</b>", parse_mode="HTML")

        elif cb == "adm:del_btn_cats":
            bot.edit_message_text(
                "❎ <b>លុបប៊ូតុងផ្សេងៗ (ទាំង 10)</b>\n"
                "👇 <i>សូមចុចលើមុខងារមួយក្នុងចំណោមទាំង 10៖</i>",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=admin_cats_keyboard("del_btn"),
            )

        elif cb.startswith("adm_confirm_del_btn:"):
            _, cat_key, prod_id = cb.split(":")
            cat_info = data["categories"][cat_key]
            prod = next((p for p in cat_info["products"] if p["id"] == prod_id), None)
            if not prod:
                return
            stock_status = "អស់ស្ដុក" if prod["stock"] <= 0 else f"ស្ដុក {prod['stock']}"
            kb = types.InlineKeyboardMarkup(row_width=1)
            kb.add(
                make_btn("🗑️ យល់ព្រមលុបប៊ូតុងនេះចេញ", callback_data=f"adm_do_del_btn:{cat_key}:{prod_id}", style="success"),
                make_btn("⬅️ ត្រឡប់ក្រោយ / មិនលុប", callback_data=f"adm_cat:del_btn:{cat_key}", style="primary"),
            )
            bot.edit_message_text(
                f"📌 <b>{cat_info['name']}</b>\n"
                f"🔹 ប៊ូតុង៖ <b>{prod['name']} - ${prod['price']:.2f} [{stock_status}]</b>\n\n"
                f"⚠️ <b>បញ្ជាក់៖ តើអ្នកពិតជាចង់លុបប៊ូតុងនេះចេញមែនទេ?</b>\n"
                f"🔻 <i>សញ្ញាបញ្ជាក់លុប៖ ចុច «យល់ព្រមលុបប៊ូតុងនេះចេញ» ខាងក្រោមដើម្បីលុបភ្លាមៗ!</i>",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=kb,
            )

        elif cb.startswith("adm_do_del_btn:"):
            _, cat_key, prod_id = cb.split(":")
            cat_info = data["categories"][cat_key]
            prod = next((p for p in cat_info["products"] if p["id"] == prod_id), None)
            removed_label = f"{prod['name']} - ${prod['price']:.2f}" if prod else prod_id
            cat_info["products"] = [p for p in cat_info["products"] if p["id"] != prod_id]
            save_data(data)
            bot.answer_callback_query(call.id, "✅ បានលុបប៊ូតុងចេញរួចរាល់!", show_alert=True)
            bot.edit_message_text(
                f"✅ <b>បានលុបប៊ូតុង «{removed_label}» ចេញរួចរាល់ហើយ!</b>\n"
                f"📌 <b>{cat_info['name']}</b>",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=admin_prods_keyboard("del_btn", cat_key),
            )

        elif cb == "adm:stock_cats":
            bot.edit_message_text(
                "📦 <b>ជ្រើសរើសមុខងារ (ទាំង 10) ដើម្បីដាក់ស្ដុក / KEY ឬ ហ្វាល់៖</b>",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=admin_cats_keyboard("stock"),
            )
        elif cb == "adm:clear_cats":
            bot.edit_message_text(
                "🗑️ <b>ជ្រើសរើសមុខងារ (ទាំង 10) ដើម្បីលុបស្ដុកទាំងអស់ (0 ស្ដុក) ឬ លុបស្ដុកមួយ (-1)៖</b>",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=admin_cats_keyboard("clear"),
            )
        elif cb == "adm:price_cats":
            bot.edit_message_text(
                "💲 <b>ជ្រើសរើសមុខងារ (ទាំង 10) ដើម្បីកែតម្លៃ / បន្ថែមម៉ោង-Esing៖</b>",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=admin_cats_keyboard("price"),
            )
        elif cb == "adm:set_qr":
            admin_states[call.from_user.id] = {"step": "wait_qr"}
            bot.send_message(
                chat_id,
                "🖼️ <b>កំណត់ QR បង់ប្រាក់</b>\n\n👉 សូមផ្ញើ <b>រូបភាព QR Code</b> មកកាន់ Bot ឥឡូវនេះ៖",
                parse_mode="HTML",
            )
        elif cb == "adm:topup_help":
            bot.edit_message_text(
                "💰 <b>បញ្ចូលលុយឱ្យភ្ញៀវ</b>\n\nវាយពាក្យបញ្ជាក្នុងឆាត៖\n<code>/addbal USER_ID ចំនួនលុយ</code>\nឧទាហរណ៍៖ <code>/addbal 123456789 5.00</code>",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=admin_main_keyboard(),
            )
        elif cb.startswith("adm_cat:"):
            _, mode, cat_key = cb.split(":")
            cat_info = data["categories"][cat_key]
            prompt_txt = (
                f"❎ <b>{cat_info['name']}</b>\n🔻 <i>ចុចលើប៊ូតុងខាងក្រោមដើម្បីមើល និងបញ្ជាក់លុប៖</i>"
                if mode == "del_btn"
                else f"📌 <b>{cat_info['name']}</b>\nជ្រើសរើសមុខងារ៖"
            )
            bot.edit_message_text(
                prompt_txt,
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=admin_prods_keyboard(mode, cat_key),
            )
        elif cb.startswith("adm_clear_all:"):
            cat_key = cb.split(":")[1]
            cat_info = data["categories"][cat_key]
            for prod in cat_info["products"]:
                prod["stock"] = 0
                prod["items"] = []
            save_data(data)
            bot.answer_callback_query(call.id, "✅ បានលុបស្ដុកទាំងអស់សល់ 0 ស្ដុកហើយ!", show_alert=True)
            bot.edit_message_text(
                f"🗑️ <b>{cat_info['name']}</b>\n✅ ស្ដុកទាំងអស់ត្រូវបានលុបសល់ <b>0 ស្ដុក</b> រួចរាល់!",
                chat_id,
                msg_id,
                parse_mode="HTML",
                reply_markup=admin_prods_keyboard("clear", cat_key),
            )
        elif cb.startswith("adm_del_one:"):
            _, cat_key, prod_id = cb.split(":")
            cat_info = data["categories"][cat_key]
            prod = next((p for p in cat_info["products"] if p["id"] == prod_id), None)
            if not prod:
                return
            if prod["stock"] > 0:
                prod["stock"] -= 1
                if prod.get("items"):
                    prod["items"].pop()
                save_data(data)
                bot.answer_callback_query(call.id, f"➖ បានលុបស្ដុកមួយ! នៅសល់ {prod['stock']} ស្ដុក", show_alert=False)
            else:
                bot.answer_callback_query(call.id, "⚠️ ស្ដុកមាន 0 រួចហើយ!", show_alert=False)
            try:
                bot.edit_message_reply_markup(chat_id, msg_id, reply_markup=admin_prods_keyboard("clear", cat_key))
            except Exception:
                pass
        elif cb.startswith("adm_prod:"):
            _, mode, cat_key, prod_id = cb.split(":")
            cat_info = data["categories"][cat_key]
            prod = next((p for p in cat_info["products"] if p["id"] == prod_id), None)
            if not prod:
                return
            if mode == "stock":
                admin_states[call.from_user.id] = {
                    "step": "wait_payload",
                    "cat_key": cat_key,
                    "prod_id": prod_id,
                }
                bot.send_message(
                    chat_id,
                    f"🔑/📁 <b>ដាក់ស្ដុកសម្រាប់ {cat_info['name']} → {prod['name']} (${prod['price']:.2f})</b>\n"
                    f"ស្ដុកបច្ចុប្បន្ន៖ <b>{prod['stock']} ស្ដុក</b>\n\n"
                    f"👉 សូមផ្ញើ <b>KEY (អត្ថបទ)</b> ឬ <b>ផ្ញើហ្វាល់ (Document/IPA/ZIP/TXT)</b> មកកាន់ Bot ឥឡូវនេះ៖",
                    parse_mode="HTML",
                )
            elif mode == "price":
                admin_states[call.from_user.id] = {
                    "step": "wait_price",
                    "cat_key": cat_key,
                    "prod_id": prod_id,
                }
                bot.send_message(
                    chat_id,
                    f"💲 <b>កែតម្លៃសម្រាប់ {prod['name']}</b> (បច្ចុប្បន្ន៖ ${prod['price']:.2f})\n"
                    f"👉 សូមវាយតម្លៃថ្មី (ឧទាហរណ៍៖ <code>0.25</code> ឬ <code>3.50</code>)៖",
                    parse_mode="HTML",
                )
        elif cb.startswith("adm_addprod:"):
            cat_key = cb.split(":")[1]
            admin_states[call.from_user.id] = {
                "step": "wait_new_prod",
                "cat_key": cat_key,
            }
            bot.send_message(
                chat_id,
                "➕ <b>បន្ថែមកញ្ចប់ម៉ោង / Esing ថ្មី</b>\n\n"
                "សូមវាយតាមទម្រង់៖ <code>ឈ្មោះកញ្ចប់ | តម្លៃ</code>\n"
                "ឧទាហរណ៍៖ <code>6ម៉ោង | 0.40</code> ឬ <code>Esing 1Y ធានា 2ខែ | 3.50</code>",
                parse_mode="HTML",
            )


@bot.message_handler(func=lambda m: m.chat.type == "private", content_types=["text", "document", "photo"])
def handle_private_inputs(message):
    sender_id = message.from_user.id
    uid_str = str(sender_id)

    if is_admin(sender_id) and sender_id in admin_states:
        state = admin_states[sender_id]
        data = load_data()
        step = state.get("step")

        if step == "wait_add_admin" and message.content_type == "text":
            try:
                new_aid = int(message.text.strip())
            except ValueError:
                bot.reply_to(message, "❌ សូមវាយ User ID ជាលេខសុទ្ធ (ឧ. <code>6214336913</code>)", parse_mode="HTML")
                return
            if new_aid not in data["admins"] and new_aid != ADMIN_ID:
                data["admins"].append(new_aid)
                save_data(data)
            admin_states.pop(sender_id, None)
            bot.reply_to(message, f"👑 <b>បានបន្ថែម Admin ថ្មី៖</b> <code>{new_aid}</code> រួចរាល់!", parse_mode="HTML")
            return

        if step == "wait_emo_home" and message.content_type == "text":
            raw = message.text.strip()
            if "|" in raw:
                lbl, eid = [x.strip() for x in raw.split("|", 1)]
            else:
                h_key = state["h_key"]
                lbl = data["home_buttons"][h_key]["label"]
                eid = raw
            h_key = state["h_key"]
            data["home_buttons"][h_key]["label"] = lbl
            data["home_buttons"][h_key]["emoji_id"] = eid
            save_data(data)
            admin_states.pop(sender_id, None)
            bot.reply_to(message, f"✨ <b>បានកំណត់ Premium Emoji រួចរាល់!</b>\nឈ្មោះ៖ <b>{lbl}</b>\nEmoji ID៖ <code>{eid}</code>", parse_mode="HTML")
            return

        if step == "wait_emo_cat" and message.content_type == "text":
            raw = message.text.strip()
            cat_key = state["cat_key"]
            if "|" in raw:
                cname, eid = [x.strip() for x in raw.split("|", 1)]
            else:
                cname = data["categories"][cat_key]["name"]
                eid = raw
            data["categories"][cat_key]["name"] = cname
            data["categories"][cat_key]["emoji_id"] = eid
            save_data(data)
            admin_states.pop(sender_id, None)
            bot.reply_to(message, f"✨ <b>បានកំណត់ Premium Emoji រួចរាល់!</b>\nមុខងារ៖ <b>{cname}</b>\nEmoji ID៖ <code>{eid}</code>", parse_mode="HTML")
            return

        if step == "wait_ren_home" and message.content_type == "text":
            new_lbl = message.text.strip()
            h_key = state["h_key"]
            data["home_buttons"][h_key]["label"] = new_lbl
            save_data(data)
            admin_states.pop(sender_id, None)
            bot.reply_to(message, f"✏️ <b>បានកែឈ្មោះប៊ូតុងទៅជា៖</b> <b>{new_lbl}</b>", parse_mode="HTML")
            return

        if step == "wait_ren_cat" and message.content_type == "text":
            new_cname = message.text.strip()
            cat_key = state["cat_key"]
            data["categories"][cat_key]["name"] = new_cname
            save_data(data)
            admin_states.pop(sender_id, None)
            bot.reply_to(message, f"✏️ <b>បានកែឈ្មោះមុខងារទៅជា៖</b> <b>{new_cname}</b>", parse_mode="HTML")
            return

        if step == "wait_qr" and message.content_type == "photo":
            file_id = message.photo[-1].file_id
            data["qr_photo_id"] = file_id
            save_data(data)
            admin_states.pop(sender_id, None)
            bot.send_photo(
                message.chat.id,
                file_id,
                caption="✅ <b>បានកំណត់រូប QR បង់ប្រាក់រួចរាល់!</b>",
                parse_mode="HTML",
            )
            return

        if step == "wait_payload":
            payload = None
            if message.content_type == "document":
                doc = message.document
                file_info = bot.get_file(doc.file_id)
                downloaded = bot.download_file(file_info.file_path)
                safe_name = f"{doc.file_unique_id}_{doc.file_name or 'file.bin'}"
                save_path = os.path.join(FILES_DIR, safe_name)
                with open(save_path, "wb") as f:
                    f.write(downloaded)
                payload = {"type": "file", "path": save_path, "name": doc.file_name or safe_name}
            elif message.content_type == "text" and message.text.strip():
                payload = {"type": "key", "value": message.text.strip()}
            else:
                bot.reply_to(message, "❌ សូមផ្ញើ KEY (អត្ថបទ) ឬ ហ្វាល់។")
                return

            state["step"] = "wait_stock_qty"
            state["payload"] = payload
            admin_states[sender_id] = state
            bot.reply_to(
                message,
                "✅ បានទទួល KEY/ហ្វាល់រួចរាល់!\n"
                "👉 <b>ដាក់ប៉ុន្មានស្ដុក?</b> (ឧទាហរណ៍៖ វាយលេខ <code>20</code> នឹងចេញ <b>20 ស្ដុក</b>)៖",
                parse_mode="HTML",
            )
            return

        elif step == "wait_stock_qty" and message.content_type == "text":
            try:
                qty = int(message.text.strip())
                if qty < 0:
                    raise ValueError()
            except ValueError:
                bot.reply_to(message, "❌ សូមវាយចំនួនស្ដុកជាលេខគត់ ឧទាហរណ៍៖ <code>20</code>", parse_mode="HTML")
                return

            cat_key = state["cat_key"]
            prod_id = state["prod_id"]
            payload = state["payload"]
            cat_info = data["categories"][cat_key]
            prod = next((p for p in cat_info["products"] if p["id"] == prod_id), None)
            if prod:
                prod["stock"] = qty
                prod["items"] = [payload for _ in range(qty)]
                save_data(data)
                bot.reply_to(
                    message,
                    f"✅ <b>រួចរាល់!</b>\n"
                    f"មុខងារ៖ <b>{cat_info['name']}</b>\n"
                    f"កញ្ចប់៖ <b>{prod['name']} - ${prod['price']:.2f}</b>\n"
                    f"ចំនួនស្ដុក៖ <b>{qty} ស្ដុក</b>",
                    parse_mode="HTML",
                )
            admin_states.pop(sender_id, None)
            return

        elif step == "wait_price" and message.content_type == "text":
            try:
                new_price = float(message.text.strip().replace("$", ""))
                if new_price < 0:
                    raise ValueError()
            except ValueError:
                bot.reply_to(message, "❌ សូមវាយតម្លៃជាលេខ ឧទាហរណ៍៖ <code>0.25</code>", parse_mode="HTML")
                return

            cat_key = state["cat_key"]
            prod_id = state["prod_id"]
            cat_info = data["categories"][cat_key]
            prod = next((p for p in cat_info["products"] if p["id"] == prod_id), None)
            if prod:
                prod["price"] = round(new_price, 2)
                save_data(data)
                bot.reply_to(
                    message,
                    f"✅ បានកែតម្លៃ <b>{prod['name']}</b> ទៅជា <b>${prod['price']:.2f}</b>",
                    parse_mode="HTML",
                )
            admin_states.pop(sender_id, None)
            return

        elif step == "wait_new_prod" and message.content_type == "text":
            raw = message.text.strip()
            if "|" not in raw:
                bot.reply_to(message, "❌ វាយតាមទម្រង់៖ <code>ឈ្មោះកញ្ចប់ | តម្លៃ</code> (ឧ. <code>6ម៉ោង | 0.40</code>)", parse_mode="HTML")
                return
            pname, pprice_str = [x.strip() for x in raw.split("|", 1)]
            try:
                pprice = round(float(pprice_str.replace("$", "")), 2)
            except ValueError:
                bot.reply_to(message, "❌ តម្លៃមិនត្រឹមត្រូវទេ។")
                return
            cat_key = state["cat_key"]
            cat_info = data["categories"][cat_key]
            new_id = f"{cat_key}_{len(cat_info['products']) + 1}"
            cat_info["products"].append({
                "id": new_id,
                "name": pname,
                "price": pprice,
                "stock": 0,
                "emoji_id": None,
                "items": [],
            })
            save_data(data)
            bot.reply_to(
                message,
                f"✅ បានបន្ថែមកញ្ចប់ថ្មី <b>{pname} - ${pprice:.2f} [ស្ដុក 0]</b> ក្នុង <b>{cat_info['name']}</b>!",
                parse_mode="HTML",
            )
            admin_states.pop(sender_id, None)
            return

    ustate = user_states.get(sender_id)
    if ustate and ustate.get("step") == "wait_trx" and message.content_type == "text":
        trx_id = message.text.strip()
        if not re.fullmatch(r"[A-Za-z0-9\-]{6,40}", trx_id):
            bot.reply_to(message, "❌ សូមផ្ញើលេខប្រតិបត្តិការ (Trx. ID) ឱ្យត្រឹមត្រូវ (ឧ. <code>179501128093292</code>)", parse_mode="HTML")
            return

        data = load_data()
        status, info_val = credit_user_for_trx(data, trx_id, uid_str)
        user_states.pop(sender_id, None)

        if status == "credited":
            bot.reply_to(
                message,
                f"✅ <b>TOP UP AUTO ជោគជ័យ!</b>\n\n"
                f"លេខប្រតិបត្តិការ៖ <code>{trx_id}</code>\n"
                f"សមតុល្យបច្ចុប្បន្នរបស់អ្នក៖ <b>${info_val:.2f}</b>",
                parse_mode="HTML",
            )
        elif status == "already_claimed":
            bot.reply_to(message, "❌ លេខប្រតិបត្តិការ (Trx. ID) នេះត្រូវបានប្រើរួចហើយ។")
        else:
            bot.reply_to(
                message,
                f"⏳ បានកត់ត្រា Trx. ID: <code>{trx_id}</code>។ "
                f"ប្រព័ន្ធកំពុងរង់ចាំសារជូនដំណឹងពី ABA AUTO PAY ដើម្បីបញ្ចូលលុយស្វ័យប្រវត្តិ...",
                parse_mode="HTML",
            )


try:
    me = bot.get_me()
    bot.set_my_commands([
        types.BotCommand("start", "ចាប់ផ្តើម / ម៉ឺនុយដើម"),
        types.BotCommand("my_order", "ការបញ្ជាទិញរបស់ខ្ញុំ"),
        types.BotCommand("admin", "ផ្ទាំងគ្រប់គ្រង Admin"),
    ])
    print(f"✅ Connected as @{me.username}")
    bot.infinity_polling(skip_pending=True, timeout=20, long_polling_timeout=20)
except Exception as e:
    print(f"❌ Bot failed to start: {e}")
