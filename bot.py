import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize data storage
accounts = {
    "BCA_Teguh": 0,
    "BCA_Tata": 0,
    "Neo": 0,
    "Bibit": 0,
    "Dompet": 0,
    "Gopay": 0
}
transactions = []  # To store transaction history

categories_income = ["Gaji", "Penghasilan Lain Lain"]
categories_expense = [
    "Makan", "Transportasi", "Belanja Mingguan", "Belanja Bulanan", "Service Kendaraan",
    "Biaya Lain - Lain", "Listrik", "PDAM", "Internet", "Hadiah"
]

# Helper functions
def calculate_total_balance():
    return sum(accounts.values())

def add_transaction(transaction):
    transactions.append(transaction)

# Commands
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "\U0001F4B0 Financial Bot Commands:\n"
        "/income <amount> <account> <category> [<date>] - Record an income\n"
        "/expense <amount> <account> <category> [<date>] - Record an expense\n"
        "/transfer <amount> <from_account> <to_account> - Transfer between accounts\n"
        "/balance - Show account balances\n"
        "/transactions - Show transaction history\n"
        "/filter_transactions <category> [<period>] - Filter transactions by category and period\n"
        "/delete_transaction <id> - Delete a transaction\n"
    )

async def income(update: Update, context: CallbackContext):
    try:
        amount = float(context.args[0])
        account = context.args[1]
        category = context.args[2]
        date = context.args[3] if len(context.args) > 3 else datetime.now().strftime('%Y-%m-%d')

        if account in accounts and category in categories_income:
            accounts[account] += amount
            add_transaction({"type": "income", "amount": amount, "account": account, "category": category, "date": date})
            await update.message.reply_text(f"Income of Rp{amount:,.0f} added to {account}. Category: {category}. Date: {date}.")
        else:
            await update.message.reply_text("Invalid account or category.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /income <amount> <account> <category> [<date>]")

async def expense(update: Update, context: CallbackContext):
    try:
        amount = float(context.args[0])
        account = context.args[1]
        category = context.args[2]
        date = context.args[3] if len(context.args) > 3 else datetime.now().strftime('%Y-%m-%d')

        if account in accounts and category in categories_expense:
            if accounts[account] >= amount:
                accounts[account] -= amount
                add_transaction({"type": "expense", "amount": amount, "account": account, "category": category, "date": date})
                await update.message.reply_text(f"Expense of Rp{amount:,.0f} deducted from {account}. Category: {category}. Date: {date}.")
                if amount > 300000:
                    await update.message.reply_text("Hemat - Hemat Jangan Borosss !!! \U0001F621")
            else:
                await update.message.reply_text("Insufficient balance.")
        else:
            await update.message.reply_text("Invalid account or category.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /expense <amount> <account> <category> [<date>]")

async def transfer(update: Update, context: CallbackContext):
    try:
        amount = float(context.args[0])
        from_account = context.args[1]
        to_account = context.args[2]

        if from_account in accounts and to_account in accounts:
            if accounts[from_account] >= amount:
                accounts[from_account] -= amount
                accounts[to_account] += amount
                add_transaction({"type": "transfer", "amount": amount, "from": from_account, "to": to_account, "date": datetime.now().strftime('%Y-%m-%d')})
                await update.message.reply_text(f"Transferred Rp{amount:,.0f} from {from_account} to {to_account}.")
            else:
                await update.message.reply_text("Insufficient balance in source account.")
        else:
            await update.message.reply_text("Invalid accounts.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /transfer <amount> <from_account> <to_account>")

async def balance(update: Update, context: CallbackContext):
    total_balance = calculate_total_balance()
    message = f"\U0001F4B0 Total Balance: Rp{total_balance:,.0f}\n"
    for account, balance in accounts.items():
        message += f"{account}: Rp{balance:,.0f}\n"
    await update.message.reply_text(message)

async def transactions_command(update: Update, context: CallbackContext):
    if not transactions:
        await update.message.reply_text("No transactions found.")
    else:
        message = "\U0001F4DD Transaction History:\n"
        for idx, txn in enumerate(transactions):
            message += f"ID: {idx}, {txn}\n"
        await update.message.reply_text(message)

async def delete_transaction(update: Update, context: CallbackContext):
    try:
        txn_id = int(context.args[0])
        if 0 <= txn_id < len(transactions):
            removed = transactions.pop(txn_id)
            await update.message.reply_text(f"Transaction {txn_id} removed: {removed}")
        else:
            await update.message.reply_text("Invalid transaction ID.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /delete_transaction <id>")

async def filter_transactions(update: Update, context: CallbackContext):
    try:
        category = context.args[0]
        period = context.args[1] if len(context.args) > 1 else "all"

        filtered = [txn for txn in transactions if txn['category'] == category]

        if period != "all":
            if period == "daily":
                today = datetime.now().strftime('%Y-%m-%d')
                filtered = [txn for txn in filtered if txn['date'] == today]
            elif period == "weekly":
                pass  # Add logic for weekly filtering
            elif period == "monthly":
                pass  # Add logic for monthly filtering

        if not filtered:
            await update.message.reply_text("No transactions found for the specified filter.")
        else:
            message = f"\U0001F4C5 Filtered Transactions (Category: {category}, Period: {period}):\n"
            for idx, txn in enumerate(filtered):
                message += f"ID: {idx}, {txn}\n"
            await update.message.reply_text(message)
    except IndexError:
        await update.message.reply_text("Usage: /filter_transactions <category> [<period>]")

# Main function
def main():
    application = Application.builder().token("7959222765:AAF42lZVxYhZqkOW2BsjtK6CdpkG0zEtPdQ").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("income", income))
    application.add_handler(CommandHandler("expense", expense))
    application.add_handler(CommandHandler("transfer", transfer))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("transactions", transactions_command))
    application.add_handler(CommandHandler("delete_transaction", delete_transaction))
    application.add_handler(CommandHandler("filter_transactions", filter_transactions))

    application.run_polling()

if __name__ == "__main__":
    main()
