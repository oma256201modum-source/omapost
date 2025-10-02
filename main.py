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
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:  # 파일이 비어있으면
                    return []
                return json.loads(data)
        except json.JSONDecodeError:
            return []
    return []


# 게시물 저장하기
def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


# 세션 상태 초기화
if "posts" not in st.session_state:
    st.session_state["posts"] = load_posts()

st.title("*익명 게시판*")

# 게시물 작성
st.subheader("게시물 작성")
with st.form("post_form", clear_on_submit=True):
    title = st.text_input("제목")
    content = st.text_area("내용")
    submitted = st.form_submit_button("등록")

    if submitted:
        if title.strip() and content.strip():
            new_post = {
                "title": title,
                "content": content,
                "comments": [],   # 댓글 저장
                "pinned": False   # 고정 여부
            }
            st.session_state["posts"].append(new_post)
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
    # pinned 게시물 먼저 나오게 정렬
    sorted_posts = sorted(
        enumerate(st.session_state["posts"]),
        key=lambda x: (not x[1].get("pinned", False), -x[0])
    )

    for idx, post in sorted_posts:
        with st.expander(f"📌 {post['title']} {'📍' if post.get('pinned') else ''}"):
            st.write(post["content"])

            # 댓글 목록
            st.markdown("💬 **댓글**")
            if post.get("comments"):
                for c_idx, comment in enumerate(post["comments"]):
                    st.write(f"- {comment}")
            else:
                st.info("아직 댓글이 없습니다.")

            # 댓글 작성
            with st.form(f"comment_form_{idx}", clear_on_submit=True):
                comment_text = st.text_input("댓글 입력", key=f"comment_{idx}")
                comment_btn = st.form_submit_button("댓글 등록")
                if comment_btn:
                    if comment_text.strip():
                        post["comments"].append(comment_text.strip())
                        save_posts(st.session_state["posts"])
                        st.success("💬 댓글이 등록되었습니다.")
                        st.rerun()

            # 삭제 기능
            with st.form(f"delete_form_{idx}"):
                password = st.text_input("관리자 비밀번호", type="password", key=f"pw_del_{idx}")
                delete_btn = st.form_submit_button("삭제")
                if delete_btn:
                    if password == ADMIN_PASSWORD:
                        st.session_state["posts"].pop(idx)
                        save_posts(st.session_state["posts"])
                        st.success("🗑️ 게시물이 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("❌ 비밀번호가 올바르지 않습니다.")

            # 고정/해제 기능 (비밀번호 필요)
            with st.form(f"pin_form_{idx}"):
                password = st.text_input("관리자 비밀번호", type="password", key=f"pw_pin_{idx}")
                pin_btn = st.form_submit_button("📍 고정하기" if not post.get("pinned") else "📍 고정 해제")
                if pin_btn:
                    if password == ADMIN_PASSWORD:
                        post["pinned"] = not post.get("pinned", False)
                        save_posts(st.session_state["posts"])
                        st.success("📌 고정 상태가 변경되었습니다.")
                        st.rerun()
                    else:
                        st.error("❌ 비밀번호가 올바르지 않습니다.")
