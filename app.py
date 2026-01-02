import streamlit as st
import requests
import time
from streamlit_autorefresh import st_autorefresh

# 1. 初始化設定
FIREBASE_URL = "https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/.json"
st.set_page_config(page_title="WOS Command Center", page_icon="⚔️", layout="wide")

# 2. 權限與刷新邏輯
is_admin = st.query_params.get("role") == "admin"

# 只有成員端 (User) 會 0.1 秒自動刷新
if not is_admin:
    st_autorefresh(interval=500, key="user_refresh")
    if st.sidebar.button("手動刷新 (Manual Refresh)"):
        st.rerun()
else:
    st.sidebar.info("管理模式：自動刷新已關閉 | Admin Mode: Auto-refresh OFF")
    if st.sidebar.button("手動刷新 (Manual Refresh)"):
        st.rerun()

st.title("⚔️ WOS 戰爭指揮系統 | War Command")

# 3. 從 Firebase 抓取即時資料
try:
    response = requests.get(FIREBASE_URL)
    data = response.json() if response.json() else {}
    status_data = data.get('rally_status', {})
    timer_data = data.get('timers', {})
except:
    status_data = {}
    timer_data = {}

# 定義核心顯示組件
def render_unit(key, display_name, show_input=True):
    current_val = status_data.get(key, False)
    start_time = timer_data.get(key, {}).get('start_at', 0)
    march_sec = timer_data.get(key, {}).get('march_sec', 0)
    
    with st.container(border=True):
        if current_val:
            elapsed = time.time() - start_time
            rally_limit = 302  # 5分鐘倒數
            total_limit = rally_limit + march_sec
            
            if elapsed < rally_limit:
                rem = int(rally_limit - elapsed)
                timer_text = f"⏳ Rally: {rem//60:02d}:{rem%60:02d}"
                bg_color = "#2e7d32" # 綠色
            elif elapsed < total_limit:
                rem = int(total_limit - elapsed)
                timer_text = f"🏹 March: {rem}s"
                bg_color = "#ef6c00" # 橘色
            else:
                timer_text = "💥 Arrived"
                bg_color = "#c62828" # 紅色
            
            # 顯示亮燈標題與計時
            st.markdown(f"""
                <div style="background-color:{bg_color}; padding:10px; border-radius:5px;">
                    <h2 style="color:white; margin:0;">{display_name}</h2>
                    <h3 style="color:white; margin:0;">{timer_text}</h3>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h2 style='color:gray;'>⚪ {display_name} (Standby)</h2>", unsafe_allow_html=True)

        # 管理員控制介面
        if is_admin:
            st.write("---")
            if show_input:
                m_sec = st.number_input(f"March Sec (行軍秒)", min_value=0, max_value=600, key=f"in_{key}", value=march_sec)
            else:
                m_sec = 0
                
            if st.button(f"切換狀態 (Switch) {display_name}", key=f"btn_{key}", use_container_width=True):
                new_status = not current_val
                base_path = f"https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/rally_status/{key}.json"
                time_path = f"https://wos-svs-default-rtdb.asia-southeast1.firebasedatabase.app/timers/{key}.json"
                
                requests.put(base_path, json=new_status)
                if new_status:
                    requests.put(time_path, json={"start_at": time.time(), "march_sec": m_sec})
                st.rerun()

# 4. 畫面佈局
# --- 第一排：主要集結組 ---
st.subheader("🔥 主要集結手 | Primary Rally Leaders")
col1, col2, col3 = st.columns(3)
with col1: render_unit("gillard", "Gillard")
with col2: render_unit("rex", "Rex")
with col3: render_unit("jing", "Jing")

st.markdown("<br>", unsafe_allow_html=True)

# --- 第二排：城堡調度 (獨立一排) ---
st.subheader("🏰 城堡支援 | Castle Support")
render_unit("castle", "更換駐守 | Switch Castle | 성 주둔 교체", show_input=False)

st.markdown("<br>", unsafe_allow_html=True)

# --- 第三排：反集結組 (拆開排列，讓 Admin 好輸入) ---
st.subheader("🛡️ 反集結組 | Counter-Rally Group")
# 這裡使用 columns 確保 User 端看的時候是橫的，但 Admin 端有獨立控制空間
col_a, col_b, col_c = st.columns(3)
with col_a: render_unit("joann", "Joann")
with col_b: render_unit("jamin", "Jamin")
with col_c: render_unit("leejun", "LeeJun")
