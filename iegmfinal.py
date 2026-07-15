import streamlit as st
import pandas as pd
import sqlite3
import os

def somar_pontos_padrao(nome_banco, ano):
    """Calcula a soma padrão de pontos para os bancos (escala original de 0-1000)."""
    caminho_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), nome_banco)
    if not os.path.exists(caminho_db):
        return 0
    try:
        conn = sqlite3.connect(caminho_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='respostas';")
        if not cursor.fetchone():
            conn.close()
            return 0
        
        cursor.execute("SELECT pontos FROM respostas WHERE ano = ?", (ano,))
        linhas = cursor.fetchall()
        conn.close()
        
        if not linhas:
            return 0
        
        total = sum(float(row[0]) for row in linhas if row[0] is not None and str(row[0]).strip() != "")
        return int(round(total))
    except Exception:
        return 0

def puxar_nota_icidade(ano):
    return somar_pontos_padrao("dados_iegm_web.db", ano)

def puxar_nota_igov(ano):
    return somar_pontos_padrao("dados_igov_ti.db", ano)

def puxar_nota_iamb(ano):
    return somar_pontos_padrao("dados_iamb.db", ano)

def puxar_nota_iplan(ano):
    return somar_pontos_padrao("dados_iplan.db", ano)

def puxar_nota_ieduc(ano):
    return somar_pontos_padrao("dados_ieduc.db", ano)

def puxar_nota_isaude(ano):
    return somar_pontos_padrao("dados_isaude.db", ano)

def puxar_nota_ifiscal(ano):
    caminho_db = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados_ifiscal.db")
    if not os.path.exists(caminho_db):
        return 0
    try:
        conn = sqlite3.connect(caminho_db)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='respostas';")
        if not cursor.fetchone():
            conn.close()
            return 0
            
        cursor.execute("SELECT pontos FROM respostas WHERE ano = ?", (ano,))
        linhas = cursor.fetchall()
        conn.close()
        
        if not linhas:
            return 0
            
        valores = []
        for row in linhas:
            if row[0] is not None and str(row[0]).strip() != "":
                valores.append(float(row[0]))
        
        if any(v <= -100.0 for v in valores):
            return 0
            
        total_pts = sum(v for v in valores if v > -100.0)
        return int(round(total_pts))
    except Exception:
        return 0

def calcular_nota_final(plan, fiscal, educ, saude, amb, cidade, gov):
    try:
        v_plan = float(plan or 0)
        v_fiscal = float(fiscal or 0)
        v_educ = float(educ or 0)
        v_saude = float(saude or 0)
        v_amb = float(amb or 0)
        v_cidade = float(cidade or 0)
        v_gov = float(gov or 0)
        
        soma_ponderada = (v_plan * 20) + (v_fiscal * 20) + (v_educ * 20) + (v_saude * 20) + (v_amb * 10) + (v_cidade * 5) + (v_gov * 5)
        nota_final = soma_ponderada / 100.0
        return int(round(nota_final))
    except Exception:
        return 0

def obter_faixa_classificacao(nota):
    if nota >= 900: return "A (Altamente Efetiva)", "#10B981"
    elif nota >= 750: return "B+ (Muito Efetiva)", "#3B82F6"
    elif nota >= 600: return "B (Efetiva)", "#F59E0B"
    elif nota >= 500: return "C+ (Em Fase de Adequação)", "#F97316"
    else: return "C (Baixo Nível de Adequação)", "#EF4444"

def recarregar_e_calcular_dados():
    anos = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030]
    registro_historico = []
    
    for ano in anos:
        plan = puxar_nota_iplan(ano)
        fiscal = puxar_nota_ifiscal(ano)
        educ = puxar_nota_ieduc(ano)
        saude = puxar_nota_isaude(ano)
        amb = puxar_nota_iamb(ano)
        cidade = puxar_nota_icidade(ano)
        gov = puxar_nota_igov(ano)
        
        nota_f = calcular_nota_final(plan, fiscal, educ, saude, amb, cidade, gov)
        faixa, _ = obter_faixa_classificacao(nota_f)
        
        registro_historico.append({
            "Ano": ano,
            "i-Plan": int(plan),
            "i-Fiscal": int(fiscal),
            "i-Educ": int(educ),
            "i-Saúde": int(saude),
            "i-Amb": int(amb),
            "i-Cidade": int(cidade),
            "i-Gov TI": int(gov),
            "Nota Final": int(nota_f),
            "Faixa": faixa.split(" (")[0]
        })
    
    df = pd.DataFrame(registro_historico)
    return calcular_variacoes_e_faixas(df)

def calcular_variacoes_e_faixas(df):
    for i in range(len(df)):
        nota_f = calcular_nota_final(
            df.loc[i, "i-Plan"],
            df.loc[i, "i-Fiscal"],
            df.loc[i, "i-Educ"],
            df.loc[i, "i-Saúde"],
            df.loc[i, "i-Amb"],
            df.loc[i, "i-Cidade"],
            df.loc[i, "i-Gov TI"]
        )
        df.loc[i, "Nota Final"] = int(nota_f)
        faixa, _ = obter_faixa_classificacao(nota_f)
        df.loc[i, "Faixa"] = faixa.split(" (")[0]

    variacoes = ["-"]
    for i in range(1, len(df)):
        nota_ant = df.loc[i-1, "Nota Final"]
        nota_at = df.loc[i, "Nota Final"]
        
        if nota_ant == 0:
            variacoes.append("▲ +100.0%" if nota_at > 0 else "0.0%")
        else:
            pct = ((nota_at - nota_ant) / nota_ant) * 100
            if pct > 0:
                variacoes.append(f"▲ +{pct:.1f}%")
            elif pct < 0:
                variacoes.append(f"▼ {pct:.1f}%")
            else:
                variacoes.append("0.0%")
                
    df["Variação %"] = variacoes
    colunas_ordenadas = ["Ano", "i-Plan", "i-Fiscal", "i-Educ", "i-Saúde", "i-Amb", "i-Cidade", "i-Gov TI", "Nota Final", "Variação %", "Faixa"]
    return df[colunas_ordenadas]

def mostrar_painel_iegm_final(ano_selecionado):
    st.subheader("🏆 Consolidação do Índice de Efetividade da Gestão Municipal (IEG-M)")
    
    if "df_historico" not in st.session_state:
        st.session_state.df_historico = recarregar_e_calcular_dados()

    if st.sidebar.button("Restaurar Dados Originais (Banco de Dados)"):
        st.session_state.df_historico = recarregar_e_calcular_dados()
        st.rerun()

    df_historico = st.session_state.df_historico

    if ano_selecionado in df_historico["Ano"].values:
        dados_ano_atual = df_historico[df_historico["Ano"] == ano_selecionado].iloc[0]
    else:
        dados_ano_atual = df_historico.iloc[0]
        
    nota_f_atual = dados_ano_atual["Nota Final"]
    faixa_atual, cor_atual = obter_faixa_classificacao(nota_f_atual)
    
    # ----------------- SEÇÃO 1: RESULTADO CONSOLIDADO -----------------
    st.markdown("---")
    st.markdown(f"### Resultado Consolidado Real: Ano de Referência {ano_selecionado}")
    
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        st.metric(label="Nota Final Calculada", value=f"{int(nota_f_atual)} pts")
    with c2:
        st.markdown("**Faixa TCESP:**")
        st.markdown(f"<div style='padding: 8px; border-radius: 8px; background-color: {cor_atual}; color: white; text-align: center; font-weight: bold;'>{faixa_atual}</div>", unsafe_allow_html=True)
    with c3:
        st.info("💡 **Fórmula TCESP:** `(i-Plan×20 + i-Fiscal×20 + i-Educ×20 + i-Saúde×20 + i-Amb×10 + i-Cidade×5 + i-Gov TI×5) / 100`")

    st.markdown("#### Desempenho das Dimensões (Escala 0-1000)")
    dados_tabela_atual = pd.DataFrame({
        "Dimensão": ["i-Plan", "i-Fiscal", "i-Educ", "i-Saúde", "i-Amb", "i-Cidade", "i-Gov TI"],
        "Peso TCESP": ["20%", "20%", "20%", "20%", "10%", "5%", "5%"],
        "Pontuação Obtida": [
            int(dados_ano_atual["i-Plan"]), int(dados_ano_atual["i-Fiscal"]),
            int(dados_ano_atual["i-Educ"]), int(dados_ano_atual["i-Saúde"]),
            int(dados_ano_atual["i-Amb"]), int(dados_ano_atual["i-Cidade"]),
            int(dados_ano_atual["i-Gov TI"])
        ]
    })
    
    st.dataframe(
        dados_tabela_atual, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Dimensão": st.column_config.TextColumn("Dimensão"),
            "Peso TCESP": st.column_config.TextColumn("Peso TCESP"),
            "Pontuação Obtida": st.column_config.NumberColumn("Pontuação Obtida", format="%d pts")
        }
    )

    # ----------------- SEÇÃO 2: GRÁFICO -----------------
    st.markdown("---")
    st.markdown("### 📊 Painel Evolutivo — Série Histórica Real (2023 a 2030)")
    df_grafico = df_historico.set_index("Ano")[["Nota Final"]]
    st.bar_chart(df_grafico)

    # ----------------- SEÇÃO 3: MATRIZ DE DADOS HISTÓRICOS -----------------
    st.markdown("---")
    st.markdown("### 📅 Matriz de Dados Históricos Consolidados")
    
    def colorir_faixa(val):
        if val == "A": return "background-color: #d1fae5; color: #065f46; font-weight: bold;"
        elif val == "B+": return "background-color: #dbeafe; color: #1e40af; font-weight: bold;"
        elif val == "B": return "background-color: #fef3c7; color: #92400e; font-weight: bold;"
        elif val == "C+": return "background-color: #ffedd5; color: #9a3412; font-weight: bold;"
        else: return "background-color: #fee2e2; color: #991b1b; font-weight: bold;"

    def colorir_variacao(val):
        if "▲" in str(val): return "color: #10B981; font-weight: bold;"
        elif "▼" in str(val): return "color: #EF4444; font-weight: bold;"
        return "color: #64748b;"

    df_estilizado = df_historico.style\
        .map(colorir_faixa, subset=["Faixa"])\
        .map(colorir_variacao, subset=["Variação %"])\
        .set_properties(**{'text-align': 'center'})\
        .set_properties(subset=["Nota Final"], **{'background-color': '#f1f5f9', 'font-weight': 'bold', 'color': '#1e293b'})

    st.dataframe(df_estilizado, use_container_width=True, hide_index=True)
    
    # Form de Ajuste
    st.markdown("### ✏️ Ajustar Pontuação")
    with st.expander("Clique aqui para editar notas da série histórica"):
        with st.form("form_edicao"):
            ano_edit = st.selectbox("Selecione o Ano para Alterar:", df_historico["Ano"].values)
            linha_original = df_historico[df_historico["Ano"] == ano_edit].iloc[0]
            
            c_ed1, c_ed2, c_ed3, c_ed4 = st.columns(4)
            with c_ed1:
                n_plan = st.number_input("i-Plan", min_value=0, max_value=1000, value=int(linha_original["i-Plan"]))
                n_fiscal = st.number_input("i-Fiscal", min_value=0, max_value=1000, value=int(linha_original["i-Fiscal"]))
            with c_ed2:
                n_educ = st.number_input("i-Educ", min_value=0, max_value=1000, value=int(linha_original["i-Educ"]))
                n_saude = st.number_input("i-Saúde", min_value=0, max_value=1000, value=int(linha_original["i-Saúde"]))
            with c_ed3:
                n_amb = st.number_input("i-Amb", min_value=0, max_value=1000, value=int(linha_original["i-Amb"]))
                n_cidade = st.number_input("i-Cidade", min_value=0, max_value=1000, value=int(linha_original["i-Cidade"]))
            with c_ed4:
                n_gov = st.number_input("i-Gov TI", min_value=0, max_value=1000, value=int(linha_original["i-Gov TI"]))
                
            btn_salvar = st.form_submit_button("Salvar Alterações e Recalcular Painel")
            
            if btn_salvar:
                df_copia = df_historico.copy()
                idx_linha = df_copia[df_copia["Ano"] == ano_edit].index[0]
                
                df_copia.loc[idx_linha, "i-Plan"] = n_plan
                df_copia.loc[idx_linha, "i-Fiscal"] = n_fiscal
                df_copia.loc[idx_linha, "i-Educ"] = n_educ
                df_copia.loc[idx_linha, "i-Saúde"] = n_saude
                df_copia.loc[idx_linha, "i-Amb"] = n_amb
                df_copia.loc[idx_linha, "i-Cidade"] = n_cidade
                df_copia.loc[idx_linha, "i-Gov TI"] = n_gov
                
                st.session_state.df_historico = calcular_variacoes_e_faixas(df_copia)
                st.success(f"Alterações de {ano_edit} salvas com sucesso!")
                st.rerun()
