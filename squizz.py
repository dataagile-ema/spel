import streamlit as st
import pandas as pd
import os
import random
from PIL import Image
import base64

# Lägg till i början av filen
CSV_CATEGORIES_FILE = 'Kategorier.csv'  # Uppdaterad sökväg

# Konstanter
CSV_DIR = 'CSV'
IMAGE_DIR = 'Images/Produktbilder'
PAGE_TITLE = "Squizz!"  # Uppdaterad med utropstecken
PAGE_ICON = "squizz_logo.svg"

# Flytta denna funktion till början av filen, efter imports
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Session state hantering
def init_session_state():
    default_states = {
        'current_question': None,
        'used_questions': set(),
        'quiz_started': False,
        'questions': None,
        'selected_categories': None
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Datahantering
def load_questions(selected_categories):
    all_questions = []
    for category in selected_categories:
        file_path = os.path.join(CSV_DIR, f"{category}.csv")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            for _, row in df.iterrows():
                all_questions.append({
                    'Category': category,
                    'Question': row['Question'],
                    'Answer': row['Answer']
                })
    return all_questions

def get_all_categories():
    categories = []
    for filename in os.listdir(CSV_DIR):
        if filename.endswith('.csv'):
            category = os.path.splitext(filename)[0]
            display_name = category.replace('Quiz_', '').replace('_', ' ')
            categories.append({'file_name': category, 'display_name': display_name})
    return sorted(categories, key=lambda x: x['display_name'])

# Bildhantering
def find_category_image(category):
    if category.startswith('Quiz_'):
        category = category[5:]
    
    category = category.replace(' ', '_')
    
    expected_filename = f"Produkt_{category}.png"
    image_path = os.path.join(IMAGE_DIR, expected_filename)
    
    return image_path if os.path.exists(image_path) else None

# Frågehantering
def get_question_key(question):
    return f"{question['Category']}_{question['Question']}"

def get_random_question():
    if not st.session_state.questions:
        return None
    
    available_questions = [q for q in st.session_state.questions 
                         if get_question_key(q) not in st.session_state.used_questions]
    
    if not available_questions:
        st.markdown("""
            <div style='padding: 1rem; background-color: #FFD700; border-radius: 0.5rem; text-align: center;'>
                <h3 style='color: #000000; margin: 0;'>🎉 Grattis! 🎉</h3>
                <p style='color: #000000; margin: 0.5rem 0;'>Du har gått igenom alla frågor!</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("Börja om med samma kategorier"):
            st.session_state.used_questions.clear()
            available_questions = st.session_state.questions
        elif st.button("Välj nya kategorier"):
            st.session_state.quiz_started = False
            st.session_state.used_questions.clear()
            st.session_state.questions = None
            st.session_state.current_question = None
            st.experimental_rerun()
            return None
        
        return None
    
    question = random.choice(available_questions)
    st.session_state.used_questions.add(get_question_key(question))
    return question

# Ny funktion för att läsa färgscheman
def get_category_colors():
    color_schemes = {}
    try:
        df = pd.read_csv(CSV_CATEGORIES_FILE, encoding='utf-8-sig')
        for _, row in df.iterrows():
            if row['Generera_ja_nej'].lower().strip() == 'ja':
                category_name = row['rubrik'].strip('"')
                color_schemes[category_name] = {
                    'border': f"#{row['border']}",
                    'outer_frame': f"#{row['outer_frame']}",
                    'inner_frame': f"#{row['inner_frame']}"
                }
    except Exception as e:
        st.error(f"Kunde inte läsa färgscheman: {e}")
    return color_schemes

# Uppdatera render_category_selection
def render_category_selection():
    # Centrera logotyp och titel på samma rad
    st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; gap: 20px; margin-bottom: 2rem;'>
            <img src='data:image/svg+xml;base64,{}' width='60'>
            <h1 style='margin: 0;'>Squizz!</h1>
        </div>
    """.format(get_base64_encoded_image("squizz_logo.svg")), unsafe_allow_html=True)
    
    all_categories = get_all_categories()
    color_schemes = get_category_colors()
    cols_per_row = 3
    
    if 'selected_category_names' not in st.session_state:
        st.session_state.selected_category_names = []

    for i in range(0, len(all_categories), cols_per_row):
        cols = st.columns(cols_per_row)
        for col_idx, category in enumerate(all_categories[i:i + cols_per_row]):
            with cols[col_idx]:
                display_name = category['display_name']
                is_selected = display_name in st.session_state.selected_category_names
                
                # Hämta färgschema för kategorin
                colors = color_schemes.get(display_name, {
                    'outer_frame': '#F0F8FF',
                    'border': '#4A90E2'
                })
                
                # Använd alltid outer_frame färgen, oavsett om kategorin är vald eller inte
                st.markdown(f"""
                    <div style='
                        padding: 0.6rem;
                        background-color: {colors['outer_frame']};
                        border: 2px solid {colors['border']};
                        border-radius: 10px;
                        margin: 5px;
                        text-align: center;
                        cursor: pointer;
                        height: 50px;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                    '>
                        <h4 style='margin: 0; line-height: 1.2; font-size: 1em;'>{display_name}</h4>
                    </div>
                """, unsafe_allow_html=True)
                
                # Checkbox med "Välj" text
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.checkbox("Välj", key=category['display_name'],
                                value=is_selected):
                        if display_name not in st.session_state.selected_category_names:
                            st.session_state.selected_category_names.append(display_name)
                    else:
                        if display_name in st.session_state.selected_category_names:
                            st.session_state.selected_category_names.remove(display_name)

    # Visa antal valda kategorier
    st.markdown(f"### Valda kategorier: {len(st.session_state.selected_category_names)}")

    # Starta Quiz-knapp
    if st.button("Starta Quiz", type="primary"):
        if st.session_state.selected_category_names:
            selected_file_names = [cat['file_name'] for cat in all_categories 
                                 if cat['display_name'] in st.session_state.selected_category_names]
            st.session_state.selected_categories = selected_file_names
            st.session_state.questions = load_questions(selected_file_names)
            st.session_state.quiz_started = True
            st.experimental_rerun()
        else:
            st.warning("Vänligen välj minst en kategori.")

def render_question():
    category_image = find_category_image(st.session_state.current_question['Category'])
    if category_image:
        try:
            image = Image.open(category_image)
            st.image(image, use_column_width=True)
        except Exception as e:
            st.error(f"Fel vid öppning av bild: {e}")
    else:
        category_display = st.session_state.current_question['Category'].replace('_', ' ')
        st.markdown(f"<h3 style='text-align: center; color: #4A90E2;'>Kategori: {category_display}</h3>", 
                   unsafe_allow_html=True)

    st.markdown(f"<div style='background-color: #F0F8FF; padding: 20px; border-radius: 10px;'>"
               f"<p style='font-size: 18px;'>{st.session_state.current_question['Question']}</p></div>", 
               unsafe_allow_html=True)

def render_quiz():
    # Lägg till en "Starta om spel"-knapp högst upp
    if st.button("⬅️ Starta om spel", type="secondary"):
        st.session_state.quiz_started = False
        st.session_state.used_questions.clear()
        st.session_state.questions = None
        st.session_state.current_question = None
        st.experimental_rerun()
        return

    if not st.session_state.questions:
        st.error("Inga frågor hittades. Kontrollera CSV-filerna och sökvägen.")
        return

    if st.session_state.current_question is None:
        new_question = get_random_question()
        if new_question is None:
            return
        st.session_state.current_question = new_question

    render_question()

    if st.button("Visa svar", key="show_answer"):
        st.markdown(f"<div style='background-color: #E6FFE6; padding: 20px; border-radius: 10px;'>"
                   f"<p style='font-size: 18px;'>Svar: {st.session_state.current_question['Answer']}</p></div>", 
                   unsafe_allow_html=True)

    progress = st.progress(0)
    if st.button("Nästa fråga", key="next_question"):
        progress.progress(random.random())
        st.session_state.current_question = get_random_question()
        if st.session_state.current_question is not None:
            st.experimental_rerun()

def main():
    # Tvinga light mode
    st.set_page_config(
        page_title="Squizz!",  # Uppdaterat till rätt namn
        page_icon="🎯",
        initial_sidebar_state="expanded",
        layout="wide",
        menu_items=None
    )

    # Lägg till custom CSS för att tvinga light mode
    st.markdown("""
        <style>
            /* Tvinga light mode styles */
            .stApp {
                background-color: white;
                color: black;
            }
            
            /* Säkerställ att text förblir svart */
            p, h1, h2, h3, h4, h5, h6 {
                color: black !important;
            }
        </style>
    """, unsafe_allow_html=True)

    init_session_state()
    
    if not st.session_state.quiz_started:
        render_category_selection()
    else:
        render_quiz()

if __name__ == "__main__":
    main()
