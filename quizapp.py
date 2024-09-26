import streamlit as st
import pandas as pd
import random
import base64

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def run():
    st.set_page_config(
        page_title="Quiz App",
        page_icon="📋",
    )

if __name__ == "__main__":
    run()

# Custom CSS for centering the buttons
st.markdown("""
<style>
div.stButton > button:first-child {
    display: block;
    margin: 0 auto;
}
iframe {
    width: 100%;
    height: 600px;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# Load quiz data from CSV
df = pd.read_csv('merged.csv')

# Shuffle questions every time quiz restarts
if 'shuffled_df' not in st.session_state:
    st.session_state.shuffled_df = df.sample(frac=1).reset_index(drop=True)

# Initialize session state variables
default_values = {
    'current_index': 0, 
    'correct_answers': 0, 
    'wrong_answers': 0, 
    'selected_option': None, 
    'answer_submitted': False,
    'show_reference': False  # Track if the reference PDF should be shown
}
for key, value in default_values.items():
    st.session_state.setdefault(key, value)

def restart_quiz():
    st.session_state.current_index = 0
    st.session_state.correct_answers = 0
    st.session_state.wrong_answers = 0
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False
    st.session_state.show_reference = False  # Reset reference state
    # Shuffle questions again
    st.session_state.shuffled_df = df.sample(frac=1).reset_index(drop=True)

def submit_answer():
    if st.session_state.selected_option is not None:
        st.session_state.answer_submitted = True
        correct_answer = st.session_state.shuffled_df.iloc[st.session_state.current_index]['Right Answer']
        if st.session_state.selected_option == correct_answer:
            st.session_state.correct_answers += 1
        else:
            st.session_state.wrong_answers += 1
    else:
        st.warning("Please select an option before submitting.")

def next_question():
    st.session_state.current_index += 1
    st.session_state.selected_option = None
    st.session_state.answer_submitted = False
    st.session_state.show_reference = False  # Reset reference state for next question

# Title of the app
st.title("Quiz App")

# Progress bar
progress = (st.session_state.current_index + 1) / len(st.session_state.shuffled_df)
st.progress(progress)

# Display the current question and options
if st.session_state.current_index < len(st.session_state.shuffled_df):
    question_item = st.session_state.shuffled_df.iloc[st.session_state.current_index]
    st.subheader(f"Question {st.session_state.current_index + 1}")
    st.write(question_item['Question'])

    options = ['A', 'B', 'C', 'D']
    correct_answer = question_item['Right Answer']

    # Show answer options or feedback
    if st.session_state.answer_submitted:
        for option in options:
            label = question_item[f'Option {option}']
            if option == correct_answer:
                st.success(f"{option}: {label} (Correct answer)")
            elif option == st.session_state.selected_option:
                st.error(f"{option}: {label} (Incorrect answer)")
            else:
                st.write(f"{option}: {label}")
        
        # Show explanation after answer is submitted
        st.markdown("**Explanation:**")
        st.info(question_item['Explanation'])

    else:
        for option in options:
            if st.button(f"{option}: {question_item[f'Option {option}']}", key=option, use_container_width=True):
                st.session_state.selected_option = option

    st.markdown("""___""")

    # Show Submit button before answer is submitted
    if not st.session_state.answer_submitted:
        st.button('Submit', on_click=submit_answer)

    # Show Next button after submission
    if st.session_state.answer_submitted:
        if st.session_state.current_index < len(st.session_state.shuffled_df) - 1:
            st.button('Next', on_click=next_question)
        else:
            st.write(f"Quiz completed! You answered {st.session_state.correct_answers} questions correctly.")
            if st.button('Restart', on_click=restart_quiz):
                pass
else:
    st.write(f"Quiz completed! You answered {st.session_state.correct_answers} questions correctly.")
    st.button('Restart', on_click=restart_quiz)

# Display statistics in the sidebar
st.sidebar.header("Quiz Statistics")
st.sidebar.write(f"Correct Answers: {st.session_state.correct_answers}")
st.sidebar.write(f"Wrong Answers: {st.session_state.wrong_answers}")

# Add question progress to sidebar
total_questions = len(st.session_state.shuffled_df)
current_question_number = st.session_state.current_index + 1
st.sidebar.write(f"Questions Completed: {current_question_number} / {total_questions}")
