import streamlit as st
from google import genai
import yfinance as yf
import pandas as pd
import plotly.express as px

# ============== SAYFA AYARLARI ==============
st.set_page_config(page_title="Finansal Şirket Analizi", layout="wide", page_icon="📈")

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# ============== ÖZEL TASARIM (CSS) ==============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0a1a3c;
    }

    /* KURAL: her şey açık renk, sonra istisnaları geri koyuyoruz */
    .stApp, .stApp * {
        color: #eef1fb !important;
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #ffffff !important;
    }

    div[data-testid="stMetric"] {
        background-color: #12285c;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #2a4080;
    }
    div[data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #ffffff !important;
    }

    /* Seçim kutusu KAPALI hâldeyken açık zeminli olduğundan yazı koyu olmalı */
    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
    }
    div[data-baseweb="select"] * {
        color: #0a1a3c !important;
    }
    /* Seçim kutusu AÇILINCA çıkan liste (popover) de açık zeminli */
    div[data-baseweb="popover"] * {
        color: #0a1a3c !important;
    }

    /* Ana buton - turuncu zemin, beyaz yazı */
    .stButton > button {
        display: block;
        margin: 30px auto;
        background: linear-gradient(135deg, #ff6b35, #f7931e) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 22px;
        font-weight: 700;
        padding: 18px 50px;
        border-radius: 50px;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
        transition: transform 0.2s;
    }
    .stButton > button, .stButton > button * {
        color: #ffffff !important;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 107, 53, 0.6);
    }

    div[data-testid="stExpander"] {
        background-color: #12285c;
        border-radius: 10px;
        border: 1px solid #2a4080;
    }

    /* Success / warning / error kutuları açık zeminli, yazı koyu olmalı */
    div[data-testid="stAlert"] {
        background-color: #eef1fb !important;
    }
    div[data-testid="stAlert"] * {
        color: #0a1a3c !important;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Finansal Şirket Analizi")
st.write("Yapay zekâ destekli hisse senedi analiz platformu")

# ============== ŞİRKET LİSTESİ (BIST) ==============
BIST_COMPANIES = {
    "Türk Hava Yolları": "THYAO.IS", "Garanti BBVA": "GARAN.IS", "Akbank": "AKBNK.IS",
    "Aselsan": "ASELS.IS", "BİM": "BIMAS.IS", "Koç Holding": "KCHOL.IS",
    "Sabancı Holding": "SAHOL.IS", "Ereğli Demir Çelik": "EREGL.IS", "Tüpraş": "TUPRS.IS",
    "Türk Telekom": "TTKOM.IS", "Turkcell": "TCELL.IS", "Şişecam": "SISE.IS",
    "Ford Otosan": "FROTO.IS", "Tofaş": "TOASO.IS", "Arçelik": "ARCLK.IS",
    "Yapı Kredi": "YKBNK.IS", "İş Bankası (C)": "ISCTR.IS", "Halkbank": "HALKB.IS",
    "Vakıfbank": "VAKBN.IS", "QNB Finansbank": "QNBFB.IS", "Migros": "MGROS.IS",
    "Coca-Cola İçecek": "CCOLA.IS", "Ülker": "ULKER.IS", "Pegasus": "PGSUS.IS",
    "Enka İnşaat": "ENKAI.IS", "Kardemir": "KRDMD.IS", "Petkim": "PETKM.IS",
    "Aksa Enerji": "AKSEN.IS", "Zorlu Enerji": "ZOREN.IS", "Kızılay": "KZBGY.IS",
    "Mavi Giyim": "MAVI.IS", "LC Waikiki": "LCWKS.IS", "Anadolu Efes": "AEFES.IS",
    "TAV Havalimanları": "TAVHL.IS", "Doğuş Otomotiv": "DOAS.IS", "Otokar": "OTKAR.IS",
    "Vestel": "VESTL.IS", "Alarko Holding": "ALARK.IS", "Global Yatırım": "GLYHO.IS",
    "İş GYO": "ISGYO.IS", "Emlak Konut GYO": "EKGYO.IS", "Torunlar GYO": "TRGYO.IS",
    "Hektaş": "HEKTS.IS", "Bagfaş": "BAGFS.IS", "Gübre Fabrikaları": "GUBRF.IS",
    "Selçuk Ecza": "SELEC.IS", "Deva Holding": "DEVA.IS", "Aksigorta": "AKGRT.IS",
    "Anadolu Sigorta": "ANSGR.IS", "Ak Sigorta": "AKGRT.IS", "Sasa Polyester": "SASA.IS",
    "Kordsa": "KORDS.IS", "Brisa": "BRISA.IS", "Goodyear": "GOODY.IS",
    "Çimsa": "CIMSA.IS", "Akçansa": "AKCNS.IS", "Konya Çimento": "KONYA.IS",
    "Trakya Cam": "TRKCM.IS", "Soda Sanayii": "SODA.IS", "Doğan Holding": "DOHOL.IS",
    "Türk Prysmian": "PRKME.IS", "Türk Telekomünikasyon": "TTKOM.IS", "Netaş": "NETAS.IS",
    "Logo Yazılım": "LOGO.IS", "Link Bilgisayar": "LINK.IS", "Datagate": "DGATE.IS",
    "İndeks Bilgisayar": "INDES.IS", "Karsan": "KARSN.IS", "Katmerciler": "KATMR.IS",
    "Bosch Fren": "BFREN.IS", "Ditaş Doğan": "DITAS.IS", "Kartonsan": "KARTN.IS",
    "Viking Kağıt": "VKING.IS", "Türk Sağlık": "TURSG.IS", "Medical Park (MLP)": "MPARK.IS",
    "Lokman Hekim": "LKMNH.IS", "Reeder": "RTALB.IS", "Penta Teknoloji": "PENTA.IS",
    "Vestel Beyaz Eşya": "VESBE.IS", "Alkim Kimya": "ALKIM.IS", "Bak Ambalaj": "BAKAB.IS",
    "Marshall Boya": "MRSHL.IS", "Berkosan": "BRKSN.IS", "Ege Endüstri": "EGEEN.IS"
}

# Şirketlere sabit, ayırt edici renkler ata
PALETTE = px.colors.qualitative.Alphabet
company_colors = {name: PALETTE[i % len(PALETTE)] for i, name in enumerate(BIST_COMPANIES.keys())}

# ============== VERİ ÇEKME (CACHE'Lİ) ==============
@st.cache_data(ttl=600, show_spinner=False)
def get_company_info(symbol):
    try:
        t = yf.Ticker(symbol)
        info = t.info
        return {
            "Fiyat": info.get("currentPrice", info.get("regularMarketPrice", 0)) or 0,
            "Kâr Marjı": round((info.get("profitMargins") or 0) * 100, 1),
            "F/K": info.get("trailingPE"),
            "Piyasa Değeri": info.get("marketCap"),
            "Toplam Gelir": info.get("totalRevenue"),
            "Borç/Özkaynak": info.get("debtToEquity"),
        }
    except Exception:
        return None

@st.cache_data(ttl=600, show_spinner=False)
def get_price_history(symbol, period="6mo"):
    try:
        return yf.Ticker(symbol).history(period=period)
    except Exception:
        return pd.DataFrame()

# ============== ÜST BÖLÜM: ŞİRKET KARŞILAŞTIRMASI ==============
st.write("---")
st.subheader("📊 Şirket Karşılaştırması")

num_companies = st.slider(
    "Karşılaştırmada kaç şirket gösterilsin?",
    min_value=5, max_value=len(BIST_COMPANIES), value=20, step=5
)

compare_names = list(BIST_COMPANIES.keys())[:num_companies]

with st.spinner(f"{num_companies} şirketin verisi yükleniyor... (ilk yüklemede biraz sürebilir)"):
    rows = []
    for name in compare_names:
        info = get_company_info(BIST_COMPANIES[name])
        if info:
            rows.append({"Şirket": name, "Fiyat (TL)": info["Fiyat"], "Kâr Marjı (%)": info["Kâr Marjı"]})

compare_df = pd.DataFrame(rows)

if not compare_df.empty:
    col1, col2 = st.columns(2)

    with col1:
        fig_price = px.bar(
            compare_df.sort_values("Fiyat (TL)", ascending=False),
            x="Şirket", y="Fiyat (TL)", color="Şirket",
            color_discrete_map=company_colors,
            title="Güncel Fiyatlar (TL)"
        )
        fig_price.update_layout(
            plot_bgcolor="#0a1a3c", paper_bgcolor="#0a1a3c",
            font=dict(color="white", size=13),
            title_font=dict(color="white", size=18, family="Space Grotesk"),
            xaxis=dict(tickfont=dict(color="#ffffff", size=13), title=None),
            yaxis=dict(tickfont=dict(color="#ffffff", size=13)),
            showlegend=False, xaxis_tickangle=-45
        )
        st.plotly_chart(fig_price, use_container_width=True)

    with col2:
        fig_margin = px.bar(
            compare_df.sort_values("Kâr Marjı (%)", ascending=False),
            x="Şirket", y="Kâr Marjı (%)", color="Şirket",
            color_discrete_map=company_colors,
            title="Kâr Marjları (%)"
        )
        fig_margin.update_layout(
            plot_bgcolor="#0a1a3c", paper_bgcolor="#0a1a3c",
            font=dict(color="white", size=13),
            title_font=dict(color="white", size=18, family="Space Grotesk"),
            xaxis=dict(tickfont=dict(color="#ffffff", size=13), title=None),
            yaxis=dict(tickfont=dict(color="#ffffff", size=13)),
            showlegend=False, xaxis_tickangle=-45
        )
        st.plotly_chart(fig_margin, use_container_width=True)
else:
    st.warning("Karşılaştırma verisi şu anda çekilemedi, lütfen daha sonra tekrar deneyin.")

# ============== ALT BÖLÜM: TEKİL ŞİRKET ANALİZİ ==============
st.write("---")
st.subheader("🔍 Detaylı Şirket Analizi")

selected_name = st.selectbox(
    "Analiz etmek istediğiniz şirketi seçin (yazarak arayabilirsiniz):",
    list(BIST_COMPANIES.keys())
)
ticker_symbol = BIST_COMPANIES[selected_name]

try:
    with st.spinner("Veriler çekiliyor..."):
        info = get_company_info(ticker_symbol)
        hist = get_price_history(ticker_symbol)

    if info is None:
        st.error("Bu şirket için veri çekilemedi. Lütfen başka bir şirket seçin.")
        st.stop()

except Exception:
    st.error("Veri çekilirken bir sorun oluştu. Lütfen sayfayı yenileyip tekrar deneyin.")
    st.stop()

st.markdown(f"### {selected_name}")

current_price = info["Fiyat"]
pe_ratio = info["F/K"]
profit_margin = info["Kâr Marjı"]
market_cap = info["Piyasa Değeri"]
revenue = info["Toplam Gelir"]
debt_to_equity = info["Borç/Özkaynak"]

col1, col2, col3 = st.columns(3)
col1.metric("Güncel Fiyat", f"{current_price} TL")
col2.metric("F/K Oranı", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A")
col3.metric("Kâr Marjı", f"%{profit_margin}")

st.write(f"**Piyasa Değeri:** {market_cap:,} TL" if isinstance(market_cap, (int, float)) else "**Piyasa Değeri:** N/A")
st.write(f"**Toplam Gelir:** {revenue:,} TL" if isinstance(revenue, (int, float)) else "**Toplam Gelir:** N/A")
st.write(f"**Borç/Özkaynak Oranı:** {debt_to_equity}" if debt_to_equity else "**Borç/Özkaynak Oranı:** N/A")

if not hist.empty:
    fig_hist = px.line(hist, x=hist.index, y="Close", title=f"{selected_name} - Son 6 Ay Fiyat Grafiği")
    fig_hist.update_traces(line_color=company_colors.get(selected_name, "#ff6b35"), line_width=3)
    fig_hist.update_layout(
        plot_bgcolor="#0a1a3c", paper_bgcolor="#0a1a3c",
        font=dict(color="white", size=13),
        title_font=dict(color="white", size=18, family="Space Grotesk"),
        xaxis=dict(tickfont=dict(color="#ffffff", size=12)),
        yaxis=dict(tickfont=dict(color="#ffffff", size=12))
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ============== AI ANALİZİ ==============
st.write("")
if st.button("🤖 YAPAY ZEKÂ İLE ANALİZ ET"):
    with st.spinner("Gemini analiz ediyor..."):
        prompt = f"""
        Aşağıdaki gerçek BIST verilerine sahip bir şirketi kısaca analiz et.
        Şirket: {selected_name} ({ticker_symbol})
        Güncel Fiyat: {current_price}
        F/K Oranı: {pe_ratio}
        Kâr Marjı: %{profit_margin}
        Piyasa Değeri: {market_cap}
        Toplam Gelir: {revenue}
        Borç/Özkaynak Oranı: {debt_to_equity}

        Bu şirketin finansal sağlığını 3-4 cümleyle, Türkçe olarak değerlendir.
        Güçlü ve zayıf yönlerini belirt. Yatırımcı için risk seviyesini
        (Düşük / Orta / Yüksek) belirt.
        """
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )
            st.success("Analiz tamamlandı!")
            st.write(response.text)

            analiz_metni = response.text.lower()
            if "düşük" in analiz_metni and "risk" in analiz_metni:
                st.success("🟢 Genel Risk Seviyesi: DÜŞÜK")
            elif "yüksek" in analiz_metni and "risk" in analiz_metni:
                st.error("🔴 Genel Risk Seviyesi: YÜKSEK")
            else:
                st.warning("🟡 Genel Risk Seviyesi: ORTA")

        except Exception as e:
            st.warning("Şu anda AI servisi yoğun, birkaç saniye sonra tekrar deneyin.")
            with st.expander("Teknik detay"):
                st.write(str(e))