import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# 1. 初始化設定 (請確保網址正確)
FIREBASE_URL = "https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/.json"

st.set_page_config(page_title="WOS War Command", page_icon="⚔️", layout="wide")

# 將刷新頻率改為 0.5 秒 (500ms) 以應對戰爭需求
st_autorefresh(interval=500, key="datarefresh")

st.title("⚔️ WOS SVS Real-time Command")

# 2. 權限判斷
is_admin = st.query_params.get("role") == "admin"

# 3. 定義多語系按鈕項目 (英、中、韓)
items = {
    "gillard": {
        "en": "Gillard Open Rally",
        "zh": "Gillard 開啟集結",
        "ko": "Gillard 집결 시작"
    },
    "rex": {
        "en": "Rex Open Rally",
        "zh": "Rex 開啟集結",
        "ko": "Rex 집결 시작"
    },
    "joann": {
        "en": "Joann Open Rally",
        "zh": "Joann 開啟集結",
        "ko": "Joann 집결 시작"
    },
    "castle": {
        "en": "Switch Castle Member",
        "zh": "更換駐守成員",
        "ko": "성 주둔 멤버 교체"
    }
}

# 4. 從 Firebase 抓取資料
try:
    response = requests.get(FIREBASE_URL)
    status_data = response.json().get('rally_status', {}) if response.json() else {}
except:
    status_data = {}

st.markdown("---")

# 5. 渲染介面
for key, labels in items.items():
    current_val = status_data.get(key, False)
    
    # 建立橫向佈局：語言顯示區 與 管理按鈕區
    col_lang, col_btn = st.columns([4, 1])
    
    with col_lang:
        if current_val:
            # 亮燈狀態：顯示三種語言並列
            st.success(f"### ✅ {labels['en']} | {labels['zh']} | {labels['ko']}")
        else:
            # 待命狀態
            st.info(f"### ⚪ {labels['en']} | {labels['zh']} | {labels['ko']}")
            
    with col_btn:
        if is_admin:
            # 管理員切換按鈕
            btn_label = "OFF (關閉)" if current_val else "ON (開啟)"
            if st.button(btn_label, key=key, use_container_width=True):
                new_status = not current_val
                update_url = f"https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/rally_status/{key}.json"
                requests.put(update_url, json=new_status)
                st.rerun()

st.markdown("---")
if is_admin:
    st.warning("⚡ **ADMIN MODE** | 管理員模式 | 관리자 모드")
else:
    st.caption("ℹ️ Auto-refreshes every 0.5s | 每 0.5 秒自動更新 | 0.5초마다 자동 새로고침")
