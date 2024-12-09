import streamlit as st
import sqlite3
import datetime
import uuid
import os

# Veritabanı bağlantısı
def get_connection():
    return sqlite3.connect('assets.db')

# Kullanıcı doğrulama
def authenticate(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

# Konum ekleme
def add_location(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO locations (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

# Konumları listeleme
def get_locations():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM locations")
    locations = [row[0] for row in c.fetchall()]
    conn.close()
    return locations

# Name ekleme
def add_name(name):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO names (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

# Names listeleme
def get_names():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name FROM names")
    names = [row[0] for row in c.fetchall()]
    conn.close()
    return names

# Demirbaş ekleme
def add_asset(name, description, quantity, location):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO assets (name, description, quantity, location) VALUES (?, ?, ?, ?)",
              (name, description, quantity, location))
    conn.commit()
    conn.close()

# Demirbaş güncelleme
def update_asset(asset_id, name, description, quantity, location):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE assets SET name=?, description=?, quantity=?, location=? WHERE id=?",
              (name, description, quantity, location, asset_id))
    conn.commit()
    conn.close()

# Demirbaş silme
def delete_asset(asset_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM assets WHERE id=?", (asset_id,))
    conn.commit()
    conn.close()

# Demirbaşları listeleme
def get_assets():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM assets")
    assets = c.fetchall()
    conn.close()
    return assets

# Demirbaş aktarma
def transfer_asset(asset_id, new_location):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE assets SET location=? WHERE id=?", (new_location, asset_id))
    conn.commit()
    conn.close()

# Yeni kullanıcı ekleme
def add_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

# MAC adresini al
def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

# Log dosyasına yaz
def log_operation(username, operation, asset_id=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mac_address = get_mac_address()
    log_entry = f"{timestamp} - {username} - {operation} - Asset ID: {asset_id} - MAC: {mac_address}\n"
    
    if not os.path.exists("logs"):
        os.makedirs("logs")
    
    with open("logs/operations.log", "a") as log_file:
        log_file.write(log_entry)

# Streamlit arayüzü
st.set_page_config(layout="wide")
st.title("Faik Şahenk MTAL | Bilişim Teknolojileri Alanı")
st.subheader("Demirbaş Takip Uygulaması")



# Kullanıcı girişi
def login():
    if 'username' not in st.session_state:
        st.subheader("Kullanıcı Girişi")
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type='password')
        if st.button("Giriş"):
            if authenticate(username, password):
                st.session_state.username = username
                st.success("Giriş başarılı!")
            else:
                st.error("Kullanıcı adı veya şifre yanlış!")
    return st.session_state.get('username', None)

username = login()

if username:
    # Kullanıcı giriş yaptıktan sonra isim ve konumları güncelle
    names = get_names()
    locations = get_locations()
    
    # Menü seçenekleri
    menu = [
        ("Demirbaş Ekle", "📦"),
        ("Demirbaşları Listele", "📋"),
        ("Demirbaş Güncelle", "✏️"),
        ("Demirbaş Sil", "🗑️"),
        ("Demirbaş Aktar", "🔄"),
        ("Ayarlar", "⚙️")
    ]

    choice = st.sidebar.selectbox("Menü", [f"{icon} {name}" for name, icon in menu])

    if choice == "📦 Demirbaş Ekle":
        st.subheader("Demirbaş Ekle")
        with st.form(key='add_asset_form'):
            col1, col2 = st.columns(2)
            with col1:
                name = st.selectbox("Demirbaş Adı", names)
            with col2:
                location = st.selectbox("Konum", locations)
            description = st.text_area("Açıklama")
            quantity = st.number_input("Miktar", min_value=1)
            submit_button = st.form_submit_button(label='Ekle')
        
        if submit_button:
            add_asset(name, description, quantity, location)
            log_operation(username, "Demirbaş Eklendi")
            st.success("Demirbaş başarıyla eklendi!")

    elif choice == "📋 Demirbaşları Listele":
        st.subheader("Demirbaşları Listele")
        
        # Filtreleme seçenekleri
        filter_option = st.selectbox("Filtreleme Seçeneği", ["Hepsi", "Konuma Göre", "Demirbaş Adına Göre"])
        
        assets = get_assets()  # Tüm demirbaşları alıyoruz
        filtered_assets = []

        if filter_option == "Konuma Göre":
            locations = get_locations()
            selected_location = st.selectbox("Konum Seçin", locations)
            filtered_assets = [asset for asset in assets if asset[4] == selected_location]

        elif filter_option == "Demirbaş Adına Göre":
            names = get_names()
            selected_name = st.selectbox("Demirbaş Adı Seçin", names)
            filtered_assets = [asset for asset in assets if asset[1] == selected_name]

        else:  # "Hepsi" seçeneği
            filtered_assets = assets

        # Toplam demirbaş sayısını göster
        st.markdown(f"**Toplam Demirbaş Sayısı:** {len(filtered_assets)}")

        if filtered_assets:
            # Tablo için verileri hazırlıyoruz
            asset_data = []
            for asset in filtered_assets:
                asset_data.append({
                    "ID": asset[0],
                    "Adı": asset[1],
                    "Açıklama": asset[2] if asset[2] else 'Yok',
                    "Miktar": asset[3] if asset[3] else 'Yok',
                    "Konum": asset[4] if asset[4] else 'Yok'
                })
            
            # Tabloyu gösteriyoruz
            st.table(asset_data)
        else:
            st.write("Henüz demirbaş eklenmemiş veya filtreye uyan demirbaş yok.")

    elif choice == "✏️ Demirbaş Güncelle":
        st.subheader("Demirbaş Güncelle")
        
        # Tüm demirbaşları alıyoruz
        assets = get_assets()
        asset_names = {asset[0]: (asset[1], asset[4]) for asset in assets}  # ID ile (Ad, Konum) eşleştiriyoruz
        
        # Kullanıcıdan güncellenecek demirbaş ID'sini seçmesini istiyoruz
        asset_id = st.selectbox("Güncellenecek Demirbaş", list(asset_names.keys()))
        
        if asset_id:
            selected_asset = asset_names[asset_id]
            st.write(f"Güncellenecek Demirbaş: {selected_asset[0]} (Konum: {selected_asset[1]})")
            
            with st.form(key='update_asset_form'):
                col1, col2 = st.columns(2)
                with col1:
                    names = get_names()
                    name = st.selectbox("Yeni Demirbaş Adı", names)
                with col2:
                    locations = get_locations()
                    location = st.selectbox("Yeni Konum", locations)
                description = st.text_area("Yeni Açıklama")
                quantity = st.number_input("Yeni Miktar", min_value=1)
                submit_button = st.form_submit_button(label='Güncelle')
            
            if submit_button:
                update_asset(asset_id, name, description, quantity, location)
                log_operation(username, "Demirbaş Güncellendi", asset_id)
                st.success("Demirbaş başarıyla güncellendi!")

    elif choice == "🗑️ Demirbaş Sil":
        st.subheader("Demirbaş Sil")
        asset_id = st.number_input("Silinecek Demirbaş ID", min_value=1)
        assets = get_assets()
        asset_names = {asset[0]: asset[1] for asset in assets}
        
        if asset_id in asset_names:
            st.write(f"Silinecek Demirbaş: {asset_names[asset_id]}")
            if st.button("Sil"):
                delete_asset(asset_id)
                log_operation(username, "Demirbaş Silindi", asset_id)
                st.success("Demirbaş başarıyla silindi!")
        else:
            st.write("Belirtilen ID'ye sahip bir demirbaş bulunamadı.")

    elif choice == "🔄 Demirbaş Aktar":
        st.subheader("Demirbaş Aktar")
        asset_id = st.number_input("Aktarılacak Demirbaş ID", min_value=1)
        assets = get_assets()
        asset_names = {asset[0]: asset[1] for asset in assets}
        
        if asset_id in asset_names:
            st.write(f"Aktarılacak Demirbaş: {asset_names[asset_id]}")
            with st.form(key='transfer_asset_form'):
                locations = get_locations()
                new_location = st.selectbox("Aktarılacak Konum", locations)
                submit_button = st.form_submit_button(label='Aktar')
            
            if submit_button:
                transfer_asset(asset_id, new_location)
                log_operation(username, "Demirbaş Aktarıldı", asset_id)
                st.success("Demirbaş başarıyla aktarıldı!")
        else:
            st.write("Belirtilen ID'ye sahip bir demirbaş bulunamadı.")

    elif choice == "⚙️ Ayarlar":
        st.subheader("Ayarlar")
        with st.form(key='add_location_form'):
            st.write("Yeni Konum Ekle")
            new_location = st.text_input("Yeni Konum Adı")
            submit_button = st.form_submit_button(label='Konum Ekle')
        
        if submit_button:
            add_location(new_location)
            log_operation(username, "Konum Eklendi")
            st.success("Yeni konum başarıyla eklendi!")
        
        with st.form(key='add_name_form'):
            st.write("Yeni Demirbaş Adı Ekle")
            new_name = st.text_input("Yeni Demirbaş Adı")
            submit_button = st.form_submit_button(label='Demirbaş Adı Ekle')
        
        if submit_button:
            add_name(new_name)
            log_operation(username, "Demirbaş Adı Eklendi")
            st.success("Yeni demirbaş adı başarıyla eklendi!")
        
        if username == "admin":
            with st.form(key='add_user_form'):
                st.write("Yeni Kullanıcı Ekle")
                new_username = st.text_input("Yeni Kullanıcı Adı")
                new_password = st.text_input("Yeni Şifre", type='password')
                submit_button = st.form_submit_button(label='Kullanıcı Ekle')
            
            if submit_button:
                add_user(new_username, new_password)
                log_operation(username, "Kullanıcı Eklendi")
                st.success("Yeni kullanıcı başarıyla eklendi!")