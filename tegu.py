import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import sqlite3
from datetime import datetime

# Ganti dengan token bot Telegram yang Anda dapatkan
TOKEN = '7959222765:AAF42lZVxYhZqkOW2BsjtK6CdpkG0zEtPdQ'

# Setup logging untuk debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Koneksi ke database SQLite
def create_db():
    conn = sqlite3.connect('keuangan.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transaksi
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  jenis TEXT,
                  jumlah REAL,
                  keterangan TEXT,
                  tanggal TEXT)''')
    conn.commit()
    conn.close()

def add_transaction(jenis: str, jumlah: float, keterangan: str):
    tanggal = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('keuangan.db')
    c = conn.cursor()
    c.execute("INSERT INTO transaksi (jenis, jumlah, keterangan, tanggal) VALUES (?, ?, ?, ?)",
              (jenis, jumlah, keterangan, tanggal))
    conn.commit()
    conn.close()

def get_summary(period: str):
    conn = sqlite3.connect('keuangan.db')
    c = conn.cursor()
    if period == 'daily':
        query = "SELECT jenis, SUM(jumlah), DATE(tanggal) FROM transaksi GROUP BY jenis, DATE(tanggal)"
    elif period == 'weekly':
        query = "SELECT jenis, SUM(jumlah), strftime('%Y-%W', tanggal) FROM transaksi GROUP BY jenis, strftime('%Y-%W', tanggal)"
    elif period == 'monthly':
        query = "SELECT jenis, SUM(jumlah), strftime('%Y-%m', tanggal) FROM transaksi GROUP BY jenis, strftime('%Y-%m', tanggal)"
    else:
        return "Invalid period"

    c.execute(query)
    result = c.fetchall()
    conn.close()
    return result

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Selamat datang di bot pencatat keuangan!')

async def record_income(update: Update, context: CallbackContext):
    try:
        amount = float(context.args[0])
        description = " ".join(context.args[1:])
        add_transaction('income', amount, description)
        await update.message.reply_text(f'Pemasukan sebesar {amount} telah tercatat.')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah! Gunakan: /income <jumlah> <deskripsi>')

async def record_expense(update: Update, context: CallbackContext):
    try:
        amount = float(context.args[0])
        description = " ".join(context.args[1:])
        add_transaction('expense', amount, description)
        await update.message.reply_text(f'Pengeluaran sebesar {amount} telah tercatat.')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah! Gunakan: /expense <jumlah> <deskripsi>')

async def show_summary(update: Update, context: CallbackContext):
    period = context.args[0] if context.args else 'daily'
    summary = get_summary(period)
    
    if isinstance(summary, str):
        await update.message.reply_text(summary)
        return
    
    response = f"Rangkuman {period.capitalize()}:\n"
    for item in summary:
        response += f"{item[0].capitalize()}: {item[1]} pada {item[2]}\n"
    await update.message.reply_text(response)

def main():
    # Buat database jika belum ada
    create_db()

    # Inisialisasi aplikasi dan dispatcher
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("income", record_income))
    application.add_handler(CommandHandler("expense", record_expense))
    application.add_handler(CommandHandler("summary", show_summary))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
