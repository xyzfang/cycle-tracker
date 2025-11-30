import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import hashlib
import re
import calendar
import random
import base64
from datetime import date, datetime, timedelta

# ==========================================
# 🎨 UI 美化模块 (V10.6: 像素级复刻您的截图)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@500;700&display=swap');
    
    /* 全局背景：极淡的灰蓝色，完全还原截图背景 */
    .stApp {
        background-color: #f0f4f8;
        font-family: 'Roboto', arial, sans-serif;
    }
    
    /* --- 登录页核心样式 --- */
    .login-wrapper {
        display: flex;
        justify-content: center;
        padding-top: 80px; /* 顶部留白 */
    }
    
    .login-card {
        background-color: white;
        width: 450px;
        min-height: 500px;
        padding: 48px 40px 36px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05); /* 非常淡的阴影 */
        border: 1px solid #dadce0; /* 边框颜色 */
        text-align: center;
    }
    
    /* Logo 样式 */
    .brand-logo {
        font-family: 'Product Sans', Arial, sans-serif;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* 谷歌四色 */
    .c-b { color: #4285F4; }
    .c-r { color: #EA4335; }
    .c-y { color: #FBBC05; }
    .c-g { color: #34A853; }
    
    .login-title {
        color: #202124;
        padding-top: 16px;
        font-size: 24px;
        font-weight: 400;
        line-height: 1.3333;
        margin-bottom: 0;
    }
    
    .login-sub {
        color: #202124;
        font-size: 16px;
        font-weight: 400;
        letter-spacing: .1px;
        line-height: 1.5;
        margin-bottom: 40px;
    }
    
    /* 输入框样式 - 极简矩形框 */
    .stTextInput > div > div > input {
        border: 1px solid #dadce0 !important;
        border-radius: 4px !important;
        padding: 13px 15px !important;
        font-size: 16px !important;
        color: #202124 !important;
        background-color: #fff !important;
    }
    
    /* 输入框聚焦时变蓝 */
    .stTextInput > div > div > input:focus {
        border: 2px solid #1a73e8 !important;
        padding: 12px 14px !important; /* 补偿2px边框 */
        outline: none !important;
    }
    
    /* 隐藏 Label */
    .stTextInput label { display: none; }

    /* 辅助链接 */
    .link-text {
        color: #1a73e8;
        font-weight: 500;
        font-size: 14px;
        text-decoration: none;
        cursor: pointer;
        display: block;
        text-align: left; /* 左对齐 */
        margin-top: 5px;
        margin-bottom: 40px;
    }
    
    .info-text {
        color: #5f6368;
        font-size: 14px;
        line-height: 1.4;
        text-align: left; /* 左对齐 */
        margin-bottom: 40px;
    }

    /* 底部按钮行 */
    .btn-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 30px;
    }
    
    /* 左侧：创建账号 (文字按钮) */
    .create-btn button {
        color: #1a73e8 !important;
        background-color: transparent !important;
        border: none !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 8px 0 !important;
        box-shadow: none !important;
    }
    .create-btn button:hover {
        background-color: #f6fafe !important;
        border-radius: 4px;
        padding: 8px 8px !important;
        margin: 0 -8px !important;
    }
    
    /* 右侧：登录 (蓝色实心按钮) */
    .login-btn button {
        background-color: #1a73e8 !important;
        color: #fff !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 0 24px !important;
        border-radius: 4px !important;
        height: 36px !important;
        line-height: 36px !important;
        border: none !important;
        box-shadow: none !important;
    }
    .login-btn button:hover {
        background-color: #2b7de9 !important;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15) !important;
    }

    /* --- App 内部样式 (保持不变) --- */
    .soft-card { background-color: #ffffff; padding: 20px; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.03); border: 1px solid #f0f0f0; margin-bottom: 15px; }
    .phase-card-menstrual { background: linear-gradient(135deg, #ffcdd2 0%, #ffebee 100%); color: #b71c1c; }
    .phase-card-follicular { background: linear-gradient(135deg, #e1bee7 0%, #f3e5f5 100%); color: #4a148c; }
    .phase-card-ovulatory { background: linear-gradient(135deg, #fff9c4 0%, #fffde7 100%); color: #f57f17; }
    .phase-card-luteal { background: linear-gradient(135deg, #c8e6c9 0%, #e8f5e9 100%); color: #1b5e20; }
    .warm-message { font-family: 'Dancing Script', cursive; font-size: 1.5em; text-align: center; margin-top: 25px; padding-top: 15px; border-top: 1px dashed rgba(0,0,0,0.1); color: rgba(0,0,0,0.6); font-weight: bold; }
    .pet-container { text-align: center; background: linear-gradient(180deg, #fff 0%, #f1f3f5 100%); border-radius: 20px; padding: 20px; border: 1px solid #eee; margin-bottom: 20px; }
    .pet-avatar { font-size: 4em; margin-bottom: 10px; animation: bounce 2s infinite; }
    .pet-status { font-size: 0.9em; color: #666; font-weight: bold; }
    @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
    .calendar-container { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-top: 5px; }
    .calendar-header { text-align: center; font-size: 0.7em; color: #aaa; font-weight: bold; }
    .calendar-day { background: #fff; border-radius: 8px; border: 1px solid #f5f5f5; min-height: 50px; padding: 2px; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; }
    .day-num { font-size: 0.6em; color: #ccc; align-self: flex-start; margin-left: 3px; line-height: 1; }
    .day-today { border: 1.5px solid #ff9a9e; background: #fffafa; }
    .mood-primary-cal { font-size: 1.4em; line-height: 1; margin-top: -2px; }
    .timeline-entry { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px dashed #eee; }
    .timeline-date { width: 50px; text-align: center; font-size: 0.8em; font-weight: bold; color: #888; background: #f8f9fa; border-radius: 8px; padding: 4px; margin-right: 15px; }
    .timeline-mood-big { font-size: 2.2em; margin-right: 15px; }
    .timeline-details { flex: 1; }
    .timeline-sub-moods { font-size: 1.1em; letter-spacing: 3px; }
    .timeline-note { font-size: 0.85em; color: #666; margin-top: 4px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🔐 安全与数据
# ==========================================
DATA_FILE = "cycle_data.json"

class DataManager:
    @staticmethod
    def load_all_data():
        if not os.path.exists(DATA_FILE): return {"users": {}}
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {"users": {}}

    @staticmethod
    def save_all_data(data):
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e: st.error(f"保存失败: {e}")

class AuthSystem:
    @staticmethod
    def make_hashes(p): return hashlib.sha256(str.encode(p)).hexdigest()
    @staticmethod
    def check_hashes(p, h): return AuthSystem.make_hashes(p) == h
    @staticmethod
    def login(u, p):
        d = DataManager.load_all_data()
        if u not in d["users"]: return False
        return AuthSystem.check_hashes(p, d["users"][u]["password"])
    @staticmethod
    def register(u, p):
        d = DataManager.load_all_data()
        if u in d["users"]: return False
        d["users"][u] = {"password": AuthSystem.make_hashes(p), "profile": {"age": 25}, "cycle_data": {"dates": [], "logs": {}}}
        DataManager.save_all_data(d)
        return True

# ==========================================
# 🏥 医疗引擎 (V10.5: 选项库大扩容)
# ==========================================
class MedicalEngine:
    MEDICAL_DB = {
        "ACOG_PMS": "ACOG. (2021). Premenstrual Syndrome (PMS).",
        "WHO_FP": "WHO. (2018). Family Planning.",
        "NUTRITION": "Am J Clin Nutr. (2016). 'Energy Balance'.",
        "ENERGY_STUDY": "J Psychosom Res. (2000). 'Menstrual cycle and voluntary physical activity'."
    }
    
    EMOJI_MAP = {
        "开心": "😆", "自信": "💃", "平静": "🍃", "能量满格": "🔋", "被爱": "🥰", "感恩": "🙏", "高效": "💪",
        "焦虑": "😖", "易怒": "😡", "悲伤": "🌧️", "疲惫": "💤", "脑雾": "🌫️", "社恐": "🫣", "内耗": "🌀", "想哭": "😢", "甚至想死": "🥀",
        "嘴馋": "😋", "痛": "🩹", "浮肿": "🎈", "无": ""
    }
    
    SYMPTOMS_OPTIONS = [
        "无", "痛经 (Cramps)", "头痛 (Headache)", "乳房胀痛 (Breast Pain)", "腰酸背痛", 
        "腹胀/水肿 (Bloating)", "长痘 (Acne)", "食欲大增", "便秘", "腹泻",
        "失眠", "嗜睡", "关节痛", "潮热/盗汗", "白带异常"
    ]

    HABITS_OPTIONS = [
        "无", "💊 止痛药", "💊 短效避孕药", "💊 维生素/补剂", "🍵 红糖姜茶", 
        "🔥 热水袋/热敷", "😴 早睡", "🦉 熬夜", "🏃‍♀️ 运动/健身", 
        "🧘‍♀️ 瑜伽/冥想", "🍺 饮酒", "☕ 咖啡因", "🍰 高糖饮食", "💓 性生活"
    ]
    
    PET_STATUS = {
        "menstrual": {"emoji": "🐱💤", "text": "嘘... 猫咪在充电 (能量低谷)", "bg": "#ffebee"},
        "follicular": {"emoji": "🐱🧶", "text": "猫咪想玩球！(精力恢复)", "bg": "#f3e5f5"},
        "ovulatory": {"emoji": "🐱👑", "text": "本喵是最美的！(魅力巅峰)", "bg": "#fffde7"},
        "luteal": {"emoji": "😾🐟", "text": "别惹我，只想要小鱼干 (情绪敏感)", "bg": "#e8f5e9"}
    }

    WARM_MESSAGES = [
        "你比自己想象的更强大，今天也要加油哦！✨", "无论今天过得怎样，都请好好爱自己。💖",
        "深呼吸，一切都会好起来的。🍃", "倾听身体的声音，它是你最好的朋友。🌸",
        "你的光芒，独一无二。🌟", "允许自己休息，也是一种能力。💤", "今天的你，也很棒！👍"
    ]

    def __init__(self, age): self.age = age
    def get_random_message(self): return random.choice(self.WARM_MESSAGES)
    def determine_phase(self, day, cycle_len):
        ovulation = cycle_len - 14
        if day <= 5: return "月经期 (Menstrual)", "menstrual"
        elif day < (ovulation - 2): return "卵泡期 (Follicular)", "follicular"
        elif day <= (ovulation + 2): return "排卵期 (Ovulatory)", "ovulatory"
        elif day <= cycle_len: return "黄体期 (Luteal)", "luteal"
        else: return "周期推迟 (Delayed)", "luteal"
    def get_pet_status(self, phase_key): return self.PET_STATUS.get(phase_key, self.PET_STATUS["menstrual"])

    def generate_report(self, phase, symptoms, primary_mood, secondary_moods, bbt, meds):
        p_mood = primary_mood if primary_mood is not None else "无"
        s_moods = secondary_moods if secondary_moods is not None else []
        meds_list = meds if meds is not None else []
        
        report = {"diagnosis": "", "mechanism": "", "diet": "", "lifestyle": "", "citation": ""}
        all_moods = [p_mood] + s_moods
        neg_moods = [m for m in all_moods if m in ["焦虑", "易怒", "悲伤", "疲惫", "内耗", "想哭", "甚至想死"]]
        
        med_feedback = []
        if "💊 止痛药" in meds_list: med_feedback.append("已记录服药，建议不要空腹服用。")
        if "☕ 咖啡因" in meds_list and phase == "luteal": med_feedback.append("黄体期摄入咖啡因可能加重焦虑。")
        if "🦉 熬夜" in meds_list: med_feedback.append("注意补觉，熬夜会影响激素平衡。")
        med_feedback_str = " ".join(med_feedback)
        
        if phase == "luteal" and neg_moods:
            report["diagnosis"] = "⚠️ **PMS 风险**"
            report["mechanism"] = "雌激素骤降影响血清素。"
            report["diet"] = "补充镁、维生素B6。"
            report["lifestyle"] = "增加光照，轻瑜伽。"
            report["citation"] = self.MEDICAL_DB['ACOG_PMS']
        else:
            report["diagnosis"] = f"当前处于 {phase}"
            report["mechanism"] = "激素水平波动正常。"
            report["diet"] = "保持均衡饮食。"
            report["lifestyle"] = f"规律作息。{med_feedback_str}"
            report["citation"] = self.MEDICAL_DB['WHO_FP']
        return report

# ==========================================
# 📄 报告生成器
# ==========================================
class ReportGenerator:
    @staticmethod
    def generate_html_report(username, user_data, avg_len):
        today = date.today().strftime("%Y-%m-%d")
        logs = user_data["cycle_data"]["logs"]
        dates = user_data["cycle_data"]["dates"]
        total_logs = len(logs)
        symptoms_count = {}
        for k, v in logs.items():
            for s in v.get("symptoms", []): 
                if s != "无": symptoms_count[s] = symptoms_count.get(s, 0) + 1
        top_symptoms = sorted(symptoms_count.items(), key=lambda x: x[1], reverse=True)[:3]
        symptom_str = ", ".join([f"{k}({v}次)" for k,v in top_symptoms]) if top_symptoms else "无明显高频症状"

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; padding: 40px; color: #333; }}
                h1 {{ color: #e91e63; border-bottom: 2px solid #e91e63; padding-bottom: 10px; }}
                h2 {{ color: #555; margin-top: 30px; }}
                .stat-box {{ background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .footer {{ margin-top: 50px; font-size: 0.8em; color: #999; text-align: center; }}
            </style>
        </head>
        <body>
            <h1>CycleHealth 医疗辅助报告</h1>
            <p><b>用户:</b> {username} &nbsp;&nbsp; <b>生成日期:</b> {today}</p>
            <h2>1. 周期概况</h2>
            <div class="stat-box">
                <p><b>平均周期长度:</b> {avg_len} 天</p>
                <p><b>记录经期次数:</b> {len(dates)} 次</p>
                <p><b>最后一次经期:</b> {dates[-1] if dates else '无数据'}</p>
            </div>
            <h2>2. 症状统计 (近6个月)</h2>
            <div class="stat-box">
                <p><b>高频症状:</b> {symptom_str}</p>
                <p><b>总记录天数:</b> {total_logs} 天</p>
            </div>
            <p style="font-size: 0.9em; color: #666;">本报告不构成医疗诊断。参考: ACOG, WHO Guidelines.</p>
        </body>
        </html>
        """
        return html

    @staticmethod
    def get_download_link(html_string, filename="medical_report.html"):
        b64 = base64.b64encode(html_string.encode()).decode()
        return f'<a href="data:text/html;base64,{b64}" download="{filename}" style="text-decoration:none; background:#e91e63; color:white; padding:8px 15px; border-radius:20px; font-weight:bold;">📄 下载医疗报告</a>'

# ==========================================
# 🗓️ 日历生成器
# ==========================================
class CalendarGenerator:
    @staticmethod
    def generate_compact_html(year, month, logs):
        cal = calendar.monthcalendar(year, month)
        today = date.today()
        parts = ['<div class="calendar-container">']
        for w in ['一','二','三','四','五','六','日']: parts.append(f'<div class="calendar-header">{w}</div>')
        for week in cal:
            for day in week:
                if day == 0: parts.append('<div class="calendar-day" style="border:none;"></div>')
                else:
                    d_str = f"{year}-{month:02d}-{day:02d}"
                    is_today = (today.year==year and today.month==month and today.day==day)
                    cls = "day-today" if is_today else ""
                    entry = logs.get(d_str, {})
                    p_mood = entry.get("primary_mood")
                    if not p_mood and entry.get("moods"): p_mood = entry["moods"][0]
                    emoji_html = ""
                    if p_mood and p_mood != "无":
                        em = MedicalEngine.EMOJI_MAP.get(p_mood, "")
                        emoji_html = f'<div class="mood-primary-cal">{em}</div>'
                    parts.append(f'<div class="calendar-day {cls}"><div class="day-num">{day}</div>{emoji_html}</div>')
        parts.append('</div>')
        return "".join(parts)

# ==========================================
# 🖥️ 主界面 (V10.6)
# ==========================================
def main_app_ui(username):
    inject_custom_css()
    all_data = DataManager.load_all_data()
    user = all_data["users"][username]
    c_data = user["cycle_data"]
    
    if "cal_year" not in st.session_state:
        st.session_state.cal_year = date.today().year
        st.session_state.cal_month = date.today().month

    today = date.today()
    if not c_data["dates"]:
        phase_name="等待记录"; phase_key="menstrual"; day=1; avg=28; next_p="--"
    else:
        dates = sorted([datetime.strptime(d,"%Y-%m-%d").date() for d in c_data["dates"]])
        last = dates[-1]
        diffs = [(dates[i+1]-dates[i]).days for i in range(len(dates)-1)]
        valid = [d for d in diffs if 15 < d < 60]
        avg = int(np.mean(valid)) if valid else 28
        day = (today - last).days + 1
        phase_name, phase_key = MedicalEngine(25).determine_phase(day, avg)
        next_p = (last + timedelta(days=avg)).strftime('%m月%d日')

    med_engine = MedicalEngine(25)
    
    # Sidebar
    with st.sidebar:
        pet = med_engine.get_pet_status(phase_key)
        st.markdown(f"""
        <div class="pet-container" style="background:{pet['bg']}">
            <div class="pet-avatar">{pet['emoji']}</div>
            <div class="pet-status">{pet['text']}</div>
        </div>
        """, unsafe_allow_html=True)
        st.header(f"👋 {username}")
        if st.button("🚪 登出"): st.session_state.logged_in = False; st.rerun()
        st.divider()
        report_html = ReportGenerator.generate_html_report(username, user, avg)
        st.markdown(ReportGenerator.get_download_link(report_html), unsafe_allow_html=True)
        st.divider()
        st.subheader("📅 最近经期")
        if c_data["dates"]:
            df = pd.DataFrame({"日期": c_data["dates"]})
            df["日期"] = pd.to_datetime(df["日期"]).dt.date
            edited = st.data_editor(df.sort_values("日期", ascending=False).head(3), key="sb_editor", use_container_width=True, hide_index=True)
            if st.button("更新"):
                dates = edited["日期"].astype(str).tolist()
                c_data["dates"] = sorted(list(set(dates)))
                DataManager.save_all_data(all_data); st.rerun()
        else:
            if st.button("记录今天"): 
                c_data["dates"].append(date.today().strftime("%Y-%m-%d"))
                DataManager.save_all_data(all_data); st.rerun()

    # Main
    col_left, col_right = st.columns([1.6, 1]) 
    with col_left:
        warm_msg = med_engine.get_random_message()
        cls = f"phase-card-{phase_key}"
        st.markdown(f"""
        <div class="soft-card {cls}" style="min-height: 220px; display:flex; flex-direction:column; justify-content:center;">
            <h3 style="margin:0; opacity:0.8;">当前正处于</h3>
            <h1 style="font-size: 3.5em; margin: 10px 0;">{phase_name}</h1>
            <div style="display:flex; justify-content:space-between; align-items:end;">
                <div><span style="font-size:1.2em; font-weight:bold;">Day {day}</span> <span style="opacity:0.7;"> / {avg} 天周期</span></div>
                <div style="text-align:right;"><div style="font-size:0.8em;">预计下次</div><div style="font-size:1.5em; font-weight:bold;">{next_p}</div></div>
            </div>
            <div class="warm-message">{warm_msg}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📝 今日身心记录")
        st.markdown('<hr style="margin-top: -10px; margin-bottom: 20px; border: 0; border-top: 1px solid #eee;">', unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="soft-card">', unsafe_allow_html=True)
            if "show_analysis" not in st.session_state: st.session_state.show_analysis = False
            
            with st.form("daily"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**情绪监测**")
                    pm = st.selectbox("🌟 主要", ["无"]+list(MedicalEngine.EMOJI_MAP.keys()))
                    sm = st.multiselect("☁️ 次要", ["无"]+list(MedicalEngine.EMOJI_MAP.keys()))
                    energy = st.slider("🔋 今日能量值", 0, 100, 60)
                    
                with c2:
                    st.markdown("**生理 & 习惯**")
                    sym = st.multiselect("症状", MedicalEngine.SYMPTOMS_OPTIONS)
                    meds = st.multiselect("💊 药箱/习惯", MedicalEngine.HABITS_OPTIONS)
                
                note = st.text_input("备注")
                
                if st.form_submit_button("💾 保存并分析"):
                    k = today.strftime("%Y-%m-%d")
                    safe_sm = [s for s in sm if s != "无"]
                    safe_sym = [s for s in sym if s != "无"]
                    safe_meds = [m for m in meds if m != "无"]
                    c_data["logs"][k] = {"primary_mood": pm, "secondary_moods": safe_sm, "energy": energy, "symptoms": safe_sym, "meds": safe_meds, "note": note}
                    DataManager.save_all_data(all_data)
                    st.session_state.show_analysis = True
                    st.session_state.last_inp = {"pm": pm, "sm": safe_sm, "sym": safe_sym, "meds": safe_meds}
                    st.rerun()

            if st.session_state.show_analysis:
                st.divider()
                i = st.session_state.last_inp
                rep = med_engine.generate_report(phase_key, i["sym"], i["pm"], i["sm"], 0, i["meds"])
                st.info(f"🧬 **{rep['diagnosis']}**: {rep['mechanism']}")
                st.success(f"🥗 {rep['diet']} | 🧘‍♀️ {rep['lifestyle']}")
                if st.button("收起"): st.session_state.show_analysis=False; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="soft-card" style="padding: 10px 15px;">', unsafe_allow_html=True)
        cc1, cc2, cc3 = st.columns([1, 2, 1])
        if cc1.button("◀", key="prev"):
            st.session_state.cal_month -= 1
            if st.session_state.cal_month == 0: st.session_state.cal_month=12; st.session_state.cal_year-=1
            st.rerun()
        with cc2: st.markdown(f"<div style='text-align:center; font-weight:bold; padding-top:5px;'>{st.session_state.cal_year}年 {st.session_state.cal_month}月</div>", unsafe_allow_html=True)
        if cc3.button("▶", key="next"):
            st.session_state.cal_month += 1
            if st.session_state.cal_month == 13: st.session_state.cal_month=1; st.session_state.cal_year+=1
            st.rerun()
        cal_html = CalendarGenerator.generate_compact_html(st.session_state.cal_year, st.session_state.cal_month, c_data["logs"])
        st.markdown(cal_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("#### 📔 心情日记")
        st.markdown('<div class="soft-card" style="padding: 0 20px;">', unsafe_allow_html=True)
        logs = c_data["logs"]
        sorted_keys = sorted(logs.keys(), reverse=True)[:10]
        if not sorted_keys:
            st.caption("暂无日记，快去记录今天吧~")
        else:
            for d_str in sorted_keys:
                entry = logs[d_str]
                p_mood = entry.get("primary_mood")
                if not p_mood and entry.get("moods"): p_mood = entry["moods"][0]
                s_moods = entry.get("secondary_moods", [])
                if not s_moods and entry.get("moods"): s_moods = entry["moods"][1:]
                note = entry.get("note", "")
                meds = entry.get("meds", [])
                
                p_emo = MedicalEngine.EMOJI_MAP.get(p_mood, "😶") if p_mood and p_mood!="无" else "😶"
                s_emo_str = "".join([MedicalEngine.EMOJI_MAP.get(m, "") for m in s_moods])
                meds_str = " ".join([f"<span style='font-size:0.8em; background:#eee; padding:2px 5px; border-radius:4px;'>{m}</span>" for m in meds])
                d_fmt = datetime.strptime(d_str, "%Y-%m-%d").strftime("%m.%d")
                st.markdown(f"""
                <div class="timeline-entry">
                    <div class="timeline-date">{d_fmt}</div>
                    <div class="timeline-mood-big">{p_emo}</div>
                    <div class="timeline-details">
                        <div class="timeline-sub-moods">{s_emo_str} {meds_str}</div>
                        <div class="timeline-note">{note if note else "无备注"}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="CycleHealth V10.6", page_icon="🌺", layout="wide")
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        inject_custom_css()
        # V10.6: 像素级复刻
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-card">
                <div class="brand-logo">
                    <span class="c-b">C</span><span class="c-r">y</span><span class="c-y">c</span><span class="c-b">l</span><span class="c-g">e</span><span class="c-r">H</span>ealth
                </div>
                <h1 class="login-title">登录</h1>
                <div class="login-sub">使用您的 CycleHealth 账号</div>
        """, unsafe_allow_html=True)
        
        u = st.text_input("Account", key="login_u", label_visibility="collapsed", placeholder="账号")
        st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True)
        p = st.text_input("Password", type="password", key="login_p", label_visibility="collapsed", placeholder="密码")
        
        st.markdown("""
                <div class="link-text">忘记了邮箱？</div>
                <div class="info-text">您用的不是自己的电脑？请使用访客模式无痕登录。<a href="#" style="color:#1a73e8;text-decoration:none;">了解详情</a></div>
                <div class="btn-row">
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([1,1])
        with c1:
            st.markdown('<div class="create-btn">', unsafe_allow_html=True)
            if st.button("创建账号"):
                if AuthSystem.register(u,p): st.success("成功")
                else: st.error("已存在")
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="login-btn">', unsafe_allow_html=True)
            if st.button("登录"):
                if AuthSystem.login(u,p): st.session_state.logged_in=True; st.session_state.username=u; st.rerun()
                else: st.error("错误")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div></div></div>', unsafe_allow_html=True)
    else: main_app_ui(st.session_state.username)

if __name__ == "__main__":
    main()