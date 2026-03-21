# --- 共通描画関数 (凡例を右側に縦表示する修正版) ---
def create_chart(df_list, loc_name, title, chart_height=300):
    df_chart = pd.DataFrame(df_list).melt('時刻', var_name='項目', value_name='人数')
    max_y = max(5, int(df_chart['人数'].max()))
    domain_list, range_list = palettes.get(loc_name, palettes["default"])
    df_chart['draw_order'] = df_chart['項目'].apply(get_order)
    tick_values = [f"{9 + m // 60:02d}:{m % 60:02d}" for m in range(0, 451, 60)] # 1時間刻みにしてスッキリ
    
    chart = alt.Chart(df_chart).mark_area(opacity=0.6, interpolate='monotone').encode(
        x=alt.X('時刻:N', axis=alt.Axis(
            labelAngle=-45, values=tick_values, ticks=True, title=None
        )), 
        y=alt.Y('人数:Q', stack=None, scale=alt.Scale(domain=[0, max_y], clamp=True), title=None), 
        color=alt.Color('項目:N', scale=alt.Scale(domain=domain_list, range=range_list), 
            legend=alt.Legend(
                orient='right', # 凡例を右側に配置
                direction='vertical', # 縦に並べる
                title=None, 
                symbolLimit=20,
                labelFontSize=10
            )
        ),
        order=alt.Order('draw_order:Q', sort='ascending') 
    ).properties(height=chart_height, title=title)
    return chart

# --- 表示切り替えロジック (縦1列に並べる修正版) ---
if loc == "📊 全地点一括（モニタリング）":
    # 縦スクロールを許可するためCSSを少しマイルドに変更
    st.markdown("""<style>html, body, [data-testid="stAppViewContainer"] { overflow-y: auto !important; position: static; }</style>""", unsafe_allow_html=True)
    st.subheader("🌐 全地点モニタリング（縦表示）")
    
    # リストを先に作成
    df_swim, df_trans, df_br, df_fin = [], [], [], []
    for mm in range(0, 451):
        t_str = f"{9 + mm // 60:02d}:{mm % 60:02d}"
        # ... (データ作成ロジックは以前と同じなので中愛) ...
        # ※実際のコードには、以前のget_countsを使ったデータ作成部分をここに含めます

    # 1列で順番に表示（スマホで見やすくなります）
    st.altair_chart(create_chart(df_swim, "スイムエリア", "🌊 スイムエリア（海中）", 250), use_container_width=True)
    st.altair_chart(create_chart(df_trans, "トランジ合算", "⛺ トランジション（A＋B）", 250), use_container_width=True)
    st.altair_chart(create_chart(df_br, "コース合算", "🚴‍♂️🏃‍♂️ コース（バイク＆ラン）", 250), use_container_width=True)
    st.altair_chart(create_chart(df_fin, "フィニッシュ", "🏁 フィニッシュ", 250), use_container_width=True)