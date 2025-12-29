import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

# 1. 初始化設定
# 記得網址結尾要加上 .json，這是 Firebase REST API 的要求
FIREBASE_URL = "https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/.json"

st.set_page_config(page_title="WOS 戰爭指揮系統", page_icon="⚔️")

# 每 3 秒自動重新整理
st_autorefresh(interval=3000, key="datarefresh")

st.title("⚔️ 戰爭即時同步看板")

# 2. 權限判斷
is_admin = st.query_params.get("role") == "admin"

# 3. 定義按鈕項目
items = {
    "gillard": "Gillard Open Rally",
    "rex": "Rex Open Rally",
    "joann": "Joann Open Rally",
    "castle": "Switch Castle Member"
}

# 4. 從 Firebase 抓取資料
try:
    response = requests.get(FIREBASE_URL)
    status_data = response.json().get('rally_status', {}) if response.json() else {}
except:
    status_data = {}

st.markdown("---")

# 5. 渲染介面
for key, label in items.items():
    current_val = status_data.get(key, False)
    
    col_text, col_btn = st.columns([3, 1])
    
    with col_text:
        if current_val:
            st.success(f"### ✅ {label}")
        else:
            st.info(f"### ⚪ {label} (待命)")
            
    with col_btn:
        if is_admin:
            if st.button("切換", key=key, use_container_width=True):
                # 更新 Firebase 資料
                new_status = not current_val
                update_url = f"https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/rally_status/{key}.json"
                requests.put(update_url, json=new_status)
                st.rerun()

st.markdown("---")
if is_admin:
    st.warning("⚡ 目前處於：**管理員模式**")
else:
    st.caption("ℹ️ 目前處於：成員模式 (每 3 秒自動更新)")
