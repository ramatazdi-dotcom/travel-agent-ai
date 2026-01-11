import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from datetime import datetime

# --- SETUP HALAMAN ---
st.set_page_config(page_title="AI Agent - Travel Assistant", page_icon="🤖", layout="wide")

# --- INITIALIZE SESSION STATE ---
if "itinerary_content" not in st.session_state:
    st.session_state.itinerary_content = ""

# --- KELAS PDF CANGGIH ---
class TravelPDF(FPDF):
    def __init__(self, client_name):
        super().__init__()
        self.client_name = client_name

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'AI AGENT TRAVEL - PROPOSAL', ln=True, align='C')
        self.set_font('Arial', 'I', 11)
        self.cell(0, 8, f'Disiapkan Khusus untuk: {self.client_name}', ln=True, align='C')
        self.set_line_width(0.5)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-20) 
        self.set_font('Arial', 'I', 8)
        self.cell(0, 5, f'Powered by Gemini 2.5 Flash | Generated on {datetime.now().strftime("%d-%m-%Y")}', ln=True, align='C')
        current_year = datetime.now().year
        self.cell(0, 5, f'Copyright (c) {current_year} AI Agent - Travel Assistant by Rama Tazdi. All rights reserved.', ln=True, align='C')

def clean_text(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

# --- SIDEBAR (INPUT API KEY) ---
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    api_key = st.text_input("Tempel API Key Google di sini", type="password")
    
    if api_key:
        st.success("✅ API Key Terhubung")
    else:
        st.warning("⚠️ Menunggu API Key")
        
    st.divider()
    st.caption("Engine: Gemini 2.5 Flash")

# --- FUNGSI AI ---
def ask_gemini(prompt_text):
    if not api_key:
        st.error("⚠️ API Key belum dimasukkan! Lihat panduan di atas.")
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash') 
        with st.spinner('Sedang menyusun proposal profesional...'):
            response = model.generate_content(prompt_text)
            return response.text
    except Exception as e:
        st.error(f"Error API: {e}")
        return None

# --- UI UTAMA ---
st.title("🤖🗺️ Ai Agent - Travel Assistant")
st.markdown("Asisten Perjalanan Pribadi Anda. Menyediakan Informasi Yang Cepat, Lengkap, dan Profesional.")

# --- WARNING & PANDUAN ---
if not api_key:
    st.warning("⚠️ **PERHATIAN:** Aplikasi ini belum aktif. Anda perlu memasukkan API Key Google agar bisa menyusun rencana.")
    with st.expander("📖 Klik di sini untuk melihat Panduan Cara Menggunakan Aplikasi & Mendapatkan API Key"):
        st.markdown("""
        **Cara Mengaktifkan Aplikasi:**
        1.  **Dapatkan Kunci Gratis:** Buka [Google AI Studio](https://aistudio.google.com/), Login, klik **Get API Key** -> **Create API Key**.
        2.  **Masukkan Kunci:** Tempel kode di kolom menu sebelah kiri (Sidebar).
        3.  **Gunakan Aplikasi:** Isi data liburan di bawah ini dan klik tombol merah.
        """)

st.markdown("---")

# --- LAYOUT DUA KOLOM ---
col1, col2 = st.columns([1, 1.2])

# KOLOM KIRI (INPUT FORM)
with col1:
    st.markdown("### 📋 Data Liburan")
    nama_klien = st.text_input("Nama Anda / Peserta", placeholder="Cth: Budi Santoso")
    tujuan = st.text_input("Tujuan Destinasi", value="Labuan Bajo")
    
    c1, c2 = st.columns(2)
    with c1:
        durasi = st.slider("Berapa Hari?", 1, 14, 4)
    with c2:
        budget = st.selectbox("Budget", ["Hemat (Backpacker)", "Standard (Keluarga)", "Luxury (Sultan)"])

    st.markdown("---")
    
    if st.button("🚀 Susun Rencana Sekarang", type="primary", use_container_width=True):
        if not api_key:
            st.error("❌ Eits, jangan lupa masukkan API Key dulu di menu sebelah kiri ya! (Lihat panduan di atas)")
        elif not nama_klien:
            st.warning("Mohon isi Nama Anda terlebih dahulu.")
        else:
            prompt_awal = f"""
            Bertindaklah sebagai Travel Consultant Profesional.
            Buatkan proposal perjalanan untuk klien bernama: {nama_klien}.
            Tujuan: {tujuan}, Durasi: {durasi} hari, Budget: {budget}.
            
            PENTING:
            1. Gunakan Bahasa Indonesia formal & rapi.
            2. Jangan pakai Emoji.
            3. Buatkan Link URL Pencarian Google Search untuk Cek Harga di Traveloka, Tiket.com, Agoda.
            
            STRUKTUR:
            - PENDAHULUAN
            - ESTIMASI HARGA & LINK BOOKING
            - ITINERARY HARIAN
            - REKOMENDASI SPESIFIK
            """
            hasil = ask_gemini(prompt_awal)
            if hasil:
                st.session_state.itinerary_content = hasil

# KOLOM KANAN (HASIL ATAU WALLPAPER)
with col2:
    if st.session_state.itinerary_content:
        # KONDISI 1: JIKA SUDAH ADA HASIL
        st.markdown("### 📄 Proposal Perjalanan")
        st.markdown(st.session_state.itinerary_content)
        st.divider()
        if st.button("🖨️ Download PDF Resmi"):
            pdf = TravelPDF(nama_klien if nama_klien else "Tamu")
            pdf.add_page()
            pdf.set_font("Arial", size=11)
            clean_content = clean_text(st.session_state.itinerary_content)
            pdf.multi_cell(0, 6, clean_content)
            pdf_bytes = pdf.output(dest='S').encode('latin-1')
            filename = f"Proposal_{nama_klien}_{tujuan}.pdf".replace(" ", "_")
            st.download_button(label="Unduh File PDF", data=pdf_bytes, file_name=filename, mime="application/pdf")
            
    else:
        # KONDISI 2: JIKA BELUM ADA HASIL (TAMPILKAN GAMBAR SAJA)
        st.image(
            "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=2021&auto=format&fit=crop", 
            caption="Jelajahi Dunia dengan AI",
            use_container_width=True
        )
        # Bagian st.info() yang dilingkari merah SUDAH DIHAPUS di sini.

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: grey; font-size: 12px;'>
        Copyright © 2026 AI Agent - Travel Assistant by Rama Tazdi. All rights reserved.<br>
    </div>
    """, 
    unsafe_allow_html=True
)