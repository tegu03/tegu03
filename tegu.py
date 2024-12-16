from telegram.ext import Updater, CommandHandler, MessageHandler
import logging
import sqlite3

# Pengaturan awal
TOKEN = "7959222765:AAF42lZVxYhZqkOW2BsjtK6CdpkG0zEtPdQ"
logging.basicConfig(level=logging.INFO)

# Membuat database
conn = sqlite3.connect('keuangan.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS keuangan
             (tanggal TEXT, jenis TEXT, jumlah REAL, keterangan TEXT)''')
conn.commit()

def start(update, context):
    context.bot.send_message(chat_id=(link unavailable), text="Selamat datang! Bot keuangan pribadi.")

def tambah(update, context):
    context.bot.send_message(chat_id=(link unavailable), text="Masukkan tanggal (YYYY-MM-DD), jenis (masuk/keluar), jumlah, dan keterangan (pisahkan dengan ',')")

def simpan(update, context):
    text = update.message.text.split(',')
    tanggal, jenis, jumlah, keterangan = text[0], text[1], float(text[2]), text[3]
    c.execute("INSERT INTO keuangan VALUES (?, ?, ?, ?)", (tanggal, jenis, jumlah, keterangan))
    conn.commit()
    context.bot.send_message(chat_id=(link unavailable), text="Data tersimpan!")

def laporan(update, context):
    context.bot.send_message(chat_id=(link unavailable), text="Pilih jenis laporan: harian, bulanan, atau mingguan")

def laporan_harian(update, context):
    tanggal = update.message.text.split(' ')[1]
    c.execute("SELECT * FROM keuangan WHERE tanggal=?", (tanggal,))
    rows = c.fetchall()
    laporan = "Laporan Harian:\n"
    for row in rows:
        laporan += f"{row[0]} - {row[1]}: {row[2]} ({row[3]})\n"
    context.bot.send_message(chat_id=(link unavailable), text=laporan)

def laporan_bulanan(update, context):
    bulan, tahun = update.message.text.split(' ')[1], update.message.text.split(' ')[2]
    c.execute("SELECT * FROM keuangan WHERE tanggal LIKE ?", (f"{tahun}-{bulan}-%",))
    rows = c.fetchall()
    laporan = f"Laporan Bulanan {bulan}/{tahun}:\n"
    for row in rows:
        laporan += f"{row[0]} - {row[1]}: {row[2]} ({row[3]})\n"
    context.bot.send_message(chat_id=(link unavailable), text=laporan)

def laporan_mingguan(update, context):
    minggu, tahun = update.message.text.split(' ')[1], update.message.text.split(' ')[2]
    # Perlu penyesuaian untuk menghitung minggu
    context.bot.send_message(chat_id=(link unavailable), text="Fitur ini belum tersedia.")

def hapus(update, context):
    context.bot.send_message(chat_id=(link unavailable), text="Masukkan tanggal untuk menghapus data")

def hapus_data(update, context):
    tanggal = update.message.text.split(' ')[1]
    c.execute("DELETE FROM keuangan WHERE tanggal=?", (tanggal,))
    conn.commit()
    context.bot.send_message(chat_id=(link unavailable), text="Data terhapus!")

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("tambah", tambah))
    dp.add_handler(MessageHandler(Filters.regex(r'^\d{4}-\d{2}-\d{2},(masuk|keluar),\d+(\.\d+)?,.+), simpan))
    dp.add_handler(CommandHandler("laporan", laporan))
    dp.add_handler(MessageHandler(Filters.regex(r'^laporan harian \d{4}-\d{2}-\d{2}), laporan_harian))
    dp.add_handler(MessageHandler(Filters.regex(r'^laporan bulanan \d{2} \d{4}), laporan_bulanan))
    dp.add_handler(MessageHandler(Filters.regex(r'^laporan mingguan \d{2} \d{4}), laporan_ming