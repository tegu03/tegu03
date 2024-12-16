import json
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# File untuk menyimpan data keuangan
data_file = 'financial_data.json'

# Inisialisasi data jika file belum ada
def initialize_data():
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        data = {
            "transactions": [],
            "balances": {
                "total": 0,
                "investment": 0,
                "bca": 0,
                "neo": 0,
                "gopay": 0,
                "wallet": 0
            }
        }
        with open(data_file, 'w') as file:
            json.dump(data, file)
        return data

# Simpan data ke file
def save_data(data):
    with open(data_file, 'w') as file:
        json.dump(data, file)

# Tambahkan transaksi
def add_transaction(data, transaction):
    data['transactions'].append(transaction)
    data['balances']['total'] += transaction['amount']
    save_data(data)

# Load data saat bot berjalan
data = initialize_data()

# Periksa transaksi harian melebihi batas tertentu
def check_daily_limit():
    from datetime import datetime

    today = datetime.now().date()
    daily_total = sum(
        t['amount'] for t in data['transactions']
        if datetime.fromisoformat(t['date']).date() == today and t['amount'] < 0
    )

    if abs(daily_total) > 300000:
        return "Hemat hemat jangan boros"
    return None

# Command start
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Halo, {user.mention_markdown_v2()}\! Saya adalah bot pengelola keuangan Anda\.\n\nKetik /help untuk melihat perintah yang tersedia\."
    )

# Command help
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "/add <masuk/keluar> <jumlah> <kategori> - Menambahkan transaksi\n"
        "/report - Menampilkan laporan keuangan\n"
        "/balance - Menampilkan saldo saat ini\n"
        "/filter <kategori> - Menampilkan transaksi berdasarkan kategori"
    )

# Tambah transaksi
def add_command(update: Update, context: CallbackContext) -> None:
    try:
        command_args = context.args
        if len(command_args) < 3:
            update.message.reply_text("Format salah. Gunakan: /add <masuk/keluar> <jumlah> <kategori>")
            return

        direction = command_args[0].lower()
        amount = int(command_args[1])
        category = command_args[2].lower()

        if direction not in ["masuk", "keluar"]:
            update.message.reply_text("Transaksi harus 'masuk' atau 'keluar'.")
            return

        if direction == "keluar":
            amount = -amount

        transaction = {
            "type": direction,
            "amount": amount,
            "category": category,
            "date": update.message.date.isoformat()
        }

        add_transaction(data, transaction)

        # Periksa batas harian
        notification = check_daily_limit()
        if notification:
            update.message.reply_text(notification)

        update.message.reply_text(f"Transaksi berhasil ditambahkan: {direction} {abs(amount)} untuk {category}.")
    except ValueError:
        update.message.reply_text("Jumlah harus berupa angka.")

# Laporan keuangan
def report_command(update: Update, context: CallbackContext) -> None:
    transactions = data['transactions']
    if not transactions:
        update.message.reply_text("Belum ada transaksi.")
        return

    report = "Laporan Keuangan:\n"
    for t in transactions:
        report += f"{t['date']}: {t['type']} {abs(t['amount'])} untuk {t['category']}\n"

    update.message.reply_text(report)

# Saldo saat ini
def balance_command(update: Update, context: CallbackContext) -> None:
    balances = data['balances']
    balance_report = (
        f"Saldo Saat Ini:\n"
        f"Total: Rp {balances['total']}\n"
        f"Investasi: Rp {balances['investment']}\n"
        f"BCA: Rp {balances['bca']}\n"
        f"Neo: Rp {balances['neo']}\n"
        f"Gopay: Rp {balances['gopay']}\n"
        f"Dompet: Rp {balances['wallet']}\n"
    )
    update.message.reply_text(balance_report)

# Filter transaksi berdasarkan kategori
def filter_command(update: Update, context: CallbackContext) -> None:
    try:
        category = context.args[0].lower()
        transactions = [t for t in data['transactions'] if t['category'] == category]

        if not transactions:
            update.message.reply_text(f"Tidak ada transaksi untuk kategori '{category}'.")
            return

        report = f"Transaksi untuk kategori '{category}':\n"
        for t in transactions:
            report += f"{t['date']}: {t['type']} {abs(t['amount'])}\n"

        update.message.reply_text(report)
    except IndexError:
        update.message.reply_text("Gunakan format: /filter <kategori>")

# Main function
def main():
    # Token bot Telegram
    TOKEN = "7959222765:AAF42lZVxYhZqkOW2BsjtK6CdpkG0zEtPdQ"

    # Set up the Updater
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("add", add_command))
    dispatcher.add_handler(CommandHandler("report", report_command))
    dispatcher.add_handler(CommandHandler("balance", balance_command))
    dispatcher.add_handler(CommandHandler("filter", filter_command))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
