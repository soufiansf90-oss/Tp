import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import calendar
import base64
from io import BytesIO
from PIL import Image

# --- 1. SETTINGS & ADVANCED NEON UI ---
st.set_page_config(page_title="369 SHADOW V43", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Inter:wght@400;600&display=swap');
    
    .stApp { background: #05070a; color: #e6edf3; font-family: 'Inter', sans-serif; }
    
    /* Welcome Message */
    .welcome-text { font-family: 'Orbitron'; color: #00d4ff; font-size: 1.4rem; text-align: center; margin-bottom: 25px; text-shadow: 0 0 15px rgba(0,212,255,0.6); letter-spacing: 2px; }
    
    /* Animation 0.5s */
    .content-fade { animation: slideUp 0.5s ease-out; }
    @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

    /* Sidebar Navigation Styling */
    [data-testid="stSidebar"] { background-color: #080b10; border-right: 2px solid #00d4ff33; }
    
    /* Custom Sidebar Radio Buttons */
    div[data-testid="stSidebar"] .stRadio > label { display: none; } /* Hide default label */
    
    div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 15px;
        padding-top: 20px;
    }

    /* تحسين شكل أزرار الاختيار في الجنب */
    div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 212, 255, 0.2);
        padding: 15px 20px !important;
        border-radius: 12px !important;
        transition: 0.3s all;
        width: 100%;
        color: #8b949e;
        font-family: 'Orbitron';
        text-transform: uppercase;
        font-size: 0.8rem;
    }

    div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        background: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid #00d4ff !important;
        color: #00d4ff !important;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
    }

    /* Journal Styling */
    .journal-win { border-left: 5px solid #34d399 !important; background: rgba(52, 211, 153, 0.05) !important; }
    .journal-loss { border-left: 5px solid #ef4444 !important; background: rgba(239, 68, 68, 0.05) !important; }
    .journal-be { border-left: 5px solid #fbbf24 !important; background: rgba(251, 191, 36, 0.05) !important; }

    /* Performance Grid */
    .perf-card { background: rgba(22, 27, 34, 0.6); border: 1px solid rgba(0, 212, 255, 0.1); padding: 20px; border-radius: 15px; text-align: center; transition: 0.3s; }
    .perf-card:hover { border-color: #00d4ff; box-shadow: 0 0 15px rgba(0, 212, 255, 0.2); }
    .perf-val { font-size: 1.8rem; font-weight: bold; font-family: 'Orbitron'; color: #e6edf3; }
    .perf-label { font-size: 0.75rem; color: #00d4ff; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; }

    div[data-testid="stMetric"] { background: rgba(22, 27, 34, 0.7) !important; border: 1px solid #30363d !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE ---
conn = sqlite3.connect('elite_v43.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, 
              outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, setup TEXT, image TEXT)''')
try: c.execute("ALTER TABLE trades ADD COLUMN image TEXT")
except: pass
conn.commit()

# --- 3. DATA PREP ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
current_balance, daily_net_pnl, initial_bal = 0.0, 0.0, 1000.0

if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    df = df.sort_values(by=['date_dt', 'id'])
    initial_bal = df['balance'].iloc[0]
    df['cum_pnl'] = df['pnl'].cumsum()
    df['equity_curve'] = initial_bal + df['cum_pnl']
    current_balance = df['equity_curve'].iloc[-1]
    daily_net_pnl = df[df['date'] == datetime.now().strftime('%Y-%m-%d')]['pnl'].sum()

# --- 4. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('<div style="text-align:center; padding: 20px 0;"><span style="font-family:Orbitron; color:#00ffcc; font-size:1.5rem; text-shadow: 0 0 10px #00ffcc66;">SHADOW SYSTEM</span></div>', unsafe_allow_html=True)
    st.divider()
    choice = st.radio("MENU", ["TERMINAL", "CALENDAR", "PERFORMANCE", "ANALYZERS", "JOURNAL"])
    st.divider()
    st.metric("EQUITY STATUS", f"${current_balance:,.2f}", f"{daily_net_pnl:+.2f} USD")

# --- 5. TOP WELCOME ---
st.markdown('<div class="welcome-text">WHAT\'S UP SHADOW, LET\'S SEE WHAT HAPPENED TODAY.</div>', unsafe_allow_html=True)

# --- 6. MAIN CONTENT ---
st.markdown('<div class="content-fade">', unsafe_allow_html=True)

if choice == "TERMINAL":
    c1, c2 = st.columns([1, 2.3])
    with c1:
        with st.form("entry_form"):
            st.markdown("### 📥 LOG ENTRY")
            d_in = st.date_input("Date", datetime.now())
            asset = st.text_input("Pair", "NAS100").upper()
            res = st.selectbox("Outcome", ["WIN", "LOSS", "BE"])
            p_val = st.number_input("P&L ($)", value=0.0)
            r_val = st.number_input("RR Ratio", value=0.0)
            setup = st.text_input("Setup").upper()
            mind = st.selectbox("Mindset", ["Focused", "Impulsive", "Revenge", "Bored"])
            img_file = st.file_uploader("Screenshot", type=['png', 'jpg', 'jpeg'])
            if st.form_submit_button("LOCK TRADE"):
                img_data = base64.b64encode(img_file.read()).decode() if img_file else None
                c.execute("INSERT INTO trades (date, pair, outcome, pnl, rr, balance, mindset, setup, image) VALUES (?,?,?,?,?,?,?,?,?)",
                          (str(d_in), asset, res, p_val, r_val, current_balance, mind, setup, img_data))
                conn.commit()
                st.rerun()
    with c2:
        if not df.empty:
            fig = go.Figure(go.Scatter(x=list(range(len(df))), y=df['equity_curve'], mode='lines+markers', line=dict(color='#00ffcc', width=3, shape='spline'), fill='tonexty', fillcolor='rgba(0,255,204,0.05)'))
            fig.update_layout(template="plotly_dark", height=480, title="ACCOUNT GROWTH CURVE", transition={'duration': 500})
            st.plotly_chart(fig, use_container_width=True)

elif choice == "CALENDAR":
    if not df.empty:
        today = datetime.now()
        cal = calendar.monthcalendar(today.year, today.month)
        cols = st.columns(7)
        for i, d_name in enumerate(["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]):
            cols[i].markdown(f"<p style='text-align:center; color:#00d4ff; font-family:Orbitron; font-size:0.7rem;'>{d_name}</p>", unsafe_allow_html=True)
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0: cols[i].markdown('<div class="cal-card" style="opacity:0.1"></div>', unsafe_allow_html=True)
                else:
                    d_str = datetime(today.year, today.month, day).strftime('%Y-%m-%d')
                    day_df = df[df['date'] == d_str]
                    p_sum = day_df['pnl'].sum()
                    style = "cal-win" if p_sum > 0 else "cal-loss" if p_sum < 0 else "cal-be" if len(day_df)>0 else ""
                    cols[i].markdown(f'<div class="cal-card {style}"><div style="font-size:0.7rem; color:#8b949e;">{day}</div><div style="font-weight:bold; font-size:0.9rem;">${p_sum:,.0f}</div></div>', unsafe_allow_html=True)

elif choice == "PERFORMANCE":
    if not df.empty:
        wins, losses = df[df['pnl'] > 0], df[df['pnl'] < 0]
        wr = (len(wins)/len(df))*100 if len(df)>0 else 0
        pf = wins['pnl'].sum() / abs(losses['pnl'].sum()) if not losses.empty else 0
        
        # Organized Grid
        st.markdown("#### ⚡ PRIMARY METRICS")
        g1, g2, g3, g4 = st.columns(4)
        for col, label, val in zip([g1,g2,g3,g4], ["Win Rate", "Profit Factor", "Avg RR", "Net P&L"], [f"{wr:.1f}%", f"{pf:.2f}", f"{df['rr'].mean():.2f}", f"${df['pnl'].sum():,.0f}"]):
            col.markdown(f'<div class="perf-card"><div class="perf-val">{val}</div><div class="perf-label">{label}</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>#### 🛡️ RISK & STREAKS", unsafe_allow_html=True)
        g5, g6, g7, g8 = st.columns(4)
        # Quick streak calculation
        outcomes = [1 if x > 0 else -1 if x < 0 else 0 for x in df['pnl']]
        mw, ml, cw, cl = 0, 0, 0, 0
        for r in outcomes:
            if r == 1: cw += 1; cl = 0; mw = max(mw, cw)
            elif r == -1: cl += 1; cw = 0; ml = max(ml, cl)

        for col, label, val in zip([g5,g6,g7,g8], ["Best Day", "Worst Day", "Max Win Streak", "Max Loss Streak"], [f"${df['pnl'].max():,.0f}", f"${df['pnl'].min():,.0f}", f"{mw} 🔥", f"{ml} 💀"]):
            col.markdown(f'<div class="perf-card"><div class="perf-val">{val}</div><div class="perf-label">{label}</div></div>', unsafe_allow_html=True)

elif choice == "ANALYZERS":
    if not df.empty:
        fig_rr = go.Figure(data=[go.Scatter(x=list(range(len(df))), y=df['rr'], mode='lines+markers', line=dict(color='#fbbf24', width=2))])
        fig_rr.update_layout(template="plotly_dark", title="RR CONSISTENCY", transition={'duration': 500})
        st.plotly_chart(fig_rr, use_container_width=True)
        st.plotly_chart(px.bar(df.groupby('mindset')['pnl'].sum().reset_index(), x='mindset', y='pnl', title="PSYCHOLOGY IMPACT", template="plotly_dark"), use_container_width=True)

elif choice == "JOURNAL":
    if not df.empty:
        st.markdown("### 📜 TRADE ARCHIVE")
        for idx, row in df.sort_values('id', ascending=False).iterrows():
            # تحديد لون الصفقة بناء على النتيجة
            j_class = "journal-win" if row['pnl'] > 0 else "journal-loss" if row['pnl'] < 0 else "journal-be"
            
            with st.container():
                st.markdown(f'<div class="{j_class}" style="padding:10px; border-radius:0 10px 10px 0; margin-bottom:10px;">', unsafe_allow_html=True)
                with st.expander(f"● {row['date']} | {row['pair']} | P&L: ${row['pnl']:,.2f} | Setup: {row['setup']}"):
                    tx, im = st.columns([1, 2])
                    with tx:
                        st.write(f"**Outcome:** {row['outcome']}")
                        st.write(f"**RR:** {row['rr']} | **Mindset:** {row['mindset']}")
                    with im:
                        if row['image']: st.image(base64.b64decode(row['image']), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
