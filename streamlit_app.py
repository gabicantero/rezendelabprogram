import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Rat Cage Manager", layout="wide")
st.title("Animal Cage Manager")

# ====== Funções para carregar/salvar dados ======
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
        df = pd.read_csv("projects.csv")
        if df.empty:
            df = pd.DataFrame(columns=["Project", "Description", "Paper Written?", "Paper Submitted?", "Journal Name", "Paper Link"])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Project", "Description", "Paper Written?", "Paper Submitted?", "Journal Name", "Paper Link"])

def save_data(df):
    df.to_csv("rat_data.csv", index=False)

def save_projects(df):
    df.to_csv("projects.csv", index=False)

# ====== Carrega dados ======
data = load_data()
projects_df = load_projects()

# ====== Lista de projetos para seleção (Add Animal, Cages) ======
projects_list = list(projects_df["Project"].unique())
if not projects_list:
    projects_list = ["No Projects Yet"]

# ====== Menu lateral ======
page = st.sidebar.selectbox("Navigation", ["Home", "Add Animal", "Cages", "Projects"])

# ====== Página Home ======
if page == "Home":
    st.subheader("Welcome to the Rezende's Lab Animal Manager App!")
    st.markdown("Use the sidebar to navigate between pages.")

# ====== Página Add Animal ======
elif page == "Add Animal":
    st.subheader("Add a New Animal")

    id = st.text_input("Animal ID")
    project = st.selectbox("Project", projects_list)
    cage = st.text_input("Cage Number")
    dob = st.date_input("Date of Birth")
    sex = st.selectbox("Sex", ["Male", "Female"])
    pregnancy = st.selectbox("Pregnant?", ["No", "Yes"])
    notes = st.text_area("Notes")
    next_action = st.text_input("Next Experiment")
    bree_expe = st.selectbox("Breeder or Experimental?", ["Breeder", "Experimental","None"])

    add_exp_date = st.checkbox("Add Experiment Date?")
    action_date = None
    if add_exp_date:
        action_date = st.date_input("Experiment Date")

    edbp = rdbp = weaning = None
    if pregnancy == "Yes":
        edbp = st.date_input("Expected Date of Birth of the Puppies")
        rdbp = st.date_input("Real Date of Birth of the Puppies")
        weaning = st.date_input("Date of Weaning")

    milk_done = []
    if next_action.lower() == "milking":
        milk_days = ['1','2','3','4','5', '6','7','8', '9','10','11', '12','13','14', '15','16' '17','18','19','20' '21']
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
            "Breeder or Experimental?": bree_expe,
            "Experiment Date": action_date,
            "Expected DOB Puppies": edbp,
            "Real DOB Puppies": rdbp,
            "Weaning Date": weaning,
            "Milking Days Done": ",".join(milk_done) if milk_done else None
        }
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)
        save_data(data)
        st.success(f"Animal {id} added successfully!")
        # Atualiza lista de projetos
        if project not in projects_list:
            projects_list.append(project)

# ====== Página Cages ======
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

        st.write("### Animals in project:")
        st.dataframe(filtered_data[["ID", "Cage", "Sex", "Breeder or Experimental?", "DOB", "Next Experiment"]])

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
                id = st.text_input("Animal ID", value=row["ID"])
                project = st.selectbox("Project", projects_list, index=projects_list.index(row["Project"]) if row["Project"] in projects_list else 0)
                cage = st.text_input("Cage Number", value=row["Cage"])
                dob = st.date_input("Date of Birth", pd.to_datetime(row["DOB"]))
                sex = st.selectbox("Sex", ["Male", "Female"], index=0 if row["Sex"] == "Male" else 1)
                pregnancy = st.selectbox("Pregnant?", ["No", "Yes"], index=0 if row["Pregnant?"] == "No" else 1)
                notes = st.text_area("Notes", value=row["Notes"])
                next_action = st.text_input("Next Experiment", value=row["Next Experiment"])
                bree_expe - st.selectbox("Breeder or Experimental", ["Breeder","Experimental","None"], index=0 if row["Breeder or Experimental"] == "Breeder" else 1)

                add_exp_date = st.checkbox("Add Experiment Date?", value=pd.notnull(row["Experiment Date"]))
                action_date = None
                if add_exp_date:
                    try:
                        action_date = pd.to_datetime(row["Experiment Date"])
                    except:
                        action_date = None
                    action_date = st.date_input("Experiment Date", value=action_date)
                
                edbp = rdbp = weaning = None
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
                        next_action, bree_expe, action_date, edbp, rdbp, weaning,
                        ",".join(milk_done) if milk_done else None
                    ]
                    save_data(data)
                    st.success("Animal updated successfully!")
                    st.session_state.show_edit = False

            if st.button("Delete Animal"):
                data = data.drop(selected_animal_index)
                save_data(data)
                st.warning("Animal deleted successfully!")
                st.session_state.show_edit = False

# ====== Página Projects ======
elif page == "Projects":
    st.subheader("📁 Projects")

    # Controle para mostrar/ocultar o formulário de adicionar projeto
    if "show_add_proj" not in st.session_state:
        st.session_state.show_add_proj = False
    if "new_proj_num_exp" not in st.session_state:
        st.session_state.new_proj_num_exp = 3
    if "new_proj_exp_names" not in st.session_state:
        st.session_state.new_proj_exp_names = [""] * st.session_state.new_proj_num_exp
    if "new_proj_exp_dates" not in st.session_state:
        st.session_state.new_proj_exp_dates = [""] * st.session_state.new_proj_num_exp

    # Função para atualizar listas de nomes e datas quando muda número de experimentos
    def update_num_exp():
        n = st.session_state["num_exp_input"]
        old_n = len(st.session_state.new_proj_exp_names)

        # Ajusta listas de nomes
        if n > old_n:
            st.session_state.new_proj_exp_names.extend([""] * (n - old_n))
            st.session_state.new_proj_exp_dates.extend([""] * (n - old_n))
        elif n < old_n:
            st.session_state.new_proj_exp_names = st.session_state.new_proj_exp_names[:n]
            st.session_state.new_proj_exp_dates = st.session_state.new_proj_exp_dates[:n]

        st.session_state.new_proj_num_exp = n

    # Botão para mostrar formulário de adicionar projeto
    if st.button("➕ Add New Project"):
        st.session_state.show_add_proj = not st.session_state.show_add_proj

    if st.session_state.show_add_proj:
        with st.form("add_project_form"):
            new_proj_name = st.text_input("Project Name")
            new_proj_desc = st.text_area("Project Description")

            # Número de experimentos com callback para atualizar listas
            n_exp = st.number_input(
                "Number of Experiments",
                min_value=1,
                max_value=10,
                value=st.session_state.new_proj_num_exp,
                step=1,
                key="num_exp_input",
                on_change=update_num_exp
            )

            # Garante que listas estejam sincronizadas
            if len(st.session_state.new_proj_exp_names) != n_exp:
                update_num_exp()

            # Inputs para nomes e datas dos experimentos (dinâmicos)
            for i in range(n_exp):
                st.session_state.new_proj_exp_names[i] = st.text_input(
                    f"Experiment {i+1} Name",
                    value=st.session_state.new_proj_exp_names[i],
                    key=f"new_exp_name_{i}"
                )
                st.session_state.new_proj_exp_dates[i] = st.text_input(
                    f"Planned Date for Experiment {i+1} (YYYY-MM-DD)",
                    value=st.session_state.new_proj_exp_dates[i],
                    key=f"new_exp_date_{i}"
                )

            submit_new_proj = st.form_submit_button("Add Project")

            if submit_new_proj:
                if new_proj_name.strip() == "":
                    st.error("Project name cannot be empty.")
                elif new_proj_name in projects_df["Project"].values:
                    st.error("Project with this name already exists.")
                else:
                    new_row = {
                        "Project": new_proj_name,
                        "Description": new_proj_desc
                    }
                    for i in range(n_exp):
                        new_row[f"Exp{i+1} Name"] = st.session_state.new_proj_exp_names[i]
                        new_row[f"Exp{i+1} Date"] = st.session_state.new_proj_exp_dates[i]
                        new_row[f"Exp{i+1} Done"] = False

            
                    projects_df = pd.concat([projects_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_projects(projects_df)
                    st.success(f"Project '{new_proj_name}' added!")

                    # Resetar formulário
                    st.session_state.show_add_proj = False
                    st.session_state.new_proj_num_exp = 3
                    st.session_state.new_proj_exp_names = [""] * 3
                    st.session_state.new_proj_exp_dates = [""] * 3

    # Mostrar projetos existentes com edição
    for idx, row in projects_df.iterrows():
        with st.expander(f"📂 {row['Project']}"):

            new_name = st.text_input("Project Name", value=row["Project"], key=f"proj_name_{idx}")
            new_desc = st.text_area("Description", value=row.get("Description", ""), key=f"desc_{idx}")

            # Detectar experimentos
            exp_nums = []
            for col in projects_df.columns:
                if col.startswith("Exp") and "Name" in col:
                    num = col.replace("Exp", "").replace("Name", "").strip()
                    if num.isdigit():
                        exp_nums.append(int(num))
            exp_nums = sorted(exp_nums)

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

                exp_date = row.get(exp_date_col, "")
                exp_done = st.checkbox("Done", value=bool(row.get(exp_done_col, False)), key=f"exp_done_{idx}_{num}")

                exp_names.append(exp_name)
                exp_dates.append(exp_date)
                exp_dones.append(exp_done)

            # Visual tracker de progresso
            total_exp = len(exp_nums)
            done_exp = sum(exp_dones)
            percent_done = int((done_exp / total_exp) * 100) if total_exp > 0 else 0

            if percent_done == 100:
                color = "green"
            elif percent_done >= 75:
                color = "lightgreen"
            elif percent_done >= 50:
                color = "yellow"
            else:
                color = "red"

            st.markdown(f"""
                <div style='width:100%;background-color:lightgray;border-radius:5px;'>
                    <div style='width:{percent_done}%;background-color:{color};padding:5px;border-radius:5px;text-align:center;'>
                        {percent_done}%
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Botão para salvar alterações no projeto
            if st.button("Save changes", key=f"save_proj_{idx}"):
                projects_df.at[idx, "Project"] = new_name
                projects_df.at[idx, "Description"] = new_desc
                for i, num in enumerate(exp_nums):
                    projects_df.at[idx, f"Exp{num} Name"] = exp_names[i]
                    projects_df.at[idx, f"Exp{num} Date"] = exp_dates[i]
                    projects_df.at[idx, f"Exp{num} Done"] = exp_dones[i]

                save_projects(projects_df)
                st.success(f"Project '{new_name}' updated!")
