import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import date, datetime, timedelta

# ==========================================
# 配置与常量
# ==========================================
DATA_FILE = "cycle_data.json"  # 升级为 JSON 文件存储

# ==========================================
# 核心逻辑类 (CycleModel)
# ==========================================
class CycleModel:
    """
    处理经期追踪、预测的核心逻辑。
    """
    def __init__(self, age: int):
        self.age = age
        # 根据年龄调整容忍度
        if self.age < 18:
            self.irregularity_tolerance = 5
        elif 18 <= self.age <= 35:
            self.irregularity_tolerance = 3
        else:
            self.irregularity_tolerance = 5

    def analyze_history(self, dates: list):
        """分析历史数据，计算平均周期长度"""
        if not dates:
            return {"avg_length": 28, "std_dev": 0, "history": []}

        # 确保日期排序
        sorted_dates = sorted([datetime.strptime(d, "%Y-%m-%d").date() if isinstance(d, str) else d for d in dates])
        
        cycles_data = []
        lengths = []
        
        # 计算每次周期的间隔
        for i in range(len(sorted_dates) - 1):
            current = sorted_dates[i]
            next_start = sorted_dates[i+1]
            length = (next_start - current).days
            
            # 过滤掉异常数据（比如记录错误的间隔）
            if 15 < length < 100:
                lengths.append(length)
                cycles_data.append({
                    "start_date": current,
                    "end_date": next_start,
                    "length": length
                })
        
        # 如果只有一次记录，无法计算间隔
        if not lengths:
            return {
                "avg_length": 28, 
                "std_dev": 0, 
                "last_date": sorted_dates[-1],
                "history": []
            }

        return {
            "avg_length": float(np.mean(lengths)),
            "std_dev": float(np.std(lengths)),
            "last_date": sorted_dates[-1],
            "history": cycles_data # 返回详细的周期历史
        }

    def predict(self, last_date, avg_len):
        """预测下一次经期和排卵日"""
        if not last_date:
            return None
        
        cycle_len = int(round(avg_len))
        next_period = last_date + timedelta(days=cycle_len)
        ovulation = next_period - timedelta(days=14) # 简易算法：下次经期前14天
        
        today = date.today()
        days_passed = (today - last_date).days + 1
        
        # 判断当前阶段
        if days_passed <= 5: phase = "月经期 (Menstrual)"
        elif days_passed <= (cycle_len - 15): phase = "卵泡期 (Follicular)"
        elif days_passed <= (cycle_len - 13): phase = "排卵期 (Ovulation)"
        elif days_passed < cycle_len: phase = "黄体期 (Luteal)"
        else: phase = "经期推迟 (Delayed)"
            
        return {
            "next_date": next_period,
            "ovulation_date": ovulation,
            "current_phase": phase,
            "day_in_cycle": days_passed
        }

# ==========================================
# 数据管理 (JSON)
# ==========================================
def load_data():
    """加载 JSON 数据，如果不存在则返回默认结构"""
    default_data = {"dates": [], "logs": {}}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_data(data):
    """保存数据到 JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        st.error(f"保存失败: {e}")

# ==========================================
# 界面主程序
# ==========================================
def main():
    st.set_page_config(page_title="CycleTracker Pro", page_icon="🌺", layout="wide")
    
    # CSS 美化
    st.markdown("""
    <style>
    .kpi-card { background-color: #f9f9f9; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #eee; }
    .highlight { color: #e91e63; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

    st.title("🌺 智能周期助手 V2.0")

    # --- 1. 数据初始化 ---
    if 'data' not in st.session_state:
        st.session_state.data = load_data()

    data = st.session_state.data
    period_dates = data.get("dates", [])
    daily_logs = data.get("logs", {})

    # --- 2. 侧边栏：设置与记录 ---
    with st.sidebar:
        st.header("⚙️ 个人设置")
        age = st.slider("年龄", 12, 60, 25)
        
        st.divider()
        st.header("📅 经期记录")
        
        # A. 添加经期开始日
        new_date = st.date_input("记录经期开始日期", value=date.today())
        str_date = new_date.strftime("%Y-%m-%d")
        
        col1, col2 = st.columns(2)
        if col1.button("➕ 标记今天来了"):
            if str_date not in period_dates:
                period_dates.append(str_date)
                period_dates.sort()
                st.session_state.data["dates"] = period_dates
                save_data(st.session_state.data)
                st.success("已记录！")
                st.rerun()
        
        if col2.button("撤销最近一次"):
            if period_dates:
                period_dates.pop()
                st.session_state.data["dates"] = period_dates
                save_data(st.session_state.data)
                st.rerun()

        st.divider()
        st.header("📝 每日打卡")
        # B. 每日症状记录
        log_date = st.date_input("选择打卡日期", value=date.today(), key="log_picker")
        log_key = log_date.strftime("%Y-%m-%d")
        
        # 获取当天的旧记录（如果有）
        today_log = daily_logs.get(log_key, {})
        
        flow = st.select_slider("经期流量", options=["无", "少量", "中等", "大量"], value=today_log.get("flow", "无"))
        pain = st.select_slider("痛经程度", options=["无痛", "轻微", "明显", "剧烈"], value=today_log.get("pain", "无痛"))
        mood = st.selectbox("今日心情", ["平静", "开心", "烦躁", "焦虑", "疲惫"], index=0)
        note = st.text_input("备注", value=today_log.get("note", ""))
        
        if st.button("💾 保存今日日记"):
            st.session_state.data["logs"][log_key] = {
                "flow": flow,
                "pain": pain,
                "mood": mood,
                "note": note
            }
            save_data(st.session_state.data)
            st.success("打卡成功！")

    # --- 3. 核心计算 ---
    model = CycleModel(age)
    stats = model.analyze_history(period_dates)
    
    # 预测逻辑
    prediction = None
    if stats.get("last_date"):
        prediction = model.predict(stats["last_date"], stats["avg_length"])

    # --- 4. 主界面展示 ---
    
    # 顶部仪表盘
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"<div class='kpi-card'>平均周期<br><span class='highlight' style='font-size:24px'>{stats['avg_length']:.1f} 天</span></div>", unsafe_allow_html=True)
    with col2:
        phase_text = prediction['current_phase'] if prediction else "无数据"
        st.markdown(f"<div class='kpi-card'>当前阶段<br><span class='highlight' style='font-size:24px'>{phase_text}</span></div>", unsafe_allow_html=True)
    with col3:
        day_text = f"第 {prediction['day_in_cycle']} 天" if prediction else "--"
        st.markdown(f"<div class='kpi-card'>周期进度<br><span class='highlight' style='font-size:24px'>{day_text}</span></div>", unsafe_allow_html=True)
    with col4:
        next_text = str(prediction['next_date']) if prediction else "--"
        st.markdown(f"<div class='kpi-card'>预计下次<br><span class='highlight' style='font-size:24px'>{next_text}</span></div>", unsafe_allow_html=True)

    st.markdown("---")

    # 两个主要板块：分析 vs 日志
    tab1, tab2 = st.tabs(["📊 周期历史分析", "📖 身体日记"])

    with tab1:
        if stats["history"]:
            st.subheader("历史周期规律")
            # 将历史数据转为 DataFrame 方便展示
            history_df = pd.DataFrame(stats["history"])
            # 格式化一下显示
            display_df = history_df[["start_date", "length"]].copy()
            display_df.columns = ["开始日期", "周期长度 (天)"]
            display_df["开始日期"] = pd.to_datetime(display_df["开始日期"]).dt.strftime('%Y-%m-%d')
            
            # 使用柱状图展示周期波动
            st.bar_chart(display_df.set_index("开始日期"))
            
            st.table(display_df.sort_values("开始日期", ascending=False))
            
            if stats["std_dev"] > 5:
                st.warning(f"⚠️ 你的周期波动较大 (标准差 {stats['std_dev']:.1f} 天)，建议多观察作息。")
            else:
                st.success(f"✅ 你的周期比较规律 (波动 ±{stats['std_dev']:.1f} 天)。")
        else:
            st.info("暂无足够的历史周期数据，请在左侧侧边栏添加至少 2 次经期记录。")

    with tab2:
        st.subheader("我的身体记录")
        if daily_logs:
            # 将日记字典转为 DataFrame
            logs_list = []
            for d, info in daily_logs.items():
                row = {"日期": d}
                row.update(info)
                logs_list.append(row)
            
            logs_df = pd.DataFrame(logs_list)
            logs_df = logs_df.sort_values("日期", ascending=False)
            
            st.dataframe(
                logs_df,
                column_config={
                    "日期": "日期",
                    "flow": "流量",
                    "pain": "痛感",
                    "mood": "心情",
                    "note": "备注"
                },
                use_container_width=True
            )
        else:
            st.write("还没有日记哦，快去左侧打卡吧！")

    # --- Footer ---
    st.markdown("---")
    st.caption("🔒 隐私保护：所有数据以 JSON 格式存储在本地，未上传云端。")

if __name__ == "__main__":
    main()