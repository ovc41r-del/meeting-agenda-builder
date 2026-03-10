# app.py
import streamlit as st
from docx import Document

# -----------------------------
# Core Functions
# -----------------------------
def extract_text_from_docx(file) -> str:
    doc = Document(file)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def split_into_topics(text: str):
    blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
    topics = []

    for block in blocks:
        lines = block.split("\n")
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        topics.append({"title": title, "body": body})

    return topics

def extract_metadata(section):
    lines = section["body"].split("\n")
    actions = []
    stakeholders = []

    for line in lines:
        lower = line.lower().strip()
        if lower.startswith("action:"):
            actions.append(line)
        if lower.startswith("owner:") or lower.startswith("stakeholder:"):
            stakeholders.append(line)

    return actions or ["No action items found."], stakeholders or ["No stakeholders listed."]

def allocate_time(sections, total_minutes):
    if not sections:
        return sections

    n = len(sections)
    base = total_minutes // n
    remainder = total_minutes % n

    for i, sec in enumerate(sections):
        sec["allocated_minutes"] = base + (1 if i < remainder else 0)

    return sections

# -----------------------------
# Dashboard Layout
# -----------------------------
st.set_page_config(
    page_title="Meeting Agenda Builder",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.header("⚙️ Controls")
uploaded_file = st.sidebar.file_uploader("Upload a .docx file", type=["docx"])
total_time = st.sidebar.number_input("Total meeting time (minutes)", min_value=0, step=5, value=60)
generate = st.sidebar.button("Generate Agenda")

# Main Title
st.title("📄 Meeting Agenda Generator")
st.write("Turn any uploaded document into a structured, time‑boxed meeting agenda.")

st.markdown("---")

# Main Logic
if uploaded_file and generate:
    raw_text = extract_text_from_docx(uploaded_file)
    topics = split_into_topics(raw_text)

    agenda = []
    for t in topics:
        actions, stakeholders = extract_metadata(t)
        agenda.append({
            "title": t["title"],
            "summary": t["body"] or "No summary available.",
            "action_items": actions,
            "stakeholders": stakeholders
        })

    agenda = allocate_time(agenda, int(total_time))

    st.header("🗂️ Generated Agenda")
    st.write(f"Total sections: **{len(agenda)}**")
    st.write(f"Total meeting time: **{total_time} minutes**")

    st.markdown("---")

    # Display each section in an expandable card
    for idx, section in enumerate(agenda, start=1):
        with st.expander(f"{idx}. {section['title']}  —  {section['allocated_minutes']} min"):
            st.subheader("Summary")
            st.write(section["summary"])

            st.subheader("Action Items")
            for ai in section["action_items"]:
                st.write(f"- {ai}")

            st.subheader("Stakeholders")
            for sh in section["stakeholders"]:
                st.write(f"- {sh}")

            st.markdown("---")

else:
    st.info("Upload a document and click **Generate Agenda** in the sidebar to begin.")
