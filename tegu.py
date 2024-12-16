import json
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
    if transaction['type'] == 'masuk':
        data['balances']['bca'] += transaction['amount']
    elif transaction['type'] == 'keluar':
        needed_amount = abs(transaction['amount'])
        for category in ['bca', 'neo', 'gopay', 'wallet']:
            if data['balances'][category] >= needed_amount:
                data['balances'][category] -= needed_amount
                break
            else:
                needed_amount -= data['balances'][category]
                data['balances'][category] = 0

    data['balances']['total'] = sum(data['balances'][key] for key in ['bca', 'neo', 'gopay', 'wallet'])
    save_data(data)

# Hapus transaksi
def delete_transaction(data, index):
    if 0 <= index < len(data['transactions']):
        transaction = data['transactions'].pop(index)
        if transaction['type'] == 'masuk':
            data['balances']['bca'] -= transaction['amount']
        elif transaction['type'] == 'keluar':
            needed_amount = abs(transaction['amount'])
            for category in reversed(['wallet', 'gopay', 'neo', 'bca']):
                data['balances'][category] += min(needed_amount, abs(transaction['amount']))
                needed_amount -= abs(transaction['amount'])
                if needed_amount <= 0:
                    break

        data['balances']['total'] = sum(data['balances'][key] for key in ['bca', 'neo', 'gopay', 'wallet'])
        save_data(data)
        return True
    return False

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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr"Halo, {user.mention_markdown_v2()}\! Saya adalah bot pengelola keuangan Anda\.\n\nKetik /help untuk melihat perintah yang tersedia\."
    )

# Command help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/add <masuk/keluar> <jumlah> <kategori> - Menambahkan transaksi\n"
        "/report - Menampilkan laporan keuangan\n"
        "/balance - Menampilkan saldo saat ini\n"
        "/filter <kategori> - Menampilkan transaksi berdasarkan kategori\n"
        "/add_balance <kategori> <jumlah> - Menambahkan saldo ke kategori tertentu\n"
        "/delete <index> - Menghapus transaksi berdasarkan nomor urut"
    )

# Tambah transaksi
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        command_args = context.args
        if len(command_args) < 3:
            await update.message.reply_text("Format salah. Gunakan: /add <masuk/keluar> <jumlah> <kategori>")
            return

        direction = command_args[0].lower()
        amount = int(command_args[1])
        category = command_args[2].lower()

        if direction not in ["masuk", "keluar"]:
            await update.message.reply_text("Transaksi harus 'masuk' atau 'keluar'.")
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
            await update.message.reply_text(notification)

        await update.message.reply_text(f"Transaksi berhasil ditambahkan: {direction} {abs(amount)} untuk {category}.")
    except ValueError:
        await update.message.reply_text("Jumlah harus berupa angka.")

# Tambah saldo ke kategori tertentu
async def add_balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        command_args = context.args
        if len(command_args) < 2:
            await update.message.reply_text("Format salah. Gunakan: /add_balance <kategori> <jumlah>")
            return

        category = command_args[0].lower()
        amount = int(command_args[1])

        if category not in ["investment", "bca", "neo", "gopay", "wallet"]:
            await update.message.reply_text("Kategori tidak valid. Pilih salah satu: investment, bca, neo, gopay, wallet.")
            return

        # Update saldo kategori
        data['balances'][category] += amount
        save_data(data)

        await update.message.reply_text(f"Saldo {category.capitalize()} berhasil ditambahkan sebesar Rp {amount}.")
    except ValueError:
        await update.message.reply_text("Jumlah harus berupa angka.")

# Hapus transaksi
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        command_args = context.args
        if len(command_args) < 1:
            await update.message.reply_text("Format salah. Gunakan: /delete <index>")
            return

        index = int(command_args[0]) - 1

        if delete_transaction(data, index):
            await update.message.reply_text(f"Transaksi nomor {index + 1} berhasil dihapus.")
        else:
            await update.message.reply_text("Index transaksi tidak valid.")
    except ValueError:
        await update.message.reply_text("Index harus berupa angka.")

# Laporan keuangan
async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    transactions = data['transactions']
    if not transactions:
        await update.message.reply_text("Belum ada transaksi.")
        return

    report = "Laporan Keuangan:\n"
    for i, t in enumerate(transactions, start=1):
        report += f"{i}. {t['date']}: {t['type']} {abs(t['amount'])} untuk {t['category']}\n"

    await update.message.reply_text(report)

# Saldo saat ini
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    await update.message.reply_text(balance_report)

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Data transaksi contoh
data = {
    'transactions': [
        {'category': 'makanan', 'date': '2024-12-01', 'type': 'debit', 'amount': 50000},
        {'category': 'transportasi', 'date': '2024-12-02', 'type': 'debit', 'amount': 20000},
        {'category': 'makanan', 'date': '2024-12-03', 'type': 'debit', 'amount': 15000},
        {'category': 'hiburan', 'date': '2024-12-04', 'type': 'debit', 'amount': 100000},
    ]
}

# Fungsi untuk memfilter transaksi berdasarkan kategori
async def filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        # Ambil kategori dari argumen
        category = context.args[0].lower()
        
        # Filter transaksi berdasarkan kategori
        transactions = [t for t in data['transactions'] if t['category'] == category]
        
        # Jika tidak ada transaksi untuk kategori yang diberikan
        if not transactions:
            await update.message.reply_text(f"Belum ada transaksi untuk kategori {category}.")
            return
        
        # Membuat laporan transaksi
        report = f"Transaksi {category.capitalize()}:\n"
        for i, t in enumerate(transactions, start=1):
            report += f"{i}. {t['date']}: {t['type']} {abs(t['amount'])}\n"
        
        # Kirim laporan transaksi
        await update.message.reply_text(report)
    
    except IndexError:
        await update.message.reply_text("Format salah. Gunakan: /filter <kategori>")

# Fungsi untuk menjalankan bot
def main():
    # Inisialisasi aplikasi bot dengan token
    application = Application.builder().token("7959222765:AAF42lZVxYhZqkOW2BsjtK6CdpkG0zEtPdQ").build()

    # Menambahkan handler untuk berbagai perintah
    application.add_handler(CommandHandler("start", start))  # Anda bisa menambahkan fungsi start
    application.add_handler(CommandHandler("help", help_command))  # Anda bisa menambahkan fungsi help_command
    application.add_handler(CommandHandler("add", add_command))  # Anda bisa menambahkan fungsi add_command
    application.add_handler(CommandHandler("add_balance", add_balance_command))  # Anda bisa menambahkan fungsi add_balance_command
    application.add_handler(CommandHandler("delete", delete_command))  # Anda bisa menambahkan fungsi delete_command
    application.add_handler(CommandHandler("report", report_command))  # Anda bisa menambahkan fungsi report_command
    application.add_handler(CommandHandler("balance", balance_command))  # Anda bisa menambahkan fungsi balance_command
    application.add_handler(CommandHandler("filter", filter_command))  # Menambahkan filter_command

    # Menjalankan aplikasi bot dengan polling
    application.run_polling()

# Menjalankan bot
if __name__ == "__main__":
    main()

