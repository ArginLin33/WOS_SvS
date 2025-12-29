import streamlit as st
import requests
import time

# 1. 初始化設定
FIREBASE_URL = "https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/.json"
st.set_page_config(page_title="WOS Command Center", page_icon="⚔️", layout="wide")

# 2. 權限與刷新按鈕
is_admin = st.query_params.get("role") == "admin"
if st.button("🔄 刷新最新狀態 / Refresh Status", use_container_width=True):
    st.rerun()

st.title("⚔️ WOS 戰爭指揮系統")

# 3. 定義項目群組
top_leaders = {
    "gillard": {"en": "Gillard", "zh": "Gillard", "ko": "Gillard"},
    "rex": {"en": "Rex", "zh": "Rex", "ko": "Rex"},
    "jing": {"en": "Jing", "zh": "Jing", "ko": "Jing"}
}

middle_items = {
    "castle": {"en": "Switch Castle Member", "zh": "更換駐守成員", "ko": "성 주둔 멤버 교체"}
}

bottom_leaders = {
    "jamin": {"en": "Jamin", "zh": "Jamin", "ko": "Jamin"},
    "joann": {"en": "Joann", "zh": "Joann", "ko": "Joann"},
    "leejing": {"en": "LeeJing", "zh": "LeeJing", "ko": "LeeJing"}
}

# 4. 從 Firebase 抓取資料
try:
    response = requests.get(FIREBASE_URL)
    data = response.json() if response.json() else {}
    status_data = data.get('rally_status', {})
    timer_data = data.get('timers', {})
except:
    status_data = {}
    timer_data = {}

def render_item(key, labels, show_timer=True):
    current_val = status_data.get(key, False)
    start_time = timer_data.get(key, {}).get('start_at', 0)
    march_sec = timer_data.get(key, {}).get('march_sec', 0)
    
    col_info, col_ctrl = st.columns([3, 1])
    
    with col_info:
        if current_val:
            # 計算時間邏輯
            elapsed = time.time() - start_time
            rally_limit = 302 # 5分鐘 + 2秒延遲
            total_limit = rally_limit + march_sec
            
            if elapsed < rally_limit:
                rem = int(rally_limit - elapsed)
                timer_text = f"⏳ 集結中 (Rallying): {rem//60:02d}:{rem%60:02d}"
            elif elapsed < total_limit:
                rem = int(total_limit - elapsed)
                timer_text = f"🏹 行軍中 (Marching): {rem}s"
            else:
                timer_text = "💥 已抵達/待命 (Arrived)"
                
            st.success(f"### ✅ {labels['en']} | {labels['zh']} | {labels['ko']}\n**{timer_text}**")
        else:
            st.info(f"### ⚪ {labels['en']} | {labels['zh']} | {labels['ko']}")

    with col_ctrl:
        if is_admin:
            # 行軍時間輸入
            if show_timer:
                m_sec = st.number_input("行軍秒(s)", min_value=0, max_value=600, key=f"in_{key}", value=march_sec)
            
            if st.button("切換 (Switch)", key=f"btn_{key}", use_container_width=True):
                new_status = not current_val
                # 更新狀態與時間戳
                base_path = f"https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/rally_status/{key}.json"
                time_path = f"https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/timers/{key}.json"
                
                requests.put(base_path, json=new_status)
                if new_status:
                    requests.put(time_path, json={"start_at": time.time(), "march_sec": m_sec if show_timer else 0})
                st.rerun()

# 5. 分區渲染
st.subheader("📍 主要集結手 (Primary Leaders)")
for k, l in top_leaders.items(): render_item(k, l)

st.divider()
st.subheader("🏰 城堡調度 (Castle Support)")
for k, l in middle_items.items(): render_item(k, l, show_timer=False)

st.divider()
st.subheader("📍 支援集結手 (Support Leaders)")
for k, l in bottom_leaders.items(): render_item(k, l)
