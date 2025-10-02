import streamlit as st
import json
import os

# 관리자 비밀번호
ADMIN_PASSWORD = "4067"

# 저장 파일 경로
DATA_FILE = "posts.json"


# 게시물 불러오기
def load_posts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


# 게시물 저장하기
def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


# 세션 상태 초기화
if "posts" not in st.session_state:
    st.session_state["posts"] = load_posts()

st.title("📌 Streamlit 미니 게시판 (파일 저장 버전)")

# 게시물 작성
st.subheader("✍️ 게시물 작성")
with st.form("post_form", clear_on_submit=True):
    title = st.text_input("제목")
    content = st.text_area("내용")
    submitted = st.form_submit_button("등록")

    if submitted:
        if title.strip() and content.strip():
            st.session_state["posts"].append({"title": title, "content": content})
            save_posts(st.session_state["posts"])
            st.success("✅ 게시물이 등록되었습니다.")
        else:
            st.warning("⚠️ 제목과 내용을 모두 입력해주세요.")

st.markdown("---")

# 게시물 목록 표시
st.subheader("📄 게시물 목록")
if not st.session_state["posts"]:
    st.info("아직 게시물이 없습니다.")
else:
    for idx, post in enumerate(st.session_state["posts"]):
        with st.expander(f"📌 {post['title']}"):
            st.write(post["content"])
            
            # 삭제 기능
            with st.form(f"delete_form_{idx}"):
                password = st.text_input("관리자 비밀번호", type="password", key=f"pw_{idx}")
                delete_btn = st.form_submit_button("삭제")
                if delete_btn:
                    if password == ADMIN_PASSWORD:
                        st.session_state["posts"].pop(idx)
                        save_posts(st.session_state["posts"])
                        st.success("🗑️ 게시물이 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("❌ 비밀번호가 올바르지 않습니다.")
