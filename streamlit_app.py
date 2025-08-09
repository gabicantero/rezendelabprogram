import streamlit as st
import pandas as pd

#Title 
st.set_page_config(page_title="Rat Cage Manager", layout="wide")
st.title("🐭 Rat Cage Manager")
st.write("Welcome! This is your cage visualization and management system.")

#DataSet
def load_data():
  try:
    return pd.read_csv("rat_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["ID", "Project", "Cage", "DOB", "Sex", "Notes", "Next Action", "Action Date"])

data = load_data()

# Barra lateral com opções de navegação
page = st.sidebar.selectbox("Navigation", ["Home", "Cages", "Projects",])

# Página: Home
if page == "Home":
    st.subheader("Welcome to the Rat Cage Manager App!")
    st.markdown("Use the sidebar to navigate between pages.")

# Página: Cages
elif page == "Cages":
    st.subheader("🔲 Cage Grid")
    st.dataframe(data)

# Página: Animals
elif page == "Animals":
    st.subheader("🐁 Animal Details")

    with st.form("add_animal"):
        st.markdown("### Add New Animal")
        id = st.text_input("Cage ID")
        project = st.text_input("Project")
        cage = st.text_input("Cage Number")
        dob = st.date_input("Date of Birth")
        eutha = st.date_input("Date of Euthanasia")
        sex = st.selectbox("Sex", ["Male", "Female", "F and M"])
        pregnancy = st.selectbox("Pregnant?", ["Yes","No"])
            if pregnancy == "Yes":
              edbp = st.date_input("Expected Date of Birth of the Puppies")
              rdbp = st.date_input("Real Date of Birth of the Puppies")
              weaning = st.date_input("Date of Weaning")
              
        notes = st.text_area("Notes")
        next_exp = st.selectbox("Next Experiments", ['Milking', 'Gut Photoconversion', 'Limphonodes Photoconversion', 'Spleen Photoconversion', 'Gut Protocol', 'Brain, Meninges, Skull'])
            
        exp_date = st.date_input("Experiment Date")

        submitted = st.form_submit_button("Add Animal")
      
        if submitted:
            new_row = {
                "ID": id,
                "Project": project,
                "Cage": cage,
                "DOB": dob,
                "Sex": sex,
                "Pregnant?": pregnancy,
                "Notes": notes,
                "Next Experiment": next_exp,
                "Experiment Date": exp_date
            }
            data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
            data.to_csv("rat_data.csv", index=False)
            st.success("New animal added successfully!")

# Página: Settings
elif page == "Settings":
    st.subheader("⚙️ Settings (Coming Soon)")

