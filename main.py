import streamlit as st
import json
import os

# 관리자 비밀번호
ADMIN_PASSWORD = "4067"

# 저장 파일 경로
DATA_FILE = "posts.json"


# --------------------------
# 게시물 불러오기 / 저장하기
# --------------------------
def load_posts():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = f.read().strip()
                if not data:
                    return []
                return json.loads(data)
        except json.JSONDecodeError:
            return []
    return []


def save_posts(posts):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)


# --------------------------
# 세션 상태 초기화
# --------------------------
if "posts" not in st.session_state:
    st.session_state["posts"] = load_posts()

# expander 상태 저장
if "expander_states" not in st.session_state:
    st.session_state["expander_states"] = {}

st.title("*6-2반 게시판*")

# --------------------------
# 게시물 작성
# --------------------------
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
                "comments": [],
                "pinned": False
            }
            st.session_state["posts"].append(new_post)
            save_posts(st.session_state["posts"])
            st.success("✅ 게시물이 등록되었습니다.")
        else:
            st.warning("⚠️ 제목과 내용을 모두 입력해주세요.")

st.markdown("---")

# --------------------------
# 게시물 목록 표시
# --------------------------
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
        # expander 상태 관리
        exp_key = f"exp_{idx}"
        if exp_key not in st.session_state["expander_states"]:
            st.session_state["expander_states"][exp_key] = True

        with st.expander(f"📌 {post['title']} {'📍' if post.get('pinned') else ''}",
                         expanded=st.session_state["expander_states"][exp_key]):
            st.session_state["expander_states"][exp_key] = st.checkbox(
                "열림", value=st.session_state["expander_states"][exp_key],
                key=f"chk_{idx}", help="체크하면 expander가 열립니다."
            )

            st.write(post["content"])

            # 댓글 목록
            st.markdown("💬 **댓글**")
            if post.get("comments"):
                for c_idx, comment in enumerate(post["comments"]):
                    st.write(f"- {comment}")
            else:
                st.info("아직 댓글이 없습니다.")

            # 댓글 작성
            comment_key = f"comment_{idx}"
            comment_text = st.text_input("댓글 입력", key=comment_key)
            if st.button("댓글 등록", key=f"comment_btn_{idx}"):
                if comment_text.strip():
                    post["comments"].append(comment_text.strip())
                    save_posts(st.session_state["posts"])
                    st.session_state[comment_key] = ""  # 입력창 초기화
                    st.success("💬 댓글이 등록되었습니다.")

            st.markdown("---")

            # 삭제 기능
            del_pw_key = f"pw_del_{idx}"
            del_password = st.text_input("관리자 비밀번호 (삭제용)", type="password", key=del_pw_key)
            if st.button("삭제", key=f"delete_btn_{idx}"):
                if del_password == ADMIN_PASSWORD:
                    st.session_state["posts"].pop(idx)
                    save_posts(st.session_state["posts"])
                    st.success("🗑️ 게시물이 삭제되었습니다.")
                    # 삭제 후 expander 상태도 같이 초기화
                    st.session_state["expander_states"].pop(exp_key, None)
                else:
                    st.error("❌ 비밀번호가 올바르지 않습니다.")

            # 고정/해제 기능
            pin_pw_key = f"pw_pin_{idx}"
            pin_password = st.text_input("관리자 비밀번호 (고정용)", type="password", key=pin_pw_key)
            pin_label = "📍 고정하기" if not post.get("pinned") else "📍 고정 해제"
            if st.button(pin_label, key=f"pin_btn_{idx}"):
                if pin_password == ADMIN_PASSWORD:
                    post["pinned"] = not post.get("pinned", False)
                    save_posts(st.session_state["posts"])
                    st.success("📌 고정 상태가 변경되었습니다.")
                else:
                    st.error("❌ 비밀번호가 올바르지 않습니다.")
