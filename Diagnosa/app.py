import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Ambil API Key dari Streamlit Secrets atau Environment Variable
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash' # Atau 'gemini-2.5-flash-lite'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah seorang ustadz. Beri pertanyaan singkat. Jawaban singkat dan faktual. Tolak pertanyaan non-sejarah."]
    },
    {
        "role": "model",
        "parts": ["Baik! Berikan permasalahannya untuk saya berikan solusinya."]
    }
]

# ==============================================================================
# FUNGSI UTAMA CHATBOT UNTUK STREAMLIT
# ==============================================================================

def main():
    st.set_page_config(page_title="Ustadz Chatbot")
    st.title("Ustadz Chatbot")
    st.write("Silakan ajukan pertanyaan seputar agama atau masalah lainnya. Saya akan berusaha memberikan solusi singkat dan faktual.")

    # Cek apakah API Key sudah diatur
    if not API_KEY:
        st.error("🚨 API Key Gemini belum diatur. Harap tambahkan `GEMINI_API_KEY` ke Streamlit Secrets Anda.")
        st.info("Untuk menambahkan Secrets, klik 'Manage app' -> 'Secrets' di antarmuka Streamlit Cloud, atau buat file `.streamlit/secrets.toml` secara lokal.")
        return

    try:
        genai.configure(api_key=API_KEY)
        # st.success("Gemini API Key berhasil dikonfigurasi.") # Bisa dihilangkan di produksi
    except Exception as e:
        st.error(f"❌ Kesalahan saat mengkonfigurasi API Key: {e}")
        st.warning("Pastikan API Key Anda benar dan koneksi internet stabil.")
        return

    # Inisialisasi model
    try:
        model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                max_output_tokens=500
            )
        )
        # st.success(f"Model '{MODEL_NAME}' berhasil diinisialisasi.") # Bisa dihilangkan
    except Exception as e:
        st.error(f"❌ Kesalahan saat inisialisasi model '{MODEL_NAME}': {e}")
        st.warning("Pastikan nama model benar dan tersedia untuk API Key Anda.")
        return

    # Inisialisasi riwayat chat di Streamlit session state
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = INITIAL_CHATBOT_CONTEXT[:] # Gunakan salinan
        st.session_state["chat_session"] = model.start_chat(history=st.session_state["chat_history"])

    # Tampilkan riwayat chat
    for message in st.session_state["chat_history"]:
        if message["role"] == "user":
            st.chat_message("user").write(message["parts"][0])
        elif message["role"] == "model":
            st.chat_message("assistant").write(message["parts"][0])

    # Input pengguna
    user_input = st.chat_input("Tulis pertanyaan Anda di sini...")

    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state["chat_history"].append({"role": "user", "parts": [user_input]})

        with st.spinner("Ustadz Chatbot sedang membalas..."):
            try:
                response = st.session_state["chat_session"].send_message(user_input, request_options={"timeout": 60})
                if response and response.text:
                    bot_response = response.text
                else:
                    bot_response = "Maaf, saya tidak bisa memberikan balasan."
            except Exception as e:
                bot_response = f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}. Coba lagi nanti."

        st.chat_message("assistant").write(bot_response)
        st.session_state["chat_history"].append({"role": "model", "parts": [bot_response]})

if __name__ == "__main__":
    main()
