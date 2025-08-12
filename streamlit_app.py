import streamlit as st
import pandas as pd
from datetime import datetime

# =======================
# Funções de carregamento e salvamento
# =======================
def load_projects():
    try:
        return pd.read_csv("projects.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Project", "Description"])

def save_projects(df):
    df.to_csv("projects.csv", index=False)

def load_cages():
    try:
        return pd.read_csv("cages.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Cage", "Project", "Type"])

def save_cages(df):
    df.to_csv("cages.csv", index=False)

def load_animals():
    try:
        return pd.read_csv("animals.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["AnimalID", "Cage", "Sex", "Type"])
        
def save_animals(df):
    df.to_csv("animals.csv", index=False)

# =======================
# Início do app
# =======================
st.set_page_config(layout="wide")
page = st.sidebar.selectbox("Navigation", ["Projects", "Cages", "Add Animals"])

projects_df = load_projects()
cages_df = load_cages()
animals_df = load_animals()

# =======================
# PAGE: PROJECTS
# =======================
if page == "Projects":
    st.subheader("📁 Projects")

    # Mostrar projetos existentes
    for idx, row in projects_df.iterrows():
        with st.expander(f"📂 {row['Project']}"):
            st.write(row["Description"])

            # Pegar colunas de experimentos
            exp_cols = [c for c in projects_df.columns if c.startswith("Exp") and "Name" in c]
            exp_nums = sorted([int(c.replace("Exp", "").replace("Name", "").strip()) for c in exp_cols])

            done_count = 0
            total_count = len(exp_nums)

            for num in exp_nums:
                name_col = f"Exp{num} Name"
                date_col = f"Exp{num} Date"
                done_col = f"Exp{num} Done"

                if done_col not in projects_df.columns:
                    projects_df[done_col] = False

                exp_name = projects_df.at[idx, name_col]
                exp_date = projects_df.at[idx, date_col]
                exp_done = st.checkbox(f"{exp_name} ({exp_date})", value=bool(row.get(done_col, False)),
                                       key=f"done_{idx}_{num}")

                if exp_done:
                    done_count += 1
                projects_df.at[idx, done_col] = exp_done

            # Calcular progresso
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

            save_projects(projects_df)

    # Formulário para adicionar novo projeto
    st.markdown("---")
    st.subheader("➕ Add New Project")

    with st.form("add_project_form"):
        new_proj_name = st.text_input("Project Name")
        new_proj_desc = st.text_area("Project Description")
        n_exp = st.number_input("Number of Experiments", min_value=1, max_value=10, value=3, step=1)

        new_exp_names = []
        new_exp_dates = []

        for i in range(1, n_exp + 1):
            new_exp_names.append(st.text_input(f"Experiment {i} Name", key=f"new_exp_name_{i}"))
            new_exp_dates.append(st.text_input(f"Planned Date for Experiment {i} (YYYY-MM-DD)", key=f"new_exp_date_{i}"))

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
                for i in range(1, n_exp + 1):
                    new_row[f"Exp{i} Name"] = new_exp_names[i - 1]
                    new_row[f"Exp{i} Date"] = new_exp_dates[i - 1]
                    new_row[f"Exp{i} Done"] = False

                projects_df = pd.concat([projects_df, pd.DataFrame([new_row])], ignore_index=True)
                save_projects(projects_df)
                st.success(f"Project '{new_proj_name}' added!")

# =======================
# PAGE: CAGES
# =======================
elif page == "Cages":
    st.subheader("🐁 Cages Management")

    # Filtro por projeto
    selected_project = st.selectbox("Select Project", ["All"] + projects_df["Project"].tolist())

    # Filtro por tipo
    selected_types = st.multiselect("Filter by Type", ["Breeder", "Experimental", "None"], default=["Breeder", "Experimental", "None"])

    filtered_cages = cages_df.copy()

    if selected_project != "All":
        filtered_cages = filtered_cages[filtered_cages["Project"] == selected_project]

    filtered_cages = filtered_cages[filtered_cages["Type"].isin(selected_types)]

    # Mostrar tabela de cages
    cage_rows = []
    for cage_id in filtered_cages["Cage"].unique():
        cage_animals = animals_df[animals_df["Cage"] == cage_id]
        total = len(cage_animals)
        males = len(cage_animals[cage_animals["Sex"] == "Male"])
        females = len(cage_animals[cage_animals["Sex"] == "Female"])
        cage_type = filtered_cages[filtered_cages["Cage"] == cage_id]["Type"].iloc[0]

        cage_rows.append({
            "Cage": cage_id,
            "Total Animals": total,
            "Males": males,
            "Females": females,
            "Type": cage_type
        })

    cage_df_display = pd.DataFrame(cage_rows)
    st.dataframe(cage_df_display)

    # Botão para ver animais
    for cage_id in filtered_cages["Cage"].unique():
        if st.button(f"See animals in {cage_id}"):
            cage_animals = animals_df[animals_df["Cage"] == cage_id]
            st.write(cage_animals)

# =======================
# PAGE: ADD ANIMALS
# =======================
elif page == "Add Animals":
    st.subheader("➕ Add New Animal")

    with st.form("add_animal_form"):
        animal_id = st.text_input("Animal ID")
        cage_id = st.text_input("Cage")
        sex = st.selectbox("Sex", ["Male", "Female"])
        animal_type = st.selectbox("Type", ["Breeder", "Experimental", "None"])
        submit_animal = st.form_submit_button("Add Animal")

        if submit_animal:
            if animal_id.strip() == "":
                st.error("Animal ID cannot be empty.")
            else:
                new_row = {
                    "AnimalID": animal_id,
                    "Cage": cage_id,
                    "Sex": sex,
                    "Type": animal_type
                }
                animals_df = pd.concat([animals_df, pd.DataFrame([new_row])], ignore_index=True)
                save_animals(animals_df)
                st.success(f"Animal '{animal_id}' added!")
