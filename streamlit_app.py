import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Rat Cage Manager", layout="wide")
st.title("🐭 Rat Cage Manager")

# Função para carregar dados dos animais
def load_data():
    try:
        return pd.read_csv("rat_data.csv")
    except FileNotFoundError:
        cols = ["ID", "Project", "Cage", "DOB", "Sex", "Pregnant?", "Notes",
                "Next Experiment", "Experiment Date", "Expected DOB Puppies",
                "Real DOB Puppies", "Weaning Date", "Milking Days Done"]
        return pd.DataFrame(columns=cols)

# Função para carregar projetos
def load_projects():
    try:
        df = pd.read_csv("projects.csv")
        if df.empty:
            df = pd.DataFrame(columns=["Project", "Description", "Paper Written?", "Paper Submitted?", "Journal Name", "Paper Link"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Project", "Description", "Paper Written?", "Paper Submitted?", "Journal Name", "Paper Link"])

def save_projects(df):
    df.to_csv("projects.csv", index=False)

def save_data(df):
    df.to_csv("rat_data.csv", index=False)

# Carregar dados e projetos
data = load_data()
projects_df = load_projects()

# Preparar lista de projetos para seleção
projects_list = list(projects_df["Project"]) if not projects_df.empty else []

# Menu lateral
page = st.sidebar.selectbox("Navigation", ["Home", "Add Animal", "Cages", "Projects"])

if page == "Home":
    st.subheader("Welcome to the Rat Cage Manager App!")
    st.markdown("Use the sidebar to navigate between pages.")

elif page == "Add Animal":
    st.subheader("🐭 Add a New Animal")

    # Estados para controles dinâmicos
    if "pregnancy" not in st.session_state:
        st.session_state.pregnancy = "No"
    if "add_exp_date" not in st.session_state:
        st.session_state.add_exp_date = False

    id = st.text_input("Animal ID")
    project = st.selectbox("Project", projects_list)
    cage = st.text_input("Cage Number")
    dob = st.date_input("Date of Birth")
    sex = st.selectbox("Sex", ["Male", "Female"])

    pregnancy = st.selectbox("Pregnant?", ["No", "Yes"], index=0 if st.session_state.pregnancy == "No" else 1)
    st.session_state.pregnancy = pregnancy

    notes = st.text_area("Notes")
    next_action = st.text_input("Next Experiment")

    add_exp_date = st.checkbox("Add Experiment Date?", value=st.session_state.add_exp_date)
    st.session_state.add_exp_date = add_exp_date

    if add_exp_date:
        action_date = st.date_input("Experiment Date")
    else:
        action_date = None

    if pregnancy == "Yes":
        edbp = st.date_input("Expected Date of Birth of the Puppies")
        rdbp = st.date_input("Real Date of Birth of the Puppies")
        weaning = st.date_input("Date of Weaning")
    else:
        edbp = None
        rdbp = None
        weaning = None

    milk_done = []
    if next_action.lower() == "milking":
        milk_days = ['3', '6', '9', '12', '15', '17', '21']
        milk_done = st.multiselect("Milking days done", milk_days)

    if st.button("Add Animal"):
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
        save_data(updated_data)
        data = updated_data
        st.success(f"Animal {id} added successfully!")

elif page == "Cages":
    st.subheader("🔲 Cage Overview")

    if data.empty:
        st.info("No animals registered yet.")
    else:
        filter_projects = ["All"] + projects_list
        selected_project = st.selectbox("Filter by project", filter_projects)

        if selected_project == "All":
            filtered_data = data.copy()
        else:
            filtered_data = data[data["Project"] == selected_project]

        # Mostrar tabela simplificada
        st.write("### Animals in project:")
        st.dataframe(filtered_data[["ID", "Cage", "Sex", "DOB", "Next Experiment"]])

        selected_animal_index = st.selectbox(
            "Select an animal to edit",
            filtered_data.index,
            format_func=lambda x: f"{filtered_data.loc[x, 'ID']} - Cage {filtered_data.loc[x, 'Cage']}"
        )

        if "show_edit" not in st.session_state:
            st.session_state.show_edit = False

        if st.button("Edit selected animal info"):
            st.session_state.show_edit = not st.session_state.show_edit

        if st.session_state.show_edit:
            row = filtered_data.loc[selected_animal_index]

            with st.form("edit_animal"):
                id_edit = st.text_input("Animal ID", value=row["ID"])
                project_edit = st.selectbox("Project", projects_list, index=projects_list.index(row["Project"]))
                cage_edit = st.text_input("Cage Number", value=row["Cage"])
                dob_edit = st.date_input("Date of Birth", pd.to_datetime(row["DOB"]))
                sex_edit = st.selectbox("Sex", ["Male", "Female"], index=0 if row["Sex"] == "Male" else 1)
                pregnancy_edit = st.selectbox("Pregnant?", ["No", "Yes"], index=0 if row["Pregnant?"] == "No" else 1)
                notes_edit = st.text_area("Notes", value=row["Notes"])
                next_action_edit = st.text_input("Next Experiment", value=row["Next Experiment"])

                add_exp_date_edit = st.checkbox("Add Experiment Date?", value=pd.notnull(row["Experiment Date"]))
                if add_exp_date_edit:
                    try:
                        action_date_edit = pd.to_datetime(row["Experiment Date"])
                    except:
                        action_date_edit = None
                    action_date_edit = st.date_input("Experiment Date", value=action_date_edit)
                else:
                    action_date_edit = None

                if pregnancy_edit == "Yes":
                    try:
                        edbp_edit = pd.to_datetime(row["Expected DOB Puppies"])
                    except:
                        edbp_edit = None
                    try:
                        rdbp_edit = pd.to_datetime(row["Real DOB Puppies"])
                    except:
                        rdbp_edit = None
                    try:
                        weaning_edit = pd.to_datetime(row["Weaning Date"])
                    except:
                        weaning_edit = None

                    edbp_edit = st.date_input("Expected Date of Birth of the Puppies", value=edbp_edit)
                    rdbp_edit = st.date_input("Real Date of Birth of the Puppies", value=rdbp_edit)
                    weaning_edit = st.date_input("Date of Weaning", value=weaning_edit)
                else:
                    edbp_edit = None
                    rdbp_edit = None
                    weaning_edit = None

                milk_done_edit = []
                if next_action_edit.lower() == "milking":
                    milk_days = ['3', '6', '9', '12', '15', '17', '21']
                    milk_done_str = str(row.get("Milking Days Done", ""))
                    milk_done_edit = milk_done_str.split(",") if milk_done_str else []
                    milk_done_edit = st.multiselect("Milking days done", milk_days, default=milk_done_edit)

                save_changes = st.form_submit_button("Save Changes")
                if save_changes:
                    data.loc[selected_animal_index] = [
                        id_edit, project_edit, cage_edit, dob_edit, sex_edit, pregnancy_edit, notes_edit,
                        next_action_edit, action_date_edit, edbp_edit, rdbp_edit, weaning_edit,
                        ",".join(milk_done_edit) if milk_done_edit else None
                    ]
                    save_data(data)
                    st.success("Animal updated successfully!")
                    st.session_state.show_edit = False

            if st.button("Delete Animal"):
                data = data.drop(selected_animal_index)
                save_data(data)
                st.warning("Animal deleted successfully!")
                st.session_state.show_edit = False

elif page == "Projects":

    if "new_proj_num_exp" not in st.session_state:
        st.session_state.new_proj_num_exp = 3
    if "show_add_proj" not in st.session_state:
        st.session_state.show_add_proj = False

    st.subheader("📁 Projects")

    if st.button("Add New Project"):
        st.session_state.show_add_proj = not st.session_state.show_add_proj

    # Lista dos projetos atuais
    for idx, row in projects_df.iterrows():
        with st.expander(f"📂 {row['Project']}"):
            edit_key = f"edit_proj_{idx}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = False

            if st.button("Edit Project", key=f"btn_edit_{idx}"):
                st.session_state[edit_key] = not st.session_state[edit_key]

            if st.session_state[edit_key]:
                with st.form(f"edit_form_{idx}", clear_on_submit=False):
                    new_name = st.text_input("Project Name", value=row["Project"], key=f"proj_name_{idx}")
                    new_desc = st.text_area("Description", value=row.get("Description", ""), key=f"desc_{idx}")

                    # Detectar experimentos
                    exp_nums = []
                    for col in projects_df.columns:
                        if col.startswith("Exp") and "Name" in col:
                            num = col.replace("Name", "").strip()
                            exp_nums.append(num)
                    exp_nums = sorted(exp_nums, key=lambda x: int(x))

                    st.markdown("### Experiments")

                    exp_names = []
                    exp_dates = []
                    exp_dones = []

                    for num in exp_nums:
                        exp_name_col = f"Exp{num} Name"
                        exp_date_col = f"Exp{num} Date"
                        exp_done_col = f"Exp{num} Done"

                        if exp_name_col not in projects_df.columns:
                            projects_df[exp_name_col] = ""
                        if exp_date_col not in projects_df.columns:
                            projects_df[exp_date_col] = ""
                        if exp_done_col not in projects_df.columns:
                            projects_df[exp_done_col] = False

                        exp_name = st.text_input(f"Experiment {num} Name", value=row.get(exp_name_col, ""), key=f"exp_name_{idx}_{num}")
                        exp_date_str = row.get(exp_date_col, "")
                        try:
                            exp_date = pd.to_datetime(exp_date_str).date() if exp_date_str else datetime.datetime.today().date()
                        except:
                            exp_date = datetime.datetime.today().date()
                        exp_date = st.date_input(f"Planned Date for Experiment {num}", value=exp_date, key=f"exp_date_{idx}_{num}")
                        exp_done = st.checkbox("Done", value=bool(row.get(exp_done_col, False)), key=f"exp_done_{idx}_{num}")

                        exp_names.append(exp_name)
                        exp_dates.append(exp_date)
                        exp_dones.append(exp_done)

                    # Paper status
                    paper_written = st.checkbox("Paper Written?", value=bool(row.get("Paper Written?", False)), key=f"paper_written_{idx}")
                    paper_submitted = st.checkbox("Paper Submitted?", value=bool(row.get("Paper Submitted?", False)), key=f"paper_submitted_{idx}")
                    journal_name = st.text_input("Journal Name", value=row.get("Journal Name", ""), key=f"journal_name_{idx}")
                    paper_link = st.text_input("Published Paper Link", value=row.get("Paper Link", ""), key=f"paper_link_{idx}")

                    # Tracker visual
                    total_exp = len(exp_nums)
                    done_exp = sum(exp_dones)
                    percent_done = int((done_exp / total_exp) * 100) if total_exp > 0 else 0
                    st.progress(percent_done)
                    st.write(f"Progress: {percent_done}% of experiments done")

                    submitted = st.form_submit_button("Save Changes")
                    if submitted:
                        projects_df.at[idx, "Project"] = new_name
                        projects_df.at[idx, "Description"] = new_desc
                        projects_df.at[idx, "Paper Written?"] = paper_written
                        projects_df.at[idx, "Paper Submitted?"] = paper_submitted
                        projects_df.at[idx, "Journal Name"] = journal_name
                        projects_df.at[idx, "Paper Link"] = paper_link
                        for i, num in enumerate(exp_nums):
                            projects_df.at[idx, f"Exp{num} Name"] = exp_names[i]
                            projects_df.at[idx, f"Exp{num} Date"] = exp_dates[i].strftime("%Y-%m-%d") if exp_dates[i] else ""
                            projects_df.at[idx, f"Exp{num} Done"] = exp_dones[i]

                        save_projects(projects_df)
                        st.success(f"Project '{new_name}' updated!")

    # Formulário para adicionar novo projeto

