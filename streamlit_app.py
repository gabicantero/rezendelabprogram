import streamlit as st
import pandas as pd
import datetime
import json
from pathlib import Path

# ---------------------------
# Config e arquivos
# ---------------------------
st.set_page_config(page_title="Rat Cage Manager", layout="wide")

ANIMALS_FILE = "animals.csv"
PROJECTS_FILE = "projects.csv"

# ---------------------------
# Funções utilitárias I/O
# ---------------------------
def load_animals():
    cols = ["ID","Project","Cage","DOB","Sex","Pregnant?","Notes",
            "Next Experiment","Breeder or Experimental?","Experiment Date",
            "Expected DOB Puppies","Real DOB Puppies","Weaning Date","Milking Days Done"]
    p = Path(ANIMALS_FILE)
    if not p.exists():
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(ANIMALS_FILE)
    # garantir colunas
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[cols]

def save_animals(df):
    df.to_csv(ANIMALS_FILE, index=False)

def load_projects():
    cols = ["Name","Description","Num_Experiments","Experiments"]  # Experiments será JSON string
    p = Path(PROJECTS_FILE)
    if not p.exists():
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(PROJECTS_FILE)
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[cols]

def save_projects(df):
    df.to_csv(PROJECTS_FILE, index=False)

# ---------------------------
# Carregar dados iniciais
# ---------------------------
animals_df = load_animals()
projects_df = load_projects()
projects_list = list(projects_df["Name"].dropna().unique())

# ---------------------------
# Helper: barra de progresso colorida
# ---------------------------
def colored_progress(percent: int):
    # percent: 0..100
    if percent >= 100:
        color = "#006400"   # dark green
    elif percent >= 75:
        color = "#32CD32"   # light green
    elif percent >= 50:
        color = "#FFD700"   # yellow/gold
    else:
        color = "#FF4B4B"   # red
    # html bar
    html = f"""
    <div style="width:100%;background:#eee;border-radius:6px;padding:3px">
      <div style="width:{percent}%;background:{color};height:18px;border-radius:4px;text-align:center;color:#fff;font-weight:600">
        {percent}%
      </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ---------------------------
# Estado da sessão para formulários dinâmicos
# ---------------------------
if "show_add_project_form" not in st.session_state:
    st.session_state.show_add_project_form = False
if "new_proj_num_exp" not in st.session_state:
    st.session_state.new_proj_num_exp = 1
if "new_proj_experiments" not in st.session_state:
    st.session_state.new_proj_experiments = [{"name": "", "date": datetime.date.today()}]
if "view_cage" not in st.session_state:
    st.session_state.view_cage = None

# ---------------------------
# Menu principal (ordem solicitada)
# ---------------------------
page = st.sidebar.radio("Menu", ["Add Animal", "Cages", "Projects"])

# ===========================
# PAGE: Add Animal
# ===========================
if page == "Add Animal":
    st.title("🐭 Add a New Animal")

    # If no projects yet, show a warning but allow adding (you can type project as "No Project Yet")
    project_options = projects_list if projects_list else ["No Projects Yet"]

    with st.form("add_animal_form", clear_on_submit=False):
        id_ = st.text_input("Animal ID")
        project = st.selectbox("Project", project_options)
        cage = st.text_input("Cage Number")
        dob = st.date_input("Date of Birth", datetime.date.today())
        sex = st.selectbox("Sex", ["Male", "Female"])
        pregnancy = st.selectbox("Pregnant?", ["No", "Yes"])
        notes = st.text_area("Notes")
        next_action = st.text_input("Next Experiment")
        bree_expe = st.selectbox("Breeder or Experimental?", ["Breeder", "Experimental", "None"])

        add_exp_date = st.checkbox("Add Experiment Date?")
        action_date = None
        if add_exp_date:
            action_date = st.date_input("Experiment Date", datetime.date.today())

        edbp = rdbp = weaning = None
        if pregnancy == "Yes":
            edbp = st.date_input("Expected Date of Birth of the Puppies", datetime.date.today())
            rdbp = st.date_input("Real Date of Birth of the Puppies", datetime.date.today())
            weaning = st.date_input("Date of Weaning", datetime.date.today())

        milk_done = []
        if next_action.strip().lower() == "milking":
            milk_days = [str(d) for d in range(1,22)]
            milk_done = st.multiselect("Milking days done", milk_days)

        submitted = st.form_submit_button("Add Animal")
        if submitted:
            if id_.strip() == "":
                st.error("Animal ID cannot be empty.")
            else:
                new_row = {
                    "ID": id_,
                    "Project": project,
                    "Cage": cage,
                    "DOB": dob.isoformat() if isinstance(dob, datetime.date) else dob,
                    "Sex": sex,
                    "Pregnant?": pregnancy,
                    "Notes": notes,
                    "Next Experiment": next_action,
                    "Breeder or Experimental?": bree_expe,
                    "Experiment Date": action_date.isoformat() if isinstance(action_date, datetime.date) else (action_date if action_date else ""),
                    "Expected DOB Puppies": edbp.isoformat() if isinstance(edbp, datetime.date) else (edbp if edbp else ""),
                    "Real DOB Puppies": rdbp.isoformat() if isinstance(rdbp, datetime.date) else (rdbp if rdbp else ""),
                    "Weaning Date": weaning.isoformat() if isinstance(weaning, datetime.date) else (weaning if weaning else ""),
                    "Milking Days Done": ",".join(milk_done) if milk_done else ""
                }
                animals_df = pd.concat([animals_df, pd.DataFrame([new_row])], ignore_index=True)
                save_animals(animals_df)
                st.success(f"Animal {id_} added successfully!")
                # atualizar lista de projetos display se necessário
                if project not in projects_list:
                    projects_list.append(project)

# ===========================
# PAGE: Cages
# ===========================
elif page == "Cages":
    st.title("🔲 Cage Overview")

    if animals_df.empty:
        st.info("No animals registered yet.")
    else:
        # filtro por projeto
        proj_options = ["All"] + (projects_list if projects_list else ["No Projects Yet"])
        selected_project = st.selectbox("Filter by project", proj_options)

        # subfiltro por tipo (multi)
        type_options = ["Breeder", "Experimental", "None"]
        selected_types = st.multiselect("Filter by Type (choose any)", type_options, default=type_options)

        # filtrar animais de acordo
        filtered = animals_df.copy()
        if selected_project != "All":
            filtered = filtered[filtered["Project"] == selected_project]
        filtered = filtered[filtered["Breeder or Experimental?"].isin(selected_types)]

        # montar tabela de cages agregada
        cages_summary = []
        cage_ids = filtered["Cage"].fillna("").unique().tolist()
        for c in cage_ids:
            if c == "" or pd.isna(c):
                continue
            cage_animals = filtered[filtered["Cage"] == c]
            total = len(cage_animals)
            males = len(cage_animals[cage_animals["Sex"] == "Male"])
            females = len(cage_animals[cage_animals["Sex"] == "Female"])
            # definir tipo da cage (priorizar Breeder se houver)
            types_present = cage_animals["Breeder or Experimental?"].unique().tolist()
            if "Breeder" in types_present:
                cage_type = "Breeder"
            elif "Experimental" in types_present:
                cage_type = "Experimental"
            else:
                cage_type = "None"
            cages_summary.append({"Cage": c, "Total Animals": total, "Males": males, "Females": females, "Type": cage_type})

        cages_table = pd.DataFrame(cages_summary)
        if cages_table.empty:
            st.info("No matching cages found for selected filters.")
        else:
            st.dataframe(cages_table)

            # Botões para ver animais em cada cage (usa session_state para lembrar qual foi solicitado)
            for row in cages_summary:
                c = row["Cage"]
                if st.button(f"See animals in {c}", key=f"see_{c}"):
                    st.session_state.view_cage = c

            if st.session_state.view_cage:
                st.markdown("---")
                st.write(f"### Animals in cage `{st.session_state.view_cage}`")
                cage_animals = filtered[filtered["Cage"] == st.session_state.view_cage]
                if cage_animals.empty:
                    st.write("No animals in this cage (with current filters).")
                else:
                    st.dataframe(cage_animals)

# ===========================
# PAGE: Projects
# ===========================
elif page == "Projects":
    st.title("📂 Projects")

    # Botão para abrir/fechar form de adicionar novo projeto
    if st.button("Add Project"):
        st.session_state.show_add_project_form = not st.session_state.show_add_project_form

    # Formulário dinâmico (aparece só se toggled)
    if st.session_state.show_add_project_form:
        with st.form("add_project_form", clear_on_submit=False):
            proj_name = st.text_input("Project Name")
            proj_desc = st.text_area("Description")

            # número dinâmico de experiments
            num_exp = st.number_input("Number of Experiments", min_value=1, step=1, value=st.session_state.new_proj_num_exp)
            # ajustar sessão
            if num_exp != st.session_state.new_proj_num_exp:
                # redimensionar lista experiments
                if num_exp > st.session_state.new_proj_num_exp:
                    # adicionar vazios
                    for _ in range(int(num_exp) - int(st.session_state.new_proj_num_exp)):
                        st.session_state.new_proj_experiments.append({"name": "", "date": datetime.date.today()})
                else:
                    # truncar
                    st.session_state.new_proj_experiments = st.session_state.new_proj_experiments[:int(num_exp)]
                st.session_state.new_proj_num_exp = int(num_exp)

            # garantir tamanho correto
            if len(st.session_state.new_proj_experiments) != int(st.session_state.new_proj_num_exp):
                st.session_state.new_proj_experiments = [{"name": "", "date": datetime.date.today()} for _ in range(int(st.session_state.new_proj_num_exp))]

            # mostrar campos dinamicamente
            for i in range(int(st.session_state.new_proj_num_exp)):
                st.session_state.new_proj_experiments[i]["name"] = st.text_input(f"Experiment {i+1} Name", value=st.session_state.new_proj_experiments[i]["name"], key=f"np_name_{i}")
                # usar date_input com default datetime.date
                dt_val = st.session_state.new_proj_experiments[i]["date"]
                if not isinstance(dt_val, datetime.date):
                    try:
                        dt_val = datetime.date.fromisoformat(str(dt_val))
                    except:
                        dt_val = datetime.date.today()
                st.session_state.new_proj_experiments[i]["date"] = st.date_input(f"Experiment {i+1} Date", value=dt_val, key=f"np_date_{i}")

            add_submit = st.form_submit_button("Save Project")
            if add_submit:
                # validações básicas
                if proj_name.strip() == "":
                    st.error("Project name cannot be empty.")
                else:
                    # construir experiments list com done=False iniciais
                    exps = []
                    for e in st.session_state.new_proj_experiments:
                        exps.append({"name": e["name"], "date": e["date"].isoformat(), "done": False})
                    new_row = {
                        "Name": proj_name,
                        "Description": proj_desc,
                        "Num_Experiments": int(st.session_state.new_proj_num_exp),
                        "Experiments": json.dumps(exps)
                    }
                    projects_df = pd.concat([projects_df, pd.DataFrame([new_row])], ignore_index=True)
                    save_projects(projects_df)
                    # atualizar lista local e limpar formulário da sessão
                    projects_list = list(projects_df["Name"].dropna().unique())
                    st.session_state.new_proj_experiments = [{"name": "", "date": datetime.date.today()}]
                    st.session_state.new_proj_num_exp = 1
                    st.session_state.show_add_project_form = False
                    st.success(f"Project '{proj_name}' added!")
                    # reload projects_df para refletir imediatamente
                    projects_df = load_projects()
                    projects_list = list(projects_df["Name"].dropna().unique())

    # Mostrar todos os projetos salvos com edição/checkbox e tracker
    if projects_df.empty:
        st.info("No projects yet. Click 'Add Project' to create one.")
    else:
        # percorre por índice para sabermos onde salvar
        for idx, row in projects_df.reset_index(drop=True).iterrows():
            name = row["Name"]
            desc = row["Description"] if pd.notna(row["Description"]) else ""
            st.subheader(f"{name}")
            st.write(desc)

            # carregar experiments json
            exps = []
            try:
                exps = json.loads(row["Experiments"]) if pd.notna(row["Experiments"]) and row["Experiments"] != "" else []
            except Exception:
                exps = []

            if not exps:
                st.info("No experiments defined for this project.")
            else:
                # Mostrar lista de experiments com checkbox — e permitir editar se clicar Edit
                # Botão editar toggle
                edit_key = f"edit_proj_{idx}"
                if edit_key not in st.session_state:
                    st.session_state[edit_key] = False
                if st.button("Edit Project", key=f"edit_{idx}"):
                    st.session_state[edit_key] = not st.session_state[edit_key]

                # seção de edição (nome/data) ou apenas checkbox/show
                exp_names = []
                exp_dates = []
                exp_dones = []

                if st.session_state[edit_key]:
                    # edição - form para este projeto
                    with st.form(f"edit_form_{idx}", clear_on_submit=False):
                        for i, e in enumerate(exps):
                            # nome e date editáveis
                            new_name = st.text_input(f"Experiment {i+1} Name", value=e.get("name",""), key=f"proj_{idx}_expname_{i}")
                            # parse date
                            try:
                                dt_val = datetime.date.fromisoformat(e.get("date",""))
                            except:
                                dt_val = datetime.date.today()
                            new_date = st.date_input(f"Experiment {i+1} Date", value=dt_val, key=f"proj_{idx}_expdate_{i}")
                            done_val = st.checkbox("Done", value=bool(e.get("done", False)), key=f"proj_{idx}_expdone_{i}")

                            exp_names.append(new_name)
                            exp_dates.append(new_date)
                            exp_dones.append(done_val)

                        save_proj_changes = st.form_submit_button("Save changes")
                        if save_proj_changes:
                            # atualizar exps
                            new_exps = []
                            for i in range(len(exps)):
                                new_exps.append({"name": exp_names[i], "date": exp_dates[i].isoformat(), "done": bool(exp_dones[i])})
                            projects_df.at[idx, "Experiments"] = json.dumps(new_exps)
                            # também atualizar Num_Experiments e Description se quiser
                            save_projects(projects_df)
                            st.success(f"Project '{name}' updated!")
                            # reload
                            projects_df = load_projects()
                else:
                    # apenas mostrar checkboxes + save progress button
                    st.write("Experiments:")
                    for i,e in enumerate(exps):
                        label = f"{e.get('name','')} ({e.get('date','')})"
                        done_key = f"proj_{idx}_expdone_view_{i}"
                        # default from stored 'done'
                        default_done = bool(e.get("done", False))
                        checked = st.checkbox(label, value=default_done, key=done_key)
                        exp_dones.append(checked)
                        exp_names.append(e.get("name",""))
                        # parse date for display also
                        try:
                            exp_dates.append(datetime.date.fromisoformat(e.get("date","")))
                        except:
                            exp_dates.append(None)

                    if st.button("Save progress", key=f"save_progress_{idx}"):
                        # salvar checked states back into projects_df
                        new_exps = []
                        for i,e in enumerate(exps):
                            new_exps.append({
                                "name": e.get("name",""),
                                "date": e.get("date",""),
                                "done": bool(exp_dones[i])
                            })
                        projects_df.at[idx, "Experiments"] = json.dumps(new_exps)
                        save_projects(projects_df)
                        st.success("Progress saved.")
                        # reload
                        projects_df = load_projects()

                # mostrar tracker colorido com percent feito
                # recompute exps_from_df to be safe
                try:
                    exps_after = json.loads(projects_df.at[idx, "Experiments"]) if pd.notna(projects_df.at[idx, "Experiments"]) else []
                except:
                    exps_after = exps
                total = len(exps_after)
                done = sum(1 for e in exps_after if e.get("done", False))
                percent = int((done/total)*100) if total>0 else 0
                colored_progress(percent)
                # também listar nome + data ao lado do tracker
                st.write("Experiment list:")
                for e in exps_after:
                    st.write(f"- {e.get('name','')} — {e.get('date','')} — {'Done' if e.get('done', False) else 'Pending'}")

# ---------------------------
# Fim do app
# ---------------------------
