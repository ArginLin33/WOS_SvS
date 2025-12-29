import streamlit as st
from firebase import firebase
from streamlit_autorefresh import st_autorefresh

# 1. 初始化 Firebase 連線
# 使用你提供的網址
FIREBASE_URL = "https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/"
fb = firebase.FirebaseApplication(FIREBASE_URL, None)

# 設定網頁標題與圖示
st.set_page_config(page_title="WOS 戰爭指揮系統", page_icon="⚔️")

# 每 3 秒自動重新整理一次網頁，確保成員看到最新狀態
st_autorefresh(interval=3000, key="datarefresh")

st.title("⚔️ 戰爭即時同步看板")

# 2. 權限判斷：網址結尾加上 ?role=admin 即可操作
query_params = st.query_params
is_admin = query_params.get("role") == "admin"

# 3. 定義按鈕項目
items = {
    "gillard": "Gillard Open Rally",
    "rex": "Rex Open Rally",
    "joann": "Joann Open Rally",
    "castle": "Switch Castle Member"
}

# 4. 從 Firebase 抓取目前的狀態
try:
    # 這裡我們抓取一個名為 'rally_status' 的節點
    status_data = fb.get('/rally_status', None) or {}
except Exception as e:
    st.error(f"連線失敗: {e}")
    status_data = {}

# 5. 顯示介面
st.markdown("---")

for key, label in items.items():
    current_val = status_data.get(key, False)
    
    # 建立兩欄：左邊顯示名稱與狀態，右邊是管理按鈕
    col_text, col_btn = st.columns([3, 1])
    
    with col_text:
        if current_val:
            st.success(f"### ✅ {label}")
        else:
            st.info(f"### ⚪ {label} (待命)")
            
    with col_btn:
        if is_admin:
            button_label = "關閉" if current_val else "開啟"
            if st.button(button_label, key=key, use_container_width=True):
                # 更新 Firebase 資料
                fb.put('/rally_status', key, not current_val)
                st.rerun()
        else:
            # 一般成員視角
            st.write("") # 保持對齊

st.markdown("---")
if is_admin:
    st.warning("⚡ 目前處於：**管理員模式** (可操控按鈕)")
else:
    st.caption("ℹ️ 目前處於：**成員模式** (僅查看狀態，網頁每 3 秒自動更新)")
