import streamlit as st
import pandas as pd
import datetime
import os 

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
    if os.path.exists("projects.csv"):
        return pd.read_csv("projects.csv")
    else:
        # Cria dataframe vazio com colunas básicas
        columns = ["Project", "Description"]
        return pd.DataFrame(columns=columns)

def save_projects(df):
    df.to_csv("projects.csv", index=False)

# Carrega os dados no início da página
projects_df = load_projects()

# Sessão para controlar adicionar experimentos no form
if "new_exp_count" not in st.session_state:
    st.session_state.new_exp_count = 1
# Carrega os dados no início da página

# Sessão para controlar adicionar experimentos no form
if "new_exp_count" not in st.session_state:
    st.session_state.new_exp_count = 1

def save_data(df):
    df.to_csv("rat_data.csv", index=False)

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
        projects_list = projects_df["Project"].dropna().unique().tolist()
        projects_list = [p for p in projects_list if p.strip() != ""]

        selected_project = st.selectbox("Filter by Project", ["All"] + projects_list)

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
import streamlit as st
import pandas as pd
import datetime

def load_projects():
    # aqui você carrega seus projetos (ex: de um CSV)
    # exemplo simplificado:
    try:
        df = pd.read_csv("projects.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Project", "Description"])
    return df

def save_projects(df):
    df.to_csv("projects.csv", index=False)

# Inicializa dataframe no session_state
if "projects_df" not in st.session_state:
    st.session_state.projects_df = load_projects()

projects_df = st.session_state.projects_df

st.subheader("📁 Projects")

# Mostrar projetos existentes e tracker
for idx, row in projects_df.iterrows():
    with st.expander(f"📂 {row['Project']}"):
        new_name = st.text_input("Project Name", value=row["Project"], key=f"proj_name_{idx}")
        new_desc = st.text_area("Description", value=row.get("Description", ""), key=f"desc_{idx}")

        exp_cols = [c for c in projects_df.columns if c.startswith("Exp") and "Name" in c]
        exp_nums = sorted([int(c.replace("Exp", "").replace("Name", "").strip()) for c in exp_cols])

        done_count = 0
        total_count = len(exp_nums)
        exp_names = []
        exp_dates = []
        exp_dones = []

        for num in exp_nums:
            name_col = f"Exp{num} Name"
            date_col = f"Exp{num} Date"
            done_col = f"Exp{num} Done"

            if done_col not in projects_df.columns:
                projects_df[done_col] = False

            exp_name = st.text_input(f"Experiment {num} Name", value=row.get(name_col, ""), key=f"exp_name_{idx}_{num}")

            exp_date_str = row.get(date_col, "")
            try:
                exp_date = pd.to_datetime(exp_date_str).date() if exp_date_str else None
            except:
                exp_date = None
            exp_date = st.date_input(f"Planned Date for Experiment {num}", value=exp_date if exp_date else datetime.datetime.today().date(), key=f"exp_date_{idx}_{num}")

            exp_done = st.checkbox("Done", value=bool(row.get(done_col, False)), key=f"exp_done_{idx}_{num}")

            if exp_done:
                done_count += 1

            exp_names.append(exp_name)
            exp_dates.append(exp_date)
            exp_dones.append(exp_done)

        percent_done = int((done_count / total_count) * 100) if total_count > 0 else 0
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

        if st.button("Save Changes", key=f"save_proj_{idx}"):
            projects_df.at[idx, "Project"] = new_name
            projects_df.at[idx, "Description"] = new_desc
            for i, num in enumerate(exp_nums):
                projects_df.at[idx, f"Exp{num} Name"] = exp_names[i]
                projects_df.at[idx, f"Exp{num} Date"] = exp_dates[i].strftime("%Y-%m-%d") if exp_dates[i] else ""
                projects_df.at[idx, f"Exp{num} Done"] = exp_dones[i]
            save_projects(projects_df)
            st.success("Project updated!")

# Controle para mostrar form de adicionar projeto
if "show_add_project_form" not in st.session_state:
    st.session_state.show_add_project_form = False
if "new_proj_exp_list" not in st.session_state:
    st.session_state.new_proj_exp_list = []

if st.button("Add New Project"):
    st.session_state.show_add_project_form = not st.session_state.show_add_project_form

if st.session_state.show_add_project_form:
    with st.form("add_project_form"):
        new_proj_name = st.text_input("Project Name")
        new_proj_desc = st.text_area("Project Description")

        add_exp = st.form_submit_button("+ Add Experiment")
        if add_exp:
            st.session_state.new_proj_exp_list.append({"name": "", "date": ""})

        for i, exp in enumerate(st.session_state.new_proj_exp_list):
            exp_name = st.text_input(f"Experiment {i+1} Name", value=exp.get("name", ""), key=f"new_exp_name_{i}")
            exp_date = st.text_input(f"Planned Date for Experiment {i+1} (YYYY-MM-DD)", value=exp.get("date", ""), key=f"new_exp_date_{i}")

            st.session_state.new_proj_exp_list[i]["name"] = exp_name
            st.session_state.new_proj_exp_list[i]["date"] = exp_date

        submit_new_proj = st.form_submit_button("Add Project")
        if submit_new_proj:
            if new_proj_name.strip() == "":
                st.error("Project name cannot be empty.")
            elif new_proj_name in projects_df["Project"].values:
                st.error("Project with this name already exists.")
            elif len(st.session_state.new_proj_exp_list) == 0:
                st.error("Add at least one experiment.")
            else:
                new_row = {
                    "Project": new_proj_name,
                    "Description": new_proj_desc,
                }
                for i, exp in enumerate(st.session_state.new_proj_exp_list, 1):
                    new_row[f"Exp{i} Name"] = exp["name"]
                    new_row[f"Exp{i} Date"] = exp["date"]
                    new_row[f"Exp{i} Done"] = False

                st.session_state.projects_df = pd.concat([projects_df, pd.DataFrame([new_row])], ignore_index=True)
                save_projects(st.session_state.projects_df)
                st.success(f"Project '{new_proj_name}' added!")

                # Resetar lista e esconder form
                st.session_state.new_proj_exp_list = []
                st.session_state.show_add_project_form = False

# Atualiza projects_df depois de salvar para manter sincronizado
projects_df = st.session_state.projects_df
            
