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
      return pd.DataFrame(columns=["ID", "Project", "Cage", "DOB", "Sex", "Notes", "Next Experiment", "Experiement Date"])

data = load_data()

# Barra lateral com opções de navegação
page = st.sidebar.selectbox("Navigation", ["Home", "Add Animal", "Cages", "Projects",])

# Página: Home
if page == "Home":
    st.subheader("Welcome to the Rat Cage Manager App!")
    st.markdown("Use the sidebar to navigate between pages.")

elif page == "Add Animal":
    st.subheader("🐭 Add a New Animal")

    with st.form("add_animal_form"):
        id = st.text_input("Animal ID")
        project = st.selectbox("Project", ["Alzheimer's and (γδ) T cells", "CD3 Project", "Jax X Tac Breastmilk")
        cage = st.text_input("Cage Number")
        dob = st.date_input("Date of Birth")
        sex = st.selectbox("Sex", ["Male", "Female"])
        notes = st.text_area("Notes")
        next_action = st.text_input("Next Experiement")
        action_date = st.date_input("Experiement Date")

        submit = st.form_submit_button("Add Animal")

        if submit:
            new_data = pd.DataFrame([{
                "ID": id,
                "Project": project,
                "Cage": cage,
                "DOB": dob,
                "Sex": sex,
                "Notes": notes,
                "Next Action": next_action,
                "Action Date": action_date
            }])
            try:
                existing_data = pd.read_csv("rat_data.csv")
                updated_data = pd.concat([existing_data, new_data], ignore_index=True)
            except FileNotFoundError:
                updated_data = new_data

            updated_data.to_csv("rat_data.csv", index=False)
            st.success(f"Animal {id} added successfully!")

# Página: Cages
elif page == "Cages":
    st.subheader("🔲 Cage Overview")

    if data.empty:
        st.info("No animals registered yet.")
    else:
        selected_index = st.selectbox("Select an animal to edit", data.index, format_func=lambda x: f"{data.loc[x, 'ID']} - Cage {data.loc[x, 'Cage']}")
        
        # Mostrar informações atuais
        st.write("### Current Information")
        st.write(data.loc[selected_index])

        # Formulário de edição
        with st.form("edit_animal"):
            id = st.text_input("Animal ID", value=data.loc[selected_index, "ID"])
            project = st.text_input("Project", value=data.loc[selected_index, "Project"])
            cage = st.text_input("Cage Number", value=data.loc[selected_index, "Cage"])
            dob = st.date_input("Date of Birth", pd.to_datetime(data.loc[selected_index, "DOB"]))
            sex = st.selectbox("Sex", ["Male", "Female"], index=0 if data.loc[selected_index, "Sex"] == "Male" else 1)
            notes = st.text_area("Notes", value=data.loc[selected_index, "Notes"])
            next_action = st.text_input("Next Experiement", value=data.loc[selected_index, "Next Experiement"])
            action_date = st.date_input("Experiement Date", pd.to_datetime(data.loc[selected_index, "Experiement Date"]))

            save_changes = st.form_submit_button("Save Changes")
            if save_changes:
                data.loc[selected_index] = [id, project, cage, dob, sex, notes, next_action, action_date]
                data.to_csv("rat_data.csv", index=False)
                st.success("Animal updated successfully!")

        # Botão para deletar
        if st.button("Delete Animal", type="primary"):
            data = data.drop(selected_index)
            data.to_csv("rat_data.csv", index=False)
            st.warning("Animal deleted successfully!")

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

