from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Token dan chat_id bot Telegram Anda
TOKEN = "7959222765:AAF42lZVxYhZqkOW2BsjtK6CdpkG0zEtPdQ"
CHAT_ID = "-1002278563937"

# Data saldo dan transaksi
data = {
    'saldo': {
        'BCA Teguh': 0,
        'BCA Tata': 0,
        'Bank Neo': 0,
        'Bibit': 0,
        'Dompet': 0,
        'Gopay': 0
    },
    'transaksi': []
}

# Fungsi untuk menambahkan saldo
async def tambah_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        jumlah = int(context.args[0])
        akun = context.args[1]
        if akun in data['saldo']:
            data['saldo'][akun] += jumlah
            await update.message.reply_text(f'{jumlah} berhasil ditambahkan ke {akun}.')
        else:
            await update.message.reply_text('Akun tidak ditemukan!')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /tambah <jumlah> <akun>')

# Fungsi untuk mengurangi saldo
async def kurang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        jumlah = int(context.args[0])
        akun = context.args[1]
        if akun in data['saldo'] and data['saldo'][akun] >= jumlah:
            data['saldo'][akun] -= jumlah
            await update.message.reply_text(f'{jumlah} berhasil dikeluarkan dari {akun}.')
        else:
            await update.message.reply_text('Saldo tidak cukup atau akun tidak ditemukan!')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /kurang <jumlah> <akun>')

# Fungsi untuk menampilkan saldo
async def saldo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    total_saldo = sum(data['saldo'].values())
    saldo_text = f"Total saldo seluruh akun: {total_saldo} IDR\n\n"
    for akun, saldo in data['saldo'].items():
        saldo_text += f"{akun}: {saldo} IDR\n"
    await update.message.reply_text(saldo_text)

# Fungsi untuk transfer saldo antar akun
async def transfer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        dari = context.args[0]
        ke = context.args[1]
        jumlah = int(context.args[2])
        if dari in data['saldo'] and ke in data['saldo'] and data['saldo'][dari] >= jumlah:
            data['saldo'][dari] -= jumlah
            data['saldo'][ke] += jumlah
            await update.message.reply_text(f'Transfer {jumlah} dari {dari} ke {ke} berhasil!')
        else:
            await update.message.reply_text('Saldo tidak cukup atau akun tidak ditemukan!')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /transfer <dari> <ke> <jumlah>')

# Fungsi untuk menghapus transaksi
async def hapus_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        id_transaksi = int(context.args[0])
        if 0 <= id_transaksi < len(data['transaksi']):
            del data['transaksi'][id_transaksi]
            await update.message.reply_text(f'Transaksi ID {id_transaksi} berhasil dihapus!')
        else:
            await update.message.reply_text('ID transaksi tidak valid!')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /hapus <id>')

# Fungsi untuk memfilter transaksi
async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        tipe = context.args[0]
        tanggal = context.args[1]
        filtered = [t for t in data['transaksi'] if t['tipe'] == tipe and t['tanggal'] == tanggal]
        if filtered:
            response = "\n".join([f"{t['tanggal']} - {t['tipe']} - {t['jumlah']} IDR" for t in filtered])
            await update.message.reply_text(response)
        else:
            await update.message.reply_text('Tidak ada transaksi yang ditemukan untuk filter tersebut.')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /filter <tipe> <tanggal>')

# Fungsi untuk memeriksa apakah total pengeluaran lebih dari 300.000
def check_hemat():
    total_hari_ini = sum(t['jumlah'] for t in data['transaksi'] if t['tipe'] == 'keluar')
    if total_hari_ini > 300000:
        return "Hemat - Hemat Jangan Borosss !!! 😡"
    return None

# Fungsi utama untuk menjalankan bot
async def main():
    application = Application.builder().token(TOKEN).build()

    # Menambahkan handler untuk setiap command
    application.add_handler(CommandHandler("tambah", tambah_command))
    application.add_handler(CommandHandler("kurang", kurang_command))
    application.add_handler(CommandHandler("saldo", saldo_command))
    application.add_handler(CommandHandler("transfer", transfer_command))
    application.add_handler(CommandHandler("hapus", hapus_command))
    application.add_handler(CommandHandler("filter", filter_command))

    # Menjalankan polling
    await application.run_polling()

# Menjalankan bot
if __name__ == "__main__":
    import asyncio
from telegram.ext import Application

async def main():
    # Inisialisasi aplikasi telegram bot Anda di sini
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Daftarkan handler Anda
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Mulai polling
    await application.run_polling()

if __name__ == '__main__':
    # Langsung jalankan loop tanpa asyncio.run
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

