import requests
from gtts import gTTS
import folium
import streamlit as st
import os
from math import radians, cos, sin, asin, sqrt

# ========= إعداداتك =========
NINJA_API_KEY = "trSmbb2hBy7x1fxl29U5Tw==BoCe7lW2YaViNhV7"

# ========= الوظائف =========

def get_iss_location():
    url = "http://api.open-notify.org/iss-now.json"
    response = requests.get(url)
    data = response.json()
    lat = float(data['iss_position']['latitude'])
    lon = float(data['iss_position']['longitude'])
    return lat, lon

def get_city_from_coords(lat, lon):
    headers = {"X-Api-Key": NINJA_API_KEY}
    url = f"https://api.api-ninjas.com/v1/reversegeocoding?lat={lat}&lon={lon}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        return data.get("name", "مكان غير معروف"), data.get("country", "دولة غير معروفة")
    return "غير معروف", "غير معروف"

def speak_message(message):
    tts = gTTS(text=message, lang='ar')
    tts.save("alert.mp3")
    os.system("start alert.mp3" if os.name == "nt" else "mpg123 alert.mp3")

def create_map(lat, lon, city, country):
    m = folium.Map(location=[lat, lon], zoom_start=3)
    folium.Marker([lat, lon], tooltip=f"🚀 المحطة الآن فوق: {city}, {country}").add_to(m)
    m.save("iss_map.html")

def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

def get_user_ip_location():
    try:
        res = requests.get("https://ipinfo.io/json")
        data = res.json()
        lat, lon = map(float, data['loc'].split(','))
        return lat, lon
    except:
        return None, None

# ========= واجهة Streamlit =========

st.set_page_config(page_title="🚀 تتبع محطة الفضاء", layout="centered")
st.markdown("""
    <h1 style="text-align:center; color:#10c6ff;">🚀 تتبع مباشر لمحطة الفضاء الدولية</h1>
    <p style="text-align:center; font-size:18px;">اعرف مكان المحطة الآن، وقُربها من موقعك في الوقت الحقيقي</p>
""", unsafe_allow_html=True)

iss_lat, iss_lon = get_iss_location()
iss_city, iss_country = get_city_from_coords(iss_lat, iss_lon)

st.subheader("📍 موقع محطة الفضاء الدولية الآن:")
st.success(f"فوق: {iss_city}, {iss_country}")
st.write(f"خط العرض: `{iss_lat}`")
st.write(f"خط الطول: `{iss_lon}`")

user_lat, user_lon = get_user_ip_location()
if user_lat and user_lon:
    distance_km = haversine(iss_lat, iss_lon, user_lat, user_lon)
    st.info(f"🌍 المسافة بينك وبين المحطة الفضائية: {int(distance_km)} كم")

    if distance_km < 1000:
        st.warning("🚨 المحطة تمر قريبًا من منطقتك!")
        speak_message("المحطة الفضائية الدولية تمر الآن بالقرب من موقعك، انظر إلى السماء!")
else:
    st.error("⚠️ لم نتمكن من تحديد موقعك تلقائيًا.")

create_map(iss_lat, iss_lon, iss_city, iss_country)
st.markdown("[📍 عرض الخريطة التفاعلية](iss_map.html)", unsafe_allow_html=True)
