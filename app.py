import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

# --- 画面設定 ---
st.set_page_config(page_title="タテトラ2026 決定版", layout="wide")
st.markdown("""
    <style>
    /* 全体表示の時はスクロールできるように設定 */
    [data-testid="stAppViewContainer"] { overflow-y: auto !important; }
    .main .block-container { padding: 1rem !important; }
    section[data-testid="stSidebar"] { width: 150px !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def get_sim_data():
    waves = [
        {"name": "G1 (STD)", "start": 15, "size": 196, "type": "STD"},
        {"name": "G2 (STD)", "start": 35, "size": 80,  "type": "STD"},
        {"name": "G3 (STD)", "start": 90, "size": 147, "type": "STD"},
        {"name": "G4 (STD)", "start": 120, "size": 181, "type": "STD"},
        {"name": "G5 (STD女子)", "start": 160, "size": 75,  "type": "STD"},
        {"name": "G6 (SP男子)", "start": 215, "size": 152, "type": "SP/CHA"},
        {"name": "G7 (SP女子)", "start": 230, "size": 46,  "type": "SP/CHA"},
        {"name": "G8 (CHA)", "start": 250, "size": 65,  "type": "SP/CHA"},
        {"name": "G9 (JrA)", "start": 295, "size": 48,  "type": "Jr"},
        {"name": "G10 (JrB)", "start": 320, "size": 50, "type": "Jr"},
        {"name": "G11 (スイミー)", "start": 350, "size": 47, "type": "Jr"},
    ]
    data = []
    np.random.seed(42)
    for w in waves:
        for i in range(w["size"]):
            delay = (i // 10) * (10 / 60)
            st_t = w["start"] + delay
            p_p = max(11, np.random.normal(17, 3.5)) 
            t1, t2 = 4, 4 
            if w["type"] == "STD":
                s_e = st_t + p_p * 2
                b_d, r_d = max(55, np.random.normal(80, 15)), max(35, np.random.normal(55, 10))
                g1, g2, g3, g4 = s_e+t1, s_e+t1+b_d, s_e+t1+b_d+t2, s_e+t1+b_d+t2+r_d
                p = {"w_name": w["name"], "type": "STD", "swim_area": (st_t, s_e), "t_a": [(s_e, g1), (g2, g3)], "t_b_p": (g2, g2+2), "t_b": [], "bike": (g1, g2), "run": (g3, g4), "fin": (g4, g4+15)}
            elif w["type"] == "SP/CHA":
                s_e = st_t + p_p * 1.0
                b_d, r_d = max(25, np.random.normal(45, 8)), max(15, np.random.normal(25, 5))
                b_st, b_en, r_st, r_en = s_e+t1, s_e+t1+b_d, s_e+t1+b_d+t2, s_e+t1+b_d+t2+r_d
                p = {"w_name": w["name"], "type": "SP/CHA", "swim_area": (st_t, s_e), "t_a": [], "t_b_p": None, "t_b": [(s_e, b_st), (b_en, r_st)], "bike": (b_st, b_en), "run": (r_st, r_en), "fin": (r_en, r_en+15)}
            else:
                s_e = st_t + p_p * 0.5
                b_d = max(2, np.random.normal(3, 1)) if "スイミー" in w["name"] else max(10, np.random.normal(20, 5))
                r_d = max(1, np.random.normal(2, 0.5)) if "スイミー" in w["name"] else max(5, np.random.normal(12, 3))
                b_st, b_en, r_st, r_en = s_e+t1, s_e+t1+b_d, s_e+t1+b_d+t2, s_e+t1+b_d+t2+r_d
                p = {"w_name": w["name"], "type": "Jr", "swim_area": (st_t, s_e), "t_a": [(s_e, b_st), (b_en, r_st)], "t_b_p": None, "t_b": [], "bike": (b_st, b_en), "run": (r_st, r_en), "fin": (r_en, r_en+15)}
            data.append(p)
    return data

pts = get_sim_data()
loc = st.sidebar.selectbox("📌 地点切替", ["📊 全地点一括（モニタリング）", "スイムエリア", "トランジA", "トランジB", "バイクエリア", "ランエリア", "フィニッシュ"])

all_groups = ["G1 (STD)", "G2 (STD)", "G3 (STD)", "G4 (STD)", "G5 (STD女子)", "G6 (SP男子)", "G7 (SP女子)", "G8 (CHA)", "G9 (JrA)", "G10 (JrB)", "G11 (スイミー)"]
ta_util = all_groups[:5] + all_groups[8:]
tb_util = all_groups[5:8]

def get_counts(target_m, l, p_list):
    if l == "スイムエリア": return {"海中合計(水)": sum(1 for p in p_list if p["swim_area"][0] <= target_m <= p["swim_area"][1])}
    if l == "トランジA": return {g: sum(1 for p in p_list if p["w_name"] == g and any(s[0] <= target_m <= s[1] for s in p["t_a"])) for g in ta_util}
    if l == "トランジB":
        res = {"STD通過(青)": sum(1 for p in p_list if p["type"]=="STD" and p["t_b_p"] and p["t_b_p"][0] <= target_m <= p["t_b_p"][1])}
        res.update({g: sum(1 for p in p_list if p["w_name"] == g and any(s[0] <= target_m <= s[1] for s in p["t_b"])) for g in tb_util})
        return res
    if l == "フィニッシュ": return {g: sum(1 for p in p_list if p["w_name"] == g and p["fin"][0] <= target_m <= p["fin"][1]) for g in all_groups}
    if l in ["バイクエリア", "ランエリア"]:
        res = {"大人": 0, "JrA": 0, "JrB": 0, "スイミー": 0}
        for p in p_list:
            target = p["bike"] if l == "バイクエリア" else p["run"]
            if target[0] <= target_m <= target[1]:
                if "JrA" in p["w_name"]: res["JrA"] += 1
                elif "JrB" in p["w_name"]: res["JrB"] += 1
                elif "スイミー" in p["w_name"]: res["スイミー"] += 1
                else: res["大人"] += 1
        return res

palettes = {
    "スイムエリア": (["海中合計(水)"], ["#00BFFF"]),
    "トランジA": (ta_util, ["#1f77b4", "#ff7f0e", "#8a2be2", "#00ced1", "#d2691e", "#FF0000", "#3CB44B", "#FF1493"]),
    "トランジB": (["STD通過(青)"] + tb_util, ["#00008B", "#17becf", "#e377c2", "#bcbd22"]),
    "バイクエリア": (["大人", "JrA", "JrB", "スイミー"], ["#9ACD32", "#FF0000", "#3CB44B", "#FF1493"]),
    "ランエリア": (["大人", "JrA", "JrB", "スイミー"], ["#FF8C00", "#FF0000", "#3CB44B", "#FF1493"]),
    "フィニッシュ": (all_groups, ["#1f77b4", "#ff7f0e", "#8a2be2", "#00ced1", "#d2691e", "#17becf", "#e377c2", "#bcbd22", "#FF0000", "#3CB44B", "#FF1493"]),
    "コース合算": (["大人(バイク)", "JrA(バイク)", "JrB(バイク)", "スイミー(バイク)", "大人(ラン)", "JrA(ラン)", "JrB(ラン)", "スイミー(ラン)"], ["#9ACD32", "#FF0000", "#3CB44B", "#FF1493", "#FF8C00", "#8B0000", "#006400", "#C71585"]),
    "トランジ合算": (ta_util + ["STD通過(青)"] + tb_util, ["#1f77b4", "#ff7f0e", "#8a2be2", "#00ced1", "#d2691e", "#FF0000", "#3CB44B", "#FF1493", "#00008B", "#17becf", "#e377c2", "#bcbd22"])
}

def create_chart(df_list, loc_name, title, h=300):
    df = pd.DataFrame(df_list).melt('時刻', var_name='項目', value_name='人数')
    dom, ran = palettes.get(loc_name, (all_groups, palettes["フィニッシュ"][1]))
    t_vals = [f"{9+m//60:02d}:{m%60:02d}" for m in range(0, 451, 60)]
    return alt.Chart(df).mark_area(opacity=0.6, interpolate='monotone').encode(
        x=alt.X('時刻:N', axis=alt.Axis(labelAngle=-45, values=t_vals, title=None)),
        y=alt.Y('人数:Q', stack=None, title=None),
        color=alt.Color('項目:N', scale=alt.Scale(domain=dom, range=ran), legend=alt.Legend(orient='right', title=None, labelFontSize=11)),
    ).properties(height=h, title=title)

if loc == "📊 全地点一括（モニタリング）":
    st.subheader("🌐 全エリア状況一括")
    df_s, df_t, df_br, df_f = [], [], [], []
    for mm in range(0, 451):
        t = f"{9+mm//60:02d}:{mm%60:02d}"
        rs, rta, rtb, rb, rr, rf = get_counts(mm, "スイムエリア", pts), get_counts(mm, "トランジA", pts), get_counts(mm, "トランジB", pts), get_counts(mm, "バイクエリア", pts), get_counts(mm, "ランエリア", pts), get_counts(mm, "フィニッシュ", pts)
        rs["時刻"], rf["時刻"] = t, t
        df_s.append(rs); df_f.append(rf)
        rt = {**rta, **rtb}; rt["時刻"] = t; df_t.append(rt)
        rbr = {"大人(バイク)": rb["大人"], "JrA(バイク)": rb["JrA"], "JrB(バイク)": rb["JrB"], "スイミー(バイク)": rb["スイミー"], "大人(ラン)": rr["大人"], "JrA(ラン)": rr["JrA"], "JrB(ラン)": rr["JrB"], "スイミー(ラン)": rr["スイミー"], "時刻": t}
        df_br.append(rbr)
    st.altair_chart(create_chart(df_s, "スイムエリア", "🌊 スイム（海中）"), use_container_width=True)
    st.altair_chart(create_chart(df_t, "トランジ合算", "⛺ トランジション（A+B）"), use_container_width=True)
    st.altair_chart(create_chart(df_br, "コース合算", "🚴‍♂️🏃‍♂️ コース（バイク＆ラン）"), use_container_width=True)
    st.altair_chart(create_chart(df_f, "フィニッシュ", "🏁 フィニッシュ"), use_container_width=True)
else:
    df_l = []
    for mm in range(0, 451):
        r = get_counts(mm, loc, pts); r["時刻"] = f"{9+mm//60:02d}:{mm%60:02d}"; df_l.append(r)
    st.altair_chart(create_chart(df_l, loc, f"📊 {loc}"), use_container_width=True)
