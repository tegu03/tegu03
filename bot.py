import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Data dummy untuk akun dan transaksi
data = {
    "BCA_Teguh": 0,
    "BCA_Tata": 0,
    "Bank_Neo": 0,
    "Bibit": 0,
    "Dompet": 0,
    "Gopay": 0,
    "transaksi": []
}

# Fungsi untuk menyimpan data (misalnya ke file)
def save_data():
    # Anda bisa menyimpan data ke file seperti JSON atau database
    pass

# Fungsi untuk menampilkan saldo seluruh akun
async def saldo_command(update: Update, context: CallbackContext) -> None:
    total_saldo = sum(data[key] for key in data if key != "transaksi")
    saldo_text = f"Total Saldo Seluruh Akun: Rp{total_saldo}\n\n"
    for akun, saldo in data.items():
        if akun != "transaksi":
            saldo_text += f"{akun}: Rp{saldo}\n"
    await update.message.reply_text(saldo_text)

# Fungsi untuk menambah uang ke saldo BCA (Teguh/Tata)
async def tambah_command(update: Update, context: CallbackContext) -> None:
    try:
        akun = context.args[0]
        jumlah = int(context.args[1])
        if akun in data and jumlah > 0:
            data[akun] += jumlah
            save_data()
            await update.message.reply_text(f"Rp{jumlah} berhasil ditambahkan ke {akun}. Saldo saat ini: Rp{data[akun]}")
        else:
            await update.message.reply_text("Akun tidak ditemukan atau jumlah tidak valid.")
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /tambah <akun> <jumlah>')

# Fungsi untuk mengurangi uang dari saldo BCA (Teguh/Tata)
async def kurang_command(update: Update, context: CallbackContext) -> None:
    try:
        akun = context.args[0]
        jumlah = int(context.args[1])
        if akun in data and data[akun] >= jumlah:
            data[akun] -= jumlah
            save_data()
            await update.message.reply_text(f"Rp{jumlah} berhasil dikurangi dari {akun}. Saldo saat ini: Rp{data[akun]}")
        else:
            await update.message.reply_text("Saldo tidak cukup atau akun tidak ditemukan.")
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /kurang <akun> <jumlah>')

# Fungsi untuk menampilkan detail transaksi masuk dan keluar
async def detail_command(update: Update, context: CallbackContext) -> None:
    # Menampilkan transaksi masuk dan keluar berdasarkan kategori
    kategori = context.args[0] if context.args else "semua"
    transaksi_text = "Detail Transaksi:\n"
    for t in data['transaksi']:
        if kategori == "semua" or t['tipe'] == kategori:
            transaksi_text += f"{t['tipe']} - {t['akun']} - Rp{t['jumlah']} - {t['waktu']}\n"
    await update.message.reply_text(transaksi_text)

# Fungsi untuk mencatat transaksi masuk
async def masuk_command(update: Update, context: CallbackContext) -> None:
    try:
        akun = context.args[0]
        jumlah = int(context.args[1])
        if akun in data:
            data['transaksi'].append({
                'tipe': 'masuk',
                'akun': akun,
                'jumlah': jumlah,
                'waktu': 'sekarang'  # Anda bisa menggunakan waktu yang sebenarnya di sini
            })
            data[akun] += jumlah
            save_data()
            await update.message.reply_text(f"Rp{jumlah} masuk ke {akun}. Saldo saat ini: Rp{data[akun]}")
        else:
            await update.message.reply_text("Akun tidak ditemukan.")
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /masuk <akun> <jumlah>')

# Fungsi untuk mencatat transaksi keluar
async def keluar_command(update: Update, context: CallbackContext) -> None:
    try:
        akun = context.args[0]
        jumlah = int(context.args[1])
        if akun in data and data[akun] >= jumlah:
            data['transaksi'].append({
                'tipe': 'keluar',
                'akun': akun,
                'jumlah': jumlah,
                'waktu': 'sekarang'
            })
            data[akun] -= jumlah
            save_data()
            await update.message.reply_text(f"Rp{jumlah} keluar dari {akun}. Saldo saat ini: Rp{data[akun]}")
        else:
            await update.message.reply_text("Saldo tidak cukup atau akun tidak ditemukan.")
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /keluar <akun> <jumlah>')

# Fungsi untuk transfer saldo antar akun
async def transfer_command(update: Update, context: CallbackContext) -> None:
    try:
        dari = context.args[0]
        ke = context.args[1]
        jumlah = int(context.args[2])
        if dari in data and ke in data and data[dari] >= jumlah:
            data[dari] -= jumlah
            data[ke] += jumlah
            data['transaksi'].append({
                'tipe': 'transfer',
                'akun': dari + ' -> ' + ke,
                'jumlah': jumlah,
                'waktu': 'sekarang'
            })
            save_data()
            await update.message.reply_text(f"Transfer Rp{jumlah} dari {dari} ke {ke} berhasil!")
        else:
            await update.message.reply_text("Saldo tidak cukup atau akun tidak ditemukan.")
    except (IndexError, ValueError):
        await update.message.reply_text('Format salah. Gunakan: /transfer <dari> <ke> <jumlah>')

# Fungsi utama untuk menjalankan bot
async def main():
    application = Application.builder().token("7959222765:AAF42lZVxYhZqkOW2BsjtK6CdpkG0zEtPdQ").build()

    # Menambahkan handler untuk berbagai perintah
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("saldo", saldo_command))
    application.add_handler(CommandHandler("tambah", tambah_command))
    application.add_handler(CommandHandler("kurang", kurang_command))
    application.add_handler(CommandHandler("masuk", masuk_command))
    application.add_handler(CommandHandler("keluar", keluar_command))
    application.add_handler(CommandHandler("transfer", transfer_command))
    application.add_handler(CommandHandler("detail", detail_command))

    # Menjalankan polling
    await application.run_polling()

# Fungsi yang dijalankan saat bot dimulai
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Selamat datang di Bot Laporan Keuangan!")

# Fungsi yang dijalankan saat help diminta
async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """
    Berikut adalah perintah yang bisa digunakan:
    /start - Memulai percakapan dengan bot
    /saldo - Menampilkan saldo seluruh akun
    /tambah - Menambahkan saldo ke akun
    /kurang - Mengurangi saldo dari akun
    /masuk - Mencatat uang masuk
    /keluar - Mencatat uang keluar
    /transfer - Transfer saldo antar akun
    /detail - Menampilkan detail transaksi
    """
    await update.message.reply_text(help_text)

if __name__ == '__main__':
    from telegram.ext import Application

    application = Application.builder().token("7959222765:AAF42lZVxYhZqkOW2BsjtK6CdpkG0zEtPdQ").build()

    # Menambahkan handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("saldo", saldo_command))
    application.add_handler(CommandHandler("tambah", tambah_command))
    application.add_handler(CommandHandler("kurang", kurang_command))
    application.add_handler(CommandHandler("masuk", masuk_command))
    application.add_handler(CommandHandler("keluar", keluar_command))
    application.add_handler(CommandHandler("transfer", transfer_command))
    application.add_handler(CommandHandler("detail", detail_command))

    # Menjalankan bot
    application.run_polling()

