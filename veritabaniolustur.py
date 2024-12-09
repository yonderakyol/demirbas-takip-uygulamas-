import sqlite3

# Veritabanı bağlantısı
conn = sqlite3.connect('assets.db')
c = conn.cursor()

# Tablo oluşturma
c.execute('''CREATE TABLE IF NOT EXISTS assets
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              description TEXT,
              quantity INTEGER,
              location TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS locations
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL UNIQUE)''')

c.execute('''CREATE TABLE IF NOT EXISTS names
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL UNIQUE)''')

c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password TEXT NOT NULL)''')

# Varsayılan kullanıcı ekleme
c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "51faiksahenk51"))

conn.commit()
conn.close()