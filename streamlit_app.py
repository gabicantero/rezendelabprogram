import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rat Cage Manager", layout="wide")
st.title("🐭 Rat Cage Manager")

# Funções para carregar dados
def load_data():
    try:
        return pd.read_csv("rat_data.csv")
    except FileNotFoundError:
        cols = ["ID", "Project", "Cage", "DOB", "Sex", "Pregnant?", "Notes",
                "Next Experiment", "Experiment Date", "Expected DOB Puppies",
                "Real DOB Puppies", "Weaning Date", "Milking Days Done"]
        return pd.DataFrame(columns=cols)

def load_projects():
    try:
        return pd.read_csv("projects.csv")["Project"].tolist()
    except FileNotFoundError:
        return ["Alzheimer's and (γδ) T cells", "CD3 Project", "Jax X Tac Breastmilk"]

data = load_data()
projects_list = load_projects()

# Menu lateral
page = st.sidebar.selectbox("Navigation", ["Home", "Add Animal", "Cages", "Projects"])

# Home
if page == "Home":
    st.subheader("Welcome to the Rat Cage Manager App!")
    st.write("Use the sidebar to navigate between pages.")

# Add Animal
elif page == "Add Animal":
    st.subheader("🐭 Add a New Animal")

    with st.form("add_animal_form"):
        id = st.text_input("Animal ID")
        project = st.selectbox("Project", projects_list)
        cage = st.text_input("Cage Number")
        dob = st.date_input("Date of Birth")
        sex = st.selectbox("Sex", ["Male", "Female"])
        pregnancy = st.selectbox("Pregnant?", ["No", "Yes"])
        notes = st.text_area("Notes")
        next_action = st.text_input("Next Experiment")

        add_exp_date = st.checkbox("Add Experiment Date?")
        if add_exp_date:
            action_date = st.date_input("Experiment Date")
        else:
            action_date = None

        # Campos extras apenas se grávida
        if pregnancy == "Yes":
            edbp = st.date_input("Expected Date of Birth of the Puppies")
            rdbp = st.date_input("Real Date of Birth of the Puppies")
            weaning = st.date_input("Date of Weaning")
        else:
            edbp = None
            rdbp = None
            weaning = None

        # Milking days se Next Experiment for Milking
        milk_done = None
        if next_action.lower() == "milking":
            milk_days = ['3', '6', '9', '12', '15', '17', '21']
            milk_done = st.multiselect("Milking days done", milk_days)

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
                "Next Experiment": next_action,
                "Experiment Date": action_date,
                "Expected DOB Puppies": edbp,
                "Real DOB Puppies": rdbp,
                "Weaning Date": weaning,
                "Milking Days Done": ",".join(milk_done) if milk_done else None
            }

            updated_data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
            updated_data.to_csv("rat_data.csv", index=False)
            st.success(f"Animal {id} added successfully!")

# Cages
elif page == "Cages":
    st.subheader("🔲 Cage Overview")

    if data.empty:
        st.info("No animals registered yet.")
    else:
        # filtro de projetos sem permitir adicionar novos
        filter_projects = ["All"] + projects_list
        selected_project = st.selectbox("Filter by project", filter_projects)
        filtered_data = data if selected_project == "All" else data[data["Project"] == selected_project]

        selected_index = st.selectbox(
            "Select an animal to edit",
            filtered_data.index,
            format_func=lambda x: f"{filtered_data.loc[x, 'ID']} - Cage {filtered_data.loc[x, 'Cage']}"
        )

        st.write("### Current Information")
        st.write(filtered_data.loc[selected_index])

        with st.form("edit_animal"):
            row = filtered_data.loc[selected_index]
            id = st.text_input("Animal ID", value=row["ID"])
            project = st.selectbox("Project", projects_list, index=projects_list.index(row["Project"]))
            cage = st.text_input("Cage Number", value=row["Cage"])
            dob = st.date_input("Date of Birth", pd.to_datetime(row["DOB"]))
            sex = st.selectbox("Sex", ["Male", "Female"], index=0 if row["Sex"] == "Male" else 1)
            pregnancy = st.selectbox("Pregnant?", ["No", "Yes"], index=0 if row["Pregnant?"] == "No" else 1)
            notes = st.text_area("Notes", value=row["Notes"])
            next_action = st.text_input("Next Experiment", value=row["Next Experiment"])

            add_exp_date = st.checkbox("Add Experiment Date?", value=pd.notnull(row["Experiment Date"]))
            if add_exp_date:
                try:
                    action_date = pd.to_datetime(row["Experiment Date"])
                except:
                    action_date = None
                action_date = st.date_input("Experiment Date", value=action_date)
            else:
                action_date = None

            # Só mostra se grávida
            if pregnancy == "Yes":
                try:
                    edbp = pd.to_datetime(row["Expected DOB Puppies"])
                except:
                    edbp = None
                try:
                    rdbp = pd.to_datetime(row["Real DOB Puppies"])
                except:
                    rdbp = None
                try:
                    weaning = pd.to_datetime(row["Weaning Date"])
                except:
                    weaning = None

                edbp = st.date_input("Expected Date of Birth of the Puppies", value=edbp)
                rdbp = st.date_input("Real Date of Birth of the Puppies", value=rdbp)
                weaning = st.date_input("Date of Weaning", value=weaning)
            else:
                edbp = None
                rdbp = None
                weaning = None

            milk_done = []
            if next_action.lower() == "milking":
                milk_days = ['3', '6', '9', '12', '15', '17', '21']
                milk_done_str = row.get("Milking Days Done", "")
                milk_done = milk_done_str.split(",") if milk_done_str else []
                milk_done = st.multiselect("Milking days done", milk_days, default=milk_done)

            save_changes = st.form_submit_button("Save Changes")
            if save_changes:
                # Atualizar a linha no dataframe original (data)
                data.loc[selected_index] = [
                    id, project, cage, dob, sex, pregnancy, notes,
                    next_action, action_date, edbp, rdbp, weaning,
                    ",".join(milk_done) if milk_done else None
                ]
                data.to_csv("rat_data.csv", index=False)
                st.success("Animal updated successfully!")

        if st.button("Delete Animal"):
            data = data.drop(selected_index)
            data.to_csv("rat_data.csv", index=False)
            st.warning("Animal deleted successfully!")

# Projects
elif page == "Projects":
    st.subheader("📋 Project List")

    st.write(pd.DataFrame({"Project": projects_list}))

    new_project = st.text_input("Add a new project")
    if new_project:
        if new_project not in projects_list:
            projects_list.append(new_project)
            pd.DataFrame({"Project": projects_list}).to_csv("projects.csv", index=False)
            st.success(f"Project '{new_project}' added successfully!")
        else:
            st.warning("Project already exists.")

