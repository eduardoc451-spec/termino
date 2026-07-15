from datetime import datetime, timezone, timedelta
import streamlit as st
import pandas as pd
import io
import sqlite3
import os
import re
import xml.sax.saxutils as saxutils

# ==========================================
# 🛠️ FUNÇÕES AUXILIARES DE TRADUÇÃO E PROCESSAMENTO
# ==========================================

def escapar_texto(texto):
    if texto is None:
        return ""
    return saxutils.escape(str(texto))

def higienizar_e_traduzir_quesito(id_quesito):
    id_original = str(id_quesito).strip()
    if id_original.endswith('.0'):
        id_original = id_original[:-2]
    if id_original == "1": id_original = "1.0"
    if id_original == "2": id_original = "2.0"
    if id_original == "3": id_original = "3.0"
    if id_original == "4": id_original = "4.0"
    if id_original == "5": id_original = "5.0"
    if id_original == "6": id_original = "6.0"
    if id_original == "7": id_original = "7.0"
    if id_original == "8": id_original = "8.0"
    if id_original == "9": id_original = "9.0"
    if id_original == "10": id_original = "10.0"
    if id_original == "11": id_original = "11.0"
    if id_original == "12": id_original = "12.0"
    
    PROVEDOR_DE_ENUNCIADOS = {
        "1.0": "A Prefeitura possui uma área ou sector que cuida de Tecnologia da Informação e Comunicação (TIC)?",
        "1.1": "Informe a quantidade de funcionários concursados, comissionados e estagiários no suporte e atendimento de primeiro nível.",
        "1.2": "A prefeitura municipal definiu formalmente as atribuições do pessoal do setor de Tecnologia da Informação e Comunicação (TIC)?",
        "1.3": "A prefeitura disponibilizou capacitação para o pessoal da área de Tecnologia da Informação e Comunicação (TIC)?",
        "1.3.1": "Informe em quais áreas houve capacitação.",
        "1.4": "Nas licitações e contratos que tenham como soluções o uso de TIC, houve participação formalizada do pessoal de TIC? (Verba municipal)",
        "1.4.1": "Assinale as etapas que o pessoal de TIC participa.",
        "1.4.2": "Sobre softwares adquiridos/licenciados nos últimos 5 anos, foi realizada análise ou estudo prévio com a participação de TIC?",
        "2.0": "A prefeitura municipal possui um PDTIC vigente que estabeleça diretrizes e metas de atingimento no futuro?",
        "2.1": "Informe a página eletrônica (link na internet) do PDTIC.",
        "2.2": "O plano de TIC vigente contempla as metas operacionais estratégicas municipais?",
        "2.3": "Qual a data da última atualização do PDTIC?",
        "3.0": "A Prefeitura dispõe de Política de Segurança da Informação formalmente instituída e de cumprimento obrigatório?",
        "3.1": "A Prefeitura estabelece procedimentos e responsabilidades quanto ao uso de TI (Termo de Responsabilidade/Compromisso)?",
        "3.1.1": "O Termo de Responsabilidade/Compromisso dispõe sobre o uso da assinatura eletrônica pelos funcionários?",
        "3.1.1.1": "Informe o tipo de assinatura eletrônica utilizada nos documentos digitais.",
        "3.2": "Os riscos de TIC são identificados de acordo com as normas brasileiras da família ISO/IEC 27000?",
        "3.2.1": "As secretarias realizam a fiscalização das áreas de risco? Informe quais normas ISO/IEC 27000 são utilizadas.",
        "3.3": "Os riscos de TIC são identificados de acordo com as normas da ABNT NBR ISO/IEC 31000?",
        "3.4": "A Prefeitura possui um Plano de Continuidade dos Serviços de Tecnologia da Informação e Comunicação (TIC)?",
        "3.5": "A Prefeitura dispõe de política de cópias de segurança (backup) formalmente instituída como norma obrigatória?",
        "3.6": "A Prefeitura possui inventário atualizado dos ativos de TIC?",
        "3.6.1": "Como é composta a base de ativos?",
        "4.0": "O município regulamentou a Lei de Acesso à Informação (Lei Federal nº 12.527/2011)?",
        "4.1": "Informe o Instrumento normativo, Número e Data da publicação (LAI).",
        "4.2": "Página eletrônica (link na internet) do instrumento normativo da LAI.",
        "5.0": "O município regulamentou a Lei sobre Eficiência Pública (Governo Digital - Lei Federal nº 14.129/2021)?",
        "5.1": "Informe o Instrumento normativo, Número e Data da publicação (Governo Digital).",
        "5.2": "Página eletrônica (link na internet) do instrumento normativo (Governo Digital).",
        "5.3": "A Prefeitura implantou soluções digitais para trâmite de processos administrativos?",
        "6.0": "A prefeitura mantém site na internet com informações atualizadas?",
        "6.1": "O site eletrônico da prefeitura continha ferramenta de pesquisa/busca interna de conteúdo?",
        "6.2": "O site possibilita o download de dados e informações em formatos abertos e não proprietários?",
        "6.3": "O site disponibiliza as respostas a perguntas mais frequentes da sociedade?",
        "6.4": "O site disponibiliza acessibilidade de conteúdo para pessoas com deficiência?",
        "7.0": "A Prefeitura disponibiliza no site o Serviço de Informação ao Cidadão (e-SIC)?",
        "7.1": "A solicitação por meio do e-SIC é simplificada?",
        "7.2": "O e-SIC apresenta possibilidade de acompanhamento da solicitação?",
        "7.3": "Há necessidade de informar os motivos para a solicitação de informações de interesse público?",
        "8.0": "A Prefeitura possui programs de computador (softwares) para gestão de processos?",
        "8.1": "Os programas de computador (softwares) englobam quais processos/setores?",
        "8.2": "Informe quais sistemas encontram-se integrados ao Sistema de Contabilidade do município.",
        "8.2.1": "Informe o nível de integração entre o Sistema da Dívida Ativa e o de Contabilidade.",
        "8.2.2": "Informe o nível de integração entre o Sistema de Precatórios e o de Contabilidade.",
        "8.3": "Assinale quais bases de dados encontram-se sob gestão direta da Prefeitura (Risco de Perdas).",
        "8.4": "Assinale quais sistemas possuem controle de acesso à informação.",
        "9.0": "A Prefeitura ofereceu services de forma online?",
        "9.1": "Quais types de serviços são oferecidos online?",
        "9.2": "Quais as formas de atendimento à distância disponibilizadas ao público pela Prefeitura?",
        "10.0": "A Prefeitura Municipal regulamentou o tratamento de dados pessoais, inclusive nos meios digitais, segundo a LGPD (Lei Federal nº 13.709/2018)?",
        "10.1": "Informe o instrumento normativo, número e data da publicação.",
        "10.2": "Informe a página eletrônica (link na internet).",
        "10.3": "Os contratos com os prestadores de serviços contêm cláusulas de observância à LGPD?",
        "10.4": "A Prefeitura Municipal realizou mapeamento de dados (data mapping)?",
        "10.5": "Foram adotadas medidas de segurança, técnicas e administrativas para proteção dos dados pessoais?",
        "10.5.1": "Informe as medidas adotadas.",
        "11.0": "A Prefeitura Municipal designou um encarregado para as operações de tratamento de dados pessoais?",
        "11.1": "Informe a página eletrônica que contenha a identidade e as informações de contato do encarregado.",
        "12.0": "Gostaria de registrar suas impressões, comentários e sugestões a respeito do presente questionário?"
    }
    
    return PROVEDOR_DE_ENUNCIADOS.get(id_original, None), PROVEDOR_DE_ENUNCIADOS

def obter_banco_respostas_real(ano, dimensão):
    mapeamento_bancos = {
        "i-Gov TI": "dados_igov_ti.db",
        "i-Educ": "dados_ieduc.db",
        "i-Saúde": "dados_isaude.db",
        "i-Plan": "dados_iplan.db",
        "i-Amb": "dados_iamb.db",
        "i-Cidade": "dados_iegm.db",
        "i-Fiscal": "dados_ifiscal.db"
    }
    
    arquivo_db = mapeamento_bancos.get(dimensão)
    if not arquivo_db or not os.path.exists(arquivo_db):
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(arquivo_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = [row[0] for row in cursor.fetchall()]
        if not tabelas:
            conn.close()
            return pd.DataFrame()
            
        tabela_real = tabelas[0]
        query = f"SELECT * FROM {tabela_real}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        coluna_ano = [col for col in df.columns if 'ano' in col.lower()]
        if coluna_ano:
            df[coluna_ano[0]] = df[coluna_ano[0]].astype(str)
            df = df[df[coluna_ano[0]].str.contains(str(ano))]
            
        return df
    except Exception as e:
        st.error(f"Erro ao ler o banco {arquivo_db}: {e}")
        return pd.DataFrame()

def localizar_colunas_exatas(df):
    colunas = list(df.columns)
    col_codigo = "id_quesito" if "id_quesito" in colunas else colunas[0]
    col_resposta = "Resposta / Situação" if "Resposta / Situação" in colunas else colunas[2] if len(colunas) > 2 else colunas[1]
    col_nota = "Nota" if "Nota" in colunas else colunas[3] if len(colunas) > 3 else colunas[-2]
    return col_codigo, col_resposta, col_nota

def aplicar_ordenacao_natural(df, col_codigo):
    df_copia = df.copy()
    def extrair_valores(texto):
        numeros = re.findall(r'\d+\.\d+|\d+', str(texto))
        return float(numeros[0]) if numeros else 9999.0

    df_copia['temp_ordem_num'] = df_copia[col_codigo].apply(extrair_valores)
    df_copia = df_copia.sort_values(by='temp_ordem_num', ascending=True)
    df_copia = df_copia.drop(columns=['temp_ordem_num'])
    return df_copia

# ==========================================
# 📄 GERADOR DE RELATÓRIO PDF (REPORTLAB)
# ==========================================

def gerar_pdf_reportlab(ano, dimensão, df_filtrado):
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=landscape(letter), 
        rightMargin=20, 
        leftMargin=20, 
        topMargin=30, 
        bottomMargin=30
    )
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#001A4D'), alignment=1)
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Normal'], fontSize=12, leading=16, textColor=colors.HexColor('#64748B'), alignment=1, spaceAfter=20)
    
    cell_text_style = ParagraphStyle('CellTextStyle', parent=styles['Normal'], fontSize=8, leading=11, textColor=colors.black)
    cell_header_style = ParagraphStyle('CellHeaderStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=colors.HexColor('#001A4D'))

    story.append(Paragraph("IEG-M Francisco Morato", title_style))
    story.append(Paragraph("EXTRATO OFICIAL DE AUDITORIA E RASTREABILIDADE", subtitle_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph(f"<b>Ano de Referência:</b> {ano}", cell_text_style))
    story.append(Paragraph(f"<b>Dimensão Selecionada:</b> {dimensão}", cell_text_style))
    story.append(Spacer(1, 15))
    
    col_codigo, col_resposta, col_nota = localizar_colunas_exatas(df_filtrado)
    
    data_tabela = [[
        Paragraph("Nº Quesito", cell_header_style),
        Paragraph("Descrição do Quesito", cell_header_style), 
        Paragraph("Resposta / Situação", cell_header_style), 
        Paragraph("Nota", cell_header_style)
    ]]
    
    dimensao_normalizada = str(dimensão).lower().replace(" ", "").replace("-", "")
    is_igov_ti = "igovti" in dimensao_normalizada

    if is_igov_ti:
        _, dicionario_mestre = higienizar_e_traduzir_quesito("1.0")
        respostas_no_banco = {}
        for _, linha in df_filtrado.iterrows():
            id_banco = str(linha[col_codigo]).strip()
            if id_banco.endswith('.0'):
                id_banco = id_banco[:-2]
            if id_banco.isdigit() and '.' not in id_banco:
                id_banco = f"{id_banco}.0"
            respostas_no_banco[id_banco] = linha

        for id_mestre, enunciado_mestre in dicionario_mestre.items():
            linha_banco = respostas_no_banco.get(id_mestre)
            if linha_banco is not None:
                resposta_crua = str(linha_banco[col_resposta]).strip()
                nota_final = str(linha_banco[col_nota])
            else:
                resposta_crua = "Não Respondido / Em Branco"
                nota_final = "—"

            if resposta_crua.startswith("[") and resposta_crua.endswith("]"):
                resposta_crua = resposta_crua.replace("[", "").replace("]", "").replace("'", "").replace('"', '').strip()
            if resposta_crua.lower() in ["none", "null", "nan", "", "selecione..."]:
                resposta_crua = "Não Respondido / Em Branco"

            data_tabela.append([
                Paragraph(escapar_texto(id_mestre), cell_text_style),
                Paragraph(escapar_texto(enunciado_mestre), cell_text_style),
                Paragraph(escapar_texto(resposta_crua), cell_text_style),
                Paragraph(escapar_texto(nota_final), cell_text_style)
            ])
    else:
        df_ordenado = aplicar_ordenacao_natural(df_filtrado, col_codigo)
        for _, linha in df_ordenado.iterrows():
            id_original = str(linha[col_codigo]).strip()
            if id_original.isdigit():
                id_original = f"{id_original}.0"
            
            texto_final = str(linha.get('Descrição do Quesito', f"Quesito de Auditoria Técnica — Referência {id_original}"))
            if "qid" in texto_final or "str(" in texto_final or "pts" in texto_final or texto_final.strip() == id_original:
                texto_final = f"Quesito de Auditoria Técnica — Referência {id_original}"

            resposta_crua = str(linha[col_resposta]).strip()
            if resposta_crua.startswith("[") and resposta_crua.endswith("]"):
                resposta_crua = resposta_crua.replace("[", "").replace("]", "").replace("'", "").replace('"', '').strip()
            if resposta_crua.lower() in ["none", "null", "nan", "", "selecione..."]:
                resposta_crua = "Não Respondido / Em Branco"
                
            data_tabela.append([
                Paragraph(escapar_texto(id_original), cell_text_style),
                Paragraph(escapar_texto(texto_final), cell_text_style),
                Paragraph(escapar_texto(resposta_crua), cell_text_style),
                Paragraph(escapar_texto(linha[col_nota]), cell_text_style)
            ])
    
    larguras = [65, 316, 316, 55]
    t = Table(data_tabela, colWidths=larguras, repeatRows=1, splitByRow=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E6F0FF')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),  
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ==========================================
# 🕒 SISTEMA DE RASTREAMENTO DINÂMICO NO BANCO FÍSICO
# ==========================================

def conectar_banco_sessoes():
    """Garante a conexão e a criação segura das tabelas físicas no arquivo SQLite."""
    conn = sqlite3.connect("sessoes_usuarios.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios_tempo (
            usuario TEXT PRIMARY KEY,
            email TEXT,
            senha TEXT,
            ultimo_login TEXT,
            tempo_acumulado_segundos INTEGER DEFAULT 0,
            sessao_ativa INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico_sessoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT,
            inicio_sessao TEXT,
            fim_sessao TEXT,
            duracao_segundos INTEGER
        )
    """)
    
    # Popula com as contas reais se estiver vazio
    cursor.execute("SELECT COUNT(*) FROM usuarios_tempo")
    if cursor.fetchone()[0] == 0:
        usuarios_padrao = [
            ("jefferson.espanha", "jefferson.espanha@franciscomorato.sp.gov.br", "123", None, 0, 0),
            ("admin", "admin@morato.sp.gov.br", "123", None, 0, 0),
            ("auditor", "auditor@morato.sp.gov.br", "123", None, 0, 0)
        ]
        cursor.executemany("""
            INSERT INTO usuarios_tempo (usuario, email, senha, ultimo_login, tempo_acumulado_segundos, sessao_ativa)
            VALUES (?, ?, ?, ?, ?, ?)
        """, usuarios_padrao)
        conn.commit()
        
    return conn, cursor

def registrar_entrada_banco(usuario):
    """
    Registra a entrada do usuário. Se o usuário 'jefferson.espanha' ou qualquer outro
    não existir na tabela, ele é criado na hora com sua senha padrão.
    """
    conn, cursor = conectar_banco_sessoes()
    usuario_sanitizado = str(usuario).lower().strip()
    
    cursor.execute("SELECT usuario FROM usuarios_tempo WHERE usuario = ?", (usuario_sanitizado,))
    existe = cursor.fetchone()
    
    if not existe:
        email_automatico = f"{usuario_sanitizado}@franciscomorato.sp.gov.br"
        cursor.execute("""
            INSERT INTO usuarios_tempo (usuario, email, senha, ultimo_login, tempo_acumulado_segundos, sessao_ativa)
            VALUES (?, ?, '123', NULL, 0, 0)
        """, (usuario_sanitizado, email_automatico))
        conn.commit()
    
    agora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        UPDATE usuarios_tempo 
        SET ultimo_login = ?, sessao_ativa = 1 
        WHERE usuario = ?
    """, (agora_str, usuario_sanitizado))
    conn.commit()
    
    st.session_state["usuario_atual_sistema"] = usuario_sanitizado
    st.session_state["inicio_sessao_atual"] = datetime.now()
    st.session_state["ultimo_checkpoint_tempo"] = datetime.now()
    
    conn.close()

def atualizar_tempo_decorrido_no_banco():
    """
    Calcula os segundos transcorridos desde a última ação/clique
    e salva direto no banco físico de forma incremental.
    """
    if "usuario_atual_sistema" not in st.session_state or "ultimo_checkpoint_tempo" not in st.session_state:
        return
        
    usuario = st.session_state["usuario_atual_sistema"]
    agora = datetime.now()
    ultimo_checkpoint = st.session_state["ultimo_checkpoint_tempo"]
    
    segundos_decorridos = int((agora - ultimo_checkpoint).total_seconds())
    
    if segundos_decorridos > 0:
        conn, cursor = conectar_banco_sessoes()
        cursor.execute("""
            UPDATE usuarios_tempo 
            SET tempo_acumulado_segundos = tempo_acumulado_segundos + ?
            WHERE usuario = ?
        """, (segundos_decorridos, usuario))
        conn.commit()
        conn.close()
        
        st.session_state["ultimo_checkpoint_tempo"] = agora

def registrar_saida_banco(usuario):
    """Fecha a sessão de forma limpa quando o logoff manual é acionado."""
    atualizar_tempo_decorrido_no_banco()
    
    conn, cursor = conectar_banco_sessoes()
    usuario_sanitizado = str(usuario).lower().strip()
    
    cursor.execute("""
        UPDATE usuarios_tempo 
        SET sessao_ativa = 0
        WHERE usuario = ?
    """, (usuario_sanitizado,))
    conn.commit()
    conn.close()
    
    st.session_state.pop("inicio_sessao_atual", None)
    st.session_state.pop("ultimo_checkpoint_tempo", None)
    st.session_state.pop("usuario_atual_sistema", None)

def auto_rastreamento_sessao_permanente():
    """Busca o usuário logado e garante o rastreamento ativo e o salvamento em cada interação."""
    chaves_comuns = ["username", "usuario", "usuario_ativo", "logged_in_user", "email", "user"]
    usuario_atual = None
    
    for chave in chaves_comuns:
        if chave in st.session_state and st.session_state[chave]:
            usuario_atual = str(st.session_state[chave]).lower().strip()
            break

    # Se não houver chave de login ativo, adota 'jefferson.espanha' como padrão
    if not usuario_atual:
        usuario_atual = "jefferson.espanha"

    # Se a sessão acabou de iniciar na memória
    if "usuario_atual_sistema" not in st.session_state:
        registrar_entrada_banco(usuario_atual)
    else:
        atualizar_tempo_decorrido_no_banco()

def formatar_tempo_amigavel(segundos):
    """Formata segundos acumulados salvos de forma legível."""
    if segundos is None or segundos == 0:
        return "0s"
    
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60
    
    partes = []
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}min")
    if segs > 0 or not partes:
        partes.append(f"{segs}s")
        
    return " ".join(partes)


# ==========================================
# 🔒 PAINEL ADMINISTRATIVO E INTERFACE DO USUÁRIO
# ==========================================

def mostrar_painel_admin(ano_global):
    """Exibe o painel de governança, o tempo de sessão acumulado e a geração de PDFs."""
    st.subheader("🔒 Painel de Controle de Governança")
    
    senha_mestra = st.text_input("🔑 Digite a senha master para desbloquear as informações:", type="password", key="admin_page_password")
    
    if senha_mestra != "fodasse":
        if senha_mestra:
            st.error("❌ Senha Mestra incorreta. Acesso negado.")
        else:
            st.info("💡 Digite a senha master do administrador para liberar a emissão de relatórios.")
        return

    st.success("🔓 Acesso Concedido!")
    
    # 1. Rastreia e salva as interações do usuário atual
    auto_rastreamento_sessao_permanente()
    usuario_atual = st.session_state.get("usuario_atual_sistema", "jefferson.espanha")
    
    # 2. Painel de Usuários
    with st.expander("👥 Visualizar Usuários do Sistema e Tempo de Sessão Ativa", expanded=True):
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔄 Atualizar Cronômetro de Sessão", use_container_width=True):
                # Força a atualização do tempo no banco físico antes de recarregar a tela
                atualizar_tempo_decorrido_no_banco()
                st.rerun()
        with col_btn2:
            if st.button("🚪 Simular Logoff de Todos", use_container_width=True):
                conn, cursor = conectar_banco_sessoes()
                cursor.execute("SELECT usuario FROM usuarios_tempo WHERE sessao_ativa = 1")
                usuarios_ativos = [r[0] for r in cursor.fetchall()]
                conn.close()
                
                for usr in usuarios_ativos:
                    registrar_saida_banco(usr)
                    
                st.success("Todas as sessões ativas foram encerradas e os tempos consolidados!")
                st.rerun()

        # Resgata dados reais do banco SQLite
        conn, cursor = conectar_banco_sessoes()
        cursor.execute("SELECT usuario, email, senha, ultimo_login, tempo_acumulado_segundos, sessao_ativa FROM usuarios_tempo")
        linhas = cursor.fetchall()
        conn.close()

        lista_usuarios = []
        for usuario, email_usr, senha_usr, ultimo_login_str, total_segundos_acumulados, ativa in linhas:
            
            # Se for o usuário ativo olhando a tabela, somamos o tempo gerado dinamicamente nesta sessão atual
            if ativa == 1 and usuario == usuario_atual and "ultimo_checkpoint_tempo" in st.session_state:
                agora = datetime.now()
                ultimo_checkpoint = st.session_state["ultimo_checkpoint_tempo"]
                tempo_decorrido_na_tela = int((agora - ultimo_checkpoint).total_seconds())
                
                status_tempo = "🟢 Conectado agora"
                tempo_total_exibido = total_segundos_acumulados + tempo_decorrido_na_tela
            elif ativa == 1:
                status_tempo = "🟢 Online"
                tempo_total_exibido = total_segundos_acumulados
            else:
                status_tempo = "🔴 Offline"
                tempo_total_exibido = total_segundos_acumulados

            lista_usuarios.append({
                "Nome de Usuário": usuario,
                "E-mail": email_usr,
                "Senha de Acesso": senha_usr,  # <--- Senha real exposta no painel de administração
                "Último Acesso": ultimo_login_str if ultimo_login_str else "—",
                "Status": status_tempo,
                "Tempo Total Acumulado (Salvo)": formatar_tempo_amigavel(tempo_total_exibido)
            })
            
        df_usuarios = pd.DataFrame(lista_usuarios)
        st.dataframe(df_usuarios, use_container_width=True)

    st.markdown("---")

    # --- GERADOR DE RELATÓRIO OFICIAL (PDF) ---
    st.markdown("### 📄 Emissão de Relatório Oficial (PDF)")
    
    col_ano, col_dim = st.columns(2)
    with col_ano:
        ano_busca = st.selectbox(
            "1. Selecione o Ano de Auditoria", 
            options=[2024, 2025, 2026, 2027, 2028], 
            index=2,
            key="admin_selectbox_ano" 
        )
    with col_dim:
        dim_busca = st.selectbox(
            "2. Selecione a Dimensão para o Extrato", 
            options=["i-Gov TI", "i-Educ", "i-Saúde", "i-Plan", "i-Amb", "i-Cidade", "i-Fiscal"],
            key="admin_selectbox_dimensao"
        )

    df_raw = obter_banco_respostas_real(ano_busca, dim_busca)

    st.markdown("---")
    
    dimensao_normalizada = str(dim_busca).lower().replace(" ", "").replace("-", "")
    is_igov_ti = "igovti" in dimensao_normalizada

    if (df_raw is not None and not df_raw.empty) or is_igov_ti:
        if df_raw is None or df_raw.empty:
            df_raw = pd.DataFrame(columns=["id_quesito", "Descrição do Quesito", "Resposta / Situação", "Nota"])
            st.warning(f"⚠️ Banco de dados local para `{dim_busca}` está vazio ou ausente. Gerando extrato apenas com a estrutura da lista mestre de quesitos.")

        df_filtrado = df_raw.copy()
        
        mapeamento_colunas_linhas = {}
        for col in df_filtrado.columns:
            col_lower = str(col).lower().strip()
            if "nº" in col_lower or ("quesito" in col_lower and "desc" not in col_lower and "resp" not in col_lower):
                mapeamento_colunas_linhas[col] = "id_quesito"
            elif "desc" in col_lower:
                mapeamento_colunas_linhas[col] = "Descrição do Quesito"
            elif "resp" in col_lower or "situa" in col_lower:
                mapeamento_colunas_linhas[col] = "Resposta / Situação"
            elif "nota" in col_lower or "ponto" in col_lower or "score" in col_lower:
                mapeamento_colunas_linhas[col] = "Nota"
                
        if mapeamento_colunas_linhas:
            df_filtrado = df_filtrado.rename(columns=mapeamento_colunas_linhas)

        total_exibido = 53 if is_igov_ti else len(df_filtrado)
        st.info(f"✨ Foram encontrados/estruturados **{total_exibido}** quesitos com sucesso para `{dim_busca}`.")
        
        pdf_oficial = gerar_pdf_reportlab(ano_busca, dim_busca, df_filtrado)
        chave_botao = f"btn_final_pdf_{dim_busca.lower().replace(' ', '').replace('-', '')}_{ano_busca}"
        
        st.download_button(
            label=f"📥 Gerar e Baixar PDF Oficial — {dim_busca} ({ano_busca})",
            data=pdf_oficial,
            file_name=f"Extrato_IEGM_{dim_busca.replace(' ', '_')}_{ano_busca}.pdf",
            mime="application/pdf",
            key=chave_botao, 
            use_container_width=True
        )
    else:
        st.warning(f"⚠️ Nenhum dado localizado nos arquivos de banco de dados para `{dim_busca}` no ano `{ano_busca}`.")