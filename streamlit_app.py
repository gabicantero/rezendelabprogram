import streamlit as st
import pandas as pd
import datetime as datetime

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
        df = pd.read_csv("projects.csv")
        # Se dataframe vazio, criar colunas básicas
        if df.empty:
            df = pd.DataFrame(columns=["Project", "Description"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Project", "Description"])

def save_projects(df):
    df.to_csv("projects.csv", index=False)

def get_experiment_columns(df):
    # Retorna lista de experimentos (pares de colunas: nome, data, done)
    exp_cols = []
    for col in df.columns:
        if col.startswith("Exp") and ("Name" in col):
            exp_num = col.replace("Name", "").strip()
            exp_cols.append(exp_num)
    return sorted(exp_cols, key=lambda x: int(x))

def create_empty_experiment_cols(n=3):
    cols = {}
    for i in range(1, n+1):
        cols[f"Exp{i} Name"] = ""
        cols[f"Exp{i} Date"] = ""
        cols[f"Exp{i} Done"] = False
    return cols

# Carrega dados e projetos
data = load_data()
projects_df = load_projects()


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
    for idx, row in projects_df.iterrows():
        with st.expander(f"📂 {row['Project']}"):
        # Nome projeto (editable)
            new_name = st.text_input("Project Name", value=row["Project"], key=f"proj_name_{idx}")
        # Descrição (editable)
            new_desc = st.text_area("Description", value=row.get("Description", ""), key=f"desc_{idx}")

        # Detectar experimentos (pares de colunas)
        exp_nums = []
        for col in projects_df.columns:
            if col.startswith("Exp") and "Name" in col:
                # extrair número
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

            # Garantir que essas colunas existam no df (pode não ter)
            if exp_name_col not in projects_df.columns:
                projects_df[exp_name_col] = ""
            if exp_date_col not in projects_df.columns:
                projects_df[exp_date_col] = ""
            if exp_done_col not in projects_df.columns:
                projects_df[exp_done_col] = False

            # Campos editáveis
            exp_name = st.text_input(f"Experiment {num} Name", value=row.get(exp_name_col, ""), key=f"exp_name_{idx}_{num}")
            exp_date_str = row.get(exp_date_col, "")
            try:
                exp_date = pd.to_datetime(exp_date_str).date() if exp_date_str else None
            except:
                exp_date = None
            exp_date = st.date_input(f"Planned Date for Experiment {num}", value=exp_date if exp_date else datetime.today().date(), key=f"exp_date_{idx}_{num}")
            exp_done = st.checkbox("Done", value=bool(row.get(exp_done_col, False)), key=f"exp_done_{idx}_{num}")

            exp_names.append(exp_name)
            exp_dates.append(exp_date)
            exp_dones.append(exp_done)

        # Botão salvar mudanças
        if st.button("Save changes", key=f"save_proj_{idx}"):
            # Atualizar nome e descrição
            projects_df.at[idx, "Project"] = new_name
            projects_df.at[idx, "Description"] = new_desc
            # Atualizar experimentos
            for i, num in enumerate(exp_nums):
                projects_df.at[idx, f"Exp{num} Name"] = exp_names[i]
                projects_df.at[idx, f"Exp{num} Date"] = exp_dates[i].strftime("%Y-%m-%d") if exp_dates[i] else ""
                projects_df.at[idx, f"Exp{num} Done"] = exp_dones[i]
            save_projects(projects_df)
            st.success(f"Project '{new_name}' updated!")

st.markdown("---")

# === ADICIONAR NOVO PROJETO ===
st.subheader("Add New Project")

with st.form("add_project_form"):
    new_proj_name = st.text_input("Project Name")
    new_proj_desc = st.text_area("Project Description")
    n_exp = st.number_input("Number of Experiments", min_value=1, max_value=10, value=3, step=1)

    # Criar listas para experimento (nome, data)
    new_exp_names = []
    new_exp_dates = []
    for i in range(1, n_exp+1):
        new_exp_names.append(st.text_input(f"Experiment {i} Name", key=f"new_exp_name_{i}"))
        new_exp_dates.append(st.date_input(f"Planned Date for Experiment {i}", value=datetime.today().date(), key=f"new_exp_date_{i}"))

    submit_new_proj = st.form_submit_button("Add Project")

    if submit_new_proj:
        if new_proj_name.strip() == "":
            st.error("Project name cannot be empty.")
        elif new_proj_name in projects_df["Project"].values:
            st.error("Project with this name already exists.")
        else:
            # Criar dict para novo projeto com colunas básicas
            new_row = {
                "Project": new_proj_name,
                "Description": new_proj_desc,
            }
            # Adicionar experimentos no formato: Exp1 Name, Exp1 Date, Exp1 Done
            for i in range(1, n_exp+1):
                new_row[f"Exp{i} Name"] = new_exp_names[i-1]
                new_row[f"Exp{i} Date"] = new_exp_dates[i-1].strftime("%Y-%m-%d")
                new_row[f"Exp{i} Done"] = False

            projects_df = pd.concat([projects_df, pd.DataFrame([new_row])], ignore_index=True)
            save_projects(projects_df)
            st.success(f"Project '{new_proj_name}' added!")

