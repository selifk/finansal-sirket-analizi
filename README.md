# Finansal Şirket Analizi

Google Gemini API ve yfinance kullanarak BIST şirketlerinin gerçek zamanlı 
finansal verilerini analiz eden, üretken yapay zekâ destekli bir Streamlit 
web uygulaması.

## Özellikler
- 80+ BIST şirketinin canlı fiyat ve finansal verisi
- Google Gemini ile AI destekli finansal sağlık analizi
- İnteraktif karşılaştırma grafikleri (Plotly)

## Çalıştırma
pip install streamlit google-genai yfinance plotly pandas
streamlit run app.py

(Kendi Gemini API key'inizi .streamlit/secrets.toml dosyasına eklemeniz gerekir)

