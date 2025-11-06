import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
import base64
# ==================== ENV & API CONFIG ====================
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("❌ Google API key not found in .env file. Please add GOOGLE_API_KEY=your_key to .env")
    st.stop()

# ==================== PAGE SETUP ====================
st.set_page_config(page_title="AI Team Stand-Up Summarizer", layout="wide")

# Custom CSS for modern UI
st.markdown("""
<style>
body {
    background-color: #F5F7FA;
}
h1, h2, h3 {
    color: #1E3A8A;
}
.block-container {
    padding-top: 2rem;
}
div[data-testid="stMarkdownContainer"] {
    font-size: 16px;
}
.summary-box {
    background-color: #FFFFFF;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    margin-top: 10px;
}
.header {
    background-color: #1E3A8A;
    color: white;
    text-align: center;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 25px;
}
</style>
""", unsafe_allow_html=True)

# ==================== HEADER ====================
#st.markdown("<div class='header'><h1>🤖 Team Stand-Up Summarizer </h1><p>Summarize team chat or meeting transcripts into Wins, Goals, Blockers, and Attendance details.</p></div>", unsafe_allow_html=True)
# Path to your logo file
logo_path = "company_logo.png"  # 👈 make sure logo.png is in the same folder as app.py

# Convert logo to Base64 for inline display
def get_base64_image(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return None

logo_base64 = get_base64_image(logo_path)

# HTML for the header
if logo_base64:
    logo_html = f"<img src='data:image/png;base64,{logo_base64}' class='logo'/>"
else:
    logo_html = "🤖"  # fallback emoji if logo not found

st.markdown(f"""
<style>
.header {{
    background-color: #87CEFA;
    color: black;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    padding: 15px 25px;
    border-radius: 10px;
    margin-bottom: 25px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.25);
}}
.logo {{
    height: 50px;
    width: auto;
    border-radius: 5px;
}}
.header-text {{
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}}
.header-text h1 {{
    font-size: 36px;
    font-weight: 700;
    margin: 0;
}}
.header-text p {{
    font-size: 16px;
    margin: 0;
    opacity: 0.9;
}}
</style>

<div class='header'>
    {logo_html}
    <div class='header-text'>
        <h1>Team Stand-Up Summarizer</h1>
        <p>Summarize team chat or meeting transcripts into simplify.</p>
    </div>
</div>
""", unsafe_allow_html=True)
# ==================== INPUT AREA ====================
st.subheader("🗂️ Input Section")

input_method = st.radio("Choose Input Method:", ["Paste Transcript", "Upload Text File"])

if input_method == "Paste Transcript":
    team_transcript = st.text_area("Paste your meeting or team transcript below:", height=300, placeholder="[2025-11-03 09:05] Alice: Yesterday I completed the new login UI...")
else:
    uploaded_file = st.file_uploader("Upload a text file", type=["txt"])
    team_transcript = uploaded_file.read().decode("utf-8") if uploaded_file else ""

# ==================== AI ANALYSIS ====================
if st.button("🚀 Generate Stand-Up Summary", use_container_width=True):
    if not team_transcript.strip():
        st.warning("Please provide a transcript or upload a file first.")
    else:
        with st.spinner("Analyzing conversation and generating summary..."):
            prompt = f"""
You are an AI assistant analyzing a team meeting transcript or chat log.

Extract and summarize the following:

1. 🧑‍🤝‍🧑 Attendance
   - List the unique participant names
   - Provide the total number of attendees

2. ⏰ Meeting Duration
   - start and end time based on timestamps (if available)
   - Calculate total duration in minutes

3. 🚧 Blockers
   - Summarize any reported issues or dependencies blocking work

4. 🏆 Wins
   - Summarize completed tasks, achievements, or successes

5. 🎯 Goals
   - Summarize upcoming tasks or next steps

Keep your output very clear, clean, well-formatted, and concise in Markdown use bold or color for side headers.

Transcript:
{team_transcript}
"""

            try:
                # Try Gemini 2.5-flash first (or fallback)
                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content(prompt)
                except Exception:
                    st.warning("⚠️ gemini-2.5-flash not available, using gemini-pro.")
                    model = genai.GenerativeModel("gemini-pro")
                    response = model.generate_content(prompt)

                summary = response.text

            except Exception as e:
                st.error(f"❌ Error generating summary: {str(e)}")
                st.stop()

   # ==================== DISPLAY SUMMARY ====================
        st.markdown("<h2 style='color:#1E3A8A;'>✅ Meeting Summary Report</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:16px;color:#333;'>Here's an analysis of your team meeting:</p>", unsafe_allow_html=True)

        # --- Clean up Markdown formatting ---
        clean_text = summary

        # Remove **bold markers**
        clean_text = re.sub(r"\*{2}(.*?)\*{2}", r"\1", clean_text)
        clean_text = re.sub(r"^\*\s*", "", clean_text, flags=re.MULTILINE)

        # Replace section headers (###, ## etc.) with stylized titles
        clean_text = re.sub(
            r"^#+\s*(.*?)$",
            r"<h4 style='color:#1E3A8A; margin-top:20px; margin-bottom:5px;'>\1</h4>",
            clean_text,
            flags=re.MULTILINE
        )

        # Convert line breaks
        clean_text = clean_text.replace("\n", "<br>")

        # Wrap content in styled summary box
        st.markdown(f"""
        <div style="
            background-color:#fff;
            border-radius:15px;
            padding:20px 25px;
            margin-top:10px;
            box-shadow:0 4px 12px rgba(0,0,0,0.1);
            font-size:16px;
            line-height:1.6;
            color:#1E3A8A;
        ">
            {clean_text}
        </div>
        """, unsafe_allow_html=True)

        st.success("✨ Summary successfully generated!")




