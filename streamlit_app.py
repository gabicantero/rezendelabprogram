import streamlit as st
import pandas as pd
import datetime
import os 

st.set_page_config(page_title="Rat Cage Manager", layout="wide")
st.title("Animal Cage Manager")

try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

PROJECTS_PATH = os.path.join(BASE_DIR, "projects.csv")
DATA_PATH = os.path.join(BASE_DIR, "data.csv")

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
    if os.path.exists(PROJECTS_PATH):
        return pd.read_csv(PROJECTS_PATH)
    else:
        return pd.DataFrame()

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
        milk_days = ['1','2','3','4','5', '6','7','8', '9','10','11', '12','13','14', '15','16','17','18','19','20' '21']
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

        if selected_project == "All":
            filtered_data = data
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
                bree_expe = st.selectbox("Breeder or Experimental", ["Breeder","Experimental","None"], index=0 if row["Breeder or Experimental"] == "Breeder" else 1)

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

    # Recarrega os projetos para garantir dados atualizados
    projects_df = load_projects()

    # Inicializa contador de experimentos para o formulário, se não existir

    # Mostra os projetos existentes com tracker e checkboxes
    for idx, row in projects_df.iterrows():
        with st.expander(f"📂 {row['Project']}"):
            st.write(f"**Description:** {row.get('Description', '')}")

            # Detecta colunas de experimentos para o projeto
            exp_cols = [c for c in projects_df.columns if c.startswith("Exp") and "Name" in c]
            exp_nums = sorted([int(c.replace("Exp", "").replace("Name", "").strip()) for c in exp_cols])

            done_count = 0
            total_count = len(exp_nums)

            for num in exp_nums:
                name_col = f"Exp{num} Name"
                date_col = f"Exp{num} Date"
                done_col = f"Exp{num} Done"

                # Se coluna Done não existir, cria e preenche com False
                if done_col not in projects_df.columns:
                    projects_df[done_col] = False

                exp_name = row.get(name_col, "")
                exp_date = row.get(date_col, "")

                # Checkbox para marcar experimento como feito
                exp_done = st.checkbox(
                    f"{exp_name} ({exp_date})",
                    value=bool(row.get(done_col, False)),
                    key=f"done_{idx}_{num}"
                )

                # Atualiza valor no dataframe em memória
                projects_df.at[idx, done_col] = exp_done

                if exp_done:
                    done_count += 1

            # Barra visual de progresso
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
            <div style='width:100%;background-color:#ddd;border-radius:5px;'>
                <div style='width:{percent_done}%;background-color:{color};padding:5px;border-radius:5px;text-align:center;'>
                    {percent_done}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    if "new_exp_count" not in st.session_state:
        st.session_state.new_exp_count = 1

    # Coloque os botões para controlar o número de experimentos AQUI,
    # antes do formulário, para que o usuário possa clicar antes de preencher
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Experiment"):
            st.session_state.new_exp_count += 1
    with col2:
        if st.button("Remove Experiment") and st.session_state.new_exp_count > 1:
            st.session_state.new_exp_count -= 1

    # Botão para adicionar experimentos fora do formulário
  
    st.markdown("---")
    st.write("### Add New Project")

    with st.form("add_project_form"):
        new_proj_name = st.text_input("Project Name")
        new_proj_desc = st.text_area("Project Description")

        # Renderiza campos para os experimentos conforme contador
        exp_names = []
        exp_dates = []
        for i in range(st.session_state.new_exp_count):
            exp_names.append(st.text_input(f"Experiment {i+1} Name", key=f"new_exp_name_{i}"))
            exp_dates.append(st.date_input(f"Planned Date for Experiment {i+1}", key=f"new_exp_date_{i}"))

        submitted = st.form_submit_button("Add Project")
        
    if st.button("Add Experiment"):
        st.session_state.new_exp_count += 1


        if submitted:
            # Validações básicas
            if new_proj_name.strip() == "":
                st.error("Project name cannot be empty.")
            elif new_proj_name in projects_df["Project"].values:
                st.error("Project with this name already exists.")
            else:
                # Monta o novo projeto para salvar
                new_row = {
                    "Project": new_proj_name,
                    "Description": new_proj_desc
                }
                for i in range(st.session_state.new_exp_count):
                    new_row[f"Exp{i+1} Name"] = exp_names[i]
                    new_row[f"Exp{i+1} Date"] = exp_dates[i].strftime("%Y-%m-%d") if exp_dates[i] else ""
                    new_row[f"Exp{i+1} Done"] = False

                projects_df = pd.concat([projects_df, pd.DataFrame([new_row])], ignore_index=True)
                save_projects(projects_df)
                st.success(f"Project '{new_proj_name}' added!")

                # Reseta o contador e limpa os inputs para próximo projeto
                st.session_state.new_exp_count = 1

                # Recarrega a página para atualizar a lista e permitir adicionar novos projetos
                st.experimental_rerun()

