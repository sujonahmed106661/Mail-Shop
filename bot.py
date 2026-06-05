"""
╔══════════════════════════════════════════════════════════════════╗
║          NEROXA SHOP BOT — Professional Reply Keyboard UI        ║
║   aiogram 3.x  |  Firebase  |  100% Reply Keyboard Navigation   ║
╚══════════════════════════════════════════════════════════════════╝
"""

import asyncio
import html as html_lib
import io
import json
import logging
import os
import random
import re
import sys
import time
import uuid
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests as _requests
import urllib.request as _urllib_request

import firebase_admin
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
import pyotp
import pytz
from aiohttp import web
from aiogram import BaseMiddleware, Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    Document,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    TelegramObject,
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv
from firebase_admin import credentials, db as fdb, storage

load_dotenv()

# ╔══════════════════════════════════════════════════════════════════╗
# ║              ⚙️  CONFIGURATION — আপনার মান এখানে বসান           ║
# ╚══════════════════════════════════════════════════════════════════╝

# ── ১. Telegram ─────────────────────────────────────────────────────
BOT_TOKEN_VALUE          = "8727550482:AAGoinHbp-0Svxa3djY8UDqQkwFFrIwltQk"
ADMIN_IDS_VALUE          = "8502686983"

# ── ২. Firebase ─────────────────────────────────────────────────────
FIREBASE_DB_URL_VALUE    = "https://mail-shop-bot-5f4f3-default-rtdb.asia-southeast1.firebasedatabase.app/"
FIREBASE_BUCKET_VALUE    = "mail-shop-bot-5f4f3.appspot.com"

# Firebase credentials dict (private key \n properly handled)
_FIREBASE_CREDS = {
    "type": "service_account",
    "project_id": "mail-shop-bot-5f4f3",
    "private_key_id": "4f863ad97d1b1fcd30b9ac1a7921c0d005e1128b",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCnDt3kAAJ7PIgF\n9b2QrAYEkf/gd0XCA34ziu8GHmuvxepMTbxmLCfZIOOflosyG/KDWZqpq546QPyQ\nmG3KmdGoCr7zPQAIv+fXCWd31kXV7IDDmRVDVoPdn7s3x44hca0O4XrB2m7wsWC0\nTCxE8/FXnHHzWS2p0Sqd896Da7LNsVXFsr6ic4JX8FGlE1ebYQiMSroUejOjk2tt\n8qV/eXgPT3WbLXWQM6cPz7Z+x4AbAwGvxeybtwoR6kwRwUH+SH47fZJ3ryKY9wVK\n9pJRMEXa9uC1r4rMUfyZZ0+fHzqSTKixVZ1cYY8AG1GOomJR7NgZ+oQpy1UA2L3B\nzTPo5TBdAgMBAAECggEAP6cXfsdOKryuq26t0xDonhcvIszvZHRGQsdeObuflnLX\nykkYTunmKQIyGN2YnfguGEQs/RcqC9I1Kbcapkajrt6hUTbd63eLk9C+ftfC9jbN\n/Tk389dkGS7CfAdqLW4N3YymZHShLs63JRudBozYWWR/upQxJPJQxaxlDTgdAehB\nRqJZtKAa0SP40MpcVcqZaWpom4wmgToUSQD2ZqnpVFesNnfrY6+0glcIfakFxTFA\nxI1+1nL0i+I0TmMy1GSQH1ABZrvN3tGrceiHfqC/v7VaLBeBbjphsiNOtM+DYw2C\nFiFOEm0VFyFk+MCLvVhm5xFdZ5bNkPvQcT7h0OgVFQKBgQDRILZKgufinJIUlAgE\n9KVyvQ/3cASjLZMehDCtZXgr3gcsbuZYuZUii5nRYfvZ3TYpgBD5JiXQmEhgaL5E\nRv+Iuw+tpzi5gyzqfFK6xr6N3YZsFUrAExAItehBbRbib1h4i6F2a0oZu0dggaMA\npqSs+ZPTEB6EdmSJ/4k6P49e4wKBgQDMgEnHt6eYyfLPNbFkWDGVF3n5JvVC5slY\nVTcqJRgrb2NoGfoPljICdeIRJcK5z2B2PeSL6mukIJEN4pyk6xLS3z9qJzECXXHV\nTb5EZ253CiFNS7TFlHcryXI7X9NXCKYJVlrthg9vkQ5V2IspOSgJV334EHobbt9X\nIJRhVK0XvwKBgQChhk2mMYPfQSWHZWroQPnFLIg3irraOmpGiL18QEJYR45s4F9k\nKjspSoAM/ExlUvnxhewWNEPC4MwOQviqjdfzCOCsNNuYVdwMZOgVQUqPEoov0yZA\nQrkAsVfpqNOjI3NG8DpO18GNLFyOCrMW3p+UxtRJkkqv7y3qdIfOiKc5FwKBgHI1\nn37roa0h8/onWXfaDW7fmp48VLNVYtNzXAisiNAROGo2P8KetjVLksLS3Oqa15uR\nu2cst4sFKR2hFqzAIFYmmir10lgoyd8/uOhI/5d5z9l0U3QZE2kf6y0fuk8cJGaI\nlOWcflhnoaLt+eI+6o41D8QPp7JUfGUTa+rjuHvPAoGBANCqwghW7dAit/itf9lC\ngfdJh9m7crtXdR2cwsuMgbZZ1dqG7NyQVe6o9Y1s5g1rt8rkmDttBI2ppx6ALofZ\nJEY9KOYdr3/2UhbEoEgx5TIvEsbCUceWBDLFGGQwFyTHKRIvvjmdyqY7fj/jNS/c\ny3Mjp+l2j95TP8qmA1kLMLjK\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-fbsvc@mail-shop-bot-5f4f3.iam.gserviceaccount.com",
    "client_id": "101800195206257118014",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40mail-shop-bot-5f4f3.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
}
FIREBASE_CREDS_JSON_VALUE = json.dumps(_FIREBASE_CREDS)

# ── ৩. Optional ─────────────────────────────────────────────────────
FORCE_JOIN_CHANNEL_VALUE = "https://t.me/NeroxaOfficial"
SUPPORT_USERNAME_VALUE   = "@NeroxaOfficial"

# ── ৪. Dongvan Mail API ─────────────────────────────────────────────
DONGVAN_API_KEY_VALUE    = "ChXbDXJGgQMYFwqYfRANwLc7i"

# ════════════════════════════════════════════════════════════════════
os.environ.setdefault("BOT_TOKEN",                BOT_TOKEN_VALUE)
os.environ.setdefault("ADMIN_IDS",                ADMIN_IDS_VALUE)
os.environ.setdefault("FIREBASE_DATABASE_URL",    FIREBASE_DB_URL_VALUE)
os.environ.setdefault("FIREBASE_STORAGE_BUCKET",  FIREBASE_BUCKET_VALUE)
os.environ.setdefault("FIREBASE_CREDENTIALS_JSON",FIREBASE_CREDS_JSON_VALUE)
os.environ.setdefault("FORCE_JOIN_CHANNEL",       FORCE_JOIN_CHANNEL_VALUE)
os.environ.setdefault("SUPPORT_USERNAME",         SUPPORT_USERNAME_VALUE)
os.environ.setdefault("DONGVAN_API_KEY",          DONGVAN_API_KEY_VALUE)
# ════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
# UNICODE BOLD HELPER
# ══════════════════════════════════════════════════════════════════

def _b(text: str) -> str:
    """Convert ASCII letters/digits → Unicode Mathematical Bold Sans-Serif.
    Emojis, spaces and punctuation are left as-is, so _b("🏠 Home") → "🏠 𝗛𝗼𝗺𝗲".
    """
    out = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(chr(0x1D5D4 + ord(ch) - ord("A")))
        elif "a" <= ch <= "z":
            out.append(chr(0x1D5EE + ord(ch) - ord("a")))
        elif "0" <= ch <= "9":
            out.append(chr(0x1D7EC + ord(ch) - ord("0")))
        else:
            out.append(ch)
    return "".join(out)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════

def _csv_list(key: str) -> List[int]:
    raw = os.getenv(key, "").strip()
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


BOT_TOKEN            = os.environ["BOT_TOKEN"]
ADMIN_IDS: List[int] = _csv_list("ADMIN_IDS")
FIREBASE_CREDS_JSON  = os.environ["FIREBASE_CREDENTIALS_JSON"]
FIREBASE_DB_URL      = os.environ["FIREBASE_DATABASE_URL"]
FIREBASE_BUCKET      = os.environ["FIREBASE_STORAGE_BUCKET"]

DONGVAN_API_KEY  = os.getenv("DONGVAN_API_KEY", DONGVAN_API_KEY_VALUE)

# Dongvan API endpoints
_DV_OAUTH2_URL     = "https://api.dongvanfb.net/api/getOauth2"
_DV_GET_CODE_URL   = "https://tools.dongvanfb.net/api/get_code_oauth2"
_DV_GET_MSGS_URL   = "https://tools.dongvanfb.net/api/get_messages_oauth2"
_DV_GRAPH_MSGS_URL = "https://tools.dongvanfb.net/api/graph_messages"

# In-memory mail sessions: uid -> {email, password, refresh_token, client_id}
_mail_sessions: Dict[int, Dict] = {}

WEBHOOK_URL: Optional[str] = os.getenv("WEBHOOK_URL") or None
WEBHOOK_PATH   = os.getenv("WEBHOOK_PATH", "/webhook")
WEBAPP_HOST    = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT    = int(os.getenv("PORT") or os.getenv("WEBAPP_PORT", "8080"))

SPAM_COOLDOWN  = float(os.getenv("SPAM_COOLDOWN_SECONDS", "2"))
SPAM_MAX_MSGS  = int(os.getenv("SPAM_MAX_MESSAGES", "5"))
SPAM_WINDOW    = float(os.getenv("SPAM_WINDOW_SECONDS", "10"))
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@support")
WELCOME_MSG    = os.getenv("WELCOME_MESSAGE", "Welcome to our premium shop!")
DEFAULT_FORCE_JOIN = os.getenv("FORCE_JOIN_CHANNEL") or None

MAIL_SHOP_FILE = Path(__file__).parent / "My_Mail_Shop_Orders.xlsx"

_MAIL_SHEET_HEADERS = [
    "Order ID", "Date (UTC)", "User ID", "Username",
    "Product", "Qty", "Total ($)", "Items Delivered",
]
_HEADER_FONT  = Font(bold=True, color="FFFFFF")
_HEADER_FILL  = PatternFill("solid", fgColor="1F4E79")
_HEADER_ALIGN = Alignment(horizontal="center", vertical="center")


def _init_mail_shop_file() -> None:
    if MAIL_SHOP_FILE.exists():
        return
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mail Orders"
    ws.append(_MAIL_SHEET_HEADERS)
    for cell in ws[1]:
        cell.font  = _HEADER_FONT
        cell.fill  = _HEADER_FILL
        cell.alignment = _HEADER_ALIGN
    ws.freeze_panes = "A2"
    wb.save(str(MAIL_SHOP_FILE))


def make_stock_template_xlsx(product_name: str) -> bytes:
    """Generate a blank xlsx template for admins to fill in stock accounts."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Stock"

    hdr_font  = Font(bold=True, color="FFFFFF")
    hdr_fill  = PatternFill("solid", fgColor="1F4E79")
    hdr_align = Alignment(horizontal="center", vertical="center")
    eg_fill   = PatternFill("solid", fgColor="E2EFDA")

    ws.append(["Email", "Password"])
    for cell in ws[1]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    examples = [
        ("user1@gmail.com", "pass1234"),
        ("user2@gmail.com", "secret99"),
        ("user3@yahoo.com",  "hello456"),
    ]
    for row in examples:
        ws.append(list(row))
        for cell in ws[ws.max_row]:
            cell.fill = eg_fill

    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 20
    ws.freeze_panes = "A2"

    note_row = ws.max_row + 2
    ws.cell(row=note_row, column=1, value="⚠ Replace example rows with real accounts. Keep Email in column A, Password in column B.")
    ws.cell(row=note_row, column=1).font = Font(italic=True, color="FF0000")

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def make_stock_export_xlsx(product_name: str, stock_items: dict) -> bytes:
    """Export current stock items for a product to xlsx (admin download)."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Stock"

    hdr_font  = Font(bold=True, color="FFFFFF")
    hdr_fill  = PatternFill("solid", fgColor="1F4E79")
    hdr_align = Alignment(horizontal="center", vertical="center")
    alt_fill  = PatternFill("solid", fgColor="DCE6F1")

    ws.append(["#", "Email", "Password", "Raw"])
    for cell in ws[1]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    # Normalise: Firebase may return list-like data in edge cases
    if isinstance(stock_items, list):
        stock_items = {str(i): v for i, v in enumerate(stock_items)}

    for i, (key, item) in enumerate(stock_items.items(), 1):
        item_str = str(item).strip()
        if ":" in item_str:
            parts = item_str.split(":", 1)
            email, password = parts[0].strip(), parts[1].strip()
        else:
            email, password = item_str, ""
        ws.append([i, email, password, item_str])
        if i % 2 == 0:
            for cell in ws[ws.max_row]:
                cell.fill = alt_fill

    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 35
    ws.column_dimensions["C"].width = 25
    ws.column_dimensions["D"].width = 65
    ws.freeze_panes = "A2"

    info_sheet = wb.create_sheet("Info")
    info_sheet.append(["Product", product_name])
    info_sheet.append(["Total Items", len(stock_items)])
    info_sheet.append(["Exported At", time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())])
    info_sheet.append([])
    info_sheet.append(["Note", "Column D (Raw) contains the original account string. Use this column when re-importing."])
    info_sheet.column_dimensions["A"].width = 18
    info_sheet.column_dimensions["B"].width = 65

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def make_all_stock_export_xlsx(products: dict, all_stocks: dict) -> bytes:
    """Export stock for ALL products into a single multi-sheet xlsx file."""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    hdr_font  = Font(bold=True, color="FFFFFF")
    hdr_fill  = PatternFill("solid", fgColor="1F4E79")
    hdr_align = Alignment(horizontal="center", vertical="center")
    alt_fill  = PatternFill("solid", fgColor="DCE6F1")

    summary_ws = wb.create_sheet("Summary")
    summary_ws.append(["Product", "Category", "Stock Count", "Exported At"])
    for cell in summary_ws[1]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    for pid, product in products.items():
        pname    = product.get("name", pid)
        category = product.get("category", "mail")
        stock    = all_stocks.get(pid) or {}
        summary_ws.append([pname, category.upper(), len(stock), time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())])

        safe_title = re.sub(r"[\\/*?:\[\]]", "", pname)[:28] or pid[:28]
        ws = wb.create_sheet(safe_title)
        ws.append(["#", "Email", "Password", "Raw"])
        for cell in ws[1]:
            cell.font      = hdr_font
            cell.fill      = hdr_fill
            cell.alignment = hdr_align
        # Normalise: Firebase may return list-like data in edge cases
        if isinstance(stock, list):
            stock = {str(i): v for i, v in enumerate(stock)}
        for i, (key, item) in enumerate(stock.items(), 1):
            item_str = str(item).strip()
            if ":" in item_str:
                parts = item_str.split(":", 1)
                email, password = parts[0].strip(), parts[1].strip()
            else:
                email, password = item_str, ""
            ws.append([i, email, password, item_str])
            if i % 2 == 0:
                for cell in ws[ws.max_row]:
                    cell.fill = alt_fill
        ws.column_dimensions["A"].width = 6
        ws.column_dimensions["B"].width = 35
        ws.column_dimensions["C"].width = 25
        ws.column_dimensions["D"].width = 65
        ws.freeze_panes = "A2"

    for col in ["A", "B", "C", "D"]:
        summary_ws.column_dimensions[col].width = 25

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def make_user_order_xlsx(
    order_id: str, product_name: str, qty: int, total: float, items: List[str]
) -> bytes:
    """Build an in-memory xlsx of the user's purchased mail accounts."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Your Order"

    info_font  = Font(bold=True)
    hdr_font   = Font(bold=True, color="FFFFFF")
    hdr_fill   = PatternFill("solid", fgColor="1F4E79")
    hdr_align  = Alignment(horizontal="center", vertical="center")
    alt_fill   = PatternFill("solid", fgColor="DCE6F1")

    for label, value in [
        ("Order ID",    order_id),
        ("Product",     product_name),
        ("Quantity",    qty),
        ("Total Paid",  f"${total:.2f}"),
    ]:
        ws.append([label, value])
        ws.cell(row=ws.max_row, column=1).font = info_font

    ws.append([])
    ws.append(["#", "Account"])
    hdr_row = ws.max_row
    for cell in ws[hdr_row]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    for i, item in enumerate(items, 1):
        ws.append([i, item])
        if i % 2 == 0:
            for cell in ws[ws.max_row]:
                cell.fill = alt_fill

    ws.column_dimensions["A"].width = 12
    ws.column_dimensions["B"].width = 55
    ws.freeze_panes = f"A{hdr_row + 1}"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def make_products_xlsx(products: dict) -> bytes:
    """Export all products to an xlsx file for admin download."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Products"

    hdr_font  = Font(bold=True, color="FFFFFF")
    hdr_fill  = PatternFill("solid", fgColor="1F4E79")
    hdr_align = Alignment(horizontal="center", vertical="center")

    headers = ["Name", "Emoji", "Category", "Price (USD)", "Delivery Mode", "Hidden", "Stock Count"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font      = hdr_font
        cell.fill      = hdr_fill
        cell.alignment = hdr_align

    alt_fill = PatternFill("solid", fgColor="DCE6F1")
    for i, (pid, p) in enumerate(products.items(), 1):
        row = [
            p.get("name", ""),
            p.get("emoji", "📦"),
            p.get("category", "mail"),
            p.get("price", 0.0),
            p.get("delivery_mode", "manual"),
            "yes" if p.get("hidden") else "no",
            p.get("stock_count", 0),
        ]
        ws.append(row)
        if i % 2 == 0:
            for cell in ws[ws.max_row]:
                cell.fill = alt_fill

    col_widths = [30, 10, 12, 14, 16, 10, 14]
    for col_idx, width in enumerate(col_widths, 1):
        ws.column_dimensions[ws.cell(1, col_idx).column_letter].width = width
    ws.freeze_panes = "A2"

    # Instructions sheet
    ws2 = wb.create_sheet("Import Guide")
    ws2.append(["📋 Import Guide — How to add products via file"])
    ws2.append([])
    ws2.append(["Column", "Description", "Allowed Values"])
    for cell in ws2[3]:
        cell.font = Font(bold=True)
    guide = [
        ("Name",          "Product name",                                   "Any text"),
        ("Emoji",         "Product emoji icon",                             "Any emoji, e.g. 📮 🌐 🔐"),
        ("Category",      "Product type",                                   "mail / vpn / proxy"),
        ("Price (USD)",   "Price per unit / per day",                       "Number, e.g. 1.50"),
        ("Delivery Mode", "How product is delivered (proxy only)",           "manual / auto"),
        ("Hidden",        "Whether product is visible to users",             "yes / no"),
    ]
    for row in guide:
        ws2.append(list(row))
    for col in ["A", "B", "C"]:
        ws2.column_dimensions[col].width = 25

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def parse_products_xlsx(content: bytes) -> List[dict]:
    """Parse an xlsx/csv file and return a list of product dicts to import."""
    results = []
    try:
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
    except Exception:
        return results

    if not rows:
        return results

    # Detect header row
    header = [str(c).strip().lower() if c else "" for c in rows[0]]
    col = {}
    for i, h in enumerate(header):
        if "name" in h:
            col["name"] = i
        elif "emoji" in h:
            col["emoji"] = i
        elif "cat" in h:
            col["category"] = i
        elif "price" in h:
            col["price"] = i
        elif "delivery" in h or "mode" in h:
            col["delivery_mode"] = i
        elif "hidden" in h:
            col["hidden"] = i

    if "name" not in col or "price" not in col:
        return results

    for row in rows[1:]:
        if not row or not row[col["name"]]:
            continue
        name  = str(row[col["name"]]).strip()
        if not name:
            continue
        try:
            price = float(str(row[col["price"]]).replace("$", "").strip())
        except Exception:
            continue
        emoji    = str(row[col["emoji"]]).strip() if "emoji" in col and row[col["emoji"]] else "📦"
        category = str(row[col["category"]]).strip().lower() if "category" in col and row[col["category"]] else "mail"
        if category not in ("mail", "vpn", "proxy"):
            category = "mail"
        delivery = str(row[col["delivery_mode"]]).strip().lower() if "delivery_mode" in col and row[col["delivery_mode"]] else "manual"
        if delivery not in ("manual", "auto"):
            delivery = "manual"
        hidden_v = str(row[col["hidden"]]).strip().lower() if "hidden" in col and row[col["hidden"]] else "no"
        hidden   = hidden_v in ("yes", "true", "1")
        results.append({
            "name": name, "emoji": emoji, "category": category,
            "price": round(price, 4), "delivery_mode": delivery, "hidden": hidden,
        })
    return results


def append_to_mail_shop_file(
    order_id: str, uid: int, username: str,
    product_name: str, qty: int, total: float,
    items: List[str], ts: int,
) -> None:
    _init_mail_shop_file()
    wb = openpyxl.load_workbook(str(MAIL_SHOP_FILE))
    ws = wb.active
    date_s  = time.strftime("%Y-%m-%d %H:%M", time.gmtime(ts))
    items_s = "\n".join(items) if items else ""
    ws.append([order_id, date_s, uid, username, product_name, qty, round(total, 2), items_s])
    # Refresh column widths
    for col in ws.columns:
        max_len = max((len(str(c.value or "")) for c in col), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)
    wb.save(str(MAIL_SHOP_FILE))

HOME_BTN   = _b("🏠 Home")
BACK_BTN   = _b("🔙 Back")
CANCEL_BTN = _b("❌ Cancel")

# ── User menu ──────────────────────────────────────────────────────
BTN_BALANCE  = _b("💰 Balance")
BTN_GET_MAIL   = _b("📮 Get Mail")
BTN_TEMP_MAIL  = _b("📧 Temp Mail")
BTN_BUY_VPN  = _b("🌐 Buy VPN")
BTN_BUY_PROXY= _b("🔐 Buy Proxy")
BTN_DEPOSIT  = _b("💵 Deposit")
BTN_GET_CODE = _b("🔓 Get Code")
BTN_GET_2FA  = _b("🔑 Get 2FA")

# ── Get Code Sub-menu ───────────────────────────────────────────────
BTN_GC_SET_MAIL = _b("📧 Set Mail")
BTN_GC_CODES    = _b("📬 Get Codes")
BTN_GC_INBOX    = _b("📁 Read Inbox")
BTN_GC_REFRESH  = _b("🔄 Refresh Inbox")
BTN_GC_FILTER   = _b("🔍 Filter Mail")
BTN_GC_CHANGE   = _b("✏️ Change Mail")
BTN_HISTORY  = _b("📜 Order History")
BTN_SUPPORT  = _b("🆘 Support")
BTN_CONFIRM  = _b("✅ Confirm Purchase")
BTN_COUPON   = _b("🎟 Apply Coupon")

# ── Duration ───────────────────────────────────────────────────────
BTN_1DAY   = _b("⏱ 1 Day")
BTN_7DAYS  = _b("⏱ 7 Days")
BTN_30DAYS = _b("⏱ 30 Days")
BTN_90DAYS = _b("⏱ 90 Days")
BTN_CUSTOM = _b("⏱ Custom")

# ── Deposit methods ────────────────────────────────────────────────
BTN_BKASH   = _b("📱 bKash")
BTN_NAGAD   = _b("📱 Nagad")
BTN_BINANCE = _b("🔶 Binance")

# ── Admin menu ─────────────────────────────────────────────────────
BTN_ADM_DASHBOARD     = _b("📊 Dashboard")
BTN_ADM_PRODUCTS      = _b("📦 Products")
BTN_ADM_STOCK         = _b("📥 Stock")
BTN_ADM_USERS         = _b("👥 Users")
BTN_ADM_DEPOSITS      = _b("💳 Deposits")
BTN_ADM_VPN_ORDERS    = _b("🌐 VPN Orders")
BTN_ADM_PROXY_ORDERS  = _b("🔐 Proxy Orders")
BTN_ADM_COUPONS       = _b("🎟 Coupons")
BTN_ADM_BROADCAST     = _b("📢 Broadcast")
BTN_ADM_SETTINGS      = _b("⚙️ Settings")
BTN_ADM_EXPORT        = _b("📋 Export Mail Orders")
BTN_ADM_PROXY_PKGS    = _b("📡 Data Packages")
BTN_PKG_ADD           = _b("➕ Add Package")

# ── Admin product actions ──────────────────────────────────────────
BTN_EDIT_NAME   = _b("✏️ Edit Name")
BTN_EDIT_PRICE  = _b("💵 Edit Price")
BTN_EDIT_EMOJI  = _b("😀 Edit Emoji")
BTN_EDIT_DESC   = _b("📝 Edit Description")
BTN_HIDE_PROD          = _b("🙈 Hide Product")
BTN_SHOW_PROD          = _b("👁 Show Product")
BTN_DELETE             = _b("🗑 Delete")
BTN_ADD_PRODUCT        = _b("➕ Add Product")
BTN_DOWNLOAD_PRODUCTS  = _b("📥 Download Products")
BTN_IMPORT_PRODUCTS    = _b("📤 Import Products")
BTN_ADD_STOCK   = _b("📥 Add Stock")

# ── Admin stock actions ────────────────────────────────────────────
BTN_UPLOAD_FILE      = _b("📤 Upload File")
BTN_MANUAL_ADD       = _b("✏️ Manual Add")
BTN_CLEAR_STOCK      = _b("🗑 Clear Stock")
BTN_GET_TEMPLATE     = _b("📋 Download Template")
BTN_DOWNLOAD_STOCK     = _b("📥 Download Stock")
BTN_DOWNLOAD_ALL_STOCK = _b("📦 Download All Stock")

# ── Admin user actions ─────────────────────────────────────────────
BTN_BAN_USER    = _b("🚫 Ban User")
BTN_UNBAN_USER  = _b("✅ Unban User")
BTN_ADD_BAL     = _b("💰 Add Balance")
BTN_REMOVE_BAL  = _b("💸 Remove Balance")

# ── Admin coupon actions ───────────────────────────────────────────
BTN_DELETE_COUPON = _b("🗑 Delete Coupon")
BTN_CREATE_COUPON = _b("➕ Create Coupon")

# ── Categories ─────────────────────────────────────────────────────
BTN_CAT_MAIL  = _b("📮 Mail (Auto Delivery)")
BTN_CAT_VPN   = _b("🌐 VPN (Manual)")
BTN_CAT_PROXY = _b("🔐 Proxy (Auto+Manual)")

# ── Proxy delivery mode toggle ──────────────────────────────────────
BTN_TOGGLE_AUTO   = _b("🤖 Set Auto Delivery")
BTN_TOGGLE_MANUAL = _b("👤 Set Manual Delivery")


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Initialise
# ══════════════════════════════════════════════════════════════════

firebase_admin.initialize_app(
    credentials.Certificate(json.loads(FIREBASE_CREDS_JSON)),
    {"databaseURL": FIREBASE_DB_URL, "storageBucket": FIREBASE_BUCKET},
)


async def _run(fn, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: fn(*args, **kwargs))


async def _safe_delete(msg) -> None:
    try:
        await msg.delete()
    except Exception:
        pass


def _session_has_oauth2(session: dict) -> bool:
    return bool(session.get("refresh_token") and session.get("client_id"))


def _truncate_msg(text: str, limit: int = 3900) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n\n<i>… (truncated, too long)</i>"


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Generic helpers
# ══════════════════════════════════════════════════════════════════

async def db_get(path: str) -> Any:
    return await _run(fdb.reference(path).get)

async def db_set(path: str, data: Any) -> None:
    await _run(fdb.reference(path).set, data)

async def db_update(path: str, data: dict) -> None:
    await _run(fdb.reference(path).update, data)

async def db_push(path: str, data: Any) -> str:
    ref = await _run(fdb.reference(path).push, data)
    return ref.key

async def db_delete(path: str) -> None:
    await _run(fdb.reference(path).delete)


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Users
# ══════════════════════════════════════════════════════════════════

async def get_user(uid: int) -> Optional[dict]:
    return await db_get(f"users/{uid}")

async def get_all_users() -> Dict[str, dict]:
    return await db_get("users") or {}

async def create_or_update_user(uid: int, username: str, full_name: str) -> dict:
    existing = await get_user(uid)
    if existing:
        await db_update(f"users/{uid}", {"username": username, "full_name": full_name})
        return {**existing, "username": username, "full_name": full_name}
    data = {
        "user_id": uid, "username": username, "full_name": full_name,
        "balance": 0.0, "is_banned": False, "joined_at": int(time.time()),
        "total_spent": 0.0, "order_count": 0,
    }
    await db_set(f"users/{uid}", data)
    return data

async def update_balance(uid: int, delta: float) -> float:
    user = await get_user(uid)
    new_bal = round((user.get("balance") or 0) + delta, 4)
    await db_update(f"users/{uid}", {"balance": new_bal})
    return new_bal

async def ban_user(uid: int, banned: bool) -> None:
    await db_update(f"users/{uid}", {"is_banned": banned})

async def get_totp_secret(uid: int) -> Optional[str]:
    user = await get_user(uid)
    return user.get("totp_secret") if user else None

async def set_totp_secret(uid: int, secret: str) -> None:
    await db_update(f"users/{uid}", {"totp_secret": secret})


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Settings
# ══════════════════════════════════════════════════════════════════

_DEFAULT_SETTINGS = {
    "usd_rate": 125.0,
    "bkash_number": "", "nagad_number": "", "binance_uid": "",
    "bkash_min": 100.0, "nagad_min": 150.0, "binance_min": 5.0,
    "support_username": SUPPORT_USERNAME,
    "welcome_message": WELCOME_MSG,
    "force_join_channel": DEFAULT_FORCE_JOIN or "",
    "force_join_channel_2": "https://t.me/NMShopUpdate",
    "low_stock_threshold": 5,
    "get_2fa_link": "",
    "shop_name": "🛍 Neroxa Shop",
    "proxy_data_options": "1 GB,5 GB,10 GB,50 GB",
}

async def get_settings() -> dict:
    data = await db_get("settings")
    if not data:
        await db_set("settings", _DEFAULT_SETTINGS)
        return dict(_DEFAULT_SETTINGS)
    return {**_DEFAULT_SETTINGS, **data}

async def update_settings(updates: dict) -> None:
    await db_update("settings", updates)


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Products
# ══════════════════════════════════════════════════════════════════

async def get_all_products() -> Dict[str, dict]:
    return await db_get("products") or {}

async def get_product(pid: str) -> Optional[dict]:
    return await db_get(f"products/{pid}")

async def create_product(name: str, price: float, emoji: str = "📮", category: str = "mail",
                         delivery_mode: str = "manual", hidden: bool = False,
                         description: str = "") -> str:
    return await db_push("products", {
        "name": name, "price": price, "emoji": emoji, "category": category,
        "delivery_mode": delivery_mode, "hidden": hidden, "description": description,
        "stock_count": 0, "created_at": int(time.time()), "total_sold": 0,
    })

async def update_product(pid: str, updates: dict) -> None:
    await db_update(f"products/{pid}", updates)

async def delete_product(pid: str) -> None:
    await db_delete(f"products/{pid}")
    await db_delete(f"stocks/{pid}")

async def get_service_products(category: str) -> Dict[str, dict]:
    all_p = await get_all_products()
    return {k: v for k, v in all_p.items() if v.get("category") == category and not v.get("hidden")}


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Stock  (BUG FIX: item reassignment inside loop)
# ══════════════════════════════════════════════════════════════════

async def add_stock_items(pid: str, items: List[str]) -> int:
    """Add items to stock. Returns number of items actually added."""
    existing = await db_get(f"stocks/{pid}") or {}
    before = len(existing)
    for raw_item in items:
        cleaned = raw_item.strip()
        if cleaned:
            existing[uuid.uuid4().hex[:16]] = cleaned
    await db_set(f"stocks/{pid}", existing)
    count = len(existing)
    await db_update(f"products/{pid}", {"stock_count": count, "hidden": count == 0})
    return count - before  # Return actually added count, not total

async def pop_stock_items(pid: str, qty: int) -> List[str]:
    existing = await db_get(f"stocks/{pid}") or {}
    keys = list(existing.keys())[:qty]
    popped = [existing[k] for k in keys]
    for k in keys:
        del existing[k]
    await db_set(f"stocks/{pid}", existing)
    new_count = len(existing)
    await db_update(f"products/{pid}", {"stock_count": new_count, "hidden": new_count == 0})
    return popped

async def clear_stock(pid: str) -> None:
    await db_delete(f"stocks/{pid}")
    await db_update(f"products/{pid}", {"stock_count": 0, "hidden": True})

async def get_stock_count(pid: str) -> int:
    data = await db_get(f"stocks/{pid}")
    return len(data) if data else 0


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Orders
# ══════════════════════════════════════════════════════════════════

async def create_order(uid: int, pid: str, product_name: str,
                       qty: int, total_price: float, items: List[str]) -> str:
    oid = await db_push("orders", {
        "user_id": uid, "product_id": pid, "product_name": product_name,
        "qty": qty, "total_price": total_price, "items": items,
        "status": "delivered", "created_at": int(time.time()),
    })
    u = await get_user(uid) or {}
    await db_update(f"users/{uid}", {
        "total_spent": round((u.get("total_spent") or 0) + total_price, 4),
        "order_count": (u.get("order_count") or 0) + 1,
    })
    prod = await get_product(pid) or {}
    await db_update(f"products/{pid}", {
        "total_sold": (prod.get("total_sold") or 0) + qty,
    })
    return oid

async def get_user_orders(uid: int) -> List[dict]:
    data = await db_get("orders")
    if not data:
        return []
    return sorted(
        [{**v, "order_id": k} for k, v in data.items() if v.get("user_id") == uid],
        key=lambda x: x.get("created_at", 0), reverse=True,
    )


# ══════════════════════════════════════════════════════════════════
# FIREBASE — VPN Orders
# ══════════════════════════════════════════════════════════════════

async def create_vpn_order(uid: int, username: str, pid: str,
                           product_name: str, duration_days: int, price: float) -> str:
    u = await get_user(uid) or {}
    await db_update(f"users/{uid}", {
        "total_spent": round((u.get("total_spent") or 0) + price, 4),
        "order_count": (u.get("order_count") or 0) + 1,
    })
    prod = await get_product(pid) or {}
    await db_update(f"products/{pid}", {
        "total_sold": (prod.get("total_sold") or 0) + 1,
    })
    return await db_push("vpn_orders", {
        "user_id": uid, "username": username, "product_id": pid,
        "product_name": product_name, "duration_days": duration_days,
        "price": price, "status": "pending", "created_at": int(time.time()),
    })

async def update_vpn_order(oid: str, updates: dict) -> None:
    await db_update(f"vpn_orders/{oid}", updates)

async def get_pending_vpn_orders() -> List[dict]:
    data = await db_get("vpn_orders")
    if not data:
        return []
    return [{**v, "order_id": k} for k, v in data.items() if v.get("status") == "pending"]

async def get_user_vpn_orders(uid: int) -> List[dict]:
    data = await db_get("vpn_orders")
    if not data:
        return []
    return sorted(
        [{**v, "order_id": k} for k, v in data.items() if v.get("user_id") == uid],
        key=lambda x: x.get("created_at", 0), reverse=True,
    )


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Proxy Orders
# ══════════════════════════════════════════════════════════════════

async def create_proxy_order(uid: int, username: str, pid: str,
                             product_name: str, duration_days, price: float,
                             items: Optional[List[str]] = None) -> str:
    delivery_mode = "auto" if items else "manual"
    status        = "delivered" if delivery_mode == "auto" else "pending"
    u = await get_user(uid) or {}
    await db_update(f"users/{uid}", {
        "total_spent": round((u.get("total_spent") or 0) + price, 4),
        "order_count": (u.get("order_count") or 0) + 1,
    })
    prod = await get_product(pid) or {}
    await db_update(f"products/{pid}", {
        "total_sold": (prod.get("total_sold") or 0) + 1,
    })
    return await db_push("proxy_orders", {
        "user_id": uid, "username": username, "product_id": pid,
        "product_name": product_name, "duration_days": duration_days,
        "price": price, "status": status, "delivery_mode": delivery_mode,
        "items": items or [], "created_at": int(time.time()),
    })

async def update_proxy_order(oid: str, updates: dict) -> None:
    await db_update(f"proxy_orders/{oid}", updates)

async def get_pending_proxy_orders() -> List[dict]:
    data = await db_get("proxy_orders")
    if not data:
        return []
    return [{**v, "order_id": k} for k, v in data.items() if v.get("status") == "pending"]

async def get_user_proxy_orders(uid: int) -> List[dict]:
    data = await db_get("proxy_orders")
    if not data:
        return []
    return sorted(
        [{**v, "order_id": k} for k, v in data.items() if v.get("user_id") == uid],
        key=lambda x: x.get("created_at", 0), reverse=True,
    )


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Deposits
# ══════════════════════════════════════════════════════════════════

async def create_deposit(uid: int, username: str, method: str,
                         amount_bdt: float, amount_usd: float,
                         trx_id: str, screenshot_url: str) -> str:
    return await db_push("deposits", {
        "user_id": uid, "username": username, "method": method,
        "amount_bdt": amount_bdt, "amount_usd": amount_usd,
        "trx_id": trx_id, "screenshot_url": screenshot_url,
        "status": "pending", "created_at": int(time.time()),
    })

async def get_deposit(dep_id: str) -> Optional[dict]:
    return await db_get(f"deposits/{dep_id}")

async def update_deposit(dep_id: str, updates: dict) -> None:
    await db_update(f"deposits/{dep_id}", updates)

async def get_pending_deposits() -> List[dict]:
    data = await db_get("deposits")
    if not data:
        return []
    return sorted(
        [{**v, "deposit_id": k} for k, v in data.items() if v.get("status") == "pending"],
        key=lambda x: x.get("created_at", 0),
    )

async def check_trx_duplicate(trx_id: str) -> bool:
    data = await db_get("deposits")
    if not data:
        return False
    return any(v.get("trx_id") == trx_id for v in data.values())

async def get_user_deposits(uid: int) -> List[dict]:
    data = await db_get("deposits")
    if not data:
        return []
    return sorted(
        [{**v, "deposit_id": k} for k, v in data.items() if v.get("user_id") == uid],
        key=lambda x: x.get("created_at", 0), reverse=True,
    )


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Coupons
# ══════════════════════════════════════════════════════════════════

async def get_coupon(code: str) -> Optional[dict]:
    data = await db_get("coupons")
    if not data:
        return None
    for k, v in data.items():
        if v.get("code", "").upper() == code.upper():
            return {**v, "coupon_id": k}
    return None

async def create_coupon(code: str, discount_pct: float, max_uses: int, expires_at: int) -> str:
    return await db_push("coupons", {
        "code": code.upper(), "discount_pct": discount_pct,
        "max_uses": max_uses, "used_count": 0, "expires_at": expires_at, "active": True,
    })

async def use_coupon(coupon_id: str) -> None:
    c = await db_get(f"coupons/{coupon_id}")
    used = (c.get("used_count") or 0) + 1
    await db_update(f"coupons/{coupon_id}", {
        "used_count": used,
        "active": used < c.get("max_uses", 1),
    })

async def get_all_coupons() -> List[dict]:
    data = await db_get("coupons")
    return [{**v, "coupon_id": k} for k, v in data.items()] if data else []

async def delete_coupon(coupon_id: str) -> None:
    await db_delete(f"coupons/{coupon_id}")


# ══════════════════════════════════════════════════════════════════
# FIREBASE — Stats & Storage
# ══════════════════════════════════════════════════════════════════

async def get_dashboard_stats() -> dict:
    users, orders, vpn, proxy, deposits = await asyncio.gather(
        db_get("users"), db_get("orders"),
        db_get("vpn_orders"), db_get("proxy_orders"), db_get("deposits"),
    )
    rev = (
        sum(v.get("total_price", 0) for v in (orders or {}).values()) +
        sum(v.get("price", 0) for v in (vpn or {}).values() if v.get("status") == "delivered") +
        sum(v.get("price", 0) for v in (proxy or {}).values() if v.get("status") == "delivered")
    )
    return {
        "total_users":      len(users) if users else 0,
        "total_revenue":    round(rev, 2),
        "total_sales":      len(orders or {}),
        "pending_deposits": sum(1 for v in (deposits or {}).values() if v.get("status") == "pending"),
        "pending_orders":   (
            sum(1 for v in (vpn or {}).values() if v.get("status") == "pending") +
            sum(1 for v in (proxy or {}).values() if v.get("status") == "pending")
        ),
    }

async def upload_screenshot(file_bytes: bytes, filename: str) -> str:
    def _up():
        b = storage.bucket()
        blob = b.blob(f"deposits/{filename}")
        blob.upload_from_string(file_bytes, content_type="image/jpeg")
        blob.make_public()
        return blob.public_url
    return await _run(_up)


# ══════════════════════════════════════════════════════════════════
# STOCK FILE PARSER  (BUG FIX: robust xlsx parsing)
# ══════════════════════════════════════════════════════════════════

def _norm(line: str) -> str:
    line = line.strip()
    if not line:
        return ""
    if "," in line and ":" not in line:
        parts = line.split(",", 1)
        return ":".join(p.strip() for p in parts)
    return line


def parse_stock_file(content: bytes, filename: str) -> List[str]:
    fname = (filename or "").lower()

    if fname.endswith(".xlsx"):
        items: List[str] = []
        try:
            wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            ws = wb.active
            if ws is None:
                logger.warning("XLSX: no active sheet found")
                return []
            for row in ws.iter_rows(values_only=True):
                # FIX: filter None, convert to str, strip whitespace
                cols = [str(c).strip() for c in row if c is not None and str(c).strip() not in ("", "None")]
                if len(cols) >= 2:
                    items.append(f"{cols[0]}:{cols[1]}")
                elif len(cols) == 1:
                    items.append(cols[0])
            wb.close()
        except Exception as e:
            logger.error("XLSX parse error: %s", e)
            raise ValueError(f"Cannot read xlsx file: {e}") from e
        return [i for i in items if i.strip()]

    if fname.endswith(".csv"):
        items = []
        try:
            text = content.decode("utf-8-sig", errors="replace")  # FIX: handle BOM
        except Exception:
            text = content.decode("latin-1", errors="replace")
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            parts = [p for p in parts if p]
            if len(parts) >= 2:
                items.append(f"{parts[0]}:{parts[1]}")
            elif len(parts) == 1:
                items.append(parts[0])
        return [i for i in items if i]

    # Plain text (.txt or unknown)
    try:
        text = content.decode("utf-8-sig", errors="replace")
    except Exception:
        text = content.decode("latin-1", errors="replace")
    return [_norm(ln) for ln in text.splitlines() if _norm(ln)]


# ══════════════════════════════════════════════════════════════════
# DONGVAN MAIL API — Service detection & helpers
# ══════════════════════════════════════════════════════════════════

_DV_SERVICE_KEYWORDS: Dict[str, List[str]] = {
    "FACEBOOK":  ["security@facebookmail.com", "facebook", "fb"],
    "INSTAGRAM": ["instagram", "mail@instagram.com"],
    "TWITTER":   ["twitter", "x.com", "notify@twitter.com"],
    "GOOGLE":    ["google", "gmail", "youtube", "no-reply@google.com"],
    "APPLE":     ["apple", "icloud", "no-reply@apple.com"],
    "TIKTOK":    ["tiktok", "douyin"],
    "AMAZON":    ["amazon", "shipment-tracking@amazon.com"],
    "SHOPEE":    ["shopee"],
    "TELEGRAM":  ["telegram"],
    "KAKAOTALK": ["kakao"],
    "LAZADA":    ["lazada"],
    "WECHAT":    ["wechat", "weixin"],
    "OUTLOOK":   ["outlook", "microsoft", "hotmail", "no-reply@microsoft.com"],
    "LINKEDIN":  ["linkedin"],
    "NETFLIX":   ["netflix"],
    "DISCORD":   ["discord"],
    "SNAPCHAT":  ["snapchat"],
    "GARENA":    ["garena", "account@garena.com"],
    "COINBASE":  ["coinbase"],
    "BINANCE":   ["binance"],
}
_DV_SERVICE_LIST = list(_DV_SERVICE_KEYWORDS.keys())


def _dv_determine_service(subject: str = "", sender_name: str = "", sender_address: str = "") -> str:
    text = f"{subject} {sender_name} {sender_address}".lower()
    for svc, keywords in _DV_SERVICE_KEYWORDS.items():
        if any(kw.lower() in text for kw in keywords):
            return svc
    return "UNKNOWN"


def _dv_extract_codes(messages_data: Optional[dict]) -> List[dict]:
    found: List[dict] = []
    if not messages_data or not messages_data.get("status") or not messages_data.get("messages"):
        return found
    _CODE_PATTERNS = [
        r'(\d{4,8})\s+is your',
        r'[Cc]ode[:\s]+(\d{4,8})',
        r'[Cc]onfirmation code[:\s]*(\d{4,8})',
        r'[Vv]erification code[:\s]*(\d{4,8})',
        r'OTP[:\s]*(\d{4,8})',
        r'mã xác nhận[:\s]*(\d{4,8})',
        r'is\s+(\d{4,8})\s',
        r'security code[:\s]*(\d{4,8})',
    ]
    for msg in messages_data["messages"]:
        subject  = msg.get("subject", "") or ""
        body     = msg.get("message", "") or ""
        from_f   = msg.get("from")
        sname    = from_f[0].get("name", "") if from_f and isinstance(from_f, list) and from_f else ""
        saddr    = from_f[0].get("address", "") if from_f and isinstance(from_f, list) and from_f else ""
        code     = msg.get("code", "") or ""
        if not code:
            combined = subject + " " + body[:2000]
            for pattern in _CODE_PATTERNS:
                m = re.search(pattern, combined)
                if m:
                    code = m.group(1)
                    break
        if code:
            found.append({
                "code": code, "service": _dv_determine_service(subject, sname, saddr),
                "sender": sname, "address": saddr, "subject": subject,
                "date": msg.get("date", "") or "", "uid": msg.get("uid", "") or "",
            })
    return found


def _dv_parse_input(text: str) -> dict:
    parts = text.strip().split("|")
    result = {"email": None, "password": None, "refresh_token": None, "client_id": None, "has_oauth2": False}
    if len(parts) >= 2:
        result["email"]    = parts[0].strip()
        result["password"] = parts[1].strip()
    if len(parts) >= 4:
        result["refresh_token"] = parts[2].strip()
        result["client_id"]     = parts[3].strip()
        result["has_oauth2"]    = True
    return result


async def _dv_oauth2(email: str, password: str) -> Optional[dict]:
    def _call():
        try:
            r = _requests.post(_DV_OAUTH2_URL, json={"email": email, "password": password, "apikey": DONGVAN_API_KEY}, timeout=30)
            d = r.json()
            if d.get("status") and "oauth2" in d:
                parts = d["oauth2"].split("|")
                if len(parts) >= 2:
                    return {"refresh_token": parts[0], "client_id": parts[1]}
        except Exception as e:
            logger.error("DV oauth2 error: %s", e)
        return None
    return await _run(_call)


async def _dv_get_messages(email: str, rt: str, cid: str) -> Optional[dict]:
    def _call():
        try:
            r = _requests.post(_DV_GET_MSGS_URL, json={"email": email, "refresh_token": rt, "client_id": cid, "list_mail": "all"}, timeout=30)
            return r.json()
        except Exception as e:
            logger.error("DV get_messages error: %s", e)
            return None
    return await _run(_call)


async def _dv_get_code(email: str, rt: str, cid: str, code_type: str = "all") -> Optional[dict]:
    def _call():
        try:
            r = _requests.post(_DV_GET_CODE_URL, json={"email": email, "refresh_token": rt, "client_id": cid, "type": code_type}, timeout=30)
            return r.json()
        except Exception as e:
            logger.error("DV get_code error: %s", e)
            return None
    return await _run(_call)


async def _dv_graph_messages(email: str, rt: str, cid: str) -> Optional[dict]:
    def _call():
        try:
            r = _requests.post(_DV_GRAPH_MSGS_URL, json={"email": email, "refresh_token": rt, "client_id": cid, "list_mail": "all"}, timeout=30)
            return r.json()
        except Exception as e:
            logger.error("DV graph_messages error: %s", e)
            return None
    return await _run(_call)


async def _dv_process_mailbox(session: dict) -> List[dict]:
    email, rt, cid = session["email"], session["refresh_token"], session["client_id"]
    msgs = await _dv_get_messages(email, rt, cid)
    if msgs and msgs.get("status") and msgs.get("messages"):
        return _dv_extract_codes(msgs)
    msgs = await _dv_graph_messages(email, rt, cid)
    if msgs and msgs.get("status") and msgs.get("messages"):
        return _dv_extract_codes(msgs)
    return []


def _dv_build_codes_display(messages: List[dict]) -> str:
    if not messages:
        return "❌ No codes found in mailbox."
    by_svc: Dict[str, List[dict]] = {}
    for m in messages:
        by_svc.setdefault(m["service"], []).append(m)
    out = f"{_SEP}\n📬 <b>CODES FOUND</b>\n{_SEP}\n\n"
    for svc, msgs in by_svc.items():
        out += f"<b>{svc}</b>\n"
        for m in msgs:
            out += f"├─ <code>{html_lib.escape(m['code'])}</code>\n"
            out += f"└─ {html_lib.escape(m['subject'][:60])}\n"
        out += "\n"
    out += f"{_SEP}\n📋 <b>COPY:</b>\n"
    for svc, msgs in by_svc.items():
        for m in msgs:
            out += f"<code>{svc} → {html_lib.escape(m['code'])}</code>\n"
    return out


def _dv_build_mailbox_display(messages: List[dict], filter_service: Optional[str] = None) -> str:
    filtered = [m for m in messages if m["service"] == filter_service.upper()] if filter_service else messages
    title    = f"📁 Filter: <b>{filter_service.upper()}</b>" if filter_service else "📁 <b>Mailbox</b>"
    if not filtered:
        return f"{title}\n{_SEP}\n❌ No messages found."
    out = f"{title}\n{_SEP}\n📊 Total: <b>{len(filtered)}</b> message(s)\n{_SEP}\n\n"
    for i, m in enumerate(filtered[:20], 1):
        code_display = f"<b>{html_lib.escape(m['code'])}</b>" if m.get("code") else "No code"
        out += f"<b>#{i}</b> <b>[{m['service']}]</b> {code_display}\n"
        out += f"└─ 📝 {html_lib.escape(m['subject'][:80])}\n"
        out += f"└─ 👤 {html_lib.escape(m.get('sender',''))}\n"
        if m.get("date"):
            out += f"└─ 🕐 {str(m['date'])[:19]}\n"
        out += "\n"
    if len(filtered) > 20:
        out += f"<i>... and {len(filtered) - 20} more</i>\n\n"
    codes_with_code = [m for m in filtered if m.get("code")]
    if codes_with_code:
        out += f"{_SEP}\n📋 <b>CODES:</b>\n"
        for m in codes_with_code:
            out += f"<code>{m['service']} → {html_lib.escape(m['code'])}</code>\n"
    return out


# ══════════════════════════════════════════════════════════════════
# FORMATTERS
# ══════════════════════════════════════════════════════════════════

TZ    = pytz.UTC
_SEP  = "━" * 22
_LINE = "─" * 22


def _dt(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=TZ).strftime("%d %b %Y, %H:%M UTC")


def fmt_welcome(shop_name: str, welcome: str, first_name: str, balance: float) -> str:
    return (
        f"<b>{shop_name}</b>\n"
        f"{_SEP}\n"
        f"{welcome}\n\n"
        f"👋 Welcome back, <b>{first_name}</b>!\n"
        f"💰 Balance: <b>${balance:.2f}</b>"
    )

def fmt_balance_screen(user: dict) -> str:
    banned = "🚫 Banned" if user.get("is_banned") else "✅ Active"
    return (
        f"💰 <b>My Balance</b>\n{_SEP}\n"
        f"👤 <b>{user.get('full_name', 'User')}</b>\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n"
        f"📛 @{user.get('username') or 'no username'}\n"
        f"{_LINE}\n"
        f"💵 Balance: <b>${user.get('balance', 0):.2f}</b>\n"
        f"💸 Total Spent: <b>${user.get('total_spent', 0):.2f}</b>\n"
        f"🛍 Total Orders: <b>{user.get('order_count', 0)}</b>\n"
        f"📅 Member Since: {_dt(user.get('joined_at', int(time.time())))}\n"
        f"{_LINE}\n"
        f"Status: {banned}"
    )

def fmt_product_list_header(category_name: str, count: int) -> str:
    return (
        f"<b>{category_name}</b>\n{_SEP}\n"
        f"📦 {count} product(s) available\nSelect a product below:"
    )

def fmt_product_detail(product: dict, stock: int) -> str:
    desc = product.get("description", "").strip()
    desc_line = f"\n📝 {desc}\n" if desc else ""
    return (
        f"{product.get('emoji', '📦')} <b>{product['name']}</b>\n{_SEP}\n"
        f"{desc_line}"
        f"💵 Price: <b>${product['price']:.2f}</b> per account\n"
        f"📦 In Stock: <b>{stock}</b>\n{_LINE}\n"
        f"Enter the quantity you want to purchase:"
    )

def fmt_service_detail(product: dict, duration_days: int) -> str:
    price = round(product["price"] * duration_days, 4)
    desc = product.get("description", "").strip()
    desc_line = f"\n📝 {desc}\n" if desc else ""
    return (
        f"{product.get('emoji', '🌐')} <b>{product['name']}</b>\n{_SEP}\n"
        f"{desc_line}"
        f"💵 Price/day: <b>${product['price']:.2f}</b>\n"
        f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"Press ✅ Confirm Purchase to place your order."
    )

def fmt_order_summary(product: dict, qty: int, total: float,
                      balance: float, discount_pct: float = 0) -> str:
    disc_line = f"🎟 Coupon: <b>-{discount_pct:.0f}%</b>\n" if discount_pct else ""
    return (
        f"🛒 <b>Order Summary</b>\n{_SEP}\n"
        f"{product.get('emoji', '📦')} {product['name']}\n"
        f"🔢 Quantity: <b>{qty}</b>\n"
        f"💵 Price: <b>${product['price']:.2f}</b> × {qty}\n"
        f"{disc_line}"
        f"💰 Total: <b>${total:.2f}</b>\n{_LINE}\n"
        f"👛 Your Balance: <b>${balance:.2f}</b>\n\n"
        f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip."
    )

def fmt_confirm_service(category: str, product: dict, days: int,
                        price: float, balance: float) -> str:
    return (
        f"🛒 <b>Order Summary</b>\n{_SEP}\n"
        f"{product.get('emoji', '📦')} {product['name']}\n"
        f"⏱ Duration: <b>{days} day(s)</b>\n"
        f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"👛 Your Balance: <b>${balance:.2f}</b>\n\n"
        f"Press ✅ Confirm Purchase to place order."
    )

def fmt_order_receipt(oid: str, product_name: str, qty: int,
                      total: float, items: List[str], new_balance: float) -> str:
    preview = "\n".join(items[:5])
    more = f"\n<i>... and {len(items) - 5} more</i>" if len(items) > 5 else ""
    return (
        f"✅ <b>Order Successful!</b>\n{_SEP}\n"
        f"🆔 Order: <code>{oid[:12]}</code>\n"
        f"📦 {product_name} × {qty}\n"
        f"💵 Paid: <b>${total:.2f}</b>\n"
        f"👛 Balance left: <b>${new_balance:.2f}</b>\n{_SEP}\n"
        f"📋 <b>Your Accounts:</b>\n"
        f"<code>{preview}{more}</code>"
    )

def fmt_service_order_placed(cat_emoji: str, cat_name: str,
                              oid: str, product_name: str, days: int, price: float) -> str:
    return (
        f"{cat_emoji} <b>{cat_name} Order Placed!</b>\n{_SEP}\n"
        f"🆔 Order: <code>{oid[:12]}</code>\n"
        f"📦 {product_name}\n"
        f"⏱ Duration: <b>{days} day(s)</b>\n"
        f"💵 Paid: <b>${price:.2f}</b>\n{_SEP}\n"
        f"⏳ Status: <b>Pending</b>\n"
        f"Our team will deliver your order shortly.\n"
        f"You'll receive a notification when ready. 🔔"
    )

def fmt_deposit_info(method_label: str, number: str, rate: float, min_amt: float, is_usd: bool = False) -> str:
    if is_usd:
        return (
            f"💵 <b>Deposit via {method_label}</b>\n{_SEP}\n"
            f"🔑 UID: <code>{number or 'Not configured'}</code>\n"
            f"💰 Minimum: <b>${min_amt:.2f} USD</b>\n{_LINE}\n"
            f"Enter the amount you are sending (in USD):"
        )
    return (
        f"💵 <b>Deposit via {method_label}</b>\n{_SEP}\n"
        f"📱 Send to: <code>{number or 'Not configured'}</code>\n"
        f"💱 Rate: <b>1 USD = {rate:.0f} BDT</b>\n"
        f"💰 Minimum: <b>{min_amt:.0f} BDT</b>\n{_LINE}\n"
        f"Enter the amount you are sending (in BDT):"
    )

def fmt_deposit_confirm(method: str, amount_bdt: float, amount_usd: float, is_usd: bool = False) -> str:
    amt_str = f"${amount_usd:.2f} USD" if is_usd else f"{amount_bdt:.0f} BDT ≈ ${amount_usd:.2f}"
    return (
        f"💵 <b>Deposit Summary</b>\n{_SEP}\n"
        f"💱 Method: <b>{method}</b>\n"
        f"💰 Amount: <b>{amt_str}</b>\n{_LINE}\n"
        f"Now send your Transaction ID / Reference number:"
    )

def fmt_deposit_submitted(dep_id: str, method: str, amount_bdt: float, amount_usd: float, is_usd: bool = False) -> str:
    amt_str = f"${amount_usd:.2f} USD" if is_usd else f"{amount_bdt:.0f} BDT ≈ ${amount_usd:.2f}"
    return (
        f"✅ <b>Deposit Request Submitted!</b>\n{_SEP}\n"
        f"🆔 ID: <code>{dep_id[:12]}</code>\n"
        f"💱 Method: <b>{method}</b>\n"
        f"💰 Amount: <b>{amt_str}</b>\n{_SEP}\n"
        f"⏳ <b>Status: Pending Review</b>\n"
        f"Your balance will be credited once verified.\n"
        f"Usually within <b>5–30 minutes</b>. 🕐"
    )

def fmt_order_history(orders: list, vpn: list, proxy: list) -> str:
    if not orders and not vpn and not proxy:
        return (
            f"📭 <b>No Orders Yet</b>\n{_SEP}\n"
            f"You haven't placed any orders.\nBrowse our products to get started!"
        )
    lines = [f"📜 <b>Order History</b>\n{_SEP}"]
    if orders:
        lines.append("📮 <b>Mail Orders</b>")
        for o in orders[:8]:
            lines.append(f"  <code>{o['order_id'][:8]}</code>  {o['product_name']} ×{o['qty']}  ${o['total_price']:.2f}")
    if vpn:
        lines.append("\n🌐 <b>VPN Orders</b>")
        for o in vpn[:8]:
            s = {"delivered": "✅", "cancelled": "❌"}.get(o["status"], "⏳")
            lines.append(f"  <code>{o['order_id'][:8]}</code>  {o['product_name']} {o['duration_days']}d  ${o['price']:.2f}  {s}")
    if proxy:
        lines.append("\n🔐 <b>Proxy Orders</b>")
        for o in proxy[:8]:
            s = {"delivered": "✅", "cancelled": "❌"}.get(o["status"], "⏳")
            data_lbl = o.get("duration_days", "—")
            lines.append(f"  <code>{o['order_id'][:8]}</code>  {o['product_name']} {data_lbl}  ${o['price']:.2f}  {s}")
    return "\n".join(lines)

def fmt_deposit_history(deposits: list) -> str:
    if not deposits:
        return f"💳 <b>No Deposits Yet</b>\n{_SEP}\nMake your first deposit to start shopping!"
    lines = [f"💳 <b>Deposit History</b>\n{_SEP}"]
    for d in deposits[:12]:
        s = {"approved": "✅", "rejected": "❌"}.get(d["status"], "⏳")
        lines.append(f"{s} <code>{d['deposit_id'][:8]}</code>  {d['method']}  {d['amount_bdt']:.0f}BDT  ${d['amount_usd']:.2f}")
    return "\n".join(lines)

def fmt_admin_dashboard(stats: dict) -> str:
    return (
        f"📊 <b>Dashboard</b>\n{_SEP}\n"
        f"👥 Total Users: <b>{stats['total_users']}</b>\n"
        f"💵 Total Revenue: <b>${stats['total_revenue']:.2f}</b>\n"
        f"🛍 Total Sales: <b>{stats['total_sales']}</b>\n"
        f"💳 Pending Deposits: <b>{stats['pending_deposits']}</b>\n"
        f"📦 Pending Orders: <b>{stats['pending_orders']}</b>"
    )

def fmt_admin_deposit_review(d: dict) -> str:
    return (
        f"💳 <b>Deposit Request</b>\n{_SEP}\n"
        f"🆔 <code>{d['deposit_id']}</code>\n"
        f"👤 @{d.get('username','—')}  (<code>{d['user_id']}</code>)\n"
        f"💱 {d['method']}\n"
        f"💰 {d['amount_bdt']:.0f} BDT ≈ <b>${d['amount_usd']:.2f}</b>\n"
        f"🔑 TRX: <code>{d.get('trx_id','—')}</code>\n"
        f"🕒 {_dt(d['created_at'])}"
    )

def fmt_admin_vpn_order(o: dict) -> str:
    return (
        f"🌐 <b>New VPN Order</b>\n{_SEP}\n"
        f"🆔 <code>{o['order_id']}</code>\n"
        f"👤 @{o.get('username','—')}  (<code>{o['user_id']}</code>)\n"
        f"📦 {o['product_name']}\n"
        f"⏱ {o['duration_days']} day(s)\n"
        f"💵 ${o['price']:.2f}\n"
        f"🕒 {_dt(o['created_at'])}"
    )

def fmt_admin_proxy_order(o: dict) -> str:
    data_lbl = o.get("duration_days", "—")
    return (
        f"🔐 <b>New Proxy Order</b>\n{_SEP}\n"
        f"🆔 <code>{o['order_id']}</code>\n"
        f"👤 @{o.get('username','—')}  (<code>{o['user_id']}</code>)\n"
        f"📦 {o['product_name']}\n"
        f"📡 Data: {data_lbl}\n"
        f"💵 ${o['price']:.2f}\n"
        f"🕒 {_dt(o['created_at'])}"
    )

def fmt_user_info(user: dict) -> str:
    banned = "🚫 Banned" if user.get("is_banned") else "✅ Active"
    return (
        f"👤 <b>User Profile</b>\n{_SEP}\n"
        f"🆔 <code>{user['user_id']}</code>\n"
        f"👤 @{user.get('username', '—')}\n"
        f"📛 {user.get('full_name', '—')}\n"
        f"💰 Balance: <b>${user.get('balance', 0):.2f}</b>\n"
        f"💸 Spent: <b>${user.get('total_spent', 0):.2f}</b>\n"
        f"🛍 Orders: <b>{user.get('order_count', 0)}</b>\n"
        f"📅 Joined: {_dt(user.get('joined_at', 0))}\n"
        f"Status: {banned}"
    )

def fmt_settings(s: dict) -> str:
    ch1  = s.get('force_join_channel') or '—'
    ch2  = s.get('force_join_channel_2') or '—'
    bkno = s.get('bkash_number') or '—'
    ngno = s.get('nagad_number') or '—'
    bnid = s.get('binance_uid') or '—'
    return (
        f"⚙️ <b>Bot Settings</b>\n{_SEP}\n"
        f"🏪 <b>{s.get('shop_name') or 'Shop'}</b>  |  💱 <b>1 USD = {s.get('usd_rate', 125):.0f} BDT</b>\n"
        f"⚠️ Low Stock Alert: <b>{s.get('low_stock_threshold', 5)}</b>\n"
        f"\n"
        f"<b>── 💳 Payment ──</b>\n"
        f"📱 bKash  <code>{bkno}</code>  · min <b>{s.get('bkash_min', 100):.0f} BDT</b>\n"
        f"📱 Nagad  <code>{ngno}</code>  · min <b>{s.get('nagad_min', 150):.0f} BDT</b>\n"
        f"🔶 Binance  <code>{bnid}</code>  · min <b>${s.get('binance_min', 5):.2f}</b>\n"
        f"\n"
        f"<b>── 🔗 Links ──</b>\n"
        f"📣 Ch1: <b>{ch1}</b>  |  Ch2: <b>{ch2}</b>\n"
        f"🆘 Support: <b>{s.get('support_username') or '—'}</b>\n"
        f"🔑 2FA Link: <b>{s.get('get_2fa_link') or '—'}</b>\n"
        f"\n"
        f"<b>── 📡 Proxy ──</b>\n"
        f"Data Options: <code>{s.get('proxy_data_options', '1 GB,5 GB,10 GB,50 GB')}</code>"
    )


# ══════════════════════════════════════════════════════════════════
# VALIDATORS
# ══════════════════════════════════════════════════════════════════

def validate_quantity(text: str, max_stock: int) -> Tuple[Optional[int], Optional[str]]:
    try:
        qty = int(text.strip())
    except ValueError:
        return None, "❌ Please enter a valid number."
    if qty <= 0:
        return None, "❌ Quantity must be at least 1."
    if qty > max_stock:
        return None, f"❌ Only <b>{max_stock}</b> in stock."
    return qty, None

def validate_amount_bdt(text: str, minimum: float) -> Tuple[Optional[float], Optional[str]]:
    try:
        amount = float(text.strip())
    except ValueError:
        return None, "❌ Please enter a valid amount."
    if amount <= 0:
        return None, "❌ Amount must be positive."
    if amount < minimum:
        return None, f"❌ Minimum deposit is <b>{minimum:.0f} BDT</b>"
    return amount, None

def validate_custom_days(text: str) -> Tuple[Optional[int], Optional[str]]:
    try:
        days = int(text.strip())
    except ValueError:
        return None, "❌ Enter a valid number of days."
    if days < 1:
        return None, "❌ Minimum 1 day."
    if days > 365:
        return None, "❌ Maximum 365 days."
    return days, None

def validate_coupon(coupon: dict) -> Tuple[bool, Optional[str]]:
    if not coupon.get("active"):
        return False, "❌ Coupon is no longer active."
    if coupon.get("expires_at", 0) < int(time.time()):
        return False, "❌ Coupon has expired."
    if coupon.get("used_count", 0) >= coupon.get("max_uses", 1):
        return False, "❌ Coupon usage limit reached."
    return True, None

def validate_price(text: str) -> Tuple[Optional[float], Optional[str]]:
    try:
        p = float(text.strip())
    except ValueError:
        return None, "❌ Enter a valid price."
    if p < 0:
        return None, "❌ Price cannot be negative."
    return p, None

def validate_discount(text: str) -> Tuple[Optional[float], Optional[str]]:
    try:
        pct = float(text.strip())
    except ValueError:
        return None, "❌ Enter a valid percentage."
    if not (0 < pct <= 100):
        return None, "❌ Must be between 1 and 100."
    return pct, None


# ══════════════════════════════════════════════════════════════════
# FSM STATES
# ══════════════════════════════════════════════════════════════════

class UserFlow(StatesGroup):
    mail_product   = State()
    mail_qty       = State()
    mail_coupon       = State()
    mail_coupon_input = State()
    mail_confirm      = State()
    set_totp_key      = State()
    vpn_product      = State()
    vpn_duration     = State()
    vpn_custom       = State()
    vpn_coupon       = State()
    vpn_coupon_input = State()
    vpn_confirm      = State()
    proxy_product           = State()
    proxy_duration          = State()
    proxy_custom            = State()
    proxy_coupon            = State()
    proxy_coupon_input      = State()
    proxy_confirm           = State()
    proxy_auto_qty          = State()
    proxy_auto_coupon       = State()
    proxy_auto_coupon_input = State()
    proxy_auto_confirm      = State()
    dep_method     = State()
    dep_amount     = State()
    dep_trx        = State()
    dep_screenshot = State()
    # Get Code / Mailbox flow
    get_code_menu   = State()
    get_code_set    = State()
    get_code_filter = State()
    # Temp Mail flow
    temp_mail_menu   = State()
    temp_mail_domain = State()

class AdminFlow(StatesGroup):
    menu              = State()
    products_list     = State()
    product_detail    = State()
    product_edit      = State()
    product_add_name  = State()
    product_add_emoji = State()
    product_add_price = State()
    product_add_cat   = State()
    product_add_desc  = State()
    stock_list        = State()
    stock_detail      = State()
    stock_uploading   = State()
    stock_manual      = State()
    user_search       = State()
    user_detail       = State()
    user_add_bal      = State()
    user_remove_bal   = State()
    coupons_list      = State()
    coupon_detail     = State()
    coupon_code       = State()
    coupon_discount   = State()
    coupon_max_uses   = State()
    coupon_expiry     = State()
    broadcast         = State()
    settings_menu     = State()
    settings_edit     = State()
    vpn_fulfill       = State()
    proxy_fulfill     = State()
    dep_reject_reason = State()
    products_import   = State()
    proxy_pkg_list    = State()
    proxy_pkg_add     = State()


# ══════════════════════════════════════════════════════════════════
# KEYBOARDS
# ══════════════════════════════════════════════════════════════════

def _kb(*rows, resize: bool = True, one_time: bool = False) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t) for t in row] for row in rows],
        resize_keyboard=resize,
        one_time_keyboard=one_time,
    )

def main_menu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_BALANCE,  BTN_GET_MAIL],
        [BTN_BUY_VPN,  BTN_BUY_PROXY],
        [BTN_DEPOSIT,  BTN_GET_CODE],
        [BTN_GET_2FA,  BTN_HISTORY],
        [BTN_TEMP_MAIL],
        [BTN_SUPPORT],
    )

def _nav_row() -> List[str]:
    return [BACK_BTN, HOME_BTN]

def products_kb(display_map: dict) -> ReplyKeyboardMarkup:
    rows = [[k] for k in display_map.keys()]
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

DURATION_MAP = {
    BTN_1DAY: 1, BTN_7DAYS: 7,
    BTN_30DAYS: 30, BTN_90DAYS: 90,
    BTN_CUSTOM: -1,
}

def duration_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_1DAY,   BTN_7DAYS],
        [BTN_30DAYS, BTN_90DAYS],
        [BTN_CUSTOM],
        [BACK_BTN, HOME_BTN],
    )

BTN_PROXY_DATA_CUSTOM = _b("📡 Custom Amount")

def parse_proxy_data_options(options_str: str) -> List[str]:
    return [o.strip() for o in options_str.split(",") if o.strip()]

def proxy_data_kb(options_str: str = "1 GB,5 GB,10 GB,50 GB") -> ReplyKeyboardMarkup:
    opts = parse_proxy_data_options(options_str)
    rows = []
    for i in range(0, len(opts), 2):
        row = [_b(opts[i])]
        if i + 1 < len(opts):
            row.append(_b(opts[i + 1]))
        rows.append(row)
    rows.append([BTN_PROXY_DATA_CUSTOM])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def parse_data_amount(text: str) -> Tuple[Optional[float], Optional[str]]:
    raw = text.strip()
    clean = raw.upper().replace("GB", "").replace("MB", "").strip()
    try:
        amount = float(clean)
    except ValueError:
        return None, "❌ Valid number লিখুন (e.g. 5 GB বা 500 MB)."
    if amount <= 0:
        return None, "❌ Amount must be positive."
    if amount > 100000:
        return None, "❌ Maximum 100000 GB/MB."
    return amount, None

def confirm_kb() -> ReplyKeyboardMarkup:
    """First confirmation — includes Apply Coupon button (mail flow only)."""
    return _kb([BTN_CONFIRM], [BTN_COUPON], [BACK_BTN, HOME_BTN])

def confirm_final_kb() -> ReplyKeyboardMarkup:
    """Final confirmation — no coupon button (used for 2nd mail confirm, VPN, Proxy)."""
    return _kb([BTN_CONFIRM], [BACK_BTN, HOME_BTN])

def input_kb() -> ReplyKeyboardMarkup:
    return _kb([CANCEL_BTN, HOME_BTN])

def tfa_inline_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh Code", callback_data="tfa_refresh")],
        [
            InlineKeyboardButton(text="⏱ Timer", callback_data="tfa_timer"),
            InlineKeyboardButton(text="🔑 Change Key", callback_data="tfa_setkey"),
        ],
    ])

def tfa_nokey_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Set My Key", callback_data="tfa_setkey")],
    ])

def _totp_secs() -> int:
    return 30 - (int(time.time()) % 30)

def _totp_bar(secs: int) -> str:
    filled = round(secs / 30 * 10)
    return "█" * filled + "░" * (10 - filled)

def _valid_totp_key(key: str) -> bool:
    try:
        pyotp.TOTP(key).now()
        return True
    except Exception:
        return False

def _fmt_totp(code: str) -> str:
    secs = _totp_secs()
    bar  = _totp_bar(secs)
    return (
        f"🔑 <b>Your 2FA Code</b>\n{_SEP}\n"
        f"<code>{code[:3]} {code[3:]}</code>\n\n"
        f"⏱ Expires in: <b>{secs}s</b>\n"
        f"[{bar}]"
    )

DEPOSIT_MAP = {
    BTN_BKASH:   "bkash",
    BTN_NAGAD:   "nagad",
    BTN_BINANCE: "binance",
}

def deposit_method_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_BKASH, BTN_NAGAD],
        [BTN_BINANCE],
        [BACK_BTN, HOME_BTN],
    )

def admin_main_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_ADM_DASHBOARD,    BTN_ADM_PRODUCTS],
        [BTN_ADM_STOCK,        BTN_ADM_USERS],
        [BTN_ADM_DEPOSITS,     BTN_ADM_VPN_ORDERS],
        [BTN_ADM_PROXY_ORDERS, BTN_ADM_COUPONS],
        [BTN_ADM_BROADCAST,    BTN_ADM_SETTINGS],
        [BTN_ADM_PROXY_PKGS,   BTN_ADM_EXPORT],
        [HOME_BTN],
    )

def proxy_pkg_manage_kb(options: list) -> ReplyKeyboardMarkup:
    rows = [[f"🗑 {o}"] for o in options]
    rows.append([BTN_PKG_ADD])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

SETTINGS_MAP = {
    _b("💱 USD Rate"):           ("usd_rate",             float, "Enter BDT per 1 USD (e.g. 125):"),
    _b("📱 bKash Number"):       ("bkash_number",          str,   "Enter bKash number:"),
    _b("📱 bKash Min Deposit"):  ("bkash_min",             float, "Enter minimum bKash deposit in BDT (e.g. 100):"),
    _b("📱 Nagad Number"):       ("nagad_number",          str,   "Enter Nagad number:"),
    _b("📱 Nagad Min Deposit"):  ("nagad_min",             float, "Enter minimum Nagad deposit in BDT (e.g. 150):"),
    _b("🔶 Binance UID"):        ("binance_uid",           str,   "Enter Binance Pay UID:"),
    _b("🔶 Binance Min Deposit"):("binance_min",           float, "Enter minimum Binance deposit in USD (e.g. 5):"),
    _b("📣 Force Join #1"):      ("force_join_channel",    str,   "Enter channel (e.g. @mychannel) or blank to disable:"),
    _b("📣 Force Join #2"):      ("force_join_channel_2",  str,   "Enter 2nd channel or blank to disable:"),
    _b("🆘 Support Link"):       ("support_username",      str,   "Enter support username (e.g. @support):"),
    _b("🔑 Get 2FA Link"):       ("get_2fa_link",          str,   "Enter the Get 2FA URL:"),
    _b("🏪 Shop Name"):          ("shop_name",             str,   "Enter shop display name:"),
    _b("💬 Welcome Message"):    ("welcome_message",       str,   "Enter welcome message text:"),
    _b("⚠️ Low Stock Alert"):    ("low_stock_threshold",   float, "Enter low stock threshold (number):"),
    _b("📡 Proxy Data Options"): ("proxy_data_options",    str,   "Enter data options separated by commas (e.g. 1 GB,5 GB,10 GB,50 GB).\nAdmin can set any GB/MB values here:"),
}

def admin_settings_kb() -> ReplyKeyboardMarkup:
    keys = list(SETTINGS_MAP.keys())
    rows = [keys[i:i+2] for i in range(0, len(keys), 2)]
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

CATEGORY_MAP = {
    BTN_CAT_MAIL:  "mail",
    BTN_CAT_VPN:   "vpn",
    BTN_CAT_PROXY: "proxy",
}

def admin_category_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_CAT_MAIL],
        [BTN_CAT_VPN],
        [BTN_CAT_PROXY],
        [CANCEL_BTN, HOME_BTN],
    )

def admin_products_kb(products: dict) -> ReplyKeyboardMarkup:
    rows = [
        [f"{p.get('emoji','📦')} {p['name']} [{p.get('category','mail').upper()}] — ${p['price']:.2f}"]
        for pid, p in products.items()
    ]
    rows.append([BTN_ADD_PRODUCT])
    rows.append([BTN_DOWNLOAD_PRODUCTS, BTN_IMPORT_PRODUCTS])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def build_admin_products_dm(products: dict) -> dict:
    return {
        f"{p.get('emoji','📦')} {p['name']} [{p.get('category','mail').upper()}] — ${p['price']:.2f}": pid
        for pid, p in products.items()
    }

def admin_product_actions_kb(hidden: bool, category: str = "mail", delivery_mode: str = "manual") -> ReplyKeyboardMarkup:
    toggle = BTN_SHOW_PROD if hidden else BTN_HIDE_PROD
    rows: list = [
        [BTN_EDIT_NAME,  BTN_EDIT_PRICE],
        [BTN_EDIT_EMOJI, toggle],
        [BTN_EDIT_DESC],
    ]
    if category == "mail" or (category == "proxy" and delivery_mode == "auto"):
        rows.append([BTN_ADD_STOCK])
    if category == "proxy":
        mode_btn = BTN_TOGGLE_MANUAL if delivery_mode == "auto" else BTN_TOGGLE_AUTO
        rows.append([mode_btn])
    rows.append([BTN_DELETE, BACK_BTN])
    rows.append([HOME_BTN])
    return _kb(*rows)

def admin_stock_products_kb(products: dict) -> ReplyKeyboardMarkup:
    rows = [[f"{p.get('emoji','📦')} {p['name']}  📦{p.get('stock_count',0)}"] for p in products.values()]
    rows.append([BTN_DOWNLOAD_ALL_STOCK])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def build_admin_stock_dm(products: dict) -> dict:
    return {
        f"{p.get('emoji','📦')} {p['name']}  📦{p.get('stock_count',0)}": pid
        for pid, p in products.items()
    }

def admin_stock_actions_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_GET_TEMPLATE, BTN_DOWNLOAD_STOCK],
        [BTN_UPLOAD_FILE, BTN_MANUAL_ADD],
        [BTN_CLEAR_STOCK],
        [BACK_BTN, HOME_BTN],
    )

def admin_user_actions_kb(is_banned: bool) -> ReplyKeyboardMarkup:
    ban_btn = BTN_UNBAN_USER if is_banned else BTN_BAN_USER
    return _kb(
        [ban_btn],
        [BTN_ADD_BAL, BTN_REMOVE_BAL],
        [BACK_BTN, HOME_BTN],
    )

def get_code_menu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [BTN_GC_SET_MAIL,  BTN_GC_CODES],
        [BTN_GC_INBOX,     BTN_GC_REFRESH],
        [BTN_GC_FILTER,    BTN_GC_CHANGE],
        [BACK_BTN, HOME_BTN],
    )

def get_code_filter_kb() -> ReplyKeyboardMarkup:
    rows = []
    row: List[str] = []
    for svc in _DV_SERVICE_LIST:
        row.append(svc)
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def admin_coupons_kb(coupons: list) -> ReplyKeyboardMarkup:
    rows = [[f"🎟 {c['code']}  {c['discount_pct']:.0f}%  ({c['used_count']}/{c['max_uses']})"] for c in coupons]
    rows.append([BTN_CREATE_COUPON])
    rows.append([BACK_BTN, HOME_BTN])
    return _kb(*rows)

def build_coupons_dm(coupons: list) -> dict:
    return {
        f"🎟 {c['code']}  {c['discount_pct']:.0f}%  ({c['used_count']}/{c['max_uses']})": c["coupon_id"]
        for c in coupons
    }

def admin_coupon_actions_kb() -> ReplyKeyboardMarkup:
    return _kb([BTN_DELETE_COUPON], [BACK_BTN, HOME_BTN])

# In-memory pending state: admin_id → context dict
_pending_fulfill: Dict[int, Dict] = {}   # VPN/Proxy credentials input
_pending_reject:  Dict[int, Dict] = {}   # Deposit reject reason input

def deposit_review_inline(dep_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Approve",      callback_data=f"dep_ok:{dep_id}"),
        InlineKeyboardButton(text="❌ Reject + Reason", callback_data=f"dep_no:{dep_id}"),
    ]])

def order_review_inline(oid: str, kind: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📝 Send Credentials", callback_data=f"{kind}_ok:{oid}"),
        InlineKeyboardButton(text="❌ Cancel & Refund",   callback_data=f"{kind}_no:{oid}"),
    ]])


# ══════════════════════════════════════════════════════════════════
# MIDDLEWARE — Anti-Spam
# ══════════════════════════════════════════════════════════════════

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self):
        self._last: Dict[int, float] = {}
        self._hist: Dict[int, deque] = defaultdict(deque)

    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)
        uid = event.from_user.id if event.from_user else None
        if uid is None or is_admin(uid):
            return await handler(event, data)
        now = time.time()
        if now - self._last.get(uid, 0) < SPAM_COOLDOWN:
            await event.answer(f"⏳ Slow down! Wait {SPAM_COOLDOWN:.0f}s between messages.")
            return
        hist = self._hist[uid]
        while hist and now - hist[0] > SPAM_WINDOW:
            hist.popleft()
        if len(hist) >= SPAM_MAX_MSGS:
            await event.answer("🚫 Too many messages. Please wait a moment.")
            return
        hist.append(now)
        self._last[uid] = now
        return await handler(event, data)


# ══════════════════════════════════════════════════════════════════
# MIDDLEWARE — Auth  (BUG FIX: also handle CallbackQuery)
# ══════════════════════════════════════════════════════════════════

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]) -> Any:
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if not user:
            return await handler(event, data)

        db_user = await create_or_update_user(user.id, user.username or "", user.full_name or "")
        data["db_user"] = db_user

        if db_user.get("is_banned") and not is_admin(user.id):
            msg = (
                "🚫 <b>Account Banned</b>\n\n"
                "Your account has been banned from this shop.\n"
                "Contact support if you think this is a mistake."
            )
            if isinstance(event, Message):
                await event.answer(msg)
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Account banned.", show_alert=True)
            return
        return await handler(event, data)


# ══════════════════════════════════════════════════════════════════
# HELPER — Force-Join check  (BUG FIX: handle https:// links)
# ══════════════════════════════════════════════════════════════════

def _parse_channel(raw: str) -> str:
    """Convert any channel format to @username or numeric ID."""
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith("https://t.me/"):
        handle = raw.split("https://t.me/")[-1].strip("/")
        if handle:
            return f"@{handle}"
    if raw.startswith("@"):
        return raw
    if raw.lstrip("-").isdigit():
        return raw
    return f"@{raw}"


def _channel_to_url(raw: str) -> str:
    """Return a clickable https://t.me/ URL from any channel format."""
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith("https://t.me/"):
        return raw
    username = raw.lstrip("@")
    return f"https://t.me/{username}"


def _channel_display_name(raw: str) -> str:
    """Return a short human-readable name for a channel."""
    raw = raw.strip()
    if raw.startswith("https://t.me/"):
        return raw.split("https://t.me/")[-1].strip("/")
    return raw.lstrip("@")


async def check_force_join(bot: Bot, uid: int) -> Tuple[bool, List[str]]:
    settings = await get_settings()
    failed = []
    for key in ("force_join_channel", "force_join_channel_2"):
        raw_ch = (settings.get(key) or "").strip()
        if not raw_ch:
            continue
        ch = _parse_channel(raw_ch)
        if not ch:
            continue
        try:
            m = await bot.get_chat_member(ch, uid)
            if m.status in ("left", "kicked"):
                failed.append(raw_ch)
        except Exception as e:
            logger.warning("Force-join check failed for %s: %s", ch, e)
    return len(failed) == 0, failed


async def send_main_menu(message: Message, state: FSMContext, text: Optional[str] = None) -> None:
    await state.clear()
    settings = await get_settings()
    user = await get_user(message.from_user.id) or {}
    shop_name = settings.get("shop_name", "🛍 Neroxa Shop")
    welcome   = settings.get("welcome_message", WELCOME_MSG)
    balance   = user.get("balance", 0)
    display   = text or fmt_welcome(shop_name, welcome, message.from_user.first_name, balance)
    await message.answer(display, reply_markup=main_menu_kb())


# ══════════════════════════════════════════════════════════════════
# GLOBAL ROUTER — Home (works from ANY state)
# ══════════════════════════════════════════════════════════════════

router_global = Router()

@router_global.message(F.text == HOME_BTN)
async def go_home(message: Message, state: FSMContext):
    await send_main_menu(message, state)


# ══════════════════════════════════════════════════════════════════
# TEMP MAIL — API Helpers & In-memory store
# ══════════════════════════════════════════════════════════════════

_TEMPMAIL_API = "https://api.internal.temp-mail.io/api/v3"

# In-memory store: uid -> {email, token, seen_ids: set, messages: {short_id: msg_dict}, msg_index: int}
_tempmail_sessions: Dict[int, dict] = {}


def _tempmail_request(url: str, payload: Optional[dict] = None) -> dict:
    headers = {"Content-Type": "application/json", "User-Agent": "NeroxaShopBot/1.0"}
    data = json.dumps(payload).encode() if payload else None
    try:
        req = _urllib_request.Request(url, data=data, headers=headers)
        with _urllib_request.urlopen(req, timeout=12) as res:
            return json.loads(res.read())
    except Exception as e:
        logger.error("TempMail request error: %s", e)
        return {}


_TEMPMAIL_DOMAIN = "bltiwd.com"

async def _tm_get_domains() -> List[str]:
    def _extract(raw) -> List[str]:
        """Recursively extract domain name strings from any API response shape."""
        if isinstance(raw, str):
            return [raw] if raw else []
        if isinstance(raw, dict):
            # {"domains": [...]}  or  {"name": "bltiwd.com"}
            if "name" in raw:
                return [str(raw["name"])]
            for key in ("domains", "data", "list"):
                if key in raw:
                    return _extract(raw[key])
            return []
        if isinstance(raw, list):
            result = []
            for item in raw:
                result.extend(_extract(item))
            return result
        return []

    def _call():
        try:
            url = f"{_TEMPMAIL_API}/domains"
            req = _urllib_request.Request(url, headers={"User-Agent": "NeroxaShopBot/1.0"})
            with _urllib_request.urlopen(req, timeout=10) as res:
                data = json.loads(res.read())
                names = [d for d in _extract(data) if d]
                return names if names else [_TEMPMAIL_DOMAIN]
        except Exception as e:
            logger.error("TempMail domains error: %s", e)
        return [_TEMPMAIL_DOMAIN]
    return await _run(_call)

async def _tm_create_email(domain: str = _TEMPMAIL_DOMAIN) -> Tuple[Optional[str], Optional[str]]:
    def _call():
        r = _tempmail_request(f"{_TEMPMAIL_API}/email/new", {
            "min_name_length": 10,
            "max_name_length": 10,
            "domain": domain,
        })
        return r.get("email"), r.get("token")
    return await _run(_call)


async def _tm_get_inbox(email: str) -> List[dict]:
    def _call():
        url = f"{_TEMPMAIL_API}/email/{email}/messages"
        headers = {"accept": "application/json", "User-Agent": "NeroxaShopBot/1.0"}
        try:
            req = _urllib_request.Request(url, headers=headers)
            with _urllib_request.urlopen(req, timeout=12) as res:
                data = json.loads(res.read())
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error("TempMail inbox error: %s", e)
            return []
    return await _run(_call)


def _tm_strip_html(html: str) -> str:
    if not html:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    for ent, ch in [("&amp;","&"),("&lt;","<"),("&gt;",">"),("&quot;",'"'),("&nbsp;"," "),("&#39;","'")]:
        text = text.replace(ent, ch)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _tm_extract_otp(body: str) -> Optional[str]:
    patterns = [
        r'\b(\d{4,8})\s+is your',
        r'[Cc]ode[:\s]+(\d{4,8})',
        r'OTP[:\s]*(\d{4,8})',
        r'[Vv]erification code[:\s]*(\d{4,8})',
        r'\b([A-Z0-9]{6,10})\b',
    ]
    for pat in patterns:
        m = re.search(pat, body[:1000])
        if m:
            return m.group(1)
    return None


def _tm_format_body(body_text: str, body_html: str) -> str:
    body = (body_text or "").strip() or _tm_strip_html(body_html or "")
    if not body:
        return "<i>No content</i>"
    otp = _tm_extract_otp(body)
    preview = body[:2000]
    result = f"<pre>{html_lib.escape(preview)}</pre>"
    if len(body) > 2000:
        result += "\n<i>… truncated</i>"
    if otp:
        result += f"\n\n🔑 <b>Code detected:</b> <code>{html_lib.escape(otp)}</code>"
    return result


def _tm_menu_kb() -> ReplyKeyboardMarkup:
    return _kb(
        [_TM_GEN],
        [_TM_INB, _TM_REF],
        [_TM_MY,  _TM_DEL],
        [_TM_DOM, _TM_RND],
        [BACK_BTN, HOME_BTN],
    )

def _tm_domain_kb(domains: List[str]) -> ReplyKeyboardMarkup:
    rows = [[_TM_RND]]                                         # Random at top
    rows += [domains[i:i+2] for i in range(0, min(len(domains), 16), 2)]
    rows.append([BACK_BTN])
    return _kb(*rows)


# ══════════════════════════════════════════════════════════════════
# ROUTER — Start & Main Menu
# ══════════════════════════════════════════════════════════════════

router_start = Router()


@router_start.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    if is_admin(message.from_user.id):
        await state.set_state(AdminFlow.menu)
        await message.answer(
            f"🔐 <b>Admin Panel</b>\n{_SEP}\nWelcome back, admin! 👋",
            reply_markup=admin_main_kb(),
        )
        return
    passed, failed_channels = await check_force_join(message.bot, message.from_user.id)
    if not passed:
        try:
            bot_info = await message.bot.get_me()
            bot_username = bot_info.username
        except Exception:
            bot_username = None
        buttons = [
            [InlineKeyboardButton(
                text=f"📢 {_channel_display_name(ch)} — Join Now",
                url=_channel_to_url(ch),
            )]
            for ch in failed_channels
        ]
        if bot_username:
            buttons.append([InlineKeyboardButton(
                text="✅ I Joined — Check Again",
                url=f"https://t.me/{bot_username}?start=check",
            )])
        await message.answer(
            f"🔒 <b>Join Required</b>\n{_SEP}\n"
            f"Please join our channel(s) to access the shop.\n\n"
            f"After joining, press <b>✅ I Joined — Check Again</b> or send /start. ✅",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
        return
    await send_main_menu(message, state)


@router_start.message(F.text == BTN_BALANCE)
async def show_balance(message: Message):
    user = await get_user(message.from_user.id) or {}
    await message.answer(fmt_balance_screen(user), reply_markup=main_menu_kb())


@router_start.message(F.text == BTN_GET_CODE)
async def get_code(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    status  = f"📧 <code>{html_lib.escape(session['email'])}</code>" if session else "❌ No mail set"
    await state.set_state(UserFlow.get_code_menu)
    await message.answer(
        f"🔓 <b>Get Code — Mail Inbox</b>\n{_SEP}\n"
        f"Current mail: {status}\n\n"
        f"Use the buttons below to manage your mailbox.",
        reply_markup=get_code_menu_kb(),
    )


# ── Get Code sub-menu handlers ─────────────────────────────────────

@router_start.message(UserFlow.get_code_menu, F.text == BACK_BTN)
async def gc_back(message: Message, state: FSMContext):
    await send_main_menu(message, state)


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_SET_MAIL)
async def gc_set_mail(message: Message, state: FSMContext):
    await state.set_state(UserFlow.get_code_set)
    await message.answer(
        f"📧 <b>Set Mail</b>\n{_SEP}\n"
        f"Send your account data in format:\n\n"
        f"<code>email|password|refresh_token|client_id</code>\n\n"
        f"Or just:\n<code>email|password</code>\n\n"
        f"(OAuth2 will be auto-fetched if not provided)\n\n"
        f"Press {BACK_BTN} to cancel.",
        reply_markup=input_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_CHANGE)
async def gc_change_mail(message: Message, state: FSMContext):
    uid = message.from_user.id
    if uid in _mail_sessions:
        del _mail_sessions[uid]
    await state.set_state(UserFlow.get_code_set)
    await message.answer(
        f"✏️ <b>Change Mail</b>\n{_SEP}\n"
        f"Session cleared! Send new account data:\n\n"
        f"<code>email|password|refresh_token|client_id</code>\n\n"
        f"Press {BACK_BTN} to cancel.",
        reply_markup=input_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_CODES)
async def gc_get_codes(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await message.answer(
            f"❌ <b>No mail set!</b>\n{_SEP}\nPress <b>📧 Set Mail</b> first.",
            reply_markup=get_code_menu_kb(),
        )
        return
    if not _session_has_oauth2(session):
        await message.answer(
            f"⚠️ <b>OAuth2 Not Set</b>\n{_SEP}\n"
            f"📧 <code>{html_lib.escape(session['email'])}</code>\n\n"
            f"Your mail was auto-set but OAuth2 token is missing.\n"
            f"Press <b>📧 Set Mail</b> and enter:\n"
            f"<code>email|password|refresh_token|client_id</code>",
            reply_markup=get_code_menu_kb(),
        )
        return
    wait = await message.answer(f"🔄 Fetching codes for <code>{html_lib.escape(session['email'])}</code>…")
    all_msgs: List[dict] = []
    code_data = await _dv_get_code(session["email"], session["refresh_token"], session["client_id"], "all")
    if code_data and code_data.get("status") and code_data.get("code"):
        svc = _dv_determine_service(code_data.get("content", ""), "", "")
        all_msgs.append({"code": code_data["code"], "service": svc,
                         "subject": code_data.get("content", ""), "sender": "",
                         "date": code_data.get("date", ""), "address": ""})
    msgs = await _dv_get_messages(session["email"], session["refresh_token"], session["client_id"])
    if msgs and msgs.get("status"):
        existing = {m["code"] for m in all_msgs}
        for c in _dv_extract_codes(msgs):
            if c["code"] not in existing:
                all_msgs.append(c)
                existing.add(c["code"])
    if not all_msgs:
        msgs2 = await _dv_graph_messages(session["email"], session["refresh_token"], session["client_id"])
        if msgs2 and msgs2.get("status"):
            all_msgs = _dv_extract_codes(msgs2)
    display = _dv_build_codes_display(all_msgs)
    await _safe_delete(wait)
    await message.answer(
        _truncate_msg(f"📧 <code>{html_lib.escape(session['email'])}</code>\n{display}"),
        reply_markup=get_code_menu_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_INBOX)
async def gc_read_inbox(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await message.answer(f"❌ <b>No mail set!</b>\n{_SEP}\nPress <b>📧 Set Mail</b> first.", reply_markup=get_code_menu_kb())
        return
    if not _session_has_oauth2(session):
        await message.answer(
            f"⚠️ <b>OAuth2 Not Set</b>\n{_SEP}\n"
            f"📧 <code>{html_lib.escape(session['email'])}</code>\n\n"
            f"Press <b>📧 Set Mail</b> and enter full credentials:\n"
            f"<code>email|password|refresh_token|client_id</code>",
            reply_markup=get_code_menu_kb(),
        )
        return
    wait = await message.answer(f"📨 Reading <code>{html_lib.escape(session['email'])}</code>…")
    messages = await _dv_process_mailbox(session)
    display  = _dv_build_mailbox_display(messages)
    await _safe_delete(wait)
    await message.answer(
        _truncate_msg(
            f"📧 <code>{html_lib.escape(session['email'])}</code>\n"
            f"🔑 <code>{html_lib.escape(session['password'])}</code>\n{display}"
        ),
        reply_markup=get_code_menu_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_REFRESH)
async def gc_refresh(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await message.answer(f"❌ <b>No mail set!</b>\n{_SEP}\nPress <b>📧 Set Mail</b> first.", reply_markup=get_code_menu_kb())
        return
    if not _session_has_oauth2(session):
        await message.answer(
            f"⚠️ <b>OAuth2 Not Set</b>\n{_SEP}\n"
            f"📧 <code>{html_lib.escape(session['email'])}</code>\n\n"
            f"Press <b>📧 Set Mail</b> and enter full credentials:\n"
            f"<code>email|password|refresh_token|client_id</code>",
            reply_markup=get_code_menu_kb(),
        )
        return
    wait = await message.answer(f"🔄 Refreshing <code>{html_lib.escape(session['email'])}</code>…")
    messages = await _dv_process_mailbox(session)
    display  = _dv_build_mailbox_display(messages)
    await _safe_delete(wait)
    await message.answer(
        _truncate_msg(f"✅ <b>Refreshed!</b>\n\n📧 <code>{html_lib.escape(session['email'])}</code>\n{display}"),
        reply_markup=get_code_menu_kb(),
    )


@router_start.message(UserFlow.get_code_menu, F.text == BTN_GC_FILTER)
async def gc_show_filter(message: Message, state: FSMContext):
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await message.answer(f"❌ <b>No mail set!</b>\n{_SEP}\nPress <b>📧 Set Mail</b> first.", reply_markup=get_code_menu_kb())
        return
    if not _session_has_oauth2(session):
        await message.answer(
            f"⚠️ <b>OAuth2 Not Set</b>\n{_SEP}\n"
            f"📧 <code>{html_lib.escape(session['email'])}</code>\n\n"
            f"Press <b>📧 Set Mail</b> and enter full credentials:\n"
            f"<code>email|password|refresh_token|client_id</code>",
            reply_markup=get_code_menu_kb(),
        )
        return
    await state.set_state(UserFlow.get_code_filter)
    await state.update_data(gc_email=session["email"])
    await message.answer(
        f"🔍 <b>Filter by Service</b>\n{_SEP}\n📧 <code>{html_lib.escape(session['email'])}</code>\n\nSelect a service:",
        reply_markup=get_code_filter_kb(),
    )


@router_start.message(UserFlow.get_code_set)
async def gc_receive_mail_data(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await state.set_state(UserFlow.get_code_menu)
        uid     = message.from_user.id
        session = _mail_sessions.get(uid)
        status  = f"📧 <code>{html_lib.escape(session['email'])}</code>" if session else "❌ No mail set"
        await message.answer(
            f"🔓 <b>Get Code — Mail Inbox</b>\n{_SEP}\nCurrent mail: {status}",
            reply_markup=get_code_menu_kb(),
        )
        return
    text = message.text or ""
    if "|" not in text:
        await message.answer("❌ Invalid format. Use: <code>email|password|refresh_token|client_id</code>", reply_markup=input_kb())
        return
    parsed = _dv_parse_input(text)
    if not parsed["email"]:
        await message.answer("❌ Invalid format. Use: <code>email|password</code>", reply_markup=input_kb())
        return
    wait = await message.answer(f"🔄 Processing <code>{html_lib.escape(parsed['email'])}</code>…")
    if not parsed["has_oauth2"]:
        oauth2 = await _dv_oauth2(parsed["email"], parsed["password"])
        if not oauth2:
            await _safe_delete(wait)
            await message.answer(
                f"❌ Failed to get OAuth2 for <code>{html_lib.escape(parsed['email'])}</code>\n\n"
                f"Check credentials or top up your Dongvan balance.\nTry again:",
                reply_markup=input_kb(),
            )
            return
        parsed["refresh_token"] = oauth2["refresh_token"]
        parsed["client_id"]     = oauth2["client_id"]
    uid = message.from_user.id
    _mail_sessions[uid] = {
        "email": parsed["email"], "password": parsed["password"],
        "refresh_token": parsed["refresh_token"], "client_id": parsed["client_id"],
    }
    msgs    = await _dv_process_mailbox(_mail_sessions[uid])
    display = _dv_build_mailbox_display(msgs)
    cid_raw = parsed["client_id"] or ""
    cid_p   = cid_raw[:20] + "…" if len(cid_raw) > 20 else cid_raw
    await _safe_delete(wait)
    await state.set_state(UserFlow.get_code_menu)
    await message.answer(
        _truncate_msg(
            f"✅ <b>Mail Set Successfully!</b>\n{_SEP}\n"
            f"📧 <code>{html_lib.escape(parsed['email'])}</code>\n"
            f"🆔 <code>{html_lib.escape(cid_p)}</code>\n\n{display}"
        ),
        reply_markup=get_code_menu_kb(),
    )


@router_start.message(UserFlow.get_code_filter)
async def gc_filter_selected(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(UserFlow.get_code_menu)
        uid     = message.from_user.id
        session = _mail_sessions.get(uid)
        status  = f"📧 <code>{html_lib.escape(session['email'])}</code>" if session else "❌ No mail set"
        await message.answer(f"🔓 <b>Get Code — Mail Inbox</b>\n{_SEP}\nCurrent mail: {status}", reply_markup=get_code_menu_kb())
        return
    filter_svc = message.text.strip().upper()
    if filter_svc not in _DV_SERVICE_KEYWORDS:
        await message.answer("❌ Select a service from the keyboard.", reply_markup=get_code_filter_kb())
        return
    uid     = message.from_user.id
    session = _mail_sessions.get(uid)
    if not session:
        await state.set_state(UserFlow.get_code_menu)
        await message.answer("❌ Session expired. Please set mail again.", reply_markup=get_code_menu_kb())
        return
    wait     = await message.answer(f"🔍 Filtering <b>{filter_svc}</b> in <code>{html_lib.escape(session['email'])}</code>…")
    messages = await _dv_process_mailbox(session)
    display  = _dv_build_mailbox_display(messages, filter_svc)
    await _safe_delete(wait)
    await message.answer(
        _truncate_msg(f"📧 <code>{html_lib.escape(session['email'])}</code>\n{display}"),
        reply_markup=get_code_filter_kb(),
    )


async def _show_2fa(message: Message) -> None:
    """Shared logic for BTN_GET_2FA button and /get2fa command."""
    uid    = message.from_user.id
    secret = await get_totp_secret(uid)
    if not secret:
        await message.answer(
            f"🔑 <b>2FA Code Generator</b>\n{_SEP}\n"
            f"You haven't set a secret key yet.\n\n"
            f"Press <b>🔑 Set My Key</b> below to add your TOTP secret.",
            reply_markup=tfa_nokey_kb(),
        )
        return
    try:
        code = pyotp.TOTP(secret).now()
    except Exception:
        await message.answer(
            f"⚠️ <b>Invalid Key</b>\n{_SEP}\n"
            f"Your saved key appears invalid. Please reset it.",
            reply_markup=tfa_nokey_kb(),
        )
        return
    await message.answer(_fmt_totp(code), reply_markup=tfa_inline_kb())


@router_start.message(F.text == BTN_GET_2FA)
async def get_2fa_btn(message: Message, state: FSMContext):
    await _show_2fa(message)


@router_start.message(Command("get2fa"))
async def get_2fa_cmd(message: Message, state: FSMContext):
    await _show_2fa(message)


@router_start.message(Command("setkey"))
async def cmd_setkey(message: Message, state: FSMContext):
    await state.set_state(UserFlow.set_totp_key)
    await message.answer(
        f"🔑 <b>Set 2FA Secret Key</b>\n{_SEP}\n"
        f"Enter your <b>Base32 TOTP secret key</b>:\n\n"
        f"<i>Example: JBSWY3DPEHPK3PXP</i>\n\n"
        f"⚠️ Keep this private — the bot only uses it to generate codes for you.",
        reply_markup=input_kb(),
    )


@router_start.message(Command("timer"))
async def cmd_timer(message: Message):
    secs = _totp_secs()
    bar  = _totp_bar(secs)
    await message.answer(
        f"⏱ <b>2FA Timer</b>\n{_SEP}\n"
        f"Current code expires in: <b>{secs} seconds</b>\n"
        f"[{bar}]"
    )


@router_start.message(UserFlow.set_totp_key)
async def receive_totp_key(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await state.clear()
        await send_main_menu(message, state)
        return
    key = message.text.strip().upper().replace(" ", "")
    if not _valid_totp_key(key):
        await message.answer(
            f"❌ <b>Invalid Key</b>\n{_SEP}\n"
            f"That doesn't look like a valid Base32 TOTP secret.\n\n"
            f"Make sure it's the key from your authenticator app (letters A–Z and digits 2–7).\n"
            f"Try again or press ❌ Cancel.",
            reply_markup=input_kb(),
        )
        return
    await set_totp_secret(message.from_user.id, key)
    code = pyotp.TOTP(key).now()
    await state.clear()
    await message.answer(
        f"✅ <b>Key Saved!</b>\n{_SEP}\n"
        f"Your 2FA key has been saved securely.\n\n"
        + _fmt_totp(code),
        reply_markup=tfa_inline_kb(),
    )
    await message.answer("⬇️ Use the buttons below or press 🏠 Home.", reply_markup=main_menu_kb())


# ── 2FA Callback Queries ──────────────────────────────────────────

@router_start.callback_query(F.data == "tfa_refresh")
async def tfa_cb_refresh(call: CallbackQuery):
    uid    = call.from_user.id
    secret = await get_totp_secret(uid)
    if not secret:
        await call.answer("❌ No key set. Press 🔑 Set My Key.", show_alert=True)
        return
    try:
        code = pyotp.TOTP(secret).now()
    except Exception:
        await call.answer("⚠️ Invalid key. Please reset.", show_alert=True)
        return
    try:
        await call.message.edit_text(_fmt_totp(code), reply_markup=tfa_inline_kb())
    except Exception:
        pass
    await call.answer("✅ Refreshed!")


@router_start.callback_query(F.data == "tfa_timer")
async def tfa_cb_timer(call: CallbackQuery):
    secs = _totp_secs()
    bar  = _totp_bar(secs)
    await call.answer(f"⏱ {secs}s remaining\n[{bar}]", show_alert=True)


@router_start.callback_query(F.data == "tfa_setkey")
async def tfa_cb_setkey(call: CallbackQuery, state: FSMContext):
    await state.set_state(UserFlow.set_totp_key)
    await call.message.answer(
        f"🔑 <b>Set 2FA Secret Key</b>\n{_SEP}\n"
        f"Enter your <b>Base32 TOTP secret key</b>:\n\n"
        f"<i>Example: JBSWY3DPEHPK3PXP</i>\n\n"
        f"⚠️ Keep this private — the bot only uses it to generate codes for you.",
        reply_markup=input_kb(),
    )
    await call.answer()


@router_start.message(F.text == BTN_SUPPORT)
async def show_support(message: Message):
    settings = await get_settings()
    support = (settings.get("support_username") or SUPPORT_USERNAME).strip()
    support_url = _channel_to_url(support)
    display = _channel_display_name(support)
    await message.answer(
        f"🆘 <b>Support</b>\n{_SEP}\n"
        f"Need help? Our support team is ready!\n\n"
        f"Click the button below to open a chat with us. 👇",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"🆘 Contact {display}", url=support_url)]
        ]),
    )


@router_start.message(F.text == BTN_HISTORY)
async def order_history(message: Message):
    uid = message.from_user.id
    mail_o, vpn_o, proxy_o = await asyncio.gather(
        get_user_orders(uid), get_user_vpn_orders(uid), get_user_proxy_orders(uid),
    )
    await message.answer(fmt_order_history(mail_o, vpn_o, proxy_o), reply_markup=main_menu_kb())
    deposits = await get_user_deposits(uid)
    if deposits:
        await message.answer(fmt_deposit_history(deposits))


# ══════════════════════════════════════════════════════════════════
# ROUTER — Mail (auto-delivery)
# ══════════════════════════════════════════════════════════════════

router_mail = Router()


@router_mail.message(F.text == BTN_GET_MAIL)
async def mail_start(message: Message, state: FSMContext):
    products = await get_all_products()
    dm = {
        f"{p.get('emoji','📮')} {p['name']}  ·  ${p['price']:.2f}  ·  {p.get('stock_count',0)} left": pid
        for pid, p in products.items()
        if p.get("category", "mail") == "mail" and not p.get("hidden")
    }
    if not dm:
        await message.answer(
            f"📮 <b>Mail Products</b>\n{_SEP}\n❌ No mail products available right now.\nCheck back later!",
            reply_markup=main_menu_kb(),
        )
        return
    await state.update_data(dm=dm)
    await state.set_state(UserFlow.mail_product)
    await message.answer(fmt_product_list_header("📮 Mail Products", len(dm)), reply_markup=products_kb(dm))


@router_mail.message(UserFlow.mail_product)
async def mail_product_selected(message: Message, state: FSMContext):
    if message.text == BACK_BTN:
        await send_main_menu(message, state)
        return
    data = await state.get_data()
    dm   = data.get("dm", {})
    pid  = dm.get(message.text)
    if not pid:
        await message.answer("❌ Please select a product from the keyboard.", reply_markup=products_kb(dm))
        return
    product = await get_product(pid)
    if not product:
        await message.answer("❌ Product not found.")
        return
    stock = await get_stock_count(pid)
    if stock == 0:
        await message.answer(
            f"❌ <b>Out of Stock</b>\n{_SEP}\n"
            f"{product.get('emoji','📦')} {product['name']} is currently out of stock.\nCheck back later!",
            reply_markup=main_menu_kb(),
        )
        await state.clear()
        return
    await state.update_data(pid=pid, product=product, stock=stock)
    await state.set_state(UserFlow.mail_qty)
    await message.answer(fmt_product_detail(product, stock), reply_markup=input_kb())


@router_mail.message(UserFlow.mail_qty)
async def mail_qty_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data = await state.get_data()
        dm = data.get("dm", {})
        await state.set_data({"dm": dm})
        await state.set_state(UserFlow.mail_product)
        await message.answer(
            fmt_product_list_header("📮 Mail Products", len(dm)),
            reply_markup=products_kb(dm),
        )
        return
    data = await state.get_data()
    qty, err = validate_quantity(message.text, data.get("stock", 0))
    if err:
        await message.answer(err)
        return
    pid     = data.get("pid")
    if not pid:
        await send_main_menu(message, state)
        return
    product = await get_product(pid) or data.get("product", {})
    await state.update_data(product=product)
    total   = round(qty * product.get("price", 0), 4)
    user    = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await state.update_data(qty=qty, total=total, coupon_id=None, discount_pct=0)
    await state.set_state(UserFlow.mail_coupon)
    await message.answer(fmt_order_summary(product, qty, total, balance), reply_markup=confirm_kb())


@router_mail.message(UserFlow.mail_coupon)
async def mail_coupon_or_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data = await state.get_data()
        dm = data.get("dm", {})
        pid = data.get("pid")
        product = data.get("product", {})
        stock = data.get("stock", 0)
        await state.set_data({"dm": dm, "pid": pid, "product": product, "stock": stock})
        await state.set_state(UserFlow.mail_qty)
        await message.answer(fmt_product_detail(product, stock), reply_markup=input_kb())
        return
    if message.text == BTN_COUPON:
        await state.set_state(UserFlow.mail_coupon_input)
        await message.answer(
            f"🎟 <b>Apply Coupon</b>\n{_SEP}\nType your coupon code below:",
            reply_markup=input_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer(
            "❌ Please press <b>✅ Confirm Purchase</b> to proceed, or <b>🎟 Apply Coupon</b> to enter a coupon code.",
            reply_markup=confirm_kb(),
        )
        return
    data    = await state.get_data()
    product = data.get("product", {})
    qty     = data.get("qty", 1)
    total   = data.get("total", 0)
    await state.set_state(UserFlow.mail_confirm)
    user    = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await message.answer(
        fmt_order_summary(product, qty, total, balance, data.get("discount_pct", 0)) +
        f"\n\n⚠️ This will deduct <b>${total:.2f}</b> from your balance.",
        reply_markup=confirm_final_kb(),
    )


@router_mail.message(UserFlow.mail_coupon_input)
async def mail_coupon_code_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data    = await state.get_data()
        dm      = data.get("dm", {})
        pid     = data.get("pid")
        product = data.get("product", {})
        stock   = data.get("stock", 0)
        qty     = data.get("qty", 1)
        total   = data.get("total", 0)
        user    = await get_user(message.from_user.id) or {}
        balance = user.get("balance", 0)
        await state.set_data({"dm": dm, "pid": pid, "product": product, "stock": stock,
                               "qty": qty, "total": total, "coupon_id": None, "discount_pct": 0})
        await state.set_state(UserFlow.mail_coupon)
        await message.answer(
            fmt_order_summary(product, qty, total, balance, 0),
            reply_markup=confirm_kb(),
        )
        return
    code   = message.text.strip()
    coupon = await get_coupon(code)
    if not coupon:
        await message.answer(
            f"❌ Invalid coupon code: <code>{code}</code>\n\nTry again or press ❌ Cancel to go back.",
            reply_markup=input_kb(),
        )
        return
    valid, err = validate_coupon(coupon)
    if not valid:
        await message.answer(err + "\n\nTry another code or press ❌ Cancel to go back.", reply_markup=input_kb())
        return
    data    = await state.get_data()
    product = data.get("product", {})
    qty     = data.get("qty", 1)
    disc    = coupon["discount_pct"]
    total   = round(qty * product.get("price", 0) * (1 - disc / 100), 4)
    await state.update_data(coupon_id=coupon["coupon_id"], discount_pct=disc, total=total)
    user    = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await state.set_state(UserFlow.mail_coupon)
    await message.answer(
        f"🎟 <b>Coupon Applied!</b>\n{_SEP}\n"
        f"Code: <code>{code.upper()}</code>\n"
        f"Discount: <b>{disc:.0f}%</b>\n"
        f"New Total: <b>${total:.2f}</b>\n\n"
        f"Press ✅ <b>Confirm Purchase</b> to proceed.",
        reply_markup=confirm_kb(),
    )


@router_mail.message(UserFlow.mail_confirm)
async def mail_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data      = await state.get_data()
        dm        = data.get("dm", {})
        pid       = data.get("pid")
        product   = data.get("product", {})
        stock     = data.get("stock", 0)
        qty       = data.get("qty", 1)
        total     = data.get("total", 0)
        disc      = data.get("discount_pct", 0)
        coupon_id = data.get("coupon_id")
        user      = await get_user(message.from_user.id) or {}
        balance   = user.get("balance", 0)
        await state.set_data({"dm": dm, "pid": pid, "product": product, "stock": stock,
                               "qty": qty, "total": total, "coupon_id": coupon_id, "discount_pct": disc})
        await state.set_state(UserFlow.mail_coupon)
        await message.answer(
            fmt_order_summary(product, qty, total, balance, disc),
            reply_markup=confirm_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer("❌ Press the Confirm Purchase button or Home to cancel.")
        return
    data    = await state.get_data()
    pid     = data.get("pid")
    product = data.get("product")
    qty     = data.get("qty")
    total   = data.get("total")
    if not pid or not product or qty is None or total is None:
        await send_main_menu(message, state)
        return
    uid     = message.from_user.id
    user    = await get_user(uid) or {}
    balance = user.get("balance", 0)

    if balance < total:
        await state.clear()
        await message.answer(
            f"❌ <b>Insufficient Balance</b>\n{_SEP}\n"
            f"💵 Required: <b>${total:.2f}</b>\n"
            f"💰 Your Balance: <b>${balance:.2f}</b>\n"
            f"Shortfall: <b>${total - balance:.2f}</b>\n\nPlease deposit to continue.",
            reply_markup=main_menu_kb(),
        )
        return
    stock = await get_stock_count(pid)
    if stock < qty:
        await state.clear()
        await message.answer(
            f"❌ <b>Not Enough Stock</b>\n{_SEP}\nOnly {stock} left. Please try a smaller quantity.",
            reply_markup=main_menu_kb(),
        )
        return
    items   = await pop_stock_items(pid, qty)
    new_bal = await update_balance(uid, -total)
    oid     = await create_order(uid, pid, product["name"], qty, total, items)
    if data.get("coupon_id"):
        await use_coupon(data["coupon_id"])
    # Append to persistent My_Mail_Shop_Orders.xlsx
    try:
        uname = (await get_user(uid) or {}).get("username", "")
        append_to_mail_shop_file(oid, uid, uname, product["name"], qty, total, items, int(time.time()))
    except Exception as _e:
        logger.warning("Mail shop file append failed: %s", _e)
    await state.clear()
    await message.answer(fmt_order_receipt(oid, product["name"], qty, total, items, new_bal), reply_markup=main_menu_kb())

    # ── Auto-set mail session when exactly 1 item is purchased ────────
    if qty == 1 and items:
        first_item = items[0]
        try:
            parsed = _dv_parse_input(first_item)
            if not parsed["email"] and ":" in first_item:
                p = first_item.split(":", 1)
                parsed["email"]    = p[0].strip()
                parsed["password"] = p[1].strip()

            if parsed["email"] and parsed["password"]:
                mail_email    = parsed["email"]
                mail_password = parsed["password"]

                # Attempt to get OAuth2 token automatically
                await message.answer(
                    f"⏳ <b>Setting up Get Code access…</b>\n"
                    f"📧 <code>{html_lib.escape(mail_email)}</code>"
                )
                oauth2 = None
                if parsed.get("has_oauth2"):
                    oauth2 = {"refresh_token": parsed["refresh_token"], "client_id": parsed["client_id"]}
                else:
                    try:
                        oauth2 = await _dv_oauth2(mail_email, mail_password)
                    except Exception as _oe:
                        logger.warning("Auto OAuth2 failed: %s", _oe)

                if oauth2:
                    _mail_sessions[uid] = {
                        "email": mail_email, "password": mail_password,
                        "refresh_token": oauth2["refresh_token"],
                        "client_id": oauth2["client_id"],
                    }
                    # Pre-load inbox
                    try:
                        msgs    = await _dv_process_mailbox(_mail_sessions[uid])
                        display = _dv_build_mailbox_display(msgs)
                    except Exception:
                        display = ""
                    await message.answer(
                        _truncate_msg(
                            f"✅ <b>Mail Auto-Set in Get Code!</b>\n{_SEP}\n"
                            f"📧 <code>{html_lib.escape(mail_email)}</code>\n"
                            f"🔑 OAuth2: ✅ Ready\n\n"
                            f"Press <b>🔓 Get Code</b> to read codes directly.\n"
                            + (f"\n{display}" if display else "")
                        )
                    )
                else:
                    # Set without OAuth2 — user can complete setup manually
                    _mail_sessions[uid] = {
                        "email": mail_email, "password": mail_password,
                        "refresh_token": "", "client_id": "",
                    }
                    await message.answer(
                        f"✅ <b>Mail Auto-Set!</b>\n{_SEP}\n"
                        f"📧 <code>{html_lib.escape(mail_email)}</code>\n"
                        f"🔑 OAuth2: ⚠️ Not available\n\n"
                        f"Press <b>🔓 Get Code</b> → <b>📧 Set Mail</b> and re-enter the mail to activate full access."
                    )
        except Exception as _ae:
            logger.warning("Auto-set mail session failed: %s", _ae)

    # Send purchased items as xlsx file to the user
    try:
        xlsx_bytes = make_user_order_xlsx(oid, product["name"], qty, total, items)
        date_str   = time.strftime("%Y%m%d_%H%M", time.gmtime())
        filename   = f"order_{oid[:8]}_{date_str}.xlsx"
        await message.answer_document(
            document=BufferedInputFile(xlsx_bytes, filename=filename),
            caption=(
                f"📋 <b>Your Accounts File</b>\n{_SEP}\n"
                f"📦 {product['name']} × {qty}\n"
                f"🆔 Order: <code>{oid[:12]}</code>\n\n"
                f"<i>Open this file to see all your accounts.</i>"
            ),
        )
    except Exception as _xe:
        logger.warning("Failed to send order xlsx to user: %s", _xe)

    # ── Low Stock Auto-Alert ───────────────────────────────────────
    try:
        remaining = await get_stock_count(pid)
        settings  = await get_settings()
        threshold = int(settings.get("low_stock_threshold", 5))
        if 0 < remaining <= threshold:
            for adm in ADMIN_IDS:
                try:
                    await message.bot.send_message(
                        adm,
                        f"⚠️ <b>Low Stock Alert!</b>\n{_SEP}\n"
                        f"📦 Product: <b>{product['name']}</b>\n"
                        f"🔢 Remaining stock: <b>{remaining}</b> item(s)\n"
                        f"Please restock soon!",
                    )
                except Exception:
                    pass
        elif remaining == 0:
            for adm in ADMIN_IDS:
                try:
                    await message.bot.send_message(
                        adm,
                        f"🚨 <b>Out of Stock!</b>\n{_SEP}\n"
                        f"📦 Product: <b>{product['name']}</b>\n"
                        f"Stock is now <b>0</b>. Product hidden from users.",
                    )
                except Exception:
                    pass
    except Exception as _se:
        logger.warning("Low stock alert failed: %s", _se)


# ══════════════════════════════════════════════════════════════════
# ROUTER — VPN
# ══════════════════════════════════════════════════════════════════

router_vpn = Router()


@router_vpn.message(F.text == BTN_BUY_VPN)
async def vpn_start(message: Message, state: FSMContext):
    products = await get_service_products("vpn")
    if not products:
        await message.answer(f"🌐 <b>VPN Products</b>\n{_SEP}\n❌ No VPN products available.", reply_markup=main_menu_kb())
        return
    dm = {f"{p.get('emoji','🌐')} {p['name']}  ·  ${p['price']:.2f}/day": pid for pid, p in products.items()}
    await state.update_data(vpn_dm=dm)
    await state.set_state(UserFlow.vpn_product)
    await message.answer(fmt_product_list_header("🌐 VPN Products", len(dm)), reply_markup=products_kb(dm))


@router_vpn.message(UserFlow.vpn_product)
async def vpn_product_selected(message: Message, state: FSMContext):
    if message.text == BACK_BTN:
        await send_main_menu(message, state)
        return
    data   = await state.get_data()
    vpn_dm = data.get("vpn_dm", {})
    pid    = vpn_dm.get(message.text)
    if not pid:
        await message.answer("❌ Select a product from the keyboard.", reply_markup=products_kb(vpn_dm))
        return
    product = await get_product(pid)
    await state.update_data(vpn_pid=pid, vpn_product=product)
    await state.set_state(UserFlow.vpn_duration)
    await message.answer(
        f"🌐 <b>{product['name']}</b>\n{_SEP}\n"
        f"💵 Price: <b>${product['price']:.2f}</b> per day\n\nSelect duration:",
        reply_markup=duration_kb(),
    )


@router_vpn.message(UserFlow.vpn_duration)
async def vpn_duration_selected(message: Message, state: FSMContext):
    if message.text == BACK_BTN:
        data   = await state.get_data()
        vpn_dm = data.get("vpn_dm", {})
        await state.set_data({"vpn_dm": vpn_dm})
        await state.set_state(UserFlow.vpn_product)
        await message.answer(fmt_product_list_header("🌐 VPN Products", len(vpn_dm)), reply_markup=products_kb(vpn_dm))
        return
    if message.text == BTN_CUSTOM:
        await state.set_state(UserFlow.vpn_custom)
        await message.answer(f"✏️ <b>Custom Duration</b>\n{_SEP}\nEnter number of days (1–365):", reply_markup=input_kb())
        return
    days = DURATION_MAP.get(message.text)
    if not days:
        await message.answer("❌ Select a duration from the keyboard.")
        return
    await _vpn_confirm(message, state, days)


@router_vpn.message(UserFlow.vpn_custom)
async def vpn_custom_days(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data    = await state.get_data()
        vpn_dm  = data.get("vpn_dm", {})
        vpn_pid = data.get("vpn_pid")
        prod    = data.get("vpn_product", {})
        await state.set_data({"vpn_dm": vpn_dm, "vpn_pid": vpn_pid, "vpn_product": prod})
        await state.set_state(UserFlow.vpn_duration)
        await message.answer(f"🌐 <b>{prod.get('name','')}</b>\n{_SEP}\nSelect duration:", reply_markup=duration_kb())
        return
    days, err = validate_custom_days(message.text)
    if err:
        await message.answer(err)
        return
    await _vpn_confirm(message, state, days)


async def _vpn_confirm(message: Message, state: FSMContext, days: int):
    data    = await state.get_data()
    pid     = data.get("vpn_pid")
    if not pid:
        await send_main_menu(message, state)
        return
    product = await get_product(pid) or data.get("vpn_product", {})
    await state.update_data(vpn_product=product)
    price   = round(product["price"] * days, 4)
    await state.update_data(vpn_days=days, vpn_price=price, vpn_coupon_id=None, vpn_discount_pct=0)
    await state.set_state(UserFlow.vpn_coupon)
    user = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await message.answer(
        f"🛒 <b>Order Summary</b>\n{_SEP}\n"
        f"🌐 {product['name']}\n"
        f"⏱ Duration: <b>{days} day(s)</b>\n"
        f"💵 Price/day: <b>${product['price']:.2f}</b>\n"
        f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"👛 Your Balance: <b>${balance:.2f}</b>\n\n"
        f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip.",
        reply_markup=confirm_kb(),
    )


@router_vpn.message(UserFlow.vpn_coupon)
async def vpn_coupon_or_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data    = await state.get_data()
        vpn_dm  = data.get("vpn_dm", {})
        vpn_pid = data.get("vpn_pid")
        prod    = data.get("vpn_product", {})
        await state.set_data({"vpn_dm": vpn_dm, "vpn_pid": vpn_pid, "vpn_product": prod})
        await state.set_state(UserFlow.vpn_duration)
        await message.answer(
            f"🌐 <b>{prod.get('name', 'VPN')}</b>\n{_SEP}\n"
            f"💵 Price/day: <b>${prod.get('price', 0):.2f}</b>\n\nSelect duration:",
            reply_markup=duration_kb(),
        )
        return
    if message.text == BTN_COUPON:
        await state.set_state(UserFlow.vpn_coupon_input)
        await message.answer(
            f"🎟 <b>Apply Coupon</b>\n{_SEP}\nType your coupon code below:",
            reply_markup=input_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer(
            "❌ Please press <b>✅ Confirm Purchase</b> to proceed, or <b>🎟 Apply Coupon</b> to enter a coupon code.",
            reply_markup=confirm_kb(),
        )
        return
    data         = await state.get_data()
    product      = data.get("vpn_product", {})
    days         = data.get("vpn_days", 0)
    price        = data.get("vpn_price", 0)
    if not product or not days:
        await send_main_menu(message, state)
        return
    discount_pct = data.get("vpn_discount_pct", 0)
    user         = await get_user(message.from_user.id) or {}
    balance      = user.get("balance", 0)
    disc_line    = f"🎟 Coupon: <b>-{discount_pct:.0f}%</b>\n" if discount_pct else ""
    await state.set_state(UserFlow.vpn_confirm)
    await message.answer(
        f"🛒 <b>Order Summary</b>\n{_SEP}\n"
        f"🌐 {product['name']}\n"
        f"⏱ Duration: <b>{days} day(s)</b>\n"
        f"💵 Price/day: <b>${product['price']:.2f}</b>\n"
        f"{disc_line}"
        f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"👛 Your Balance: <b>${balance:.2f}</b>\n\n"
        f"⚠️ This will deduct <b>${price:.2f}</b> from your balance.",
        reply_markup=confirm_final_kb(),
    )


@router_vpn.message(UserFlow.vpn_coupon_input)
async def vpn_coupon_code_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data    = await state.get_data()
        vpn_dm  = data.get("vpn_dm", {})
        vpn_pid = data.get("vpn_pid")
        product = data.get("vpn_product", {})
        days    = data.get("vpn_days", 0)
        price   = data.get("vpn_price", 0)
        user    = await get_user(message.from_user.id) or {}
        disc    = 0
        disc_line = ""
        await state.set_data({"vpn_dm": vpn_dm, "vpn_pid": vpn_pid, "vpn_product": product,
                               "vpn_days": days, "vpn_price": price,
                               "vpn_coupon_id": None, "vpn_discount_pct": 0})
        await state.set_state(UserFlow.vpn_coupon)
        await message.answer(
            f"🛒 <b>Order Summary</b>\n{_SEP}\n"
            f"🌐 {product['name']}\n"
            f"⏱ Duration: <b>{days} day(s)</b>\n"
            f"💵 Price/day: <b>${product['price']:.2f}</b>\n"
            f"{disc_line}"
            f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
            f"👛 Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    code   = message.text.strip()
    coupon = await get_coupon(code)
    if not coupon:
        await message.answer(
            f"❌ Invalid coupon code: <code>{code}</code>\n\nTry again or press ❌ Cancel to go back.",
            reply_markup=input_kb(),
        )
        return
    valid, err = validate_coupon(coupon)
    if not valid:
        await message.answer(err + "\n\nTry another code or press ❌ Cancel to go back.", reply_markup=input_kb())
        return
    data    = await state.get_data()
    product = data.get("vpn_product", {})
    days    = data.get("vpn_days", 0)
    disc    = coupon["discount_pct"]
    price   = round(product.get("price", 0) * days * (1 - disc / 100), 4)
    await state.update_data(vpn_coupon_id=coupon["coupon_id"], vpn_discount_pct=disc, vpn_price=price)
    user    = await get_user(message.from_user.id) or {}
    await state.set_state(UserFlow.vpn_coupon)
    await message.answer(
        f"🎟 <b>Coupon Applied!</b>\n{_SEP}\n"
        f"Code: <code>{code.upper()}</code>\n"
        f"Discount: <b>{disc:.0f}%</b>\n"
        f"New Total: <b>${price:.2f}</b>\n\n"
        f"Press ✅ <b>Confirm Purchase</b> to proceed.",
        reply_markup=confirm_kb(),
    )


@router_vpn.message(UserFlow.vpn_confirm)
async def vpn_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data    = await state.get_data()
        product = data.get("vpn_product", {})
        days    = data.get("vpn_days", 0)
        price   = data.get("vpn_price", 0)
        disc    = data.get("vpn_discount_pct", 0)
        disc_line = f"🎟 Coupon: <b>-{disc:.0f}%</b>\n" if disc else ""
        user    = await get_user(message.from_user.id) or {}
        await state.set_state(UserFlow.vpn_coupon)
        await message.answer(
            f"🛒 <b>Order Summary</b>\n{_SEP}\n"
            f"🌐 {product['name']}\n"
            f"⏱ Duration: <b>{days} day(s)</b>\n"
            f"💵 Price/day: <b>${product['price']:.2f}</b>\n"
            f"{disc_line}"
            f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
            f"👛 Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer("❌ Press the Confirm Purchase button or go back.")
        return
    data    = await state.get_data()
    product = data.get("vpn_product")
    days    = data.get("vpn_days")
    price   = data.get("vpn_price")
    vpn_pid = data.get("vpn_pid")
    if not product or days is None or price is None or not vpn_pid:
        await send_main_menu(message, state)
        return
    uid     = message.from_user.id
    user    = await get_user(uid) or {}
    if (user.get("balance") or 0) < price:
        await state.clear()
        await message.answer(
            f"❌ <b>Insufficient Balance</b>\n{_SEP}\nRequired: <b>${price:.2f}</b>  ·  Yours: <b>${user.get('balance',0):.2f}</b>",
            reply_markup=main_menu_kb(),
        )
        return
    await update_balance(uid, -price)
    if data.get("vpn_coupon_id"):
        await use_coupon(data["vpn_coupon_id"])
    oid = await create_vpn_order(uid, user.get("username",""), vpn_pid, product["name"], days, price)
    await state.clear()
    await message.answer(fmt_service_order_placed("🌐", "VPN", oid, product["name"], days, price), reply_markup=main_menu_kb())
    for adm in ADMIN_IDS:
        try:
            await message.bot.send_message(
                adm,
                fmt_admin_vpn_order({"order_id": oid, "user_id": uid, "username": user.get("username",""),
                                     "product_name": product["name"], "duration_days": days,
                                     "price": price, "created_at": int(time.time())}),
                reply_markup=order_review_inline(oid, "vpn"),
            )
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════
# ROUTER — Proxy
# ══════════════════════════════════════════════════════════════════

router_proxy = Router()


@router_proxy.message(F.text == BTN_BUY_PROXY)
async def proxy_start(message: Message, state: FSMContext):
    products = await get_service_products("proxy")
    if not products:
        await message.answer(f"🔐 <b>Proxy Products</b>\n{_SEP}\n❌ No proxy products available.", reply_markup=main_menu_kb())
        return
    dm = {}
    for pid, p in products.items():
        mode = p.get("delivery_mode", "manual")
        if mode == "auto":
            stock = p.get("stock_count", 0)
            label = f"{p.get('emoji','🔐')} {p['name']}  🤖  📦{stock}  ·  ${p['price']:.2f}"
        else:
            label = f"{p.get('emoji','🔐')} {p['name']}  👤  ·  ${p['price']:.2f}/GB"
        dm[label] = pid
    await state.update_data(proxy_dm=dm)
    await state.set_state(UserFlow.proxy_product)
    await message.answer(fmt_product_list_header("🔐 Proxy Products", len(dm)), reply_markup=products_kb(dm))


@router_proxy.message(UserFlow.proxy_product)
async def proxy_product_selected(message: Message, state: FSMContext):
    if message.text == BACK_BTN:
        await send_main_menu(message, state)
        return
    data     = await state.get_data()
    proxy_dm = data.get("proxy_dm", {})
    pid      = proxy_dm.get(message.text)
    if not pid:
        await message.answer("❌ Select a product from the keyboard.", reply_markup=products_kb(proxy_dm))
        return
    product = await get_product(pid)
    await state.update_data(proxy_pid=pid, proxy_product=product)

    if product.get("delivery_mode", "manual") == "auto":
        # ── Auto delivery: ask for quantity like Mail ──────────────
        stock = await get_stock_count(pid)
        if stock == 0:
            await message.answer(
                f"🔐 <b>{product['name']}</b>\n{_SEP}\n❌ Out of stock. Try another product.",
                reply_markup=products_kb(data.get("proxy_dm", {})),
            )
            return
        await state.update_data(proxy_stock=stock)
        await state.set_state(UserFlow.proxy_auto_qty)
        await message.answer(
            f"🔐 <b>{product['name']}</b>\n{_SEP}\n"
            f"💵 Price: <b>${product['price']:.2f}</b> per item\n"
            f"📦 In Stock: <b>{stock}</b>\n\n"
            f"How many do you want? (1–{stock}):",
            reply_markup=input_kb(),
        )
    else:
        # ── Manual delivery: data amount selection ─────────────────
        settings = await get_settings()
        data_opts = settings.get("proxy_data_options", "1 GB,5 GB,10 GB,50 GB")
        await state.update_data(proxy_data_opts=data_opts)
        await state.set_state(UserFlow.proxy_duration)
        await message.answer(
            f"🔐 <b>{product['name']}</b>\n{_SEP}\n"
            f"💵 Price: <b>${product['price']:.2f}</b> per GB\n\nSelect data amount:",
            reply_markup=proxy_data_kb(data_opts),
        )


# ── AUTO PROXY — qty & confirm ──────────────────────────────────────

@router_proxy.message(UserFlow.proxy_auto_qty)
async def proxy_auto_qty_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data     = await state.get_data()
        proxy_dm = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts})
        await state.set_state(UserFlow.proxy_product)
        await message.answer(fmt_product_list_header("🔐 Proxy Products", len(proxy_dm)), reply_markup=products_kb(proxy_dm))
        return
    data  = await state.get_data()
    stock = data.get("proxy_stock", 0)
    qty, err = validate_quantity(message.text, stock)
    if err:
        await message.answer(err)
        return
    pid     = data.get("proxy_pid")
    if not pid:
        await send_main_menu(message, state)
        return
    product = await get_product(pid) or data.get("proxy_product", {})
    await state.update_data(proxy_product=product)
    total   = round(qty * product.get("price", 0), 4)
    user    = await get_user(message.from_user.id) or {}
    await state.update_data(proxy_qty=qty, proxy_price=total, proxy_auto_coupon_id=None, proxy_auto_discount_pct=0)
    await state.set_state(UserFlow.proxy_auto_coupon)
    await message.answer(
        f"🛒 <b>Order Summary</b>\n{_SEP}\n"
        f"🔐 {product['name']}\n"
        f"🔢 Quantity: <b>{qty}</b>\n"
        f"💵 Price: <b>${product['price']:.2f}</b> × {qty}\n"
        f"💰 Total: <b>${total:.2f}</b>\n{_LINE}\n"
        f"👛 Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
        f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip.",
        reply_markup=confirm_kb(),
    )


@router_proxy.message(UserFlow.proxy_auto_coupon)
async def proxy_auto_coupon_or_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN, HOME_BTN):
        data     = await state.get_data()
        proxy_dm = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid = data.get("proxy_pid")
        prod     = data.get("proxy_product", {})
        stock    = data.get("proxy_stock", 0)
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": prod, "proxy_stock": stock})
        await state.set_state(UserFlow.proxy_auto_qty)
        await message.answer(
            fmt_product_detail(prod, stock) if prod else fmt_product_list_header("🔐 Proxy Products", len(proxy_dm)),
            reply_markup=input_kb() if prod else products_kb(proxy_dm),
        )
        return
    if message.text == BTN_COUPON:
        await state.set_state(UserFlow.proxy_auto_coupon_input)
        await message.answer(
            f"🎟 <b>Apply Coupon</b>\n{_SEP}\nType your coupon code below:",
            reply_markup=input_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer(
            "❌ Please press <b>✅ Confirm Purchase</b> to proceed, or <b>🎟 Apply Coupon</b> to enter a coupon code.",
            reply_markup=confirm_kb(),
        )
        return
    data         = await state.get_data()
    product      = data.get("proxy_product", {})
    qty          = data.get("proxy_qty", 1)
    total        = data.get("proxy_price", 0)
    discount_pct = data.get("proxy_auto_discount_pct", 0)
    user         = await get_user(message.from_user.id) or {}
    disc_line    = f"🎟 Coupon: <b>-{discount_pct:.0f}%</b>\n" if discount_pct else ""
    await state.set_state(UserFlow.proxy_auto_confirm)
    await message.answer(
        f"🛒 <b>Order Summary</b>\n{_SEP}\n"
        f"🔐 {product['name']}\n"
        f"🔢 Quantity: <b>{qty}</b>\n"
        f"💵 Price: <b>${product['price']:.2f}</b> × {qty}\n"
        f"{disc_line}"
        f"💰 Total: <b>${total:.2f}</b>\n{_LINE}\n"
        f"👛 Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
        f"⚠️ This will deduct <b>${total:.2f}</b> from your balance.",
        reply_markup=confirm_final_kb(),
    )


@router_proxy.message(UserFlow.proxy_auto_coupon_input)
async def proxy_auto_coupon_code_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data    = await state.get_data()
        proxy_dm = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid = data.get("proxy_pid")
        product = data.get("proxy_product", {})
        stock   = data.get("proxy_stock", 0)
        qty     = data.get("proxy_qty", 1)
        total   = data.get("proxy_price", 0)
        user    = await get_user(message.from_user.id) or {}
        disc    = 0
        disc_line = ""
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": product, "proxy_stock": stock,
                               "proxy_qty": qty, "proxy_price": total,
                               "proxy_auto_coupon_id": None, "proxy_auto_discount_pct": 0})
        await state.set_state(UserFlow.proxy_auto_coupon)
        await message.answer(
            f"🛒 <b>Order Summary</b>\n{_SEP}\n"
            f"🔐 {product['name']}\n"
            f"🔢 Quantity: <b>{qty}</b>\n"
            f"💵 Price: <b>${product['price']:.2f}</b> × {qty}\n"
            f"{disc_line}"
            f"💰 Total: <b>${total:.2f}</b>\n{_LINE}\n"
            f"👛 Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    code   = message.text.strip()
    coupon = await get_coupon(code)
    if not coupon:
        await message.answer(
            f"❌ Invalid coupon code: <code>{code}</code>\n\nTry again or press ❌ Cancel to go back.",
            reply_markup=input_kb(),
        )
        return
    valid, err = validate_coupon(coupon)
    if not valid:
        await message.answer(err + "\n\nTry another code or press ❌ Cancel to go back.", reply_markup=input_kb())
        return
    data    = await state.get_data()
    product = data.get("proxy_product", {})
    qty     = data.get("proxy_qty", 1)
    disc    = coupon["discount_pct"]
    total   = round(qty * product.get("price", 0) * (1 - disc / 100), 4)
    await state.update_data(proxy_auto_coupon_id=coupon["coupon_id"], proxy_auto_discount_pct=disc, proxy_price=total)
    user    = await get_user(message.from_user.id) or {}
    await state.set_state(UserFlow.proxy_auto_coupon)
    await message.answer(
        f"🎟 <b>Coupon Applied!</b>\n{_SEP}\n"
        f"Code: <code>{code.upper()}</code>\n"
        f"Discount: <b>{disc:.0f}%</b>\n"
        f"New Total: <b>${total:.2f}</b>\n\n"
        f"Press ✅ <b>Confirm Purchase</b> to proceed.",
        reply_markup=confirm_kb(),
    )


@router_proxy.message(UserFlow.proxy_auto_confirm)
async def proxy_auto_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN, HOME_BTN):
        data     = await state.get_data()
        proxy_dm = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid = data.get("proxy_pid")
        product  = data.get("proxy_product", {})
        stock    = data.get("proxy_stock", 0)
        qty      = data.get("proxy_qty", 1)
        total    = data.get("proxy_price", 0)
        disc     = data.get("proxy_auto_discount_pct", 0)
        disc_line = f"🎟 Coupon: <b>-{disc:.0f}%</b>\n" if disc else ""
        user     = await get_user(message.from_user.id) or {}
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": product, "proxy_stock": stock,
                               "proxy_qty": qty, "proxy_price": total,
                               "proxy_auto_coupon_id": data.get("proxy_auto_coupon_id"),
                               "proxy_auto_discount_pct": disc})
        await state.set_state(UserFlow.proxy_auto_coupon)
        await message.answer(
            f"🛒 <b>Order Summary</b>\n{_SEP}\n"
            f"🔐 {product.get('name', '')}\n"
            f"🔢 Quantity: <b>{qty}</b>\n"
            f"💵 Price: <b>${product.get('price', 0):.2f}</b> × {qty}\n"
            f"{disc_line}"
            f"💰 Total: <b>${total:.2f}</b>\n{_LINE}\n"
            f"👛 Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer("❌ Press the Confirm Purchase button or go back.", reply_markup=confirm_final_kb())
        return
    data    = await state.get_data()
    pid     = data.get("proxy_pid")
    product = data.get("proxy_product", {})
    qty     = data.get("proxy_qty", 1)
    total   = data.get("proxy_price", 0)
    if not pid or not product:
        await send_main_menu(message, state)
        return
    uid     = message.from_user.id
    user    = await get_user(uid) or {}
    balance = user.get("balance", 0)

    if balance < total:
        await state.clear()
        await message.answer(
            f"❌ <b>Insufficient Balance</b>\n{_SEP}\n"
            f"💵 Required: <b>${total:.2f}</b>\n"
            f"💰 Your Balance: <b>${balance:.2f}</b>\n"
            f"Shortfall: <b>${total - balance:.2f}</b>\n\nPlease deposit to continue.",
            reply_markup=main_menu_kb(),
        )
        return
    stock = await get_stock_count(pid)
    if stock < qty:
        await state.clear()
        await message.answer(
            f"❌ <b>Not Enough Stock</b>\n{_SEP}\nOnly {stock} left. Please try a smaller quantity.",
            reply_markup=main_menu_kb(),
        )
        return

    items   = await pop_stock_items(pid, qty)
    new_bal = await update_balance(uid, -total)
    if data.get("proxy_auto_coupon_id"):
        await use_coupon(data["proxy_auto_coupon_id"])
    oid     = await create_proxy_order(uid, user.get("username", ""), pid, product["name"], "Auto", total, items=items)
    await state.clear()

    preview = "\n".join(items[:5])
    more    = f"\n<i>... and {len(items) - 5} more</i>" if len(items) > 5 else ""
    await message.answer(
        f"✅ <b>Proxy Order Delivered!</b>\n{_SEP}\n"
        f"🆔 Order: <code>{oid[:12]}</code>\n"
        f"🔐 {product['name']} × {qty}\n"
        f"💵 Paid: <b>${total:.2f}</b>\n"
        f"👛 Balance left: <b>${new_bal:.2f}</b>\n{_SEP}\n"
        f"📋 <b>Your Proxies:</b>\n<code>{preview}{more}</code>",
        reply_markup=main_menu_kb(),
    )

    # Low stock alert
    try:
        remaining = await get_stock_count(pid)
        settings  = await get_settings()
        threshold = int(settings.get("low_stock_threshold", 5))
        if 0 < remaining <= threshold:
            for adm in ADMIN_IDS:
                try:
                    await message.bot.send_message(
                        adm,
                        f"⚠️ <b>Low Stock Alert!</b>\n{_SEP}\n"
                        f"🔐 {product['name']}\n📦 Only <b>{remaining}</b> proxy item(s) left!",
                    )
                except Exception:
                    pass
    except Exception:
        pass


# ── MANUAL PROXY — duration & confirm ──────────────────────────────

@router_proxy.message(UserFlow.proxy_duration)
async def proxy_duration_selected(message: Message, state: FSMContext):
    if message.text == BACK_BTN:
        data            = await state.get_data()
        proxy_dm        = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts})
        await state.set_state(UserFlow.proxy_product)
        await message.answer(fmt_product_list_header("🔐 Proxy Products", len(proxy_dm)), reply_markup=products_kb(proxy_dm))
        return
    if message.text == BTN_PROXY_DATA_CUSTOM:
        await state.set_state(UserFlow.proxy_custom)
        await message.answer(f"📡 <b>Custom Data Amount</b>\n{_SEP}\nEnter data amount (e.g. 3 GB, 500 MB):", reply_markup=input_kb())
        return
    data = await state.get_data()
    data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
    all_opts_bold = [_b(o) for o in parse_proxy_data_options(data_opts)]
    if message.text not in all_opts_bold:
        await message.answer("❌ Select a data option from the keyboard.")
        return
    raw_label = parse_proxy_data_options(data_opts)[all_opts_bold.index(message.text)]
    await _proxy_confirm(message, state, raw_label)


@router_proxy.message(UserFlow.proxy_custom)
async def proxy_custom_days(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data            = await state.get_data()
        proxy_dm        = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid       = data.get("proxy_pid")
        prod            = data.get("proxy_product", {})
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": prod})
        await state.set_state(UserFlow.proxy_duration)
        await message.answer(f"🔐 <b>{prod.get('name','')}</b>\n{_SEP}\nSelect data amount:", reply_markup=proxy_data_kb(proxy_data_opts))
        return
    amount, err = parse_data_amount(message.text)
    if err:
        await message.answer(err)
        return
    raw = message.text.strip()
    unit = "MB" if "MB" in raw.upper() else "GB"
    label = f"{amount:.0f} {unit}" if amount == int(amount) else f"{amount} {unit}"
    await _proxy_confirm(message, state, label)


async def _proxy_confirm(message: Message, state: FSMContext, data_label: str):
    data    = await state.get_data()
    pid     = data.get("proxy_pid")
    if not pid:
        await send_main_menu(message, state)
        return
    product = await get_product(pid) or data.get("proxy_product", {})
    await state.update_data(proxy_product=product)
    amount, _ = parse_data_amount(data_label)
    amount = amount or 1.0
    price   = round(product.get("price", 0) * amount, 4)
    await state.update_data(proxy_days=data_label, proxy_price=price, proxy_coupon_id=None, proxy_discount_pct=0)
    await state.set_state(UserFlow.proxy_coupon)
    user = await get_user(message.from_user.id) or {}
    balance = user.get("balance", 0)
    await message.answer(
        f"🛒 <b>Order Summary</b>\n{_SEP}\n"
        f"🔐 {product['name']}\n"
        f"📡 Data: <b>{data_label}</b>\n"
        f"💵 Price/GB: <b>${product['price']:.2f}</b>\n"
        f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"👛 Your Balance: <b>${balance:.2f}</b>\n\n"
        f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip.",
        reply_markup=confirm_kb(),
    )


@router_proxy.message(UserFlow.proxy_coupon)
async def proxy_coupon_or_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data            = await state.get_data()
        proxy_dm        = data.get("proxy_dm", {})
        proxy_data_opts = data.get("proxy_data_opts", "1 GB,5 GB,10 GB,50 GB")
        proxy_pid       = data.get("proxy_pid")
        prod            = data.get("proxy_product", {})
        await state.set_data({"proxy_dm": proxy_dm, "proxy_data_opts": proxy_data_opts,
                               "proxy_pid": proxy_pid, "proxy_product": prod})
        await state.set_state(UserFlow.proxy_duration)
        await message.answer(
            f"🔐 <b>{prod.get('name', 'Proxy')}</b>\n{_SEP}\n"
            f"💵 Price/GB: <b>${prod.get('price', 0):.2f}</b>\n\nSelect data amount:",
            reply_markup=proxy_data_kb(proxy_data_opts),
        )
        return
    if message.text == BTN_COUPON:
        await state.set_state(UserFlow.proxy_coupon_input)
        await message.answer(
            f"🎟 <b>Apply Coupon</b>\n{_SEP}\nType your coupon code below:",
            reply_markup=input_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer(
            "❌ Please press <b>✅ Confirm Purchase</b> to proceed, or <b>🎟 Apply Coupon</b> to enter a coupon code.",
            reply_markup=confirm_kb(),
        )
        return
    data         = await state.get_data()
    product      = data.get("proxy_product", {})
    days         = data.get("proxy_days", "")
    price        = data.get("proxy_price", 0)
    if not product or not days:
        await send_main_menu(message, state)
        return
    discount_pct = data.get("proxy_discount_pct", 0)
    user         = await get_user(message.from_user.id) or {}
    balance      = user.get("balance", 0)
    disc_line    = f"🎟 Coupon: <b>-{discount_pct:.0f}%</b>\n" if discount_pct else ""
    await state.set_state(UserFlow.proxy_confirm)
    await message.answer(
        f"🛒 <b>Order Summary</b>\n{_SEP}\n"
        f"🔐 {product['name']}\n"
        f"📡 Data: <b>{days}</b>\n"
        f"💵 Price/GB: <b>${product['price']:.2f}</b>\n"
        f"{disc_line}"
        f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
        f"👛 Your Balance: <b>${balance:.2f}</b>\n\n"
        f"⚠️ This will deduct <b>${price:.2f}</b> from your balance.",
        reply_markup=confirm_final_kb(),
    )


@router_proxy.message(UserFlow.proxy_coupon_input)
async def proxy_coupon_code_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data    = await state.get_data()
        product = data.get("proxy_product", {})
        days    = data.get("proxy_days", "")
        price   = data.get("proxy_price", 0)
        user    = await get_user(message.from_user.id) or {}
        disc    = data.get("proxy_discount_pct", 0)
        disc_line = f"🎟 Coupon: <b>-{disc:.0f}%</b>\n" if disc else ""
        await state.set_state(UserFlow.proxy_coupon)
        await message.answer(
            f"🛒 <b>Order Summary</b>\n{_SEP}\n"
            f"🔐 {product['name']}\n"
            f"📡 Data: <b>{days}</b>\n"
            f"💵 Price/GB: <b>${product['price']:.2f}</b>\n"
            f"{disc_line}"
            f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
            f"👛 Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    code   = message.text.strip()
    coupon = await get_coupon(code)
    if not coupon:
        await message.answer(
            f"❌ Invalid coupon code: <code>{code}</code>\n\nTry again or press ❌ Cancel to go back.",
            reply_markup=input_kb(),
        )
        return
    valid, err = validate_coupon(coupon)
    if not valid:
        await message.answer(err + "\n\nTry another code or press ❌ Cancel to go back.", reply_markup=input_kb())
        return
    data    = await state.get_data()
    product = data.get("proxy_product", {})
    days    = data.get("proxy_days", "")
    disc    = coupon["discount_pct"]
    amt, _  = parse_data_amount(days)
    amt     = amt or 1.0
    price   = round(product.get("price", 0) * amt * (1 - disc / 100), 4)
    await state.update_data(proxy_coupon_id=coupon["coupon_id"], proxy_discount_pct=disc, proxy_price=price)
    user    = await get_user(message.from_user.id) or {}
    await state.set_state(UserFlow.proxy_coupon)
    await message.answer(
        f"🎟 <b>Coupon Applied!</b>\n{_SEP}\n"
        f"Code: <code>{code.upper()}</code>\n"
        f"Discount: <b>{disc:.0f}%</b>\n"
        f"New Total: <b>${price:.2f}</b>\n\n"
        f"Press ✅ <b>Confirm Purchase</b> to proceed.",
        reply_markup=confirm_kb(),
    )


@router_proxy.message(UserFlow.proxy_confirm)
async def proxy_confirm(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, CANCEL_BTN):
        data    = await state.get_data()
        product = data.get("proxy_product", {})
        days    = data.get("proxy_days", "")
        price   = data.get("proxy_price", 0)
        disc    = data.get("proxy_discount_pct", 0)
        disc_line = f"🎟 Coupon: <b>-{disc:.0f}%</b>\n" if disc else ""
        user    = await get_user(message.from_user.id) or {}
        await state.set_state(UserFlow.proxy_coupon)
        await message.answer(
            f"🛒 <b>Order Summary</b>\n{_SEP}\n"
            f"🔐 {product['name']}\n"
            f"📡 Data: <b>{days}</b>\n"
            f"💵 Price/GB: <b>${product['price']:.2f}</b>\n"
            f"{disc_line}"
            f"💰 Total: <b>${price:.2f}</b>\n{_LINE}\n"
            f"👛 Your Balance: <b>${user.get('balance', 0):.2f}</b>\n\n"
            f"Have a coupon code? Enter it below,\nor press ✅ Confirm Purchase to skip.",
            reply_markup=confirm_kb(),
        )
        return
    if message.text != BTN_CONFIRM:
        await message.answer("❌ Press the Confirm Purchase button or go back.", reply_markup=confirm_final_kb())
        return
    data    = await state.get_data()
    product = data.get("proxy_product", {})
    days    = data.get("proxy_days", "")
    price   = data.get("proxy_price", 0)
    if not product or not days:
        await send_main_menu(message, state)
        return
    uid     = message.from_user.id
    user    = await get_user(uid) or {}
    if (user.get("balance") or 0) < price:
        await state.clear()
        await message.answer(
            f"❌ <b>Insufficient Balance</b>\n{_SEP}\nRequired: <b>${price:.2f}</b>  ·  Yours: <b>${user.get('balance',0):.2f}</b>",
            reply_markup=main_menu_kb(),
        )
        return
    await update_balance(uid, -price)
    if data.get("proxy_coupon_id"):
        await use_coupon(data.get("proxy_coupon_id"))
    oid = await create_proxy_order(uid, user.get("username",""), data.get("proxy_pid",""), product.get("name",""), days, price)
    await state.clear()
    await message.answer(
        f"🔐 <b>Proxy Order Placed!</b>\n{_SEP}\n"
        f"🆔 Order: <code>{oid[:12]}</code>\n"
        f"📦 {product['name']}\n"
        f"📡 Data: <b>{days}</b>\n"
        f"💵 Paid: <b>${price:.2f}</b>\n{_SEP}\n"
        f"⏳ Status: <b>Pending</b>\n"
        f"Our team will deliver your order shortly.\n"
        f"You'll receive a notification when ready. 🔔",
        reply_markup=main_menu_kb()
    )
    for adm in ADMIN_IDS:
        try:
            await message.bot.send_message(
                adm,
                f"🔐 <b>New Proxy Order</b>\n{_SEP}\n"
                f"🆔 <code>{oid}</code>\n"
                f"👤 {uid}  @{user.get('username','')}\n"
                f"📦 {product['name']}\n"
                f"📡 Data: <b>{days}</b>\n"
                f"💵 ${price:.2f}\n"
                f"🕐 {_dt(int(time.time()))}",
                reply_markup=order_review_inline(oid, "proxy"),
            )
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════
# ROUTER — Deposit
# ══════════════════════════════════════════════════════════════════

router_deposit = Router()


@router_deposit.message(F.text == BTN_DEPOSIT)
async def deposit_start(message: Message, state: FSMContext):
    await state.set_state(UserFlow.dep_method)
    user = await get_user(message.from_user.id) or {}
    await message.answer(
        f"💵 <b>Add Funds</b>\n{_SEP}\n"
        f"💰 Current Balance: <b>${user.get('balance',0):.2f}</b>\n\nChoose your payment method:",
        reply_markup=deposit_method_kb(),
    )


@router_deposit.message(UserFlow.dep_method)
async def deposit_method_chosen(message: Message, state: FSMContext):
    if message.text == BACK_BTN:
        await send_main_menu(message, state)
        return
    method_key = DEPOSIT_MAP.get(message.text)
    if not method_key:
        await message.answer("❌ Select a payment method from the keyboard.")
        return
    settings = await get_settings()
    if method_key == "bkash":
        number  = settings.get("bkash_number", "")
        min_amt = settings.get("bkash_min", 100)
        label   = "bKash"
    elif method_key == "nagad":
        number  = settings.get("nagad_number", "")
        min_amt = settings.get("nagad_min", 150)
        label   = "Nagad"
    else:
        number  = settings.get("binance_uid", "")
        min_amt = settings.get("binance_min", 5)
        label   = "Binance"
    rate   = settings.get("usd_rate", 125)
    is_usd = (method_key == "binance")
    await state.update_data(method_key=method_key, method_label=label, min_amt=min_amt, rate=rate, is_usd=is_usd)
    await state.set_state(UserFlow.dep_amount)
    await message.answer(fmt_deposit_info(label, number, rate, min_amt, is_usd), reply_markup=input_kb())


@router_deposit.message(UserFlow.dep_amount)
async def deposit_amount_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        await state.set_state(UserFlow.dep_method)
        await message.answer("💵 Select payment method:", reply_markup=deposit_method_kb())
        return
    data   = await state.get_data()
    is_usd = data.get("is_usd", False)
    if is_usd:
        amount_usd, err = validate_price(message.text)
        if err:
            await message.answer(err)
            return
        if amount_usd <= 0:
            await message.answer("❌ Amount must be positive.")
            return
        if amount_usd < data.get("min_amt", 0):
            await message.answer(f"❌ Minimum Binance deposit is <b>${data.get('min_amt', 0):.2f} USD</b>")
            return
        rate       = data.get("rate") or 125
        amount_bdt = round(amount_usd * rate, 2)
    else:
        amount_bdt, err = validate_amount_bdt(message.text, data.get("min_amt", 0))
        if err:
            await message.answer(err)
            return
        rate = data.get("rate") or 0
        if rate <= 0:
            await message.answer("❌ Exchange rate is not configured. Contact admin.")
            return
        amount_usd = round(amount_bdt / rate, 4)
    await state.update_data(amount_bdt=amount_bdt, amount_usd=amount_usd)
    await state.set_state(UserFlow.dep_trx)
    await message.answer(fmt_deposit_confirm(data.get("method_label", ""), amount_bdt, amount_usd, is_usd), reply_markup=input_kb())


@router_deposit.message(UserFlow.dep_trx)
async def deposit_trx_entered(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data = await state.get_data()
        await state.set_state(UserFlow.dep_amount)
        await message.answer(fmt_deposit_info(data.get("method_label", ""), "", data.get("rate", 0), data.get("min_amt", 0), data.get("is_usd", False)), reply_markup=input_kb())
        return
    trx = message.text.strip()
    if await check_trx_duplicate(trx):
        await message.answer(
            f"❌ <b>Duplicate Transaction</b>\n{_SEP}\n"
            f"This TRX ID has already been submitted.\nContact support if this is an error."
        )
        return
    await state.update_data(trx_id=trx)
    await state.set_state(UserFlow.dep_screenshot)
    await message.answer(
        f"📸 <b>Upload Screenshot</b>\n{_SEP}\n"
        f"Please send a clear screenshot of your payment.\n\n<i>This helps our team verify faster. ⚡</i>",
        reply_markup=input_kb(),
    )


@router_deposit.message(UserFlow.dep_screenshot)
async def deposit_screenshot(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN):
        data = await state.get_data()
        await state.set_state(UserFlow.dep_trx)
        await message.answer(
            f"📝 <b>Transaction ID</b>\n{_SEP}\nPlease enter your TRX ID / Transaction reference:",
            reply_markup=input_kb(),
        )
        return
    if not message.photo:
        await message.answer("❌ Please send a photo/screenshot of your payment.")
        return
    data      = await state.get_data()
    uid       = message.from_user.id
    user      = await get_user(uid) or {}
    photo     = message.photo[-1]
    file_id   = photo.file_id          # always use Telegram file_id — no Firebase needed

    # Try Firebase upload for a permanent URL (optional, non-blocking)
    screenshot_url = ""
    try:
        file       = await message.bot.get_file(photo.file_id)
        file_bytes = (await message.bot.download_file(file.file_path)).read()
        screenshot_url = await upload_screenshot(file_bytes, f"{uid}_{int(time.time())}.jpg")
    except Exception as e:
        logger.warning("Screenshot Firebase upload skipped: %s", e)

    method_label = data.get("method_label", "")
    amount_bdt   = data.get("amount_bdt", 0)
    amount_usd   = data.get("amount_usd", 0)
    trx_id       = data.get("trx_id", "")
    dep_id = await create_deposit(
        uid, user.get("username", ""), method_label,
        amount_bdt, amount_usd, trx_id, screenshot_url,
    )
    await state.clear()
    await message.answer(
        fmt_deposit_submitted(dep_id, method_label, amount_bdt, amount_usd, data.get("is_usd", False)),
        reply_markup=main_menu_kb(),
    )
    for adm in ADMIN_IDS:
        try:
            dep = {
                "deposit_id": dep_id, "user_id": uid, "username": user.get("username", ""),
                "method": method_label, "amount_bdt": amount_bdt,
                "amount_usd": amount_usd, "trx_id": trx_id,
                "screenshot_url": screenshot_url, "created_at": int(time.time()),
            }
            text      = fmt_admin_deposit_review(dep)
            kb_inline = deposit_review_inline(dep_id)
            # Always send the photo using Telegram file_id — reliable even if Firebase failed
            await message.bot.send_photo(adm, photo=file_id, caption=text, reply_markup=kb_inline)
        except Exception as ex:
            logger.warning("Admin deposit notify error (uid=%s): %s", adm, ex)
            try:
                await message.bot.send_message(adm, text, reply_markup=kb_inline)
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════════
# ROUTER — Temp Mail
# ══════════════════════════════════════════════════════════════════

router_tempmail = Router()

_TM_GEN  = _b("📧 Generate Email")
_TM_INB  = _b("📬 Check Inbox")
_TM_REF  = _b("🔄 Refresh")
_TM_MY   = _b("📋 My Email")
_TM_DEL  = _b("🗑 Delete Email")
_TM_DOM  = _b("🌐 Change Domain")
_TM_RND  = _b("🎲 Random Domain")
_TM_BTNS = {_TM_GEN, _TM_INB, _TM_REF, _TM_MY, _TM_DEL, _TM_DOM, _TM_RND}


@router_tempmail.message(F.text == BTN_TEMP_MAIL)
async def tempmail_entry(message: Message, state: FSMContext):
    uid = message.from_user.id
    await state.set_state(UserFlow.temp_mail_menu)
    sess = _tempmail_sessions.get(uid)
    if sess:
        email = sess.get("email", "")
        txt = (
            f"📧 <b>Temp Mail</b>\n{_SEP}\n"
            f"✅ Active email:\n<code>{html_lib.escape(email)}</code>\n\n"
            f"Choose an action:"
        )
    else:
        txt = (
            f"📧 <b>Temp Mail</b>\n{_SEP}\n"
            f"Get a free disposable email address instantly.\n\n"
            f"Press <b>📧 Generate Email</b> to create one."
        )
    await message.answer(txt, reply_markup=_tm_menu_kb())


@router_tempmail.message(UserFlow.temp_mail_menu, F.text.in_({BACK_BTN, HOME_BTN}))
async def tempmail_back(message: Message, state: FSMContext):
    await send_main_menu(message, state)


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_GEN)
async def tempmail_generate(message: Message, state: FSMContext):
    uid = message.from_user.id
    # use domain saved in session, or default
    chosen_domain = (_tempmail_sessions.get(uid) or {}).get("chosen_domain", _TEMPMAIL_DOMAIN)
    await message.answer(f"⏳ Generating email on <b>@{chosen_domain}</b>…")
    email, token = await _tm_create_email(chosen_domain)
    if not email:
        await message.answer("❌ Failed to generate email. Please try again.", reply_markup=_tm_menu_kb())
        return
    _tempmail_sessions[uid] = {
        "email": email, "token": token,
        "chosen_domain": chosen_domain,
        "seen_ids": set(), "messages": {}, "msg_index": 0,
    }
    ts = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    await message.answer(
        f"✅ <b>Email Generated!</b>\n{_SEP}\n"
        f"📧 <code>{html_lib.escape(email)}</code>\n\n"
        f"<i>Tap the address above to copy it</i>\n"
        f"🕐 Created: {ts}",
        reply_markup=_tm_menu_kb(),
    )


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_MY)
async def tempmail_myemail(message: Message, state: FSMContext):
    uid  = message.from_user.id
    sess = _tempmail_sessions.get(uid)
    if not sess:
        await message.answer("❌ No active email. Press <b>📧 Generate Email</b> first.", reply_markup=_tm_menu_kb())
        return
    await message.answer(
        f"📋 <b>Your current email:</b>\n{_SEP}\n"
        f"<code>{html_lib.escape(sess['email'])}</code>\n\n"
        f"<i>Tap to copy</i>",
        reply_markup=_tm_menu_kb(),
    )


@router_tempmail.message(UserFlow.temp_mail_menu, F.text.in_({_TM_INB, _TM_REF}))
async def tempmail_inbox(message: Message, state: FSMContext):
    uid     = message.from_user.id
    refresh = message.text == _TM_REF
    sess    = _tempmail_sessions.get(uid)
    if not sess:
        await message.answer("❌ No email found. Generate one first.", reply_markup=_tm_menu_kb())
        return

    email = sess["email"]
    await message.answer(f"🔍 Checking inbox for <code>{html_lib.escape(email)}</code>…")
    messages = await _tm_get_inbox(email)

    if not messages:
        await message.answer("📭 <b>Inbox is empty.</b>\n\n<i>Emails may take a moment to arrive.</i>", reply_markup=_tm_menu_kb())
        return

    seen     = sess.get("seen_ids", set())
    new_msgs = [m for m in messages if str(m.get("id", "")) not in seen]

    if refresh and not new_msgs:
        await message.answer(
            f"🔄 No new messages. Total: <b>{len(messages)}</b> email(s).",
            reply_markup=_tm_menu_kb(),
        )
        return

    show_msgs = new_msgs if new_msgs else messages

    stored   = sess.get("messages", {})
    mi       = sess.get("msg_index", 0)
    id_map: Dict[str, str] = {}

    for msg in messages:
        full_id  = str(msg.get("id", ""))
        existing = next((k for k, v in stored.items() if str(v.get("id", "")) == full_id), None)
        if existing:
            id_map[full_id] = existing
        else:
            short_id = f"m{mi}"
            mi += 1
            stored[short_id] = msg
            id_map[full_id]  = short_id

    _tempmail_sessions[uid]["messages"]  = stored
    _tempmail_sessions[uid]["msg_index"] = mi

    for i, msg in enumerate(show_msgs[:10]):
        full_id     = str(msg.get("id", ""))
        short_id    = id_map.get(full_id, f"m{i}")
        sender      = html_lib.escape(str(msg.get("from", "Unknown"))[:60])
        subject     = html_lib.escape(str(msg.get("subject", "(No Subject)"))[:80])
        received    = str(msg.get("created_at", ""))[:19]
        raw_preview = (msg.get("body_text") or "")[:100].replace("\n", " ")
        preview     = html_lib.escape(raw_preview)

        card = (
            f"📩 <b>Mail #{i+1}</b>\n"
            f"👤 <b>From:</b> {sender}\n"
            f"📌 <b>Subject:</b> {subject}\n"
        )
        if received:
            card += f"🕐 {received}\n"
        if preview:
            card += f"\n<i>{preview}…</i>"

        inline_kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📖 Read Full Email", callback_data=f"tm_read:{uid}:{short_id}")
        ]])
        await message.answer(card, reply_markup=inline_kb)
        seen.add(full_id)
        await asyncio.sleep(0.3)

    _tempmail_sessions[uid]["seen_ids"] = seen
    label = "new" if new_msgs else "total"
    await message.answer(
        f"✅ Showing <b>{len(show_msgs)}</b> {label} email(s).",
        reply_markup=_tm_menu_kb(),
    )


@router_tempmail.callback_query(F.data.startswith("tm_read:"))
async def tempmail_read_callback(call: CallbackQuery):
    await call.answer()
    parts = call.data.split(":", 2)
    if len(parts) < 3:
        await call.answer("❌ Invalid.", show_alert=True)
        return
    uid_str, short_id = parts[1], parts[2]
    try:
        uid = int(uid_str)
    except ValueError:
        return
    sess = _tempmail_sessions.get(uid)
    if not sess:
        await call.message.answer("❌ Session expired. Please generate a new email.")
        return
    msg = sess.get("messages", {}).get(short_id)
    if not msg:
        await call.message.answer("❌ Email not found. Try checking inbox again.")
        return

    sender   = html_lib.escape(str(msg.get("from", "Unknown")))
    subject  = html_lib.escape(str(msg.get("subject", "(No Subject)")))
    received = str(msg.get("created_at", ""))[:19]

    header = (
        f"📨 <b>Full Email</b>\n{_SEP}\n"
        f"👤 <b>From:</b> {sender}\n"
        f"📌 <b>Subject:</b> {subject}\n"
    )
    if received:
        header += f"🕐 <b>Received:</b> {received}\n"
    header += _SEP

    await call.message.answer(header)

    body_formatted = _tm_format_body(
        msg.get("body_text", ""),
        msg.get("body_html", ""),
    )
    chunk_size = 3800
    chunks = [body_formatted[i:i+chunk_size] for i in range(0, len(body_formatted), chunk_size)]
    for chunk in chunks:
        if chunk.strip():
            await call.message.answer(chunk)
            await asyncio.sleep(0.2)


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_DEL)
async def tempmail_delete(message: Message, state: FSMContext):
    uid  = message.from_user.id
    sess = _tempmail_sessions.pop(uid, None)
    if sess:
        deleted = html_lib.escape(sess["email"])
        await message.answer(
            f"🗑 <b>Email deleted.</b>\n{_SEP}\n"
            f"<code>{deleted}</code>\n\n"
            f"<i>Generate a new one anytime.</i>",
            reply_markup=_tm_menu_kb(),
        )
    else:
        await message.answer("❌ No active email to delete.", reply_markup=_tm_menu_kb())


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_DOM)
async def tempmail_change_domain(message: Message, state: FSMContext):
    uid = message.from_user.id
    current = (_tempmail_sessions.get(uid) or {}).get("chosen_domain", _TEMPMAIL_DOMAIN)
    await message.answer("⏳ Fetching available domains…")
    domains = await _tm_get_domains()
    if _TEMPMAIL_DOMAIN not in domains:
        domains.insert(0, _TEMPMAIL_DOMAIN)
    await state.set_state(UserFlow.temp_mail_domain)
    await state.update_data(tm_domains=domains)
    await message.answer(
        f"🌐 <b>Choose Domain</b>\n{_SEP}\n"
        f"Current: <code>@{current}</code>\n\n"
        f"Select a domain for your next email.\n"
        f"<i>({len(domains)} domains available)</i>",
        reply_markup=_tm_domain_kb(domains),
    )


@router_tempmail.message(UserFlow.temp_mail_menu, F.text == _TM_RND)
async def tempmail_random_domain(message: Message, state: FSMContext):
    """Pick a random domain from the API list instantly from the main menu."""
    uid = message.from_user.id
    await message.answer("🎲 Picking a random domain…")
    domains = await _tm_get_domains()
    if not domains:
        domains = [_TEMPMAIL_DOMAIN]
    chosen = random.choice(domains)
    sess = _tempmail_sessions.get(uid) or {}
    sess["chosen_domain"] = chosen
    _tempmail_sessions[uid] = sess
    await message.answer(
        f"🎲 <b>Random domain selected:</b> <code>@{chosen}</code>\n\n"
        f"Press 📧 <b>Generate Email</b> to create a new address with this domain.",
        reply_markup=_tm_menu_kb(),
    )


@router_tempmail.message(UserFlow.temp_mail_domain)
async def tempmail_domain_selected(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN, CANCEL_BTN):
        await state.set_state(UserFlow.temp_mail_menu)
        uid = message.from_user.id
        current = (_tempmail_sessions.get(uid) or {}).get("chosen_domain", _TEMPMAIL_DOMAIN)
        await message.answer(
            f"📧 <b>Temp Mail</b>\n{_SEP}\nDomain unchanged: <code>@{current}</code>",
            reply_markup=_tm_menu_kb(),
        )
        return
    data    = await state.get_data()
    domains = data.get("tm_domains", [_TEMPMAIL_DOMAIN])
    uid     = message.from_user.id
    # Handle random button inside domain chooser screen too
    if message.text == _TM_RND:
        chosen = random.choice(domains)
        sess = _tempmail_sessions.get(uid) or {}
        sess["chosen_domain"] = chosen
        _tempmail_sessions[uid] = sess
        await state.set_state(UserFlow.temp_mail_menu)
        await message.answer(
            f"🎲 <b>Random domain selected:</b> <code>@{chosen}</code>\n\n"
            f"Press 📧 <b>Generate Email</b> to use it.",
            reply_markup=_tm_menu_kb(),
        )
        return
    chosen = message.text.strip().lstrip("@")
    if chosen not in domains:
        await message.answer("❌ Please select a domain from the list.")
        return
    # save chosen domain; preserve existing session data if present
    sess = _tempmail_sessions.get(uid) or {}
    sess["chosen_domain"] = chosen
    _tempmail_sessions[uid] = sess
    await state.set_state(UserFlow.temp_mail_menu)
    await message.answer(
        f"✅ <b>Domain set to</b> <code>@{chosen}</code>\n\n"
        f"Press 📧 <b>Generate Email</b> to create a new address with this domain.",
        reply_markup=_tm_menu_kb(),
    )


# ══════════════════════════════════════════════════════════════════
# ROUTER — Admin Panel
# ══════════════════════════════════════════════════════════════════

router_admin = Router()


@router_admin.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Access denied.")
        return
    await state.clear()
    await state.set_state(AdminFlow.menu)
    await message.answer(f"🔐 <b>Admin Panel</b>\n{_SEP}\nWelcome back, admin!", reply_markup=admin_main_kb())


@router_admin.message(AdminFlow.menu, F.text == HOME_BTN)
async def admin_to_home(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.menu)
    await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())


# ── Dashboard ──────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_DASHBOARD)
async def admin_dashboard(message: Message):
    stats = await get_dashboard_stats()
    await message.answer(fmt_admin_dashboard(stats), reply_markup=admin_main_kb())


# ── Deposit inline callbacks ───────────────────────────────────────

@router_admin.callback_query(F.data.startswith("dep_ok:"))
async def approve_deposit(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("🚫 Denied", show_alert=True)
        return
    dep_id = call.data.split(":", 1)[1]
    dep    = await get_deposit(dep_id)
    if not dep or dep.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    await update_deposit(dep_id, {"status": "approved"})
    new_bal = await update_balance(dep["user_id"], dep["amount_usd"])
    try:
        await call.message.edit_caption((call.message.caption or "") + "\n\n✅ APPROVED", reply_markup=None)
    except Exception:
        try:
            await call.message.edit_text((call.message.text or "") + "\n\n✅ APPROVED", reply_markup=None)
        except Exception:
            pass
    await call.answer("✅ Approved")
    try:
        await call.bot.send_message(
            dep["user_id"],
            f"✅ <b>Deposit Approved!</b>\n{_SEP}\n"
            f"💵 Amount: <b>${dep['amount_usd']:.2f}</b>\n"
            f"💰 New Balance: <b>${new_bal:.2f}</b>",
        )
    except Exception:
        pass


@router_admin.callback_query(F.data.startswith("dep_no:"))
async def reject_deposit(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("🚫 Denied", show_alert=True)
        return
    dep_id = call.data.split(":", 1)[1]
    dep    = await get_deposit(dep_id)
    if not dep or dep.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    _pending_reject[call.from_user.id] = {"dep_id": dep_id, "dep": dep, "msg": call.message}
    await state.set_state(AdminFlow.dep_reject_reason)
    await call.answer("✏️ Enter reject reason")
    await call.message.answer(
        f"❌ <b>Reject Deposit</b>\n{_SEP}\n"
        f"User: @{dep.get('username','—')}  |  Amount: <b>${dep['amount_usd']:.2f}</b>\n\n"
        f"✏️ <b>Type the rejection reason to send to the user:</b>\n"
        f"<i>(e.g. Wrong TRX ID, screenshot unclear)</i>\n\n"
        f"Press /cancel to abort.",
    )


# ── Deposits list ──────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_DEPOSITS)
async def admin_deposits(message: Message):
    pending = await get_pending_deposits()
    if not pending:
        await message.answer("✅ No pending deposits.", reply_markup=admin_main_kb())
        return
    await message.answer(f"💳 <b>{len(pending)} Pending Deposit(s)</b>", reply_markup=admin_main_kb())
    for dep in pending[:10]:
        try:
            text      = fmt_admin_deposit_review(dep)
            kb_inline = deposit_review_inline(dep["deposit_id"])
            ss        = dep.get("screenshot_url", "")
            if ss and ss.startswith("http"):
                await message.answer_photo(photo=ss, caption=text, reply_markup=kb_inline)
            else:
                await message.answer(text, reply_markup=kb_inline)
        except Exception as e:
            logger.warning("Deposit display error: %s", e)


# ── VPN order callbacks ────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_VPN_ORDERS)
async def admin_vpn_orders(message: Message):
    pending = await get_pending_vpn_orders()
    if not pending:
        await message.answer("✅ No pending VPN orders.", reply_markup=admin_main_kb())
        return
    await message.answer(f"🌐 <b>{len(pending)} Pending VPN Order(s)</b>", reply_markup=admin_main_kb())
    for o in pending[:10]:
        await message.answer(fmt_admin_vpn_order(o), reply_markup=order_review_inline(o["order_id"], "vpn"))


@router_admin.callback_query(F.data.startswith("vpn_ok:"))
async def deliver_vpn(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("🚫 Denied", show_alert=True)
        return
    oid = call.data.split(":", 1)[1]
    o   = await db_get(f"vpn_orders/{oid}")
    if not o or o.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    _pending_fulfill[call.from_user.id] = {"oid": oid, "uid": o["user_id"], "kind": "vpn",
                                            "product_name": o["product_name"], "days": o["duration_days"]}
    await state.set_state(AdminFlow.vpn_fulfill)
    await call.answer("📝 Enter credentials now")
    await call.message.answer(
        f"📝 <b>VPN Credentials</b>\n{_SEP}\n"
        f"Order: <code>{oid[:12]}</code>\n"
        f"Product: <b>{o['product_name']}</b>  ·  {o['duration_days']} days\n\n"
        f"✏️ <b>Type the credentials to send to the user:</b>\n"
        f"<i>(e.g. username, password, server info)</i>\n\n"
        f"Press /cancel to abort.",
    )


@router_admin.callback_query(F.data.startswith("vpn_no:"))
async def cancel_vpn(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("🚫 Denied", show_alert=True)
        return
    oid = call.data.split(":", 1)[1]
    o   = await db_get(f"vpn_orders/{oid}")
    if not o or o.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    uid   = o.get("user_id")
    price = o.get("price", 0)
    await update_vpn_order(oid, {"status": "cancelled"})
    if uid:
        await update_balance(uid, price)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer("❌ Cancelled & refunded")
    try:
        await call.bot.send_message(
            uid,
            f"❌ <b>VPN Order Cancelled</b>\n{_SEP}\n"
            f"📦 {o.get('product_name','?')} order was cancelled.\n"
            f"💵 Refund: <b>${price:.2f}</b> added to your balance.",
        )
    except Exception:
        pass


# ── Proxy order callbacks ──────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_PROXY_ORDERS)
async def admin_proxy_orders(message: Message):
    pending = await get_pending_proxy_orders()
    if not pending:
        await message.answer("✅ No pending proxy orders.", reply_markup=admin_main_kb())
        return
    await message.answer(f"🔐 <b>{len(pending)} Pending Proxy Order(s)</b>", reply_markup=admin_main_kb())
    for o in pending[:10]:
        await message.answer(fmt_admin_proxy_order(o), reply_markup=order_review_inline(o["order_id"], "proxy"))


@router_admin.callback_query(F.data.startswith("proxy_ok:"))
async def deliver_proxy(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        await call.answer("🚫 Denied", show_alert=True)
        return
    oid = call.data.split(":", 1)[1]
    o   = await db_get(f"proxy_orders/{oid}")
    if not o or o.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    _pending_fulfill[call.from_user.id] = {"oid": oid, "uid": o["user_id"], "kind": "proxy",
                                            "product_name": o["product_name"], "days": o["duration_days"]}
    await state.set_state(AdminFlow.proxy_fulfill)
    await call.answer("📝 Enter credentials now")
    await call.message.answer(
        f"📝 <b>Proxy Credentials</b>\n{_SEP}\n"
        f"Order: <code>{oid[:12]}</code>\n"
        f"Product: <b>{o['product_name']}</b>  ·  📡 {o.get('duration_days', '—')}\n\n"
        f"✏️ <b>Type the proxy details to send to the user:</b>\n"
        f"<i>(e.g. IP:Port, username, password)</i>\n\n"
        f"Press /cancel to abort.",
    )


@router_admin.callback_query(F.data.startswith("proxy_no:"))
async def cancel_proxy(call: CallbackQuery):
    if not is_admin(call.from_user.id):
        await call.answer("🚫 Denied", show_alert=True)
        return
    oid = call.data.split(":", 1)[1]
    o   = await db_get(f"proxy_orders/{oid}")
    if not o or o.get("status") != "pending":
        await call.answer("Already processed.", show_alert=True)
        return
    uid   = o.get("user_id")
    price = o.get("price", 0)
    await update_proxy_order(oid, {"status": "cancelled"})
    if uid:
        await update_balance(uid, price)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer("❌ Cancelled & refunded")
    try:
        await call.bot.send_message(
            uid,
            f"❌ <b>Proxy Order Cancelled</b>\n{_SEP}\n"
            f"📦 {o.get('product_name','?')} order was cancelled.\n"
            f"💵 Refund: <b>${price:.2f}</b> added to your balance.",
        )
    except Exception:
        pass


# ── VPN Credentials Fulfillment ────────────────────────────────────

@router_admin.message(AdminFlow.vpn_fulfill)
async def vpn_credentials_received(message: Message, state: FSMContext):
    if message.text and message.text.lower() in ("/cancel", BACK_BTN, HOME_BTN):
        _pending_fulfill.pop(message.from_user.id, None)
        await state.set_state(AdminFlow.menu)
        await message.answer("❌ Cancelled.", reply_markup=admin_main_kb())
        return
    if not message.text:
        await message.answer("❌ Please send the credentials as <b>text</b> (no files or photos).")
        return
    ctx = _pending_fulfill.pop(message.from_user.id, None)
    if not ctx:
        await state.set_state(AdminFlow.menu)
        await message.answer("❌ Session expired.", reply_markup=admin_main_kb())
        return
    await update_vpn_order(ctx["oid"], {"status": "delivered"})
    await state.set_state(AdminFlow.menu)
    await message.answer(
        "✅ <b>Delivered!</b> Credentials sent to user.",
        reply_markup=admin_main_kb(),
    )
    try:
        await message.bot.send_message(
            ctx["uid"],
            f"✅ <b>VPN Order Delivered!</b>\n{_SEP}\n"
            f"📦 <b>{ctx['product_name']}</b>  ·  {ctx['days']} day(s)\n\n"
            f"🔑 <b>Your Credentials:</b>\n<pre>{message.text}</pre>",
        )
    except Exception:
        pass


# ── Proxy Credentials Fulfillment ──────────────────────────────────

@router_admin.message(AdminFlow.proxy_fulfill)
async def proxy_credentials_received(message: Message, state: FSMContext):
    if message.text and message.text.lower() in ("/cancel", BACK_BTN, HOME_BTN):
        _pending_fulfill.pop(message.from_user.id, None)
        await state.set_state(AdminFlow.menu)
        await message.answer("❌ Cancelled.", reply_markup=admin_main_kb())
        return
    if not message.text:
        await message.answer("❌ Please send the proxy details as <b>text</b> (no files or photos).")
        return
    ctx = _pending_fulfill.pop(message.from_user.id, None)
    if not ctx:
        await state.set_state(AdminFlow.menu)
        await message.answer("❌ Session expired.", reply_markup=admin_main_kb())
        return
    await update_proxy_order(ctx["oid"], {"status": "delivered"})
    await state.set_state(AdminFlow.menu)
    await message.answer(
        "✅ <b>Delivered!</b> Proxy details sent to user.",
        reply_markup=admin_main_kb(),
    )
    try:
        await message.bot.send_message(
            ctx["uid"],
            f"✅ <b>Proxy Order Delivered!</b>\n{_SEP}\n"
            f"📦 <b>{ctx['product_name']}</b>  ·  📡 {ctx['days']}\n\n"
            f"🔑 <b>Your Proxy Details:</b>\n<pre>{message.text}</pre>",
        )
    except Exception:
        pass


# ── Deposit Reject Reason ───────────────────────────────────────────

@router_admin.message(AdminFlow.dep_reject_reason)
async def deposit_reject_reason_received(message: Message, state: FSMContext):
    if message.text and message.text.lower() in ("/cancel", BACK_BTN, HOME_BTN):
        _pending_reject.pop(message.from_user.id, None)
        await state.set_state(AdminFlow.menu)
        await message.answer("❌ Cancelled.", reply_markup=admin_main_kb())
        return
    ctx = _pending_reject.pop(message.from_user.id, None)
    if not ctx:
        await state.set_state(AdminFlow.menu)
        await message.answer("❌ Session expired.", reply_markup=admin_main_kb())
        return
    dep_id = ctx["dep_id"]
    dep    = ctx["dep"]
    reason = message.text or "No reason given."
    await update_deposit(dep_id, {"status": "rejected", "reject_reason": reason})
    orig_msg = ctx["msg"]
    try:
        await orig_msg.edit_caption(
            (orig_msg.caption or "") + f"\n\n❌ REJECTED\nReason: {reason}", reply_markup=None
        )
    except Exception:
        try:
            await orig_msg.edit_text(
                (orig_msg.text or "") + f"\n\n❌ REJECTED\nReason: {reason}", reply_markup=None
            )
        except Exception:
            pass
    await state.set_state(AdminFlow.menu)
    await message.answer("❌ Deposit rejected.", reply_markup=admin_main_kb())
    try:
        await message.bot.send_message(
            dep["user_id"],
            f"❌ <b>Deposit Rejected</b>\n{_SEP}\n"
            f"Amount: <b>${dep['amount_usd']:.2f}</b> was not credited.\n\n"
            f"📋 <b>Reason:</b> {reason}\n\n"
            f"Contact support if you think this is an error.",
        )
    except Exception:
        pass


# ── Products ───────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_PRODUCTS)
async def admin_products(message: Message, state: FSMContext):
    products = await get_all_products()
    dm = build_admin_products_dm(products)
    await state.update_data(products=products, dm=dm)
    await state.set_state(AdminFlow.products_list)
    await message.answer(
        f"📦 <b>Products</b>\n{_SEP}\n{len(products)} product(s) total.\nSelect one to manage:",
        reply_markup=admin_products_kb(products),
    )


@router_admin.message(AdminFlow.products_list)
async def admin_products_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text == BTN_ADD_PRODUCT:
        await state.set_state(AdminFlow.product_add_name)
        await message.answer("Enter product name:", reply_markup=input_kb())
        return
    if message.text == BTN_DOWNLOAD_PRODUCTS:
        products = await get_all_products()
        if not products:
            await message.answer("❌ No products found.")
            return
        xlsx_bytes = make_products_xlsx(products)
        date_str   = time.strftime("%Y%m%d_%H%M", time.gmtime())
        await message.answer_document(
            document=BufferedInputFile(xlsx_bytes, filename=f"products_{date_str}.xlsx"),
            caption=(
                f"📦 <b>All Products</b>\n{_SEP}\n"
                f"Total: <b>{len(products)}</b> product(s)\n\n"
                f"<i>Edit this file and upload it via 📤 Import Products to add new products in bulk.</i>"
            ),
        )
        return
    if message.text == BTN_IMPORT_PRODUCTS:
        await state.set_state(AdminFlow.products_import)
        await message.answer(
            f"📤 <b>Import Products</b>\n{_SEP}\n"
            f"Send an <b>.xlsx</b> file to import products in bulk.\n\n"
            f"<b>Required columns:</b>\n"
            f"• <b>Name</b> — product name\n"
            f"• <b>Emoji</b> — icon (e.g. 📮 🌐 🔐)\n"
            f"• <b>Category</b> — mail / vpn / proxy\n"
            f"• <b>Price (USD)</b> — price per unit\n"
            f"• <b>Delivery Mode</b> — manual / auto (proxy only)\n"
            f"• <b>Hidden</b> — yes / no\n\n"
            f"💡 Tip: Download the current products file first to use it as a template.",
            reply_markup=_kb([CANCEL_BTN, HOME_BTN]),
        )
        return
    data = await state.get_data()
    pid  = data.get("dm", {}).get(message.text)
    if not pid:
        await message.answer("❌ Select a product from the keyboard.")
        return
    product = await get_product(pid)
    await state.update_data(pid=pid, product=product)
    await state.set_state(AdminFlow.product_detail)
    hidden        = product.get("hidden", False)
    category      = product.get("category", "mail")
    delivery_mode = product.get("delivery_mode", "manual")
    desc          = product.get("description", "").strip()
    mode_label = ""
    if category == "proxy":
        mode_label = f"\n🚀 Delivery: <b>{'🤖 Auto (Stock)' if delivery_mode == 'auto' else '👤 Manual (Admin)'}</b>"
    desc_line = f"\n📝 <i>{desc}</i>" if desc else "\n📝 <i>No description</i>"
    await message.answer(
        f"{product.get('emoji','📦')} <b>{product['name']}</b>\n{_SEP}\n"
        f"💵 Price: ${product['price']:.2f}\n"
        f"📦 Stock: {product.get('stock_count',0)}\n"
        f"🏷 Category: {category.upper()}{mode_label}\n"
        f"👁 Visible: {'No 🙈' if hidden else 'Yes 👁'}\n"
        f"🛍 Sold: {product.get('total_sold',0)}"
        f"{desc_line}",
        reply_markup=admin_product_actions_kb(hidden, category, delivery_mode),
    )


@router_admin.message(AdminFlow.product_detail)
async def admin_product_detail_action(message: Message, state: FSMContext):
    data    = await state.get_data()
    pid     = data.get("pid")
    product = data.get("product", {})
    if message.text in (BACK_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    if message.text in (BTN_HIDE_PROD, BTN_SHOW_PROD):
        new_h   = not product.get("hidden", False)
        await update_product(pid, {"hidden": new_h})
        updated = await get_product(pid)
        await state.update_data(product=updated)
        await message.answer(
            f"✅ Product is now {'hidden 🙈' if new_h else 'visible 👁'}.",
            reply_markup=admin_product_actions_kb(
                updated.get("hidden", False),
                updated.get("category", "mail"),
                updated.get("delivery_mode", "manual"),
            ),
        )
        return
    if message.text in (BTN_TOGGLE_AUTO, BTN_TOGGLE_MANUAL):
        if product.get("category", "mail") != "proxy":
            await message.answer("❌ Only proxy products have a delivery mode.")
            return
        new_mode = "auto" if message.text == BTN_TOGGLE_AUTO else "manual"
        await update_product(pid, {"delivery_mode": new_mode})
        updated = await get_product(pid)
        await state.update_data(product=updated)
        label = "🤖 Auto (Stock)" if new_mode == "auto" else "👤 Manual (Admin)"
        await message.answer(
            f"✅ Delivery mode → <b>{label}</b>",
            reply_markup=admin_product_actions_kb(updated.get("hidden", False), "proxy", new_mode),
        )
        return
    if message.text == BTN_ADD_STOCK:
        cat  = product.get("category", "mail")
        dmode = product.get("delivery_mode", "manual")
        if not (cat == "mail" or (cat == "proxy" and dmode == "auto")):
            await message.answer("❌ Stock management is only for Mail or Auto-Proxy products.")
            return
        stock = await get_stock_count(pid)
        settings = await get_settings()
        warn = "\n⚠️ <b>Low Stock Alert!</b>" if stock <= settings.get("low_stock_threshold", 5) else ""
        await state.update_data(stock_pid=pid, stock_product=product)
        await state.set_state(AdminFlow.stock_detail)
        await message.answer(
            f"📥 <b>{product['name']}</b>\n{_SEP}\n"
            f"📦 Current Stock: <b>{stock}</b>{warn}\n\nChoose an action:",
            reply_markup=admin_stock_actions_kb(),
        )
        return
    if message.text == BTN_DELETE:
        await delete_product(pid)
        await message.answer("🗑 Deleted.")
        await _back_to_products(message, state)
        return
    field_map = {
        BTN_EDIT_NAME:  "name",
        BTN_EDIT_PRICE: "price",
        BTN_EDIT_EMOJI: "emoji",
        BTN_EDIT_DESC:  "description",
    }
    field = field_map.get(message.text)
    if field:
        await state.update_data(edit_field=field)
        await state.set_state(AdminFlow.product_edit)
        prompts = {
            "name":        "Enter new product name:",
            "price":       "Enter new price (USD):",
            "emoji":       "Enter new emoji:",
            "description": "Enter new description (or send — to remove it):",
        }
        await message.answer(prompts[field], reply_markup=input_kb())
        return
    await message.answer("❌ Select from keyboard.")


@router_admin.message(AdminFlow.product_edit)
async def receive_product_edit(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    data  = await state.get_data()
    field = data.get("edit_field", "name")
    pid   = data.get("pid")
    value = message.text.strip()
    if field == "price":
        price, err = validate_price(value)
        if err:
            await message.answer(err)
            return
        await update_product(pid, {"price": price})
    elif field == "description":
        # "—" or "-" means remove description
        new_desc = "" if value in ("—", "-") else value
        await update_product(pid, {"description": new_desc})
    else:
        await update_product(pid, {field: value})
    updated = await get_product(pid)
    await state.update_data(product=updated)
    await state.set_state(AdminFlow.product_detail)
    field_label = "Description" if field == "description" else field.capitalize()
    await message.answer(
        f"✅ <b>{field_label} updated!</b>\n{updated.get('emoji','📦')} {updated['name']} — ${updated['price']:.2f}",
        reply_markup=admin_product_actions_kb(
            updated.get("hidden", False),
            updated.get("category", "mail"),
            updated.get("delivery_mode", "manual"),
        ),
    )


@router_admin.message(AdminFlow.products_import)
async def admin_products_import(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    if not message.document:
        await message.answer(
            "❌ Please send an <b>.xlsx</b> file.\n\nPress ❌ Cancel to go back.",
            reply_markup=_kb([CANCEL_BTN, HOME_BTN]),
        )
        return
    fname = message.document.file_name or ""
    if not fname.lower().endswith(".xlsx"):
        await message.answer(
            f"❌ Unsupported file type: <code>{fname}</code>\nOnly <b>.xlsx</b> files are supported.\n\nPress ❌ Cancel to go back.",
            reply_markup=_kb([CANCEL_BTN, HOME_BTN]),
        )
        return
    try:
        file       = await message.bot.get_file(message.document.file_id)
        file_bytes = (await message.bot.download_file(file.file_path)).read()
    except Exception as e:
        await message.answer(f"❌ Failed to download file: {e}", reply_markup=_kb([CANCEL_BTN, HOME_BTN]))
        return
    parsed = parse_products_xlsx(file_bytes)
    if not parsed:
        await message.answer(
            "❌ No valid products found in the file.\n\n"
            "Make sure the file has <b>Name</b> and <b>Price (USD)</b> columns.\n\n"
            "Press ❌ Cancel to go back.",
            reply_markup=_kb([CANCEL_BTN, HOME_BTN]),
        )
        return
    created = 0
    skipped = 0
    for p in parsed:
        try:
            await create_product(p["name"], p["price"], p["emoji"], p["category"],
                                  p.get("delivery_mode", "manual"), p.get("hidden", False))
            created += 1
        except Exception:
            skipped += 1
    await _back_to_products(message, state)
    lines = [f"  • {p['emoji']} {p['name']} [{p['category'].upper()}] — ${p['price']:.2f}" for p in parsed[:10]]
    preview = "\n".join(lines) + (f"\n  <i>... and {len(parsed) - 10} more</i>" if len(parsed) > 10 else "")
    await message.answer(
        f"✅ <b>Import Complete!</b>\n{_SEP}\n"
        f"✅ Created: <b>{created}</b> product(s)\n"
        f"❌ Skipped: <b>{skipped}</b>\n\n"
        f"<b>Imported products:</b>\n{preview}",
    )


@router_admin.message(AdminFlow.product_add_name)
async def add_product_name(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    await state.update_data(pname=message.text.strip())
    await state.set_state(AdminFlow.product_add_emoji)
    await message.answer("Enter emoji (e.g. 📮 🌐 🔐):", reply_markup=input_kb())


@router_admin.message(AdminFlow.product_add_emoji)
async def add_product_emoji(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    await state.update_data(pemoji=message.text.strip())
    await state.set_state(AdminFlow.product_add_price)
    await message.answer("Enter price in USD:", reply_markup=input_kb())


@router_admin.message(AdminFlow.product_add_price)
async def add_product_price(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    price, err = validate_price(message.text)
    if err:
        await message.answer(err)
        return
    await state.update_data(pprice=price)
    await state.set_state(AdminFlow.product_add_cat)
    await message.answer("Select category:", reply_markup=admin_category_kb())


@router_admin.message(AdminFlow.product_add_cat)
async def add_product_category(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    cat = CATEGORY_MAP.get(message.text)
    if not cat:
        await message.answer("❌ Select from keyboard.", reply_markup=admin_category_kb())
        return
    await state.update_data(pcat=cat)
    await state.set_state(AdminFlow.product_add_desc)
    await message.answer(
        "📝 <b>Product Description</b> (optional)\n\n"
        "Enter a short description shown to users when they view this product.\n"
        "<i>Example: Fast residential proxies, 99% uptime guarantee</i>\n\n"
        "Or press <b>⏭ Skip</b> to leave it blank.",
        reply_markup=_kb(["⏭ Skip"], [CANCEL_BTN]),
    )


@router_admin.message(AdminFlow.product_add_desc)
async def add_product_desc(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_products(message, state)
        return
    data = await state.get_data()
    desc = "" if message.text.strip() in ("⏭ Skip", "skip", "-") else message.text.strip()
    await create_product(
        data.get("pname", ""), data.get("pprice", 0.0),
        data.get("pemoji", "📦"), data.get("pcat", "mail"),
        description=desc,
    )
    desc_preview = f"\n📝 {desc}" if desc else ""
    await message.answer(
        f"✅ <b>Product Created!</b>\n{_SEP}\n"
        f"{data.get('pemoji','📦')} {data.get('pname','')} — ${data.get('pprice',0):.2f} [{data.get('pcat','mail').upper()}]"
        f"{desc_preview}"
    )
    await _back_to_products(message, state)


async def _back_to_products(message: Message, state: FSMContext):
    products = await get_all_products()
    dm = build_admin_products_dm(products)
    await state.update_data(products=products, dm=dm)
    await state.set_state(AdminFlow.products_list)
    await message.answer("📦 <b>Products</b>", reply_markup=admin_products_kb(products))


# ── Stock ──────────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_STOCK)
async def admin_stock(message: Message, state: FSMContext):
    products = await get_all_products()
    stockable = {
        k: v for k, v in products.items()
        if v.get("category") == "mail"
        or (v.get("category") == "proxy" and v.get("delivery_mode") == "auto")
    }
    if not stockable:
        await message.answer(
            "📥 No stockable products yet.\nCreate Mail products or Auto-Proxy products first.",
            reply_markup=admin_main_kb(),
        )
        return
    dm = build_admin_stock_dm(stockable)
    await state.update_data(stock_products=stockable, stock_dm=dm)
    await state.set_state(AdminFlow.stock_list)
    await message.answer(
        f"📥 <b>Stock Management</b>\n{_SEP}\n"
        f"📮 Mail & 🤖 Auto-Proxy products:\nSelect a product:",
        reply_markup=admin_stock_products_kb(stockable),
    )


@router_admin.message(AdminFlow.stock_list)
async def admin_stock_list_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text == BTN_DOWNLOAD_ALL_STOCK:
        data     = await state.get_data()
        products = data.get("stock_products", {})
        if not products:
            await message.answer("❌ No stockable products found.", reply_markup=admin_main_kb())
            return
        await message.answer("⏳ Exporting all stock, please wait…")
        try:
            all_stocks = {}
            for pid_key in products:
                all_stocks[pid_key] = await db_get(f"stocks/{pid_key}") or {}
            total_items = sum(len(v) for v in all_stocks.values())
            xlsx_bytes  = make_all_stock_export_xlsx(products, all_stocks)
            date_str    = time.strftime("%Y%m%d_%H%M", time.gmtime())
            await message.answer_document(
                document=BufferedInputFile(xlsx_bytes, filename=f"all_stock_{date_str}.xlsx"),
                caption=(
                    f"📦 <b>All Stock Export</b>\n{_SEP}\n"
                    f"📂 Products: <b>{len(products)}</b>\n"
                    f"📋 Total Items: <b>{total_items}</b>\n\n"
                    f"<i>Each product has its own sheet. Column D (Raw) is the original account string for re-importing.</i>"
                ),
            )
        except Exception as e:
            logger.error("All-stock export error: %s", e)
            await message.answer(f"❌ Export failed: {e}")
        return
    data = await state.get_data()
    pid  = data.get("stock_dm", {}).get(message.text)
    if not pid:
        await message.answer("❌ Select from keyboard.")
        return
    product  = await get_product(pid)
    stock    = await get_stock_count(pid)
    settings = await get_settings()
    warn     = "\n⚠️ <b>Low Stock Alert!</b>" if stock <= settings.get("low_stock_threshold", 5) else ""
    await state.update_data(stock_pid=pid, stock_product=product)
    await state.set_state(AdminFlow.stock_detail)
    await message.answer(
        f"📥 <b>{product['name']}</b>\n{_SEP}\n"
        f"📦 Current Stock: <b>{stock}</b>{warn}\n\nChoose an action:",
        reply_markup=admin_stock_actions_kb(),
    )


@router_admin.message(AdminFlow.stock_detail)
async def admin_stock_detail_action(message: Message, state: FSMContext):
    data    = await state.get_data()
    pid     = data.get("stock_pid")
    product = data.get("stock_product", {})
    if message.text == BACK_BTN:
        mail_p = data.get("stock_products", {})
        await state.set_state(AdminFlow.stock_list)
        await message.answer("📥 <b>Stock Management</b>", reply_markup=admin_stock_products_kb(mail_p))
        return
    if message.text == HOME_BTN:
        await state.set_state(AdminFlow.menu)
        await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text == BTN_GET_TEMPLATE:
        try:
            tmpl = make_stock_template_xlsx(product["name"])
            safe_name = product["name"].replace(" ", "_")[:20]
            await message.answer_document(
                document=BufferedInputFile(tmpl, filename=f"stock_template_{safe_name}.xlsx"),
                caption=(
                    f"📋 <b>Stock Template — {product['name']}</b>\n{_SEP}\n"
                    f"1️⃣  Open this file in Excel / Google Sheets\n"
                    f"2️⃣  Delete the 3 example rows (green)\n"
                    f"3️⃣  Fill in real accounts: Email in <b>column A</b>, Password in <b>column B</b>\n"
                    f"4️⃣  Save and upload back with <b>📤 Upload File</b>"
                ),
                reply_markup=admin_stock_actions_kb(),
            )
        except Exception as _te:
            logger.warning("Template send failed: %s", _te)
            await message.answer("❌ Failed to generate template.", reply_markup=admin_stock_actions_kb())
        return
    if message.text == BTN_DOWNLOAD_STOCK:
        stock_data = await db_get(f"stocks/{pid}") or {}
        if not stock_data:
            await message.answer(
                f"📭 <b>No stock found</b>\n{_SEP}\n"
                f"Product <b>{product['name']}</b> has no stock items yet.",
                reply_markup=admin_stock_actions_kb(),
            )
            return
        try:
            xlsx_bytes = make_stock_export_xlsx(product["name"], stock_data)
            safe_name  = re.sub(r"[^\w]", "_", product["name"])[:20]
            date_str   = time.strftime("%Y%m%d_%H%M", time.gmtime())
            await message.answer_document(
                document=BufferedInputFile(xlsx_bytes, filename=f"stock_{safe_name}_{date_str}.xlsx"),
                caption=(
                    f"📥 <b>Stock Export — {product['name']}</b>\n{_SEP}\n"
                    f"📦 Total Items: <b>{len(stock_data)}</b>\n\n"
                    f"<i>Column D (Raw) is the original account string — use it when re-importing via 📤 Upload File.</i>"
                ),
                reply_markup=admin_stock_actions_kb(),
            )
        except Exception as e:
            logger.error("Stock export error: %s", e)
            await message.answer(f"❌ Failed to generate stock file: {e}", reply_markup=admin_stock_actions_kb())
        return
    if message.text == BTN_UPLOAD_FILE:
        await state.set_state(AdminFlow.stock_uploading)
        await message.answer(
            f"📤 <b>Upload Stock</b>\n{_SEP}\n"
            f"Product: <b>{product['name']}</b>\n\n"
            f"Send a <b>.txt</b> / <b>.csv</b> / <b>.xlsx</b> file\n"
            f"Format: <code>email:password</code> (one per row/line)\n\n"
            f"<i>For xlsx: put email in column A, password in column B</i>",
            reply_markup=input_kb(),
        )
        return
    if message.text == BTN_MANUAL_ADD:
        await state.set_state(AdminFlow.stock_manual)
        await message.answer(
            f"✏️ <b>Manual Add</b>\n{_SEP}\n"
            f"Product: <b>{product['name']}</b>\n\n"
            f"Type accounts one per line:\n<code>email@gmail.com:password</code>",
            reply_markup=input_kb(),
        )
        return
    if message.text == BTN_CLEAR_STOCK:
        await clear_stock(pid)
        await message.answer(
            f"🗑 Stock cleared for <b>{product['name']}</b>.",
            reply_markup=admin_stock_actions_kb(),
        )
        return
    await message.answer("❌ Select from keyboard.")


@router_admin.message(AdminFlow.stock_uploading, F.document)
async def receive_stock_file(message: Message, state: FSMContext):
    data    = await state.get_data()
    pid     = data.get("stock_pid")
    product = data.get("stock_product", {})
    doc: Document = message.document

    # Check file type before downloading
    fname = (doc.file_name or "file.txt").lower()
    if not (fname.endswith(".txt") or fname.endswith(".csv") or fname.endswith(".xlsx")):
        await message.answer(
            f"❌ Unsupported file type: <b>{doc.file_name}</b>\n"
            f"Please send a <b>.txt</b>, <b>.csv</b>, or <b>.xlsx</b> file.",
            reply_markup=admin_stock_actions_kb(),
        )
        await state.set_state(AdminFlow.stock_detail)
        return

    await message.answer("⏳ Processing file…")
    try:
        file = await message.bot.get_file(doc.file_id)
        raw  = (await message.bot.download_file(file.file_path)).read()
    except Exception as e:
        await message.answer(f"❌ Failed to download file: {e}", reply_markup=admin_stock_actions_kb())
        await state.set_state(AdminFlow.stock_detail)
        return

    try:
        items = parse_stock_file(raw, doc.file_name or "file.txt")
    except Exception as e:
        await message.answer(f"❌ Parse error: {e}", reply_markup=admin_stock_actions_kb())
        await state.set_state(AdminFlow.stock_detail)
        return

    if not items:
        await message.answer(
            "❌ No valid accounts found in the file.\n"
            "Make sure the file has email:password format.",
            reply_markup=admin_stock_actions_kb(),
        )
        await state.set_state(AdminFlow.stock_detail)
        return

    added     = await add_stock_items(pid, items)
    new_count = await get_stock_count(pid)
    await state.set_state(AdminFlow.stock_detail)
    await message.answer(
        f"✅ <b>{added} accounts added</b> ({len(items)} lines read)\n{_SEP}\n"
        f"Product: <b>{product['name']}</b>\n📦 Total Stock: <b>{new_count}</b>",
        reply_markup=admin_stock_actions_kb(),
    )


@router_admin.message(AdminFlow.stock_uploading)
async def stock_not_file(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.stock_detail)
        await message.answer("Cancelled.", reply_markup=admin_stock_actions_kb())
        return
    await message.answer("❌ Please send a <b>.txt</b>, <b>.csv</b> or <b>.xlsx</b> file — not a text message.")


@router_admin.message(AdminFlow.stock_manual)
async def receive_manual_stock(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.stock_detail)
        await message.answer("Cancelled.", reply_markup=admin_stock_actions_kb())
        return
    data    = await state.get_data()
    pid     = data.get("stock_pid")
    product = data.get("stock_product", {})
    lines   = [ln.strip() for ln in message.text.splitlines() if ln.strip()]
    if not lines:
        await message.answer("❌ No valid lines found.")
        return
    added     = await add_stock_items(pid, lines)
    new_count = await get_stock_count(pid)
    await state.set_state(AdminFlow.stock_detail)
    await message.answer(
        f"✅ <b>{added} accounts added</b>\n{_SEP}\nProduct: <b>{product['name']}</b>\n📦 Total Stock: <b>{new_count}</b>",
        reply_markup=admin_stock_actions_kb(),
    )


# ── Users ──────────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_USERS)
async def admin_users(message: Message, state: FSMContext):
    all_users = await get_all_users()
    await state.set_state(AdminFlow.user_search)
    await message.answer(
        f"👥 <b>User Management</b>\n{_SEP}\n"
        f"Total Users: <b>{len(all_users)}</b>\n\nEnter a Telegram User ID to look up:",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )


@router_admin.message(AdminFlow.user_search)
async def admin_search_user(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    try:
        uid = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Enter a valid numeric user ID.")
        return
    user = await get_user(uid)
    if not user:
        await message.answer("❌ User not found.")
        return
    await state.update_data(target_uid=uid, target_user=user)
    await state.set_state(AdminFlow.user_detail)
    await message.answer(fmt_user_info(user), reply_markup=admin_user_actions_kb(user.get("is_banned", False)))


@router_admin.message(AdminFlow.user_detail)
async def admin_user_action(message: Message, state: FSMContext):
    data = await state.get_data()
    uid  = data.get("target_uid")
    user = data.get("target_user", {})
    if message.text == BACK_BTN:
        await state.set_state(AdminFlow.user_search)
        await message.answer("👥 Enter User ID:", reply_markup=_kb([BACK_BTN, HOME_BTN]))
        return
    if message.text == HOME_BTN:
        await state.set_state(AdminFlow.menu)
        await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text in (BTN_BAN_USER, BTN_UNBAN_USER):
        new_b   = not user.get("is_banned", False)
        await ban_user(uid, new_b)
        updated = await get_user(uid)
        await state.update_data(target_user=updated)
        await message.answer(
            f"✅ User <code>{uid}</code> {'banned 🚫' if new_b else 'unbanned ✅'}",
            reply_markup=admin_user_actions_kb(updated.get("is_banned", False)),
        )
        try:
            await message.bot.send_message(
                uid,
                "🚫 Your account has been banned." if new_b else "✅ Your account has been unbanned.",
            )
        except Exception:
            pass
        return
    if message.text == BTN_ADD_BAL:
        await state.set_state(AdminFlow.user_add_bal)
        await message.answer(f"💰 Enter USD amount to add to <code>{uid}</code>:", reply_markup=input_kb())
        return
    if message.text == BTN_REMOVE_BAL:
        await state.set_state(AdminFlow.user_remove_bal)
        await message.answer(f"💸 Enter USD amount to remove from <code>{uid}</code>:", reply_markup=input_kb())
        return
    await message.answer("❌ Select from keyboard.")


@router_admin.message(AdminFlow.user_add_bal)
async def admin_add_bal(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data = await state.get_data()
        user = data.get("target_user", {})
        await state.set_state(AdminFlow.user_detail)
        await message.answer(fmt_user_info(user), reply_markup=admin_user_actions_kb(user.get("is_banned", False)))
        return
    amount, err = validate_price(message.text)
    if err:
        await message.answer(err)
        return
    data    = await state.get_data()
    uid     = data.get("target_uid")
    new_bal = await update_balance(uid, amount)
    updated = await get_user(uid)
    await state.update_data(target_user=updated)
    await state.set_state(AdminFlow.user_detail)
    await message.answer(
        f"✅ Added <b>${amount:.2f}</b> → New Balance: <b>${new_bal:.2f}</b>",
        reply_markup=admin_user_actions_kb(updated.get("is_banned", False)),
    )
    try:
        await message.bot.send_message(
            uid,
            f"💰 <b>Balance Added!</b>\n{_SEP}\n➕ ${amount:.2f}\n💰 New Balance: ${new_bal:.2f}",
        )
    except Exception:
        pass


@router_admin.message(AdminFlow.user_remove_bal)
async def admin_remove_bal(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        data = await state.get_data()
        user = data.get("target_user", {})
        await state.set_state(AdminFlow.user_detail)
        await message.answer(fmt_user_info(user), reply_markup=admin_user_actions_kb(user.get("is_banned", False)))
        return
    amount, err = validate_price(message.text)
    if err:
        await message.answer(err)
        return
    data    = await state.get_data()
    uid     = data.get("target_uid")
    new_bal = await update_balance(uid, -amount)
    updated = await get_user(uid)
    await state.update_data(target_user=updated)
    await state.set_state(AdminFlow.user_detail)
    await message.answer(
        f"✅ Removed <b>${amount:.2f}</b> → New Balance: <b>${new_bal:.2f}</b>",
        reply_markup=admin_user_actions_kb(updated.get("is_banned", False)),
    )


# ── Coupons ────────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_COUPONS)
async def admin_coupons(message: Message, state: FSMContext):
    coupons = await get_all_coupons()
    dm = build_coupons_dm(coupons)
    await state.update_data(coupons=coupons, coupons_dm=dm)
    await state.set_state(AdminFlow.coupons_list)
    await message.answer(f"🎟 <b>Coupons</b>\n{_SEP}\n{len(coupons)} coupon(s) total.", reply_markup=admin_coupons_kb(coupons))


@router_admin.message(AdminFlow.coupons_list)
async def admin_coupons_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    if message.text == BTN_CREATE_COUPON:
        await state.set_state(AdminFlow.coupon_code)
        await message.answer("Enter coupon code (alphanumeric, e.g. SAVE20):", reply_markup=input_kb())
        return
    data = await state.get_data()
    cid  = data.get("coupons_dm", {}).get(message.text)
    if not cid:
        await message.answer("❌ Select from keyboard.")
        return
    coupons = data.get("coupons", [])
    coupon  = next((c for c in coupons if c["coupon_id"] == cid), None)
    if not coupon:
        await message.answer("❌ Not found.")
        return
    expires = time.strftime("%d %b %Y", time.gmtime(coupon.get("expires_at", 0)))
    await state.update_data(selected_cid=cid)
    await state.set_state(AdminFlow.coupon_detail)
    await message.answer(
        f"🎟 <b>{coupon['code']}</b>\n{_SEP}\n"
        f"🏷 Discount: <b>{coupon['discount_pct']:.0f}%</b>\n"
        f"🔢 Used: <b>{coupon['used_count']}/{coupon['max_uses']}</b>\n"
        f"📅 Expires: <b>{expires}</b>\n"
        f"Status: {'✅ Active' if coupon.get('active') else '❌ Inactive'}",
        reply_markup=admin_coupon_actions_kb(),
    )


@router_admin.message(AdminFlow.coupon_detail)
async def admin_coupon_action(message: Message, state: FSMContext):
    data = await state.get_data()
    cid  = data.get("selected_cid")
    if message.text in (BACK_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    if message.text == BTN_DELETE_COUPON:
        await delete_coupon(cid)
        await _back_to_coupons(message, state)
        return
    await message.answer("❌ Select from keyboard.")


@router_admin.message(AdminFlow.coupon_code)
async def coupon_create_code(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    code = message.text.strip().upper()
    if not code.isalnum():
        await message.answer("❌ Alphanumeric only (letters and numbers).")
        return
    await state.update_data(c_code=code)
    await state.set_state(AdminFlow.coupon_discount)
    await message.answer("Enter discount % (1–100):", reply_markup=input_kb())


@router_admin.message(AdminFlow.coupon_discount)
async def coupon_create_discount(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    pct, err = validate_discount(message.text)
    if err:
        await message.answer(err)
        return
    await state.update_data(c_pct=pct)
    await state.set_state(AdminFlow.coupon_max_uses)
    await message.answer("Enter max number of uses:", reply_markup=input_kb())


@router_admin.message(AdminFlow.coupon_max_uses)
async def coupon_create_max_uses(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    try:
        max_uses = int(message.text.strip())
        assert max_uses > 0
    except (ValueError, AssertionError):
        await message.answer("❌ Enter a positive integer.")
        return
    await state.update_data(c_max=max_uses)
    await state.set_state(AdminFlow.coupon_expiry)
    await message.answer("Enter validity in days (e.g. 30):", reply_markup=input_kb())


@router_admin.message(AdminFlow.coupon_expiry)
async def coupon_create_expiry(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, HOME_BTN):
        await _back_to_coupons(message, state)
        return
    try:
        days = int(message.text.strip())
        assert days > 0
    except (ValueError, AssertionError):
        await message.answer("❌ Enter a positive number of days.")
        return
    data       = await state.get_data()
    expires_at = int(time.time()) + days * 86400
    c_code = data.get("c_code", "")
    c_pct  = data.get("c_pct", 0)
    c_max  = data.get("c_max", 1)
    await create_coupon(c_code, c_pct, c_max, expires_at)
    await message.answer(
        f"✅ <b>Coupon Created!</b>\n{_SEP}\n"
        f"Code: <code>{c_code}</code>\n"
        f"Discount: <b>{c_pct:.0f}%</b>\n"
        f"Max Uses: <b>{c_max}</b>\n"
        f"Valid for: <b>{days} days</b>",
    )
    await _back_to_coupons(message, state)


async def _back_to_coupons(message: Message, state: FSMContext):
    coupons = await get_all_coupons()
    dm = build_coupons_dm(coupons)
    await state.update_data(coupons=coupons, coupons_dm=dm)
    await state.set_state(AdminFlow.coupons_list)
    await message.answer("🎟 <b>Coupons</b>", reply_markup=admin_coupons_kb(coupons))


# ── Export Mail Orders ─────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_EXPORT)
async def admin_export_orders(message: Message):
    _init_mail_shop_file()

    if not MAIL_SHOP_FILE.exists():
        await message.answer("📋 No mail orders file found yet.", reply_markup=admin_main_kb())
        return

    wb = openpyxl.load_workbook(str(MAIL_SHOP_FILE))
    ws = wb.active
    total_rows = ws.max_row - 1  # subtract header

    if total_rows <= 0:
        await message.answer("📋 No mail orders recorded yet.", reply_markup=admin_main_kb())
        return

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    await message.answer_document(
        document=BufferedInputFile(buf.read(), filename="My_Mail_Shop_Orders.xlsx"),
        caption=(
            f"📋 <b>My Mail Shop Orders</b>\n{_SEP}\n"
            f"📦 Total Orders: <b>{total_rows}</b>\n"
            f"🗓 Updated: {time.strftime('%d %b %Y %H:%M')} UTC"
        ),
        reply_markup=admin_main_kb(),
    )


# ── Broadcast ──────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_BROADCAST)
async def admin_broadcast_start(message: Message, state: FSMContext):
    await state.set_state(AdminFlow.broadcast)
    await message.answer(
        f"📢 <b>Broadcast</b>\n{_SEP}\n"
        f"Send a text message or photo+caption.\nIt will be sent to ALL users.\n\n"
        f"Press {BACK_BTN} to cancel.",
        reply_markup=_kb([BACK_BTN, HOME_BTN]),
    )


@router_admin.message(AdminFlow.broadcast)
async def receive_broadcast(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("❌ Cancelled.", reply_markup=admin_main_kb())
        return
    if not message.text and not message.photo:
        await message.answer("❌ Send text or a photo with caption.")
        return
    await state.set_state(AdminFlow.menu)
    users  = await get_all_users()
    uids   = list(users.keys())
    status = await message.answer(f"📢 Broadcasting to <b>{len(uids)}</b> users…")
    sent = failed = 0
    for uid_str in uids:
        try:
            uid = int(uid_str)
            if message.photo:
                await message.bot.send_photo(uid, photo=message.photo[-1].file_id, caption=message.caption or "")
            else:
                await message.bot.send_message(uid, message.text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    try:
        await status.edit_text(
            f"📢 <b>Broadcast Complete!</b>\n{_SEP}\n✅ Sent: <b>{sent}</b>\n❌ Failed: <b>{failed}</b>"
        )
    except Exception:
        await message.answer(
            f"📢 <b>Broadcast Complete!</b>\n{_SEP}\n✅ Sent: <b>{sent}</b>\n❌ Failed: <b>{failed}</b>"
        )
    await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())


# ── Settings ───────────────────────────────────────────────────────

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_SETTINGS)
async def admin_settings(message: Message, state: FSMContext):
    settings = await get_settings()
    await state.set_state(AdminFlow.settings_menu)
    await message.answer(fmt_settings(settings), reply_markup=admin_settings_kb())


@router_admin.message(AdminFlow.settings_menu)
async def admin_settings_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())
        return
    info = SETTINGS_MAP.get(message.text)
    if not info:
        await message.answer("❌ Select from keyboard.")
        return
    key, type_, prompt = info
    await state.update_data(s_key=key, s_type=type_.__name__)
    await state.set_state(AdminFlow.settings_edit)
    await message.answer(
        f"⚙️ <b>{message.text}</b>\n{_SEP}\n{prompt}\n\n<i>Send blank to clear this value.</i>",
        reply_markup=input_kb(),
    )


@router_admin.message(AdminFlow.settings_edit)
async def receive_setting(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        settings = await get_settings()
        await state.set_state(AdminFlow.settings_menu)
        await message.answer(fmt_settings(settings), reply_markup=admin_settings_kb())
        return
    data      = await state.get_data()
    key       = data.get("s_key", "")
    type_name = data.get("s_type", "str")
    raw       = message.text.strip()
    if type_name == "float" and raw:
        try:
            value: Any = float(raw)
        except ValueError:
            await message.answer("❌ Enter a valid number.")
            return
        if key == "usd_rate" and value <= 0:
            await message.answer("❌ USD rate must be greater than 0.")
            return
        if key in ("bkash_min", "nagad_min", "binance_min") and value < 0:
            await message.answer("❌ Minimum deposit cannot be negative.")
            return
        if key == "referral_bonus_pct" and not (0 <= value <= 100):
            await message.answer("❌ Bonus % must be between 0 and 100.")
            return
    else:
        value = raw
    await update_settings({key: value})
    settings = await get_settings()
    await state.set_state(AdminFlow.settings_menu)
    await message.answer(
        f"✅ <b>Updated!</b>  {key} → <code>{value or '(cleared)'}</code>\n\n" + fmt_settings(settings),
        reply_markup=admin_settings_kb(),
    )


# ══════════════════════════════════════════════════════════════════
# ADMIN — Proxy Data Packages Manager
# ══════════════════════════════════════════════════════════════════

def _pkg_options(settings: dict) -> list:
    raw = settings.get("proxy_data_options", "1 GB,5 GB,10 GB,50 GB")
    return [o.strip() for o in raw.split(",") if o.strip()]

def _pkg_summary(options: list) -> str:
    if not options:
        return "<i>No packages set. Add one below.</i>"
    lines = "\n".join(f"  • <b>{o}</b>" for o in options)
    return lines

@router_admin.message(AdminFlow.menu, F.text == BTN_ADM_PROXY_PKGS)
async def admin_proxy_pkgs(message: Message, state: FSMContext):
    settings = await get_settings()
    opts = _pkg_options(settings)
    await state.set_state(AdminFlow.proxy_pkg_list)
    await message.answer(
        f"📡 <b>Proxy Data Packages</b>\n{_SEP}\n"
        f"Current packages:\n{_pkg_summary(opts)}\n\n"
        f"Tap 🗑 <b>a package</b> to remove it, or ➕ <b>Add Package</b> to add new.",
        reply_markup=proxy_pkg_manage_kb(opts),
    )


@router_admin.message(AdminFlow.proxy_pkg_list)
async def proxy_pkg_list_action(message: Message, state: FSMContext):
    if message.text in (BACK_BTN, HOME_BTN):
        await state.set_state(AdminFlow.menu)
        await message.answer("🔐 <b>Admin Panel</b>", reply_markup=admin_main_kb())
        return

    if message.text == BTN_PKG_ADD:
        await state.set_state(AdminFlow.proxy_pkg_add)
        await message.answer(
            f"📡 <b>Add Data Package</b>\n{_SEP}\n"
            f"Enter the data size to add:\n"
            f"<i>Examples: 1 GB · 5 GB · 500 MB · 2.5 GB</i>",
            reply_markup=input_kb(),
        )
        return

    if message.text.startswith("🗑 "):
        label = message.text[2:].strip()
        settings = await get_settings()
        opts = _pkg_options(settings)
        if label in opts:
            opts.remove(label)
            await update_settings({"proxy_data_options": ",".join(opts)})
        settings = await get_settings()
        opts = _pkg_options(settings)
        await message.answer(
            f"🗑 <b>Removed:</b> {label}\n\n"
            f"📡 <b>Current packages:</b>\n{_pkg_summary(opts)}",
            reply_markup=proxy_pkg_manage_kb(opts),
        )
        return

    await message.answer("❌ Tap a package to remove, or ➕ Add Package.")


@router_admin.message(AdminFlow.proxy_pkg_add)
async def proxy_pkg_add_input(message: Message, state: FSMContext):
    if message.text in (CANCEL_BTN, BACK_BTN, HOME_BTN):
        settings = await get_settings()
        opts = _pkg_options(settings)
        await state.set_state(AdminFlow.proxy_pkg_list)
        await message.answer(
            f"📡 <b>Proxy Data Packages</b>\n{_SEP}\n"
            f"Current packages:\n{_pkg_summary(opts)}",
            reply_markup=proxy_pkg_manage_kb(opts),
        )
        return

    raw = message.text.strip()
    amount, err = parse_data_amount(raw)
    if err or not amount:
        await message.answer(
            f"❌ Invalid format.\nEnter like: <code>5 GB</code> or <code>500 MB</code>",
            reply_markup=input_kb(),
        )
        return

    unit = "MB" if "MB" in raw.upper() else "GB"
    label = f"{int(amount)} {unit}" if amount == int(amount) else f"{amount} {unit}"

    settings = await get_settings()
    opts = _pkg_options(settings)
    if label in opts:
        await message.answer(f"⚠️ <b>{label}</b> is already in the list.", reply_markup=input_kb())
        return

    opts.append(label)
    await update_settings({"proxy_data_options": ",".join(opts)})
    settings = await get_settings()
    opts = _pkg_options(settings)
    await state.set_state(AdminFlow.proxy_pkg_list)
    await message.answer(
        f"✅ <b>Added:</b> {label}\n\n"
        f"📡 <b>Current packages:</b>\n{_pkg_summary(opts)}",
        reply_markup=proxy_pkg_manage_kb(opts),
    )


# ══════════════════════════════════════════════════════════════════
# DISPATCHER
# ══════════════════════════════════════════════════════════════════

def build_dp() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(AntiSpamMiddleware())
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())   # FIX: apply to callbacks too

    dp.include_router(router_global)   # HOME first — highest priority
    dp.include_router(router_admin)    # Admin before user so AdminFlow states take priority
    dp.include_router(router_start)
    dp.include_router(router_mail)
    dp.include_router(router_vpn)
    dp.include_router(router_proxy)
    dp.include_router(router_deposit)
    dp.include_router(router_tempmail)
    return dp


# ══════════════════════════════════════════════════════════════════
# STARTUP / SHUTDOWN
# ══════════════════════════════════════════════════════════════════

async def on_startup(bot: Bot) -> None:
    if WEBHOOK_URL:
        full = f"{WEBHOOK_URL.rstrip('/')}{WEBHOOK_PATH}"
        await bot.set_webhook(full)
        logger.info("Webhook → %s", full)
    else:
        await bot.delete_webhook()
        logger.info("Polling mode active")
    me = await bot.get_me()
    logger.info("@%s (id=%s) is online ✅", me.username, me.id)


async def on_shutdown(bot: Bot) -> None:
    if WEBHOOK_URL:
        await bot.delete_webhook()
    logger.info("Bot shut down.")


# ══════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════

def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp  = build_dp()

    if WEBHOOK_URL:
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)
        app = web.Application()
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        logger.info("Webhook server %s:%s%s", WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_PATH)
        web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
    else:
        asyncio.run(_poll(dp, bot))


async def _poll(dp: Dispatcher, bot: Bot) -> None:
    await on_startup(bot)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await on_shutdown(bot)


if __name__ == "__main__":
    main()
