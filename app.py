import streamlit as st
import pandas as pd
import json
import os
import datetime
import time
import yt_dlp
import wave
import numpy as np
import base64
import plotly.graph_objects as go

STATS_FILE = "vtuber_ranking.json"
LOGO_FILE = "logo.png" 
BEAR_FILE = "しろくま_透過_余白削除.png" 
SETTINGS_FILE = "settings.json"

st.set_page_config(page_title="きりっぱ！ - Vみどころサーチ", page_icon=BEAR_FILE, layout="wide")

st.markdown("""
<style>
    [data-testid="stHeader"] {
        background-color: rgba(200, 240, 255, 0.5) !important;
        backdrop-filter: blur(5px) !important; 
    }

    .stApp {
        background-color: transparent !important;
        background-image: 
            url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cg fill='white' opacity='0.6'%3E%3Ccircle cx='50' cy='55' r='33'/%3E%3Ccircle cx='22' cy='25' r='16'/%3E%3Ccircle cx='78' cy='25' r='16'/%3E%3C/g%3E%3C/svg%3E"),
            linear-gradient(180deg, #FFF4F7 0%, #FFD6E4 100%) !important;
        background-size: 80px 80px, auto !important; 
        background-attachment: fixed !important; 
    }

    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.85) !important;
        border-right: 3px dashed #FFB6C1;
    }

    p, span, div, h1, h2, h3, h4, h5, h6, label {
        color: #444444 !important;
    }

    .stNumberInput label, .stTextInput label, .stMultiSelect label {
        background-color: rgba(255, 255, 255, 0.8) !important;
        padding: 4px 10px !important;
        border-radius: 8px !important;
        display: inline-block;
        font-weight: bold !important;
    }

    .stTextInput div[data-baseweb="input"], 
    .stMultiSelect div[data-baseweb="select"],
    .stTextArea textarea {
        border: 2px solid #87CEEB !important;
        border-radius: 12px !important;
        background-color: #FFFFFF !important;
        color: #444444 !important;
        box-shadow: 0 2px 5px rgba(135, 206, 235, 0.2) !important;
    }
    
    div[data-baseweb="base-input"],
    div[data-baseweb="base-input"] > input,
    .stMultiSelect div[data-baseweb="select"] > div {
        background-color: transparent !important;
        border: none !important;
        color: #444444 !important;
    }

    .stTextInput div[data-baseweb="input"]:focus-within, 
    .stMultiSelect div[data-baseweb="select"]:focus-within,
    .stTextArea textarea:focus {
        border: 2px solid #FF96C5 !important;
        box-shadow: 0 4px 8px rgba(255, 105, 180, 0.3) !important;
    }

    span[data-baseweb="tag"] {
        background-color: #FFF0F5 !important;
        color: #FF1493 !important;
        border: 1px solid #FFB6C1 !important;
    }

    div.stButton > button {
        background: linear-gradient(45deg, #FFB6C1, #FF69B4) !important;
        color: white !important;
        border-radius: 30px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(255, 182, 193, 0.4) !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
        width: 100%;
        transition: all 0.3s ease;
    }

    .stCodeBlock, pre, code {
        background-color: rgba(255, 255, 255, 0.8) !important;
        color: #444444 !important;
        border: 2px dashed #87CEEB !important;
        border-radius: 10px !important;
    }

    div.stDownloadButton > button {
        background: #FFFFFF !important;
        color: #FF69B4 !important;
        border: 2px solid #FFB6C1 !important;
        border-radius: 20px !important;
        padding: 5px 15px !important;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 350px !important; 
    }
    
    .fixed-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: rgba(255, 255, 255, 0.95);
        padding: 15px 10px; 
        border-top: 2px dashed #FFB6C1;
        text-align: center;
        z-index: 999999; 
    }
    
    /* 💡 ご意見フォームボタンのホバーエフェクト用CSS */
    .feedback-btn {
        background: linear-gradient(45deg, #87CEEB, #FF96C5);
        color: white !important;
        padding: 12px;
        border-radius: 30px;
        text-align: center;
        display: block;
        text-decoration: none;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(255, 105, 180, 0.3);
        transition: all 0.3s ease;
        margin-top: 10px;
    }
    .feedback-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(255, 105, 180, 0.4);
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

if os.path.exists(LOGO_FILE):
    with open(LOGO_FILE, "rb") as f:
        b64_encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;"><img src="data:image/png;base64,{b64_encoded}" style="width: 65%; max-width: 700px; pointer-events: none;"></div>""", unsafe_allow_html=True)

st.markdown('<p style="text-align: center; font-weight: bold; margin-bottom: 30px;">配信のコメントの密度や配信の音量から盛り上がったシーンを特定します！</p>', unsafe_allow_html=True)

loaded_settings = {
    "keywords": ["草", "w", "笑", "てぇてぇ", "たすかる", "！？", "え", "やば"],
    "neg_keywords": ["おかえり", "ただいま", "おつ", "お疲れ", "待機", "わこつ"],
    "use_audio": True,
    "use_repeat": True
}
if os.path.exists(SETTINGS_FILE):
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            loaded_settings.update(json.load(f))
    except:
        pass

if "custom_tags" not in st.session_state: st.session_state.custom_tags = []
if "custom_neg_tags" not in st.session_state: st.session_state.custom_neg_tags = []

def add_tag():
    new_tag = st.session_state.new_tag_input.strip()
    if new_tag and new_tag not in st.session_state.custom_tags: st.session_state.custom_tags.append(new_tag)
    st.session_state.new_tag_input = "" 

def add_neg_tag():
    new_tag = st.session_state.new_neg_tag_input.strip()
    if new_tag and new_tag not in st.session_state.custom_neg_tags: st.session_state.custom_neg_tags.append(new_tag)
    st.session_state.new_neg_tag_input = "" 

st.sidebar.markdown("### 🎯 抽出キーワード")
preset_keywords = list(set(["草", "w", "笑", "てぇてぇ", "たすかる", "！？", "え", "やば", "かわいい", "神", "助かる", "放送事故"] + loaded_settings["keywords"]))
selected_keywords = st.sidebar.multiselect("基本のキーワード", options=preset_keywords, default=loaded_settings["keywords"])
st.sidebar.text_input("独自のキーワード", key="new_tag_input", on_change=add_tag)
if st.session_state.custom_tags: st.session_state.custom_tags = st.sidebar.multiselect("追加した独自のキーワード", options=st.session_state.custom_tags, default=st.session_state.custom_tags)
final_keywords = selected_keywords + st.session_state.custom_tags

st.sidebar.markdown("---")
st.sidebar.markdown("### ⛔ 除外キーワード（ノイズ除去）")
preset_neg_keywords = list(set(["おかえり", "ただいま", "おつ", "お疲れ", "待機", "ノシ", "バイバイ", "こん", "わこつ", "初見"] + loaded_settings["neg_keywords"]))
selected_neg_keywords = st.sidebar.multiselect("基本の除外キーワード", options=preset_neg_keywords, default=loaded_settings["neg_keywords"])
st.sidebar.text_input("独自の除外キーワード", key="new_neg_tag_input", on_change=add_neg_tag)
if st.session_state.custom_neg_tags: st.session_state.custom_neg_tags = st.sidebar.multiselect("追加した独自の除外キーワード", options=st.session_state.custom_neg_tags, default=st.session_state.custom_neg_tags)
final_negative_keywords = selected_neg_keywords + st.session_state.custom_neg_tags

st.sidebar.markdown("---")
use_audio_analysis = st.sidebar.checkbox("🎙️ 音量（絶叫・爆笑）も加味して抽出する", value=loaded_settings["use_audio"])
use_repeat_analysis = st.sidebar.checkbox("🔄 コメントの連投（弾幕）も加味して抽出する", value=loaded_settings["use_repeat"])

st.sidebar.markdown("---")
if st.sidebar.button("💾 今の設定をデフォルトとして保存"):
    new_settings = {
        "keywords": final_keywords,
        "neg_keywords": final_negative_keywords,
        "use_audio": use_audio_analysis,
        "use_repeat": use_repeat_analysis
    }
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_settings, f, ensure_ascii=False, indent=4)
    st.sidebar.success("✅ 設定を保存しました！次回からもこの状態で起動します。")

st.sidebar.markdown("---")
exclude_ranking = st.sidebar.checkbox("この解析をランキングに登録しない", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("👑 切り抜き回数ランキング")
ranking_period = st.sidebar.radio("集計期間", ["今日", "今月", "すべて（累計）"], horizontal=True)

if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        try: stats = json.load(f)
        except: stats = {}
    if stats:
        today = datetime.date.today()
        filtered_stats = []
        for name, data in stats.items():
            history = data.get("history", []) if isinstance(data, dict) else ["2000-01-01"] * data
            valid_count = 0
            for date_str in history:
                try:
                    d = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                    if ranking_period == "今日" and d == today: valid_count += 1
                    elif ranking_period == "今月" and d.year == today.year and d.month == today.month: valid_count += 1
                    elif ranking_period == "すべて（累計）": valid_count += 1
                except: pass
            if valid_count > 0: filtered_stats.append((name, valid_count))
        filtered_stats.sort(key=lambda x: x[1], reverse=True)
        for rank, (name, count) in enumerate(filtered_stats[:5], 1):
            icon = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"{rank}位"
            st.sidebar.markdown(f"**{icon}**：{name} ({count}回)")
    else: st.sidebar.write("まだデータがありません。")
else: st.sidebar.write("まだデータがありません。")

# 💡 ここが新規追加のご意見フォームセクションです！
st.sidebar.markdown("---")
st.sidebar.subheader("💬 ご意見・ご要望")
st.sidebar.caption("バグの報告や「こんな機能が欲しい！」などのリクエストをお待ちしています🐾")
st.sidebar.markdown(
    '<a href="https://forms.gle/h4UYXqLvSd79uPAbA" target="_blank" class="feedback-btn">📝 ご意見フォームを開く</a>',
    unsafe_allow_html=True
)

st.sidebar.markdown("<div style='height: 150px;'></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
video_url = st.text_input("YouTubeのアーカイブURLを入力してください👇")

def time_to_minutes(t_str):
    if not isinstance(t_str, str): return 0
    parts = t_str.split(":")
    if len(parts) == 3: return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 2: return int(parts[0])
    return 0

if st.button("解析を開始する") or "df_all" in st.session_state:
    if "current_url" not in st.session_state or st.session_state.current_url != video_url:
        st.session_state.current_url = video_url
        if "df_all" in st.session_state: del st.session_state.df_all
        if "top_peaks" in st.session_state: del st.session_state.top_peaks
        if "plot_df" in st.session_state: del st.session_state.plot_df
        if "audio_volumes" in st.session_state: del st.session_state.audio_volumes
        if "comment_counts" in st.session_state: del st.session_state.comment_counts
        
    if video_url != "":
        video_id = ""
        if "v=" in video_url: video_id = video_url.split("v=")[1][:11]
        elif "youtu.be/" in video_url: video_id = video_url.split("youtu.be/")[1][:11]
        elif "/live/" in video_url: video_id = video_url.split("/live/")[1][:11]
        elif "/shorts/" in video_url: video_id = video_url.split("/shorts/")[1][:11]

        if len(video_id) == 11:
            if "df_all" not in st.session_state:
                st.info(f"動画ID「{video_id}」の解析を開始します...")
                status_text = st.empty()
                progress_bar = st.progress(0.0)
                ydl_opts_chat = {'skip_download': True, 'writesubtitles': True, 'subtitleslangs': ['live_chat'], 'outtmpl': f'{video_id}', 'quiet': True, 'no_warnings': True, 'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None}
                
                try:
                    status_text.warning("💬 コメントデータを解析中…")
                    progress_bar.progress(0.1)
                    channel_name = "不明なチャンネル"
                    with yt_dlp.YoutubeDL(ydl_opts_chat) as ydl:
                        info_dict = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
                        channel_name = info_dict.get('uploader', '不明なチャンネル')
                    
                    filename = f"{video_id}.live_chat.json"
                    raw_chat_data = []
                    if os.path.exists(filename):
                        with open(filename, 'r', encoding='utf-8') as f:
                            for line in f:
                                try:
                                    data = json.loads(line)
                                    action = data.get('replayChatItemAction', {}).get('actions', [{}])[0]
                                    item = action.get('addChatItemAction', {}).get('item', {})
                                    renderer = item.get('liveChatTextMessageRenderer', {})
                                    if not renderer: continue
                                    time_text = renderer.get('timestampText', {}).get('simpleText', '0:00')
                                    runs = renderer.get('message', {}).get('runs', [])
                                    text = "".join([r.get('text', '') for r in runs if 'text' in r])
                                    if text: raw_chat_data.append({"time_str": time_text, "message": text})
                                except: pass
                        os.remove(filename)
                    
                    if not raw_chat_data:
                        st.error("❌ チャットデータが見つかりませんでした。")
                    else:
                        audio_volumes = {}
                        if use_audio_analysis:
                            status_text.warning("🎙️ 音声データをダウンロード中...")
                            progress_bar.progress(0.4)
                            audio_file = f"{video_id}_audio.wav"
                            ydl_opts_audio = {'format': 'bestaudio/best', 'outtmpl': f'{video_id}_audio.%(ext)s', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'wav'}], 'quiet': True, 'no_warnings': True, 'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None}
                            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl: ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
                            if os.path.exists(audio_file):
                                status_text.warning("📊 音量を波形解析中...")
                                progress_bar.progress(0.7)
                                try:
                                    with wave.open(audio_file, 'rb') as wf:
                                        fr = wf.getframerate(); nc = wf.getnchannels(); nf = wf.getnframes(); audio_data = wf.readframes(nf)
                                        audio_array = np.frombuffer(audio_data, dtype=np.int16)
                                        if nc > 1: audio_array = audio_array.reshape(-1, nc).max(axis=1)
                                        spm = fr * 60
                                        for i in range(0, len(audio_array), spm):
                                            chunk = audio_array[i:i+spm]
                                            if len(chunk) > 0:
                                                peak = np.max(np.abs(chunk))
                                                audio_volumes[i // spm] = 20 * np.log10(peak / 32768.0) if peak > 0 else -60.0
                                except: pass
                                os.remove(audio_file)
                        
                        status_text.warning("🧠 AIハイブリッド解析中...")
                        progress_bar.progress(0.9)
                        df_all = pd.DataFrame(raw_chat_data)
                        if final_negative_keywords:
                            neg_pattern = '|'.join(final_negative_keywords)
                            df_all = df_all[~df_all['message'].str.contains(neg_pattern, case=False, na=False)]
                        df_all["minute"] = df_all["time_str"].apply(time_to_minutes)
                        df_f = df_all[df_all['message'].str.contains('|'.join(final_keywords), case=False, na=False)] if final_keywords else df_all
                        comment_counts = df_f.groupby("minute").size()
                        rep_counts = df_all.groupby(["minute", "message"]).size().groupby("minute").max()
                        
                        scores = {}
                        for minute in df_all["minute"].unique():
                            score = float(comment_counts.get(minute, 0))
                            if use_repeat_analysis and rep_counts.get(minute, 0) >= 3: score += float(rep_counts.get(minute, 0)) * 1.5
                            if score > 0:
                                if use_audio_analysis and audio_volumes:
                                    vf = max(0.1, audio_volumes.get(minute, -60) + 60)
                                    scores[minute] = score * (vf ** 1.5)
                                else: scores[minute] = score

                        if scores:
                            top_peaks = pd.Series(scores).nlargest(5)
                            status_text.success(f"✨ 取得・解析完了！ ({len(raw_chat_data)}件)")
                            progress_bar.progress(1.0)
                            if not exclude_ranking:
                                today_str = datetime.date.today().strftime("%Y-%m-%d")
                                if not os.path.exists(STATS_FILE):
                                    with open(STATS_FILE, "w", encoding="utf-8") as f: json.dump({}, f)
                                with open(STATS_FILE, "r", encoding="utf-8") as f:
                                    try: saved_stats = json.load(f)
                                    except: saved_stats = {}
                                if channel_name not in saved_stats: saved_stats[channel_name] = {"history": []}
                                saved_stats[channel_name]["history"].append(today_str)
                                with open(STATS_FILE, "w", encoding="utf-8") as f: json.dump(saved_stats, f, ensure_ascii=False, indent=4)

                            st.session_state.df_all = df_all
                            st.session_state.top_peaks = top_peaks
                            st.session_state.audio_volumes = audio_volumes
                            st.session_state.comment_counts = comment_counts
                            
                            max_min = df_all["minute"].max()
                            plot_df = pd.DataFrame({"minute": range(max_min + 1)})
                            plot_df["comment"] = plot_df["minute"].map(lambda m: comment_counts.get(m, 0))
                            
                            max_cmt = plot_df["comment"].max()
                            if max_cmt > 0:
                                scale_factor = 50.0 / max_cmt
                                plot_df["comment_scaled"] = plot_df["comment"] * scale_factor
                            else:
                                plot_df["comment_scaled"] = plot_df["comment"]

                            plot_df["audio_scaled"] = plot_df["minute"].map(
                                lambda m: max(0, (audio_volumes.get(m, -60) + 8) * (60.0 / 8.0)) if use_audio_analysis and audio_volumes else 0
                            )
                            st.session_state.plot_df = plot_df
                            st.session_state.max_min = max_min

                        else: st.warning("シーンが見つかりませんでした。")
                except Exception as e: st.error(f"エラーが発生しました: {e}")
                
            if "plot_df" in st.session_state:
                plot_df = st.session_state.plot_df
                top_peaks = st.session_state.top_peaks
                df_all = st.session_state.df_all
                max_min = st.session_state.max_min

                st.markdown('<h3 style="color:#FF69B4; margin-top: 10px; margin-bottom: 0px;">📈 感情ヒートマップ</h3>', unsafe_allow_html=True)
                st.caption("気になる波形の「点」をクリックすると、その時間が下のプレビュー枠にセットされます！右上の（＋/ー）ボタンでズーム可能です。")
                
                fig = go.Figure()
                
                if use_audio_analysis and st.session_state.audio_volumes:
                    fig.add_trace(go.Scatter(
                        x=plot_df["minute"], y=plot_df["audio_scaled"], 
                        fill='tozeroy', mode='lines+markers', name='音量（絶叫度）', 
                        line=dict(color='#FF4B4B', width=2),
                        marker=dict(size=4, opacity=0.5), 
                        fillcolor='rgba(255, 75, 75, 0.3)',
                        hovertemplate='絶叫スコア: %{y:.1f}<extra></extra>'
                    ))
                fig.add_trace(go.Scatter(
                    x=plot_df["minute"], y=plot_df["comment_scaled"], 
                    customdata=plot_df["comment"], 
                    fill='tozeroy', mode='lines+markers', name='コメント密度', 
                    line=dict(color='#00C9A7', width=2),
                    marker=dict(size=5), 
                    fillcolor='rgba(0, 201, 167, 0.4)',
                    hovertemplate='コメント数: %{customdata} 件/分<extra></extra>'
                ))

                circle_nums = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤"}
                annotations = []
                for rank, (pm, sc) in enumerate(top_peaks.items(), 1):
                    cn = circle_nums.get(rank, str(rank))
                    y_val = max(
                        plot_df.loc[plot_df["minute"]==pm, "audio_scaled"].values[0] if use_audio_analysis else 0, 
                        plot_df.loc[plot_df["minute"]==pm, "comment_scaled"].values[0]
                    )
                    annotations.append(dict(
                        x=pm, y=y_val,
                        text=f"{cn}", 
                        showarrow=True, arrowhead=0, arrowcolor="#FF1493", arrowwidth=2,
                        font=dict(size=20, color="#FF1493", family="Arial Black"),
                        ax=0, ay=-35
                    ))

                fig.update_layout(
                    clickmode='event+select',
                    dragmode='pan', 
                    annotations=annotations,
                    xaxis=dict(title="時間（分）", fixedrange=False, gridcolor='rgba(255, 182, 193, 0.3)'),
                    yaxis=dict(title="相対的な盛り上がり度", fixedrange=True, gridcolor='rgba(255, 182, 193, 0.3)', showticklabels=False),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(255, 255, 255, 0.6)',
                    hovermode="x unified",
                    height=350,
                    margin=dict(l=10, r=10, t=40, b=10),
                    legend=dict(
                        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
                        bgcolor="rgba(240, 240, 240, 0.95)", 
                        bordercolor="rgba(200, 200, 200, 0.8)",
                        borderwidth=1,
                        font=dict(color="#333333", size=13) 
                    )
                )

                selected_points = st.plotly_chart(
                    fig, 
                    use_container_width=True, 
                    config={
                        'scrollZoom': False, 
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': [
                            'zoom2d', 'pan2d', 'select2d', 'lasso2d', 
                            'autoScale2d', 'resetScale2d', 
                            'hoverClosestCartesian', 'hoverCompareCartesian', 
                            'toggleSpikelines', 'toImage'
                        ]
                    },
                    on_select="rerun" 
                )

                clicked_minute = 0
                if selected_points and "selection" in selected_points and selected_points["selection"].get("points"):
                    clicked_minute = int(selected_points["selection"]["points"][0]["x"])

                st.markdown('<h4 style="color: #FF1493; margin-top: 10px;">🔍 気になる波形をクリックして直接チェック！</h4>', unsafe_allow_html=True)
                
                col_a, col_b = st.columns([1.5, 1])
                with col_a:
                    st.info("⬇︎グラフをクリックで気になるシーンをチェック⬇︎")
                    check_min = st.number_input("チェックしたい時間（分）", min_value=0, max_value=int(max_min), value=clicked_minute, step=1)
                    start_sec = check_min * 60
                    h, r = divmod(start_sec, 3600); m, s = divmod(r, 60); t_format = f"{h}:{m:02}:{s:02}" if h > 0 else f"{m}:{s:02}"
                    custom_link = f"https://youtu.be/{video_id}?t={start_sec}"
                    
                    st.markdown(f"<br>**[▶️ YouTubeのサイトで {t_format} から開く]({custom_link})**", unsafe_allow_html=True)
                with col_b:
                    try:
                        st.video(f"https://www.youtube.com/watch?v={video_id}", start_time=start_sec)
                    except:
                        st.video(f"https://www.youtube.com/watch?v={video_id}")

                st.markdown('<h3 style="color:#FF69B4; margin-top: 30px;">🏆 おすすめシーン5選</h3>', unsafe_allow_html=True)
                for rank, (pm, sc) in enumerate(top_peaks.items(), 1):
                    cn = circle_nums.get(rank, str(rank))
                    youtube_link = f"https://youtu.be/{video_id}?t={max(0, (pm * 60) - 45)}"
                    h, r = divmod(max(0, (pm * 60) - 45), 3600); m, s = divmod(r, 60); tf = f"{h}:{m:02}:{s:02}" if h > 0 else f"{m}:{s:02}"
                    st.markdown(f"#### シーン{cn}： [▶️ {tf} から再生する]({youtube_link})")
                    st.info(" / ".join(df_all[df_all["minute"] == pm]["message"].tolist()[:20])) 
                    csv_data = df_all[df_all["minute"] == pm][["time_str", "message"]].to_csv(index=False).encode('utf-8-sig') 
                    st.download_button(label=f"📥 シーン{cn}のチャットログをCSVで保存", data=csv_data, file_name=f"scene{rank}_{pm}min.csv", mime="text/csv", key=f"dl_{rank}")
                    st.write(" ") 

        else: st.error("URLからIDが見つかりませんでした。")
    else: st.warning("URLを入力してください！")

st.markdown("<br><br>", unsafe_allow_html=True)

bear_img_html = ""
if os.path.exists(BEAR_FILE):
    with open(BEAR_FILE, "rb") as f: bear_b64 = base64.b64encode(f.read()).decode()
    bear_img_html = f'<div style="position: absolute; right: 20px; bottom: 0px; width: 190px; z-index: 2;"><img src="data:image/png;base64,{bear_b64}" style="width: 100%; object-fit: contain; pointer-events: none; display: block;"></div>'

st.markdown(f"""
<div style="background-color: rgba(255, 255, 255, 0.95); padding: 30px 40px; border-radius: 20px; border: 2px dashed #FF69B4; margin-bottom: 20px; position: relative;">
    <div style="margin-right: 200px; position: relative; z-index: 1;">
        <h3 style="color: #333; margin-top: 0; margin-bottom: 15px; font-size: 22px; font-weight: bold;">🎨 【開発者からのお知らせ】</h3>
        <p style="color: #444; font-size: 16px; line-height: 1.8; margin-bottom: 20px;">
            ダウンロードしたCSVデータをFinal Cut Proで一瞬でテロップ化できる、<b>「FCP専用テロップパック」</b>を販売中です！<br>
            無料でお試しいただける体験版も公開していますので、ぜひ動画編集の時短に活用してみてください！
        </p>
        <a href="https://shirokuma-edit.booth.pm/" target="_blank" style="background-color: #FFB6C1; color: #007AFF !important; padding: 12px 30px; border-radius: 30px; display: inline-block; text-decoration: none; font-weight: bold; box-shadow: 0 4px 10px rgba(255, 182, 193, 0.4); font-size: 16px;">👉 FCP専用テロップパックの詳細・無料版はこちら</a>
    </div>
    {bear_img_html}
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="fixed-footer">
    <span style="font-size: 13px; color: #FF69B4; font-weight:bold;">✨作者のガチ愛用デスク環境✨</span><br>
    <div style="display: flex; justify-content: center; align-items: center; gap: 15px; margin-top: 8px; flex-wrap: wrap;">

<div>
<a href="https://hb.afl.rakuten.co.jp/ichiba/53c126d5.7554f1b2.53c126d6.3c9763d5/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fpixiogaming%2Fpsw1s-outlet%2F&link_type=pict&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0Iiwic2l6ZSI6IjEyOHgxMjgiLCJuYW0iOjEsIm5hbXAiOiJyaWdodCIsImNvbSI6MSwiY29tcCI6ImRvd24iLCJwcmljZSI6MSwiYm9yIjoxLCJjb2wiOjEsImJidG4iOjEsInByb2QiOjAsImFtcCI6ZmFsc2V9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hgb/53c126d5.7554f1b2.53c126d6.3c9763d5/?me_id=1410833&item_id=10000184&pc=https%3A%2F%2Fthumbnail.image.rakuten.co.jp%2F%400_mall%2Fpixiogaming%2Fcabinet%2Foutlet%2Fpsw1s-outlet.jpg%3F_ex%3D128x128&s=128x128&t=pict" border="0" style="margin:2px" alt="" title=""></a>
</div>

<div>
<a href="https://hb.afl.rakuten.co.jp/ichiba/53c26d5b.4838841e.53c26d5c.7370c7d7/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fbiccamera%2F4573661274715%2F&link_type=pict&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0Iiwic2l6ZSI6IjEyOHgxMjgiLCJuYW0iOjEsIm5hbXAiOiJyaWdodCIsImNvbSI6MSwiY29tcCI6ImRvd24iLCJwcmljZSI6MCwiYm9yIjoxLCJjb2wiOjEsImJidG4iOjEsInByb2QiOjAsImFtcCI6ZmFsc2V9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hgb/53c26d5b.4838841e.53c26d5c.7370c7d7/?me_id=1269553&item_id=15311486&pc=https%3A%2F%2Fthumbnail.image.rakuten.co.jp%2F%400_mall%2Fbiccamera%2Fcabinet%2Fproduct%2F15031%2F00000014663193_a01.jpg%3F_ex%3D128x128&s=128x128&t=pict" border="0" style="margin:2px" alt="" title=""></a></div>

<div>
<a href="https://hb.afl.rakuten.co.jp/ichiba/53c271c0.ac761e1f.53c271c1.c6da3b4f/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fkzstore%2F2734-000637%2F&link_type=pict&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0Iiwic2l6ZSI6IjEyOHgxMjgiLCJuYW0iOjEsIm5hbXAiOiJyaWdodCIsImNvbSI6MSwiY29tcCI6ImRvd24iLCJwcmljZSI6MCwiYm9yIjoxLCJjb2wiOjEsImJidG4iOjEsInByb2QiOjAsImFtcCI6ZmFsc2V9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hgb/53c271c0.ac761e1f.53c271c1.c6da3b4f/?me_id=1397949&item_id=10000294&pc=https%3A%2F%2Fthumbnail.image.rakuten.co.jp%2F%400_mall%2Fkzstore%2Fcabinet%2Famayahoo%2F10812595%2Fimgrc0098271065.jpg%3F_ex%3D128x128&s=128x128&t=pict" border="0" style="margin:2px" alt="" title=""></a>
</div>

<div>
<a href="https://hb.afl.rakuten.co.jp/ichiba/53c27012.6caecdbc.53c27013.b5b33047/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fmeikeishop%2Fli-hy-0205-bk-qu-ws%2F&link_type=pict&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0Iiwic2l6ZSI6IjEyOHgxMjgiLCJuYW0iOjEsIm5hbXAiOiJyaWdodCIsImNvbSI6MSwiY29tcCI6ImRvd24iLCJwcmljZSI6MCwiYm9yIjoxLCJjb2wiOjEsImJidG4iOjEsInByb2QiOjAsImFtcCI6ZmFsc2V9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hgb/53c27012.6caecdbc.53c27013.b5b33047/?me_id=1437079&item_id=10000076&pc=https%3A%2F%2Fthumbnail.image.rakuten.co.jp%2F%400_mall%2Fmeikeishop%2Fcabinet%2F12629649%2Fimgrc0122209607.jpg%3F_ex%3D128x128&s=128x128&t=pict" border="0" style="margin:2px" alt="" title=""></a>
</div>

<div>
<a href="https://hb.afl.rakuten.co.jp/ichiba/53c27325.0710778d.53c27326.d87e62f9/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Flogicool%2Fm575spd%2F&link_type=pict&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0Iiwic2l6ZSI6IjEyOHgxMjgiLCJuYW0iOjEsIm5hbXAiOiJyaWdodCIsImNvbSI6MSwiY29tcCI6ImRvd24iLCJwcmljZSI6MCwiYm9yIjoxLCJjb2wiOjEsImJidG4iOjEsInByb2QiOjAsImFtcCI6ZmFsc2V9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hgb/53c27325.0710778d.53c27326.d87e62f9/?me_id=1386625&item_id=10000682&pc=https%3A%2F%2Fthumbnail.image.rakuten.co.jp%2F%400_mall%2Flogicool%2Fcabinet%2Fprd%2Fmice%2Fm575spd%2Fm575spd_s_r.jpg%3F_ex%3D128x128&s=128x128&t=pict" border="0" style="margin:2px" alt="" title=""></a>
</div>

<div>
<a href="https://hb.afl.rakuten.co.jp/ichiba/53c268f0.57d8bf58.53c268f1.34ec6ab7/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fsedrick%2Fsed-dnz-sd%2F&link_type=pict&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0Iiwic2l6ZSI6IjEyOHgxMjgiLCJuYW0iOjEsIm5hbXAiOiJyaWdodCIsImNvbSI6MSwiY29tcCI6ImRvd24iLCJwcmljZSI6MCwiYm9yIjoxLCJjb2wiOjEsImJidG4iOjEsInByb2QiOjAsImFtcCI6ZmFsc2V9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hgb/53c268f0.57d8bf58.53c268f1.34ec6ab7/?me_id=1410760&item_id=10000519&pc=https%3A%2F%2Fthumbnail.image.rakuten.co.jp%2F%400_mall%2Fsedrick%2Fcabinet%2F11504393%2F11725876%2F1.jpg%3F_ex%3D128x128&s=128x128&t=pict" border="0" style="margin:2px" alt="" title=""></a>
</div>

<div>
<a href="https://hb.afl.rakuten.co.jp/ichiba/53c2752a.d1f87b11.53c2752b.aeefbf20/?pc=https%3A%2F%2Fitem.rakuten.co.jp%2Fakindo%2Fwf-g700n-wz%2F&link_type=pict&ut=eyJwYWdlIjoiaXRlbSIsInR5cGUiOiJwaWN0Iiwic2l6ZSI6IjEyOHgxMjgiLCJuYW0iOjEsIm5hbXAiOiJyaWdodCIsImNvbSI6MSwiY29tcCI6ImRvd24iLCJwcmljZSI6MCwiYm9yIjoxLCJjb2wiOjEsImJidG4iOjEsInByb2QiOjAsImFtcCI6ZmFsc2V9" target="_blank" rel="nofollow sponsored noopener" style="word-wrap:break-word;"><img src="https://hbb.afl.rakuten.co.jp/hgb/53c2752a.d1f87b11.53c2752b.aeefbf20/?me_id=1190384&item_id=10197640&pc=https%3A%2F%2Fthumbnail.image.rakuten.co.jp%2F%400_mall%2Fakindo%2Fcabinet%2Fl38%2Fwf-g700n-wz.jpg%3F_ex%3D128x128&s=128x128&t=pict" border="0" style="margin:2px" alt="" title=""></a>
</div>


    
</div>
""", unsafe_allow_html=True)