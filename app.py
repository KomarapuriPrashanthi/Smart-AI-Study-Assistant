import streamlit as st
import os, json
from datetime import datetime
import plotly.graph_objects as go

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="AI Study Assistant", page_icon="🎓",
                   layout="wide", initial_sidebar_state="expanded")

from database import (init_db, register_user, login_user,
                      save_document, get_documents, delete_document,
                      save_quiz_result, get_all_quizzes,
                      save_flashcard, get_flashcards, delete_flashcard,
                      save_summary, get_summaries,
                      log_activity, get_activity_log, get_stats)
from file_reader import extract_text, get_page_count
from ai_functions import doc_chat, generate_quiz, generate_flashcards, generate_summary

init_db()
os.makedirs("uploads", exist_ok=True)

# ══ COLOURS ══════════════════════════════════════════════════════════════════
MOCHA = "#6B4226"; DARK = "#2C1A0E"; BEIGE = "#F5F0E8"
LIGHT = "#EDE8DC"; MUTED = "#8B7355"; CARD = "#FFFFFF"
GREEN = "#2E7D32"; RED = "#C62828"

# ══ CSS ══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Lato:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {{ font-family:'Lato',sans-serif; background:{BEIGE}; color:{DARK}; }}
.stApp {{ background:{BEIGE}; }}
.block-container {{ padding:1.8rem 2.2rem; max-width:1180px; }}

/* sidebar */
[data-testid="stSidebar"] {{ background:{DARK} !important; border-right:3px solid {MOCHA}; }}
[data-testid="stSidebar"] * {{ color:{BEIGE} !important; }}
[data-testid="stSidebar"] .stButton>button {{
    background:transparent; border:none; color:{BEIGE} !important;
    text-align:left; width:100%; padding:9px 16px; border-radius:8px;
    font-size:14px; transition:background .2s;
}}
[data-testid="stSidebar"] .stButton>button:hover {{ background:{MOCHA} !important; }}

/* buttons */
.stButton>button {{
    background:{LIGHT}; color:{DARK}; border:1.5px solid #D4C9B8; border-radius:8px;
    padding:9px 20px; font-weight:600; font-size:14px; transition:all .2s;
    text-align:left !important;
}}
.stButton>button p {{
    text-align:left !important;
    width:100%;
}}
.stButton>button:hover {{ background:{DARK}; transform:translateY(-1px); }}

/* inputs */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea {{
    border-radius:8px; border:1.5px solid #D4C9B8; background:white;
}}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus {{ border-color:{MOCHA}; box-shadow:0 0 0 2px rgba(107,66,38,.15); }}

/* select boxes */
.stSelectbox>div>div {{ border-radius:8px; border:1.5px solid #D4C9B8; }}

/* headings */
h1,h2,h3 {{ font-family:'Playfair Display',serif; color:{DARK}; }}

/* tabs */
.stTabs [data-baseweb="tab-list"] {{ background:{LIGHT}; border-radius:10px; padding:4px; gap:4px; }}
.stTabs [data-baseweb="tab"] {{ border-radius:8px; font-family:'Lato',sans-serif; padding:6px 18px; }}
.stTabs [aria-selected="true"] {{ background:{MOCHA} !important; color:white !important; }}

/* hide streamlit chrome */
#MainMenu, footer, .stDeployButton {{ visibility:hidden; display:none; }}

/* file uploader — wider, less cramped */
[data-testid="stFileUploader"] {{ 
    background:white; border:2px dashed {MOCHA}; border-radius:14px;
    padding:28px 40px; 
}}
[data-testid="stFileUploader"] label {{ display:none; }}

/* metric card */
.mcard {{
    background:white; border-radius:14px; padding:22px 18px;
    text-align:center; box-shadow:0 2px 12px rgba(107,66,38,.10);
    border:1px solid #E8E0D0;
}}
.mcard .val {{ font-size:2.1rem; font-weight:700; color:{MOCHA}; font-family:'Playfair Display',serif; }}
.mcard .lbl {{ font-size:.78rem; color:{MUTED}; margin-top:4px; text-transform:uppercase; letter-spacing:.5px; }}

/* study card */
.scard {{
    background:white; border-radius:14px; padding:20px 24px;
    box-shadow:0 2px 12px rgba(107,66,38,.08); margin-bottom:14px;
    border:1px solid #E8E0D0;
}}

/* chat bubbles */
.cb-user {{
    background:{MOCHA}; color:white; padding:11px 16px;
    border-radius:18px 18px 4px 18px; margin:8px 0;
    max-width:72%; margin-left:auto; font-size:.91rem;
}}
.cb-bot {{
    background:white; color:{DARK}; padding:11px 16px;
    border-radius:18px 18px 18px 4px; margin:8px 0;
    max-width:78%; border:1px solid #E8E0D0; font-size:.91rem;
    box-shadow:0 1px 5px rgba(0,0,0,.06);
}}

/* flashcard */
.fc-card {{
    background:white; border-radius:18px; padding:44px 36px;
    text-align:center; box-shadow:0 4px 24px rgba(107,66,38,.13);
    border:2px solid {LIGHT}; min-height:200px;
}}

/* quiz option styles */
.opt-normal {{ background:white; border:2px solid #E8E0D0; border-radius:10px; padding:12px 18px; margin:6px 0; }}
.opt-correct {{ background:#E8F5E9; border:2px solid {GREEN}; border-radius:10px; padding:12px 18px; margin:6px 0; color:{GREEN}; font-weight:600; }}
.opt-wrong   {{ background:#FFEBEE; border:2px solid {RED};   border-radius:10px; padding:12px 18px; margin:6px 0; color:{RED};   font-weight:600; }}
</style>
""", unsafe_allow_html=True)


# ══ SESSION STATE ═════════════════════════════════════════════════════════════
def ss(key, val=None):
    if key not in st.session_state:
        st.session_state[key] = val

ss("auth", False); ss("user", None); ss("page", "Dashboard")
ss("chat_hist", []); ss("chat_input_key", 0); ss("chat_doc_text", ""); ss("chat_doc_name", "")
ss("quiz_qs", []); ss("quiz_idx", 0); ss("quiz_ans", {}); ss("quiz_done", False); ss("quiz_score", 0); ss("quiz_doc", "")
ss("fc_idx", 0); ss("fc_flip", False); ss("fc_score", {"right": 0, "wrong": 0})
ss("latest_summary", ""); ss("latest_summary_name", "")

def uid(): return st.session_state.user["id"]
def uname(): return st.session_state.user["name"]

def nav(p):
    st.session_state.page = p
    st.rerun()
    
def fmt_date(s):
    try:
        dt = datetime.fromisoformat(s)
        now = datetime.now()
        diff = now - dt
        total_seconds = int(diff.total_seconds())
        if total_seconds < 60:
            return "Just now"
        if total_seconds < 3600:
            m = total_seconds // 60
            return f"{m} min ago"
        if total_seconds < 86400:
            h = total_seconds // 3600
            return f"{h}h ago"
        if diff.days == 1:
            return "Yesterday"
        if diff.days < 7:
            return f"{diff.days}d ago"
        return dt.strftime("%d %b %Y")
    except:
        return s

def ficon(fn):
    return {"pdf":"📄","docx":"📝","doc":"📝","txt":"📋"}.get(fn.rsplit(".",1)[-1].lower(),"📎")


# ══ AUTH ══════════════════════════════════════════════════════════════════════
def page_auth():
    c1, c2 = st.columns([1,1])
    with c1:
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,{DARK} 0%,{MOCHA} 100%);
             border-radius:20px;padding:60px 40px;text-align:center;height:500px;
             display:flex;flex-direction:column;justify-content:center;align-items:center;'>
          <div style='font-size:4rem;margin-bottom:14px;'>🎓</div>
          <div style='font-family:Playfair Display,serif;font-size:2rem;color:{BEIGE};font-weight:700;'>AI Study Assistant</div>
          <div style='color:#C4A882;margin-top:10px;font-size:.95rem;'>Learn Smarter. Study Better.</div>
          <div style='margin-top:30px;color:{LIGHT};font-size:.9rem;line-height:2;'>
            ✨ Chat with PDFs &nbsp;·&nbsp; ❓ AI Quizzes<br>
            🃏 Smart Flashcards &nbsp;·&nbsp; 📊 Progress Tracking
          </div>
        </div>""", unsafe_allow_html=True)
    with c2:
        t1, t2 = st.tabs(["Sign In","Create Account"])
        with t1:
            st.markdown("### Welcome Back! 👋")
            em = st.text_input("Email", key="li_em", placeholder="student@example.com")
            pw = st.text_input("Password", type="password", key="li_pw", placeholder="••••••••")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign In", key="btn_li", use_container_width=True):
                if em and pw:
                    u = login_user(em, pw)
                    if u:
                        st.session_state.auth = True
                        st.session_state.user = u
                        st.rerun()
                    else: st.error("Invalid email or password.")
                else: st.warning("Fill in all fields.")
        with t2:
            st.markdown("### Create Account 🚀")
            nm = st.text_input("Full Name", key="su_nm", placeholder="Your Name")
            em2 = st.text_input("Email", key="su_em", placeholder="student@example.com")
            pw2 = st.text_input("Password", type="password", key="su_pw", placeholder="Min 6 chars")
            pw3 = st.text_input("Confirm Password", type="password", key="su_pw2")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", key="btn_su", use_container_width=True):
                if nm and em2 and pw2 and pw3:
                    if pw2 != pw3: st.error("Passwords don't match.")
                    elif len(pw2) < 6: st.error("Password too short.")
                    else:
                        ok, msg = register_user(nm, em2, pw2)
                        if ok: st.success("Account created! Please sign in.")
                        else: st.error(msg)
                else: st.warning("Fill in all fields.")


# ══ SIDEBAR ═══════════════════════════════════════════════════════════════════
def sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center;padding:22px 16px 16px;border-bottom:1px solid {MOCHA};margin-bottom:14px;'>
          <div style='font-size:2.4rem;'>🎓</div>
          <div style='font-family:Playfair Display,serif;font-size:1.05rem;font-weight:700;color:{BEIGE};'>AI Study Assistant</div>
          <div style='font-size:.72rem;color:#C4A882;margin-top:2px;'>Learn Smarter. Study Better.</div>
        </div>""", unsafe_allow_html=True)

        pages = [("🏠","Dashboard"),("📁","My Documents"),("💬","Chat with PDF"),
                 ("❓","Quiz Generator"),("🃏","Flashcards"),("📋","Summaries"),
                 ("📅","Study Planner"),("📊","Progress")]
        for icon, name in pages:
            if st.button(f"{icon}  {name}", key=f"nav_{name}", use_container_width=True):
                nav(name)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<div style='padding:10px 16px;color:#C4A882;font-size:.8rem;'>Logged in as<br><b style='color:{BEIGE};'>{uname()}</b></div>", unsafe_allow_html=True)
        if st.button("🚪  Logout", key="logout", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()


# ══ DASHBOARD ═════════════════════════════════════════════════════════════════
def page_dashboard():
    h = datetime.now().hour
    greet = "Good morning" if h < 12 else ("Good afternoon" if h < 17 else "Good evening")
    st.markdown(f"<h2>{greet}, {uname().split()[0]}! 👋</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-top:-14px;margin-bottom:24px;'>Let's continue your learning journey.</p>", unsafe_allow_html=True)

    stats = get_stats(uid())
    acc = round(stats["quiz_score"]/stats["quiz_total"]*100) if stats["quiz_total"] else 0

    c1,c2,c3,c4 = st.columns(4)
    for col,(v,l,ic) in zip([c1,c2,c3,c4],[
        (stats["docs"],"Documents Uploaded","📄"),
        (stats["quizzes"],"Quizzes Taken","❓"),
        (stats["flashcards"],"Flashcards Created","🃏"),
        (f"{acc}%","Quiz Accuracy","🎯"),
    ]):
        col.markdown(f"<div class='mcard'><div style='font-size:1.5rem;'>{ic}</div><div class='val'>{v}</div><div class='lbl'>{l}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([3,2])
    docs = get_documents(uid())

    with left:
        st.markdown("<div class='scard'>", unsafe_allow_html=True)
        h1,h2 = st.columns([3,1])
        h1.markdown("**Recent Activity**")
        if h2.button("View All", key="da_va"): nav("My Documents")
        if docs:
            for d in docs[:4]:
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #F0EAE0;'>
                  <span style='font-size:1.5rem;'>{ficon(d['filename'])}</span>
                  <div style='flex:1;'>
                    <div style='font-weight:600;font-size:.9rem;'>{d['filename']}</div>
                    <div style='color:{MUTED};font-size:.8rem;'>Uploaded {fmt_date(d['uploaded_at'])}</div>
                  </div>
                  <span style='color:{MUTED};font-size:.8rem;'>{d.get('pages',0)} pages</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No documents yet. Upload your first study material!")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='scard'>", unsafe_allow_html=True)
        st.markdown("**Study Progress**")
        overall = min(100, stats["docs"]*8 + stats["quizzes"]*5 + stats["flashcards"]//3)
        fig = go.Figure(go.Pie(values=[overall, 100-overall], hole=.72,
            marker_colors=[MOCHA, LIGHT], textinfo="none", hoverinfo="skip"))
        fig.update_layout(showlegend=False, margin=dict(t=5,b=5,l=5,r=5), height=180,
            paper_bgcolor="rgba(0,0,0,0)",
            annotations=[dict(text=f"<b>{overall}%</b>", x=.5, y=.5,
                              font_size=22, font_color=MOCHA, showarrow=False)])
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        st.markdown(f"<div style='text-align:center;color:{MUTED};font-size:.84rem;'>Overall Progress</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>**Quick Actions**", unsafe_allow_html=True)
    q1,q2,q3,q4 = st.columns(4)
    if q1.button("📤 Upload Document", use_container_width=True): nav("My Documents")
    if q2.button("💬 Chat with PDF",    use_container_width=True): nav("Chat with PDF")
    if q3.button("❓ Generate Quiz",    use_container_width=True): nav("Quiz Generator")
    if q4.button("🃏 Flashcards",       use_container_width=True): nav("Flashcards")


# ══ MY DOCUMENTS ══════════════════════════════════════════════════════════════
def page_documents():
    st.markdown("<h2>My Documents 📁</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-top:-14px;'>Upload and manage your study materials</p>", unsafe_allow_html=True)

    # Wide uploader — no extra button
    st.markdown("<div style='max-width:680px;'>", unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drag and drop or browse — PDF, DOCX, DOC, TXT (max 200 MB)",
        type=["pdf","docx","doc","txt"], key="uploader"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded is not None:
        # Save only once per upload (check by filename+size)
        key = f"uploaded_{uploaded.name}_{uploaded.size}"
        if key not in st.session_state:
            st.session_state[key] = True
            os.makedirs("uploads", exist_ok=True)
            save_path = os.path.join("uploads", f"{uid()}_{uploaded.name}")
            with open(save_path, "wb") as f:
                f.write(uploaded.getbuffer())
            pages = get_page_count(save_path)
            ext = os.path.splitext(uploaded.name)[1].lower().strip(".")
            save_document(uid(), uploaded.name, save_path, ext, pages)
            log_activity(uid(), "upload", uploaded.name)
            st.success(f"✅ '{uploaded.name}' uploaded successfully!")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    search = st.text_input("🔍 Search documents...", placeholder="Search documents...", key="doc_search")

    docs = get_documents(uid())
    if search:
        docs = [d for d in docs if search.lower() in d["filename"].lower()]

    if docs:
        for d in docs:
            icon = ficon(d["filename"])
            c1,c2,c3,c4,c5 = st.columns([0.5,4,1.5,1.2,0.8])
            c1.markdown(f"<div style='font-size:1.5rem;padding-top:6px;'>{icon}</div>", unsafe_allow_html=True)
            c2.markdown(f"**{d['filename']}**  \n<span style='color:{MUTED};font-size:.8rem;'>Uploaded {fmt_date(d['uploaded_at'])}</span>", unsafe_allow_html=True)
            c3.markdown(f"<div style='padding-top:6px;color:{MUTED};font-size:.84rem;'>{d.get('pages',0)} pages</div>", unsafe_allow_html=True)
            if c4.button("💬 Chat", key=f"chat_{d['id']}"):
                st.session_state.chat_doc_name = d["filename"]
                st.session_state.chat_doc_text = extract_text(d["filepath"])
                st.session_state.chat_hist = []
                nav("Chat with PDF")
            if c5.button("🗑️", key=f"del_{d['id']}"):
                delete_document(d["id"], uid())
                st.rerun()
            st.markdown("<hr style='margin:4px 0;border-color:#F0EAE0;'>", unsafe_allow_html=True)
    else:
        st.info("No documents found. Upload your study materials to get started!")


# ══ CHAT WITH PDF ═════════════════════════════════════════════════════════════
def page_chat():
    st.markdown("<h2>Chat with Documents 💬</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-top:-14px;'>Ask anything about your documents</p>", unsafe_allow_html=True)

    docs = get_documents(uid())
    if not docs:
        st.warning("Please upload a document first.")
        if st.button("Go to My Documents"): nav("My Documents")
        return

    doc_names = [d["filename"] for d in docs]
    curr = st.session_state.chat_doc_name
    idx = doc_names.index(curr) if curr in doc_names else 0
    sel = st.selectbox("Select document to chat with:", doc_names, index=idx, key="chat_sel")
    sel_doc = next((d for d in docs if d["filename"] == sel), None)

    if sel != st.session_state.chat_doc_name:
        st.session_state.chat_doc_name = sel
        st.session_state.chat_doc_text = extract_text(sel_doc["filepath"]) if sel_doc else ""
        st.session_state.chat_hist = []

    # Chat window
    st.markdown("<div style='min-height:200px;max-height:380px;overflow-y:auto;padding:10px 0;'>", unsafe_allow_html=True)
    if not st.session_state.chat_hist:
        st.markdown(f"<div style='text-align:center;padding:50px;color:{MUTED};'>👋 Hi! Ask me anything about <b>{sel}</b></div>", unsafe_allow_html=True)
    for msg in st.session_state.chat_hist:
        cls = "cb-user" if msg["role"]=="user" else "cb-bot"
        prefix = "🧑" if msg["role"]=="user" else "🤖"
        st.markdown(f"<div class='{cls}'>{prefix} {msg['content']}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Input row
    ic, bc = st.columns([5,1])
    user_input = ic.text_input("", placeholder="Type your question here...",
                            key=f"chat_inp_{st.session_state.chat_input_key}",
                            label_visibility="collapsed")
    send = bc.button("Send ➤", key="chat_send")
    
    if send and user_input.strip():
        try:
            with st.spinner("Thinking..."):
                reply = doc_chat(st.session_state.chat_doc_text,
                                st.session_state.chat_hist.copy(), user_input)
            st.session_state.chat_hist.append({"role":"user","content":user_input})
            st.session_state.chat_hist.append({"role":"assistant","content":reply})
            log_activity(uid(), "chat", sel)
            st.session_state.chat_input_key += 1
            st.rerun()
        except Exception as e:
            st.error(f"AI Error: {e}")

    if st.session_state.chat_hist:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_hist = []
            st.rerun()


# ══ QUIZ ══════════════════════════════════════════════════════════════════════
def page_quiz():
    st.markdown("<h2>Quiz Generator ❓</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-top:-14px;'>Generate quizzes from your documents</p>", unsafe_allow_html=True)

    docs = get_documents(uid())
    if not docs:
        st.warning("Please upload a document first.")
        return

    # ── Setup (no active quiz) ──
    if not st.session_state.quiz_qs:
        left, _ = st.columns([1.4, 1])
        with left:
            st.markdown("<div class='scard'>", unsafe_allow_html=True)
            st.markdown("**Configure Your Quiz**")
            doc_names = [d["filename"] for d in docs]
            sel_doc = st.selectbox("Select Document", doc_names, key="qz_doc")
            num_q = st.number_input("Number of Questions", 3, 20, 10, key="qz_num")
            diff = st.selectbox("Difficulty Level", ["Easy","Medium","Hard"], index=1, key="qz_diff")
            qtype = st.selectbox("Question Type", ["Multiple Choice","True/False"], key="qz_type")
            if st.button("🚀 Generate Quiz", key="gen_qz", use_container_width=True):
                doc_obj = next((d for d in docs if d["filename"] == sel_doc), None)
                if doc_obj:
                    try:
                        with st.spinner("Generating quiz with AI..."):
                            text = extract_text(doc_obj["filepath"])
                            qs = generate_quiz(text, int(num_q), diff, qtype)
                        st.session_state.quiz_qs   = qs
                        st.session_state.quiz_idx  = 0
                        st.session_state.quiz_ans  = {}
                        st.session_state.quiz_done = False
                        st.session_state.quiz_score = 0
                        st.session_state.quiz_doc  = sel_doc
                        log_activity(uid(), "quiz_generate", sel_doc)
                        st.rerun()
                    except ValueError as e:
                        st.error(f"API Error: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Quiz results screen ──
    if st.session_state.quiz_done:
        qs    = st.session_state.quiz_qs
        ans   = st.session_state.quiz_ans
        score = st.session_state.quiz_score
        total = len(qs)
        pct   = round(score/total*100) if total else 0

        st.markdown(f"""
        <div class='scard' style='text-align:center;padding:32px;'>
          <div style='font-size:3.5rem;'>{"🏆" if pct>=80 else "📚"}</div>
          <div style='font-family:Playfair Display,serif;font-size:2.2rem;color:{MOCHA};font-weight:700;'>{score} / {total}</div>
          <div style='font-size:1.1rem;color:{MUTED};'>{pct}% Correct</div>
          <div style='margin-top:12px;font-size:1rem;color:{"#2E7D32" if pct>=70 else "#C62828"};'>
            {"🎉 Great job! Keep it up!" if pct>=70 else "💪 Keep practising — you'll get there!"}
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>**Review — Question by Question**", unsafe_allow_html=True)
        for i, q in enumerate(qs):
            correct_letter = q.get("answer","").strip().upper()
            given = str(ans.get(i,"")).strip()
            is_ok = given.upper().startswith(correct_letter) if correct_letter else False
            mark = "✅" if is_ok else "❌"
            opts = q.get("options",[])
            correct_full = next((o for o in opts if o.upper().startswith(correct_letter)), correct_letter)

            st.markdown(f"<div class='scard' style='padding:16px 20px;margin-bottom:10px;'>", unsafe_allow_html=True)
            st.markdown(f"**{i+1}. {q['question']}**")
            for opt in opts:
                letter = opt.strip().upper()[0] if opt else ""
                if letter == correct_letter:
                    st.markdown(f"<div class='opt-correct'>✅ {opt}</div>", unsafe_allow_html=True)
                elif opt == given and not is_ok:
                    st.markdown(f"<div class='opt-wrong'>❌ {opt} (your answer)</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='opt-normal'>{opt}</div>", unsafe_allow_html=True)
            if not is_ok:
                st.markdown(f"<div style='color:{GREEN};font-size:.88rem;margin-top:6px;'>✅ Correct answer: <b>{correct_full}</b></div>", unsafe_allow_html=True)
            if q.get("explanation"):
                st.caption(f"💡 {q['explanation']}")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🔄 New Quiz", key="new_qz"):
            st.session_state.quiz_qs = []
            st.session_state.quiz_done = False
            st.rerun()
        return

    # ── Active quiz (answering) ──
    qs    = st.session_state.quiz_qs
    total = len(qs)
    ans   = st.session_state.quiz_ans

    st.progress(len(ans)/total)
    st.markdown(f"<div style='color:{MUTED};font-size:.88rem;margin-bottom:16px;'>{len(ans)} of {total} answered</div>", unsafe_allow_html=True)

    for i, q in enumerate(qs):
        st.markdown(f"<div class='scard'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:1rem;font-weight:700;color:{DARK};margin-bottom:10px;'>Q{i+1}. {q['question']}</div>", unsafe_allow_html=True)
        opts = q.get("options", [])
        chosen = ans.get(i, None)
        if opts:
            for opt in opts:
                chosen = ans.get(i, None)
                prefix = "✔ " if chosen == opt else ""
                if st.button(f"{prefix}{opt}", key=f"opt_{i}_{opt[:8]}", use_container_width=True):
                    st.session_state.quiz_ans[i] = opt
                    st.rerun()
            st.markdown("<style>div[data-testid='stVerticalBlock'] .stButton>button p{text-align:left !important;}</style>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if len(ans) == total:
        if st.button("✅ Submit Quiz & See Results", key="submit_qz", use_container_width=True):
            score = 0
            for i, q in enumerate(qs):
                correct = q.get("answer","").strip().upper()
                given   = str(ans.get(i,"")).strip().upper()
                if given.startswith(correct) or correct in given:
                    score += 1
            st.session_state.quiz_score = score
            st.session_state.quiz_done  = True
            save_quiz_result(uid(), st.session_state.quiz_doc, score, total)
            log_activity(uid(), "quiz_taken", f"{score}/{total}")
            st.rerun()
    else:
        st.info(f"Answer all {total} questions to submit. ({total - len(ans)} remaining)")


# ══ FLASHCARDS ════════════════════════════════════════════════════════════════
def page_flashcards():
    st.markdown("<h2>Flashcards 🃏</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-top:-14px;'>Create and study with AI-powered flashcards</p>", unsafe_allow_html=True)

    cards = get_flashcards(uid())
    decks = sorted(set(c["deck_name"] for c in cards)) if cards else []

    t1, t2 = st.tabs(["All Flashcards","Generate Flashcards"])

    # ── All ──
    with t1:
        if not cards:
            st.info("No flashcards yet. Add some or generate from a document!")
        else:
            deck_f = st.selectbox("Filter by deck", ["All Decks"]+decks, key="fc_df")
            filtered = cards if deck_f=="All Decks" else [c for c in cards if c["deck_name"]==deck_f]
            for card in filtered:
                c1,c2,c3 = st.columns([3,3,0.5])
                c1.markdown(f"<div style='padding:10px;background:#F9F6F0;border-radius:8px;font-size:.9rem;'><b>Q:</b> {card['question']}</div>", unsafe_allow_html=True)
                c2.markdown(f"<div style='padding:10px;background:#F0EDE4;border-radius:8px;font-size:.9rem;'><b>A:</b> {card['answer']}</div>", unsafe_allow_html=True)
                if c3.button("🗑️", key=f"dfc_{card['id']}"):
                    delete_flashcard(card["id"], uid())
                    st.rerun()

    # ── Study mode ──
    with t2:
        st.markdown("**Generate Flashcards from Document**")
        docs = get_documents(uid())
        if not docs:
            st.warning("Upload a document first.")
        else:
            # ── Generation form (only shown when no cards generated yet) ──
            if not st.session_state.get("fc_generated"):
                sel = st.selectbox("Select Document", [d["filename"] for d in docs], key="fc_ai_sel")
                num = st.slider("Number of Flashcards", 5, 20, 10, key="fc_ai_num")
                dn2 = st.text_input("Deck Name", placeholder="Auto-generated deck", key="fc_ai_dn")
                if st.button("🤖 Generate Flashcards", key="fc_ai_gen"):
                    doc_obj = next((d for d in docs if d["filename"] == sel), None)
                    if doc_obj:
                        try:
                            with st.spinner("Generating flashcards with AI..."):
                                text = extract_text(doc_obj["filepath"])
                                generated = generate_flashcards(text, num)
                            deck = dn2 or sel.rsplit(".", 1)[0]
                            for item in generated:
                                save_flashcard(uid(), deck, item["question"], item["answer"])
                            log_activity(uid(), "flashcard_generate", sel)
                            # Store generated cards in session for study
                            st.session_state.fc_generated = generated
                            st.session_state.fc_gen_idx = 0
                            st.session_state.fc_gen_flip = False
                            st.session_state.fc_gen_score = {"right": 0, "wrong": 0}
                            st.session_state.fc_gen_done = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"AI Error: {e}")

            # ── Results screen after all cards reviewed ──
            elif st.session_state.get("fc_gen_done"):
                sc = st.session_state.fc_gen_score
                total = sc["right"] + sc["wrong"]
                pct = round(sc["right"] / total * 100) if total else 0
                st.markdown(f"""
                <div style='background:white;border-radius:18px;padding:40px;text-align:center;
                    box-shadow:0 4px 24px rgba(107,66,38,.13);border:2px solid #EDE8DC;'>
                <div style='font-size:3.5rem;'>{"🏆" if pct>=70 else "📚"}</div>
                <div style='font-family:Playfair Display,serif;font-size:2rem;color:#6B4226;font-weight:700;margin-top:10px;'>
                    {sc["right"]} / {total}
                </div>
                <div style='font-size:1.1rem;color:#8B7355;margin-top:6px;'>{pct}% Cards Got Right</div>
                <div style='margin-top:14px;font-size:1rem;color:{"#2E7D32" if pct>=70 else "#C62828"};'>
                    {"🎉 Excellent! You know this topic well!" if pct>=70 else "💪 Keep reviewing — practice makes perfect!"}
                </div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Generate New Flashcards", key="fc_gen_reset", use_container_width=True):
                    st.session_state.fc_generated = None
                    st.session_state.fc_gen_done = False
                    st.rerun()

            # ── Flashcard study mode ──
            else:
                cards = st.session_state.fc_generated
                idx = st.session_state.fc_gen_idx
                flip = st.session_state.fc_gen_flip
                sc = st.session_state.fc_gen_score
                total_cards = len(cards)

                if idx >= total_cards:
                    st.session_state.fc_gen_done = True
                    st.rerun()

                card = cards[idx]
                reviewed = sc["right"] + sc["wrong"]

                # Progress bar
                st.markdown(f"<div style='color:#8B7355;font-size:.85rem;margin-bottom:10px;'>Card {idx+1} of {total_cards} &nbsp;·&nbsp; ✅ {sc['right']} right &nbsp;·&nbsp; ❌ {sc['wrong']} wrong</div>", unsafe_allow_html=True)
                st.progress((idx) / total_cards)
                st.markdown("<br>", unsafe_allow_html=True)

                # Vertical rectangle card
                content = card["answer"] if flip else card["question"]
                label = "ANSWER" if flip else "QUESTION"
                label_color = "#2E7D32" if flip else "#6B4226"

                st.markdown(f"""
                <div style='
                    background:white;
                    border-radius:20px;
                    padding:60px 40px;
                    text-align:center;
                    box-shadow:0 6px 30px rgba(107,66,38,.15);
                    border:2px solid {"#C8E6C9" if flip else "#EDE8DC"};
                    min-height:280px;
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    align-items:center;
                    margin:0 auto;
                    max-width:560px;
                '>
                <div style='font-size:.75rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:1.5px;color:{label_color};margin-bottom:20px;'>
                    {label}
                </div>
                <div style='font-size:1.2rem;line-height:1.7;color:#2C1A0E;font-weight:{"600" if flip else "400"};'>
                    {content}
                </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                if not flip:
                    # Only show Flip button
                    col = st.columns([1, 2, 1])[1]
                    if col.button("🔄 Flip Card — See Answer", key="fc_gen_flip_btn", use_container_width=True):
                        st.session_state.fc_gen_flip = True
                        st.rerun()
                else:
                    # Show Right / Wrong buttons
                    c1, c2 = st.columns(2)
                    if c1.button("✅  Got it Right!", key="fc_gen_right", use_container_width=True):
                        st.session_state.fc_gen_score["right"] += 1
                        st.session_state.fc_gen_idx += 1
                        st.session_state.fc_gen_flip = False
                        st.rerun()
                    if c2.button("❌  Got it Wrong", key="fc_gen_wrong", use_container_width=True):
                        st.session_state.fc_gen_score["wrong"] += 1
                        st.session_state.fc_gen_idx += 1
                        st.session_state.fc_gen_flip = False
                        st.rerun()

# ══ SUMMARIES ═════════════════════════════════════════════════════════════════
def page_summaries():
    st.markdown("<h2>AI Summary 📋</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-top:-14px;'>Get AI-generated summaries of your documents</p>", unsafe_allow_html=True)

    docs = get_documents(uid())
    if not docs:
        st.warning("Upload a document first.")
        return

    left, right = st.columns([1,2])
    with left:
        st.markdown("<div class='scard'>", unsafe_allow_html=True)
        st.markdown("**Generate Summary**")
        sel = st.selectbox("Select Document", [d["filename"] for d in docs], key="sm_sel")
        if st.button("✨ Generate Summary", key="gen_sm", use_container_width=True):
            doc_obj = next((d for d in docs if d["filename"]==sel), None)
            if doc_obj:
                try:
                    with st.spinner("Generating AI summary..."):
                        text = extract_text(doc_obj["filepath"])
                        summ = generate_summary(text, sel)
                    save_summary(uid(), doc_obj["id"], sel, summ)
                    st.session_state.latest_summary = summ
                    st.session_state.latest_summary_name = sel
                    log_activity(uid(), "summary", sel)
                    st.rerun()
                except Exception as e:
                    st.error(f"AI Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

        prev = get_summaries(uid())
        if prev:
            st.markdown("**Previous Summaries**")
            for s in prev[:6]:
                nm = s.get("document_name","Unknown")
                if st.button(f"📄 {nm[:28]}", key=f"ls_{s['id']}"):
                    st.session_state.latest_summary = s["summary_text"]
                    st.session_state.latest_summary_name = nm
                    st.rerun()

    with right:
        if st.session_state.latest_summary:
            st.markdown(f"<div class='scard'><b>📋 {st.session_state.latest_summary_name}</b><hr style='border-color:#F0EAE0;'>", unsafe_allow_html=True)
            st.markdown(st.session_state.latest_summary)
            st.markdown("</div>", unsafe_allow_html=True)
            st.download_button("⬇️ Download Summary",
                data=st.session_state.latest_summary,
                file_name=f"summary_{st.session_state.latest_summary_name}.txt",
                mime="text/plain")
        else:
            st.markdown(f"<div style='text-align:center;padding:80px;color:{MUTED};'><div style='font-size:3rem;'>📋</div><div style='margin-top:12px;'>Select a document and click Generate Summary</div></div>", unsafe_allow_html=True)


# ══ STUDY PLANNER ═════════════════════════════════════════════════════════════
def page_planner():
    st.markdown("<h2>Study Planner 📅</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-top:-14px;'>Plan and organise your study sessions</p>", unsafe_allow_html=True)

    ss("planner_tasks", [])

    left, right = st.columns([1,2])
    with left:
        st.markdown("<div class='scard'>", unsafe_allow_html=True)
        st.markdown("**Add Study Task**")
        title   = st.text_input("Task",     placeholder="e.g. Review Chapter 3", key="pt")
        subject = st.text_input("Subject",  placeholder="e.g. Data Structures",  key="ps")
        date    = st.date_input("Date", key="pd")
        dur     = st.number_input("Duration (mins)", 15, 480, 60, 15, key="pdu")
        pri     = st.selectbox("Priority", ["High","Medium","Low"], key="pp")
        if st.button("➕ Add Task", key="add_task", use_container_width=True):
            if title:
                st.session_state.planner_tasks.append(
                    {"title":title,"subject":subject,"date":str(date),
                     "duration":dur,"priority":pri,"done":False})
                st.success("Task added!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        tasks = st.session_state.planner_tasks
        pc = {"High":RED,"Medium":"#E65100","Low":GREEN}
        if tasks:
            for i, t in enumerate(tasks):
                style = "opacity:.5;text-decoration:line-through;" if t.get("done") else ""
                col, btn = st.columns([5,1])
                col.markdown(f"""
                <div class='scard' style='{style}border-left:4px solid {pc.get(t["priority"],MOCHA)};'>
                  <div style='font-weight:600;'>{t['title']}</div>
                  <div style='color:{MUTED};font-size:.85rem;'>
                    📚 {t['subject']} · 📅 {t['date']} · ⏱️ {t['duration']} min
                    · <span style='color:{pc.get(t["priority"],MOCHA)};font-weight:600;'>{t['priority']}</span>
                  </div>
                </div>""", unsafe_allow_html=True)
                with btn:
                    if not t.get("done"):
                        if st.button("✅", key=f"dt_{i}"):
                            st.session_state.planner_tasks[i]["done"] = True; st.rerun()
                    if st.button("🗑️", key=f"rt_{i}"):
                        st.session_state.planner_tasks.pop(i); st.rerun()
        else:
            st.markdown(f"<div style='text-align:center;padding:80px;color:{MUTED};'><div style='font-size:3rem;'>📅</div><div style='margin-top:12px;'>No tasks yet!</div></div>", unsafe_allow_html=True)


# ══ PROGRESS ══════════════════════════════════════════════════════════════════
def page_progress():
    import pandas as pd

    st.markdown("<h2>Your Study Progress 📊</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{MUTED};margin-top:-14px;'>Realistic stats based on your actual activity</p>", unsafe_allow_html=True)

    stats  = get_stats(uid())
    quizzes = get_all_quizzes(uid())
    cards  = get_flashcards(uid())
    log    = get_activity_log(uid())

    acc = round(stats["quiz_score"]/stats["quiz_total"]*100) if stats["quiz_total"] else 0

    c1,c2,c3,c4 = st.columns(4)
    for col,(v,l,ic) in zip([c1,c2,c3,c4],[
        (stats["quizzes"],"Quizzes Taken","❓"),
        (f"{acc}%","Quiz Accuracy","🎯"),
        (stats["flashcards"],"Flashcards","🃏"),
        (stats["docs"],"Documents","📄"),
    ]):
        col.markdown(f"<div class='mcard'><div style='font-size:1.4rem;'>{ic}</div><div class='val'>{v}</div><div class='lbl'>{l}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([3,2])

    # ── Quiz history chart ──
    with left:
        st.markdown("<div class='scard'>", unsafe_allow_html=True)
        st.markdown("**Quiz Score History**")
        if quizzes:
            df = pd.DataFrame(quizzes)
            df["pct"] = (df["score"]/df["total"]*100).round(1)
            df["label"] = df["document_name"].str[:18] + " #" + (df.index+1).astype(str)
            fig = go.Figure(go.Scatter(
                x=list(range(1,len(df)+1)), y=df["pct"].tolist(),
                mode="lines+markers",
                line=dict(color=MOCHA, width=2.5),
                marker=dict(size=9, color=MOCHA),
                fill="tozeroy", fillcolor="rgba(107,66,38,.08)",
                text=df["label"], hovertemplate="%{text}: %{y:.0f}%<extra></extra>"
            ))
            fig.update_layout(
                height=220, margin=dict(t=10,b=10,l=10,r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(range=[0,110], title="Score %", gridcolor="#F0EAE0"),
                xaxis=dict(title="Quiz #", gridcolor="#F0EAE0"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("Take some quizzes to see your score history here.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Activity breakdown ──
    with right:
        st.markdown("<div class='scard'>", unsafe_allow_html=True)
        st.markdown("**Activity Breakdown**")
        acts = {}
        for entry in log:
            a = entry["activity"].replace("_"," ").title()
            acts[a] = acts.get(a,0)+1
        if acts:
            fig2 = go.Figure(go.Pie(
                labels=list(acts.keys()), values=list(acts.values()), hole=.5,
                marker_colors=[MOCHA,"#A0522D","#D2691E","#8B4513","#C4A882"],
                textinfo="percent+label",
            ))
            fig2.update_layout(height=240, margin=dict(t=10,b=10,l=10,r=10),
                               paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
        else:
            st.info("No activity yet. Start studying!")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Recent activity log ──
    st.markdown("<div class='scard'>", unsafe_allow_html=True)
    st.markdown("**Recent Activity Log**")
    if log:
        for entry in log[:15]:
            act  = entry["activity"].replace("_"," ").title()
            det  = f" — {entry['detail']}" if entry.get("detail") else ""
            when = fmt_date(entry["created_at"])
            st.markdown(f"<div style='padding:6px 0;border-bottom:1px solid #F0EAE0;'>🟤 <b>{act}</b>{det} <span style='color:{MUTED};float:right;font-size:.82rem;'>{when}</span></div>", unsafe_allow_html=True)
    else:
        st.info("No activity logged yet.")
    st.markdown("</div>", unsafe_allow_html=True) 


# ══ ROUTER ════════════════════════════════════════════════════════════════════
def main():
    if not st.session_state.auth:
        page_auth()
        return
    sidebar()
    p = st.session_state.page
    if   p == "Dashboard":      page_dashboard()
    elif p == "My Documents":   page_documents()
    elif p == "Chat with PDF":  page_chat()
    elif p == "Quiz Generator": page_quiz()
    elif p == "Flashcards":     page_flashcards()
    elif p == "Summaries":      page_summaries()
    elif p == "Study Planner":  page_planner()
    elif p == "Progress":       page_progress()

if __name__ == "__main__":
    main()