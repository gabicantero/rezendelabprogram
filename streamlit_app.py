import streamlit as st
import pandas as pd

st.set_page_config(page_title="Rat Cage Manager", layout="wide")
st.title("🐭 Rat Cage Manager")

# Função para carregar dados
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
        return pd.read_csv("projects.csv")["Project"].tolist()
    except FileNotFoundError:
        return ["Alzheimer's and (γδ) T cells", "CD3 Project", "Jax X Tac Breastmilk"]

# Carrega dados e projetos
data = load_data()
projects_list = load_projects()

# Menu lateral
page = st.sidebar.selectbox("Navigation", ["Home", "Add Animal", "Cages", "Projects"])

if page == "Home":
    st.subheader("Welcome to the Rat Cage Manager App!")
    st.markdown("Use the sidebar to navigate between pages.")

elif page == "Add Animal":
    st.subheader("🐭 Add a New Animal")

    # Controla estado para campos dinâmicos
    if "pregnancy" not in st.session_state:
        st.session_state.pregnancy = "No"
    if "add_exp_date" not in st.session_state:
        st.session_state.add_exp_date = False

    # Inputs principais
    id = st.text_input("Animal ID")
    project = st.selectbox("Project", projects_list)
    cage = st.text_input("Cage Number")
    dob = st.date_input("Date of Birth")
    sex = st.selectbox("Sex", ["Male", "Female"])

    # Pregnant? e controle de estado
    pregnancy = st.selectbox("Pregnant?", ["No", "Yes"], index=0 if st.session_state.pregnancy == "No" else 1)
    st.session_state.pregnancy = pregnancy

    notes = st.text_area("Notes")
    next_action = st.text_input("Next Experiment")

    # Checkbox para adicionar data do experimento
    add_exp_date = st.checkbox("Add Experiment Date?", value=st.session_state.add_exp_date)
    st.session_state.add_exp_date = add_exp_date

    if add_exp_date:
        action_date = st.date_input("Experiment Date")
    else:
        action_date = None

    # Campos extras se grávida
    if pregnancy == "Yes":
        edbp = st.date_input("Expected Date of Birth of the Puppies")
        rdbp = st.date_input("Real Date of Birth of the Puppies")
        weaning = st.date_input("Date of Weaning")
    else:
        edbp = None
        rdbp = None
        weaning = None

    # Milking days se next_action == milking
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
        updated_data.to_csv("rat_data.csv", index=False)
        data = updated_data  # Atualiza dados locais

        st.success(f"Animal {id} added successfully!")

elif page == "Cages":
    st.subheader("🔲 Cage Overview")

    if data.empty:
        st.info("No animals registered yet.")
    else:
        # Filtro por projeto
        filter_projects = ["All"] + projects_list
        selected_project = st.selectbox("Filter by project", filter_projects)

        if selected_project == "All":
            filtered_data = data.copy()
        else:
            filtered_data = data[data["Project"] == selected_project]

        # Tabela simplificada
        st.write("### Animals in project:")
        st.dataframe(filtered_data[["ID", "Cage", "Sex", "DOB", "Next Experiment"]])

        # Selecionar animal para edição
        selected_animal_index = st.selectbox(
            "Select an animal to edit",
            filtered_data.index,
            format_func=lambda x: f"{filtered_data.loc[x, 'ID']} - Cage {filtered_data.loc[x, 'Cage']}"
        )

        # Botão para mostrar/esconder edição
        if "show_edit" not in st.session_state:
            st.session_state.show_edit = False

        if st.button("Edit selected animal info"):
            st.session_state.show_edit = not st.session_state.show_edit

        if st.session_state.show_edit:
            row = filtered_data.loc[selected_animal_index]

            with st.form("edit_animal"):
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
                    milk_done_str = str(row.get("Milking Days Done", ""))
                    milk_done = milk_done_str.split(",") if milk_done_str else []
                    milk_done = st.multiselect("Milking days done", milk_days, default=milk_done)

                save_changes = st.form_submit_button("Save Changes")
                if save_changes:
                    data.loc[selected_animal_index] = [
                        id, project, cage, dob, sex, pregnancy, notes,
                        next_action, action_date, edbp, rdbp, weaning,
                        ",".join(milk_done) if milk_done else None
                    ]
                    data.to_csv("rat_data.csv", index=False)
                    st.success("Animal updated successfully!")
                    st.session_state.show_edit = False

            if st.button("Delete Animal"):
                data = data.drop(selected_animal_index)
                data.to_csv("rat_data.csv", index=False)
                st.warning("Animal deleted successfully!")
                st.session_state.show_edit = False

            save_changes = st.form_submit_button("Save Changes")

            if save_changes:
        # tudo aqui dentro indentado com 4 espaços a mais que o 'if'
                data.loc[selected_animal_index] = [...]
                data.to_csv("rat_data.csv", index=False)
                st.success("Animal updated successfully!")

elif page == "Projects":
    st.subheader("📁 Projects")

    # Carregar dados dos projetos
    try:
        projects_df = pd.read_csv("projects.csv")
    except FileNotFoundError:
        # Se não existir, cria um DataFrame vazio com colunas padrão
        projects_df = pd.DataFrame(columns=["Project", "Description", "Experiment 1", "Experiment 2", "Experiment 3"])

    # Mostrar lista de projetos como accordion expansível
    for idx, row in projects_df.iterrows():
        with st.expander(f"📂 {row['Project']}"):
            # Mostrar descrição com possibilidade de editar
            new_desc = st.text_area("Description", value=row["Description"], key=f"desc_{idx}")

            # Tracker simples para experimentos
            st.write("Experiment Progress:")
            exp_cols = [col for col in projects_df.columns if col.startswith("Experiment")]
            # Mostrar checkboxes para cada experimento
            exp_status = []
            for col in exp_cols:
                done = bool(row[col] == "Done")
                checked = st.checkbox(col, value=done, key=f"exp_{idx}_{col}")
                exp_status.append(checked)

            # Botão para salvar alterações no projeto
            if st.button("Save changes", key=f"save_proj_{idx}"):
                projects_df.at[idx, "Description"] = new_desc
                # Atualiza status dos experimentos
                for i, col in enumerate(exp_cols):
                    projects_df.at[idx, col] = "Done" if exp_status[i] else ""
                projects_df.to_csv("projects.csv", index=False)
                st.success(f"Project '{row['Project']}' updated!")

    st.markdown("---")
    st.subheader("Add New Project")

    with st.form("add_project_form"):
        new_proj_name = st.text_input("Project Name")
        new_proj_desc = st.text_area("Project Description")
        # Supondo 3 experimentos iniciais vazios
        submit_new_proj = st.form_submit_button("Add Project")

        if submit_new_proj:
            if new_proj_name.strip() == "":
                st.error("Project name cannot be empty.")
            else:
                # Verifica se já existe
                if new_proj_name in projects_df["Project"].values:
                    st.error("Project with this name already exists.")
                else:
                    new_row = {
                        "Project": new_proj_name,
                        "Description": new_proj_desc,
                        "Experiment 1": "",
                        "Experiment 2": "",
                        "Experiment 3": ""
                    }
                    projects_df = pd.concat([projects_df, pd.DataFrame([new_row])], ignore_index=True)
                    projects_df.to_csv("projects.csv", index=False)
                    st.success(f"Project '{new_proj_name}' added!")
