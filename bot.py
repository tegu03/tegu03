import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import asyncio

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
    "Dompet_Teguh": 0,
    "Dompet_Tata": 0,
    "Gopay_Teguh": 0,
    "Gopay_Tata": 0,
    "Shopee_Teguh": 0,
    "Shopee_Tata": 0
}
transactions = []  # To store transaction history

# Helper functions
def calculate_total_balance():
    return sum(accounts.values())

def add_transaction(detail):
    transactions.append(detail)

# Commands
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Welcome to Financial Bot!\nCommands:\n"
        "/add_account <name> <initial_balance> - Add a new account\n"
        "/income <amount> <account> <category> - Record an income\n"
        "/expense <amount> <account> <category> - Record an expense\n"
        "/transfer <amount> <from_account> <to_account> - Transfer between accounts\n"
        "/balance - Show account balances\n"
        "/transactions - Show transaction history\n"
        "/delete_transaction <id> - Delete a transaction\n"
        "For detailed usage, type /help"
    )

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Detailed usage:\n"
        "/add_account <name> <initial_balance> - Add a new account.\n"
        "/income <amount> <account> <category> - Record an income.\n"
        "/expense <amount> <account> <category> - Record an expense.\n"
        "/transfer <amount> <from_account> <to_account> - Transfer between accounts.\n"
        "/balance - Display account balances.\n"
        "/transactions - Display transaction history.\n"
        "/delete_transaction <id> - Delete a transaction by ID."
    )

async def add_account(update: Update, context: CallbackContext):
    try:
        name = context.args[0]
        initial_balance = float(context.args[1])
        if name in accounts:
            await update.message.reply_text(f"Account {name} already exists.")
        else:
            accounts[name] = initial_balance
            await update.message.reply_text(f"Account {name} added with balance {initial_balance}.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /add_account <name> <initial_balance>")

async def income(update: Update, context: CallbackContext):
    try:
        amount = float(context.args[0])
        account = context.args[1]
        category = " ".join(context.args[2:])
        if account in accounts:
            accounts[account] += amount
            add_transaction({"type": "income", "amount": amount, "account": account, "category": category})
            await update.message.reply_text(f"Income of {amount} added to {account}. Category: {category}.")
        else:
            await update.message.reply_text(f"Account {account} does not exist.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /income <amount> <account> <category>")

async def expense(update: Update, context: CallbackContext):
    try:
        amount = float(context.args[0])
        account = context.args[1]
        category = " ".join(context.args[2:])
        if account in accounts:
            if accounts[account] >= amount:
                accounts[account] -= amount
                add_transaction({"type": "expense", "amount": amount, "account": account, "category": category})
                await update.message.reply_text(f"Expense of {amount} deducted from {account}. Category: {category}.")
                if amount > 300000:
                    await update.message.reply_text("Hemat - Hemat Jangan Borosss !!! 😡")
            else:
                await update.message.reply_text("Insufficient balance.")
        else:
            await update.message.reply_text(f"Account {account} does not exist.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /expense <amount> <account> <category>")

async def transfer(update: Update, context: CallbackContext):
    try:
        amount = float(context.args[0])
        from_account = context.args[1]
        to_account = context.args[2]
        if from_account in accounts and to_account in accounts:
            if accounts[from_account] >= amount:
                accounts[from_account] -= amount
                accounts[to_account] += amount
                add_transaction({"type": "transfer", "amount": amount, "from": from_account, "to": to_account})
                await update.message.reply_text(f"Transferred {amount} from {from_account} to {to_account}.")
            else:
                await update.message.reply_text("Insufficient balance in source account.")
        else:
            await update.message.reply_text("One or both accounts do not exist.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /transfer <amount> <from_account> <to_account>")

async def balance(update: Update, context: CallbackContext):
    total_balance = calculate_total_balance()
    message = f"Total Balance: {total_balance}\n"
    for account, balance in accounts.items():
        message += f"{account}: {balance}\n"
    await update.message.reply_text(message)

async def transactions_command(update: Update, context: CallbackContext):
    if not transactions:
        await update.message.reply_text("No transactions found.")
    else:
        message = "Transaction History:\n"
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

# Main function
def main():
    application = Application.builder().token("7959222765:AAF42lZVxYhZqkOW2BsjtK6CdpkG0zEtPdQ").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_account", add_account))
    application.add_handler(CommandHandler("income", income))
    application.add_handler(CommandHandler("expense", expense))
    application.add_handler(CommandHandler("transfer", transfer))
    application.add_handler(CommandHandler("balance", balance))
    application.add_handler(CommandHandler("transactions", transactions_command))
    application.add_handler(CommandHandler("delete_transaction", delete_transaction))

    application.run_polling()

if __name__ == "__main__":
    main()
