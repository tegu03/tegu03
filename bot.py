import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import json
from datetime import datetime, timedelta

# Impor konfigurasi
from config import TOKEN, CHAT_ID

# Data transaksi dan saldo (bisa disimpan dalam file atau database)
data = {
    'saldo': {
        'BCA_teguh': 0,
        'BCA_tata': 0,
        'Neo': 0,
        'Bibit': 0,
        'Dompet': 0,
        'Gopay': 0,
    },
    'transaksi': [],
}

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Fungsi untuk menyimpan data
def save_data():
    with open("data.json", "w") as file:
        json.dump(data, file)

# Fungsi untuk memuat data
def load_data():
    try:
        with open("data.json", "r") as file:
            global data
            data = json.load(file)
    except FileNotFoundError:
        save_data()

# Fungsi untuk mengirim pesan ke grup Telegram
def send_message_to_chat(message: str):
    updater.bot.send_message(chat_id=CHAT_ID, text=message)

# Fungsi untuk menambah saldo (uang masuk)
async def tambah_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        akun = context.args[0]  # BCA_teguh, BCA_tata, dsb.
        jumlah = int(context.args[1])
        
        if akun in data['saldo']:
            data['saldo'][akun] += jumlah
            data['transaksi'].append({
                'tipe': 'masuk',
                'akun': akun,
                'jumlah': jumlah,
                'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_data()
            await update.message.reply_text(f'Saldo {akun} berhasil ditambah sebesar Rp{jumlah:,}!')
        else:
            await update.message.reply_text('Akun tidak valid!')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /tambah <akun> <jumlah>')

# Fungsi untuk mengurangi saldo (uang keluar)
async def kurang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        akun = context.args[0]  # BCA_teguh, BCA_tata, dsb.
        jumlah = int(context.args[1])

        if akun in data['saldo'] and data['saldo'][akun] >= jumlah:
            data['saldo'][akun] -= jumlah
            data['transaksi'].append({
                'tipe': 'keluar',
                'akun': akun,
                'jumlah': jumlah,
                'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_data()
            await update.message.reply_text(f'Saldo {akun} berhasil dikurangi sebesar Rp{jumlah:,}!')
        else:
            await update.message.reply_text('Saldo tidak cukup atau akun tidak valid!')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /kurang <akun> <jumlah>')

# Fungsi untuk melihat detail transaksi masuk berdasarkan periode
async def detail_masuk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        periode = context.args[0]  # 'harian', 'mingguan', 'bulanan'
        now = datetime.now()
        
        if periode == 'harian':
            filtered = [t for t in data['transaksi'] if t['tipe'] == 'masuk' and t['tanggal'].startswith(now.strftime('%Y-%m-%d'))]
        elif periode == 'mingguan':
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            filtered = [t for t in data['transaksi'] if t['tipe'] == 'masuk' and week_start.strftime('%Y-%m-%d') <= t['tanggal'][:10] <= week_end.strftime('%Y-%m-%d')]
        elif periode == 'bulanan':
            filtered = [t for t in data['transaksi'] if t['tipe'] == 'masuk' and t['tanggal'][:7] == now.strftime('%Y-%m')]
        else:
            await update.message.reply_text('Periode tidak valid! Gunakan: harian, mingguan, atau bulanan.')
            return

        total_masuk = sum(t['jumlah'] for t in filtered)
        await update.message.reply_text(f'Total Uang Masuk ({periode}): Rp{total_masuk:,}')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /detail_masuk <periode>')

# Fungsi untuk melihat total saldo dan masing-masing akun
async def saldo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    total_saldo = sum(data['saldo'].values())
    saldo_message = f'Total Saldo: Rp{total_saldo:,}\n\n'
    for akun, saldo in data['saldo'].items():
        saldo_message += f'{akun}: Rp{saldo:,}\n'
    await update.message.reply_text(saldo_message)

# Fungsi untuk memeriksa pengeluaran lebih dari 300.000
def check_hemat():
    total_hari_ini = sum(t['jumlah'] for t in data['transaksi'] if t['tipe'] == 'keluar')
    if total_hari_ini > 300000:
        send_message_to_chat("Hemat - Hemat Jangan Borosss !!! 😡")

# Fungsi untuk menghapus transaksi
async def hapus_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        transaction_id = int(context.args[0])
        if transaction_id < len(data['transaksi']):
            del data['transaksi'][transaction_id]
            save_data()
            await update.message.reply_text(f'Transaksi dengan ID {transaction_id} berhasil dihapus!')
        else:
            await update.message.reply_text('ID transaksi tidak valid!')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /hapus <id>')

# Fungsi untuk transfer saldo antar akun
async def transfer_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        dari = context.args[0]
        ke = context.args[1]
        jumlah = int(context.args[2])

        if dari in data['saldo'] and ke in data['saldo'] and data['saldo'][dari] >= jumlah:
            data['saldo'][dari] -= jumlah
            data['saldo'][ke] += jumlah
            data['transaksi'].append({
                'tipe': 'transfer',
                'dari': dari,
                'ke': ke,
                'jumlah': jumlah,
                'tanggal': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_data()
            await update.message.reply_text(f'Transfer {jumlah} dari {dari} ke {ke} berhasil!')
        else:
            await update.message.reply_text('Saldo tidak cukup atau akun tidak valid!')
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /transfer <dari> <ke> <jumlah>')

# Fungsi utama untuk menjalankan bot
async def main():
    load_data()
    
    # Membuat aplikasi dan dispatcher
    application = Application.builder().token(TOKEN).build()

    # Menambahkan handler untuk setiap perintah
    application.add_handler(CommandHandler("start", lambda update, context: update.message.reply_text("Selamat datang di Bot Laporan Keuangan!")))
    application.add_handler(CommandHandler("tambah", tambah_command))
    application.add_handler(CommandHandler("kurang", kurang_command))
    application.add_handler(CommandHandler("detail_masuk", detail_masuk_command))
    application.add_handler(CommandHandler("saldo", saldo_command))
    application.add_handler(CommandHandler("hapus", hapus_command))
    application.add_handler(CommandHandler("transfer", transfer_command))

    # Memulai polling
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
