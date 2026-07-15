import streamlit as st
import pandas as pd
from datetime import datetime, date

def obter_cronograma_padrao():
    """
    Retorna a lista padrão com as 14 etapas do cronograma.
    As datas padrão já vêm configuradas para o ciclo de 2027.
    """
    return [
        {
            "Etapa": 1,
            "Descrição da Atividade": "Disponibilização do Questionário Principal no Portal de Sistemas do TCESP",
            "Data Limite": date(2026, 12, 19),
            "Responsáveis / Observações": "TCESP"
        },
        {
            "Etapa": 2,
            "Descrição da Atividade": "Envio de comunicado institucional informando a abertura do sistema",
            "Data Limite": date(2027, 1, 6),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M"
        },
        {
            "Etapa": 3,
            "Descrição da Atividade": "1º prazo de preenchimento do questionário via instrumento (Drive) e produção de documentos para anexação",
            "Data Limite": date(2027, 1, 31),
            "Responsáveis / Observações": "Pontos focais das Secretarias"
        },
        {
            "Etapa": 4,
            "Descrição da Atividade": "1ª revisão do preenchimento e tira-dúvidas com pontos focais que concluíram",
            "Data Limite": date(2027, 1, 31),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M: Pontos focais das Secretarias"
        },
        {
            "Etapa": 5,
            "Descrição da Atividade": "2º prazo de preenchimento do questionário via instrumento (Drive) e produção de documentos para anexação (areas pendentes)",
            "Data Limite": date(2027, 2, 20),
            "Responsáveis / Observações": "Pontos focais das secretarias"
        },
        {
            "Etapa": 6,
            "Descrição da Atividade": "Alimentação da Plataforma TCE/SP",
            "Data Limite": date(2027, 2, 23),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M"
        },
        {
            "Etapa": 7,
            "Descrição da Atividade": "2ª revisita e adequações junto aos pontos focais que já preencheram",
            "Data Limite": date(2027, 2, 23),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M: Pontos focais das Secretarias"
        },
        {
            "Etapa": 8,
            "Descrição da Atividade": "3º prazo de preenchimento do questionário via instrumento (Drive) e produção de documentos (parcial ou não realizado)",
            "Data Limite": date(2027, 3, 13),
            "Responsáveis / Observações": "Pontos focais das Secretarias"
        },
        {
            "Etapa": 9,
            "Descrição da Atividade": "Revisão final das informações – Secretaria de Habitação, Meio Ambiente, Clima e Energia (I-AMB)",
            "Data Limite": date(2027, 3, 16),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M / Secretarias / Pontos focais"
        },
        {
            "Etapa": 10,
            "Descrição da Atividade": "Revisão final – Finanças (I-GOV TI); Des. Econômico (I-Fiscal); Segurança Cidadã (I-Cidade)",
            "Data Limite": date(2027, 3, 17),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M / Secretarias / Pontos focais"
        },
        {
            "Etapa": 11,
            "Descrição da Atividade": "Revisão final – Secretaria de Educação (I-EDUC)",
            "Data Limite": date(2027, 3, 18),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M / Secretaria / Pontos focais"
        },
        {
            "Etapa": 12,
            "Descrição da Atividade": "Revisão final – Secretaria de Finanças e Gestão (I-PLAN)",
            "Data Limite": date(2027, 3, 19),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M / Secretarias / Pontos focais"
        },
        {
            "Etapa": 13,
            "Descrição da Atividade": "Revisão final – SAME (I-SAÚDE)",
            "Data Limite": date(2027, 3, 20),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M / Secretarias / Pontos focais"
        },
        {
            "Etapa": 14,
            "Descrição da Atividade": "Revisita final para validação, adequações e consolidação das informações para envio ao TCESP",
            "Data Limite": date(2027, 3, 26),
            "Responsáveis / Observações": "Diretoria de ODS e IEG-M / Secretarias"
        }
    ]

def mostrar_painel_prazos():
    """Função principal que renderiza a aba de Prazos e Alertas."""
    
    st.markdown("### 📅 Gestão Ativa de Prazos e Alertas - Ciclo 2027")
    st.markdown("Configure as datas do cronograma, inclua ou remova etapas e acompanhe em tempo real o status do processo.")

    # Inicialização do banco de prazos no State para manter edições durante a sessão
    if "cronograma_db" not in st.session_state:
        st.session_state.cronograma_db = obter_cronograma_padrao()

    hoje = date.today()
    
    # Exibição da data atual formatada
    st.info(f"📆 **Data Atual de Análise:** {hoje.strftime('%d/%m/%Y')}")

    # ABA CORRIGIDA AQUI: Adicionado 'aba_instrucoes' na declaração das abas
    aba_visualizacao, aba_edicao, aba_instrucoes = st.tabs([
        "📊 Painel de Status", 
        "✏️ Configurar Datas e Prazos",
        "📖 Instruções de Preenchimento"
    ])

    with aba_visualizacao:
        dados_calculados = []
        concluidas_ou_atrasadas = 0
        pendentes_futuras = 0
        nao_iniciadas = 0

        for item in st.session_state.cronograma_db:
            data_limite = item.get("Data Limite") or item.get("Data Limit")
            
            if data_limite is None:
                status = "⚪ Não Iniciado"
                dias_texto = "Aguardando definição de data"
                data_exibicao = "--/--/----"
                nao_iniciadas += 1
            else:
                data_exibicao = data_limite.strftime("%d/%m/%Y")
                diferenca = (data_limite - hoje).days
                
                if diferenca < 0:
                    status = "🔴 Prazo Excedido"
                    dias_texto = f"Atrasado há {abs(diferenca)} dias"
                    concluidas_ou_atrasadas += 1
                elif diferenca == 0:
                    status = "🟡 Vence Hoje!"
                    dias_texto = "Último dia!"
                    pendentes_futuras += 1
                else:
                    status = "🟢 Em andamento"
                    dias_texto = f"Restam {diferenca} dias"
                    pendentes_futuras += 1

            dados_calculados.append({
                "Etapa": item["Etapa"],
                "Atividade / Descrição": item["Descrição da Atividade"],
                "Data Limite": data_exibicao,
                "Tempo Restante": dias_texto,
                "Status": status,
                "Responsáveis": item["Responsáveis / Observações"]
            })

        df_visualizacao = pd.DataFrame(dados_calculados)

        # KPIs no topo
        col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
        with col_kpi1:
            st.metric(label="Aguardando Definição (Não Iniciado)", value=nao_iniciadas)
        with col_kpi2:
            st.metric(label="Em andamento / No Prazo", value=pendentes_futuras)
        with col_kpi3:
            st.metric(label="Prazos Excedidos", value=concluidas_ou_atrasadas)

        st.markdown("---")
        
        # Estilização visual para as linhas de Status
        def colorir_status(val):
            if "🔴" in val:
                return 'background-color: #FEE2E2; color: #991B1B; font-weight: bold;'
            elif "🟡" in val:
                return 'background-color: #FEF3C7; color: #92400E; font-weight: bold;'
            elif "⚪" in val:
                return 'background-color: #F1F5F9; color: #475569; font-style: italic;'
            return 'background-color: #D1FAE5; color: #065F46; font-weight: bold;'

        if not df_visualizacao.empty:
            df_styled = df_visualizacao.style.map(colorir_status, subset=['Status'])
            
            st.dataframe(
                df_styled, 
                use_container_width=True, 
                column_config={
                    "Etapa": st.column_config.NumberColumn(width="small"),
                    "Atividade / Descrição": st.column_config.TextColumn(width="large"),
                    "Data Limite": st.column_config.TextColumn(width="medium"),
                    "Tempo Restante": st.column_config.TextColumn(width="medium"),
                    "Status": st.column_config.TextColumn(width="medium")
                },
                hide_index=True
            )
        else:
            st.info("Nenhuma etapa cadastrada no momento. Vá na aba de configuração para adicionar etapas.")

    with aba_edicao:
        st.markdown("#### Ajustar Datas e Responsáveis por Etapa")
        st.write("Marque 'Definir data' para habilitar a escolha da data (DD/MM/AAAA) ou clique em 🗑️ para excluir a etapa.")

        # Reordenar números das etapas dinamicamente para não deixar furos na numeração após exclusões
        for idx, item in enumerate(st.session_state.cronograma_db):
            item["Etapa"] = idx + 1

        edicoes = []
        indice_para_excluir = None

        # Renderização dinâmica das linhas de edição
        for i, item in enumerate(st.session_state.cronograma_db):
            data_atual_item = item.get("Data Limite") or item.get("Data Limit")
            possui_data = data_atual_item is not None
            
            col_etapa, col_desc, col_possui, col_data, col_resp, col_excluir = st.columns([1, 4, 1.8, 2.2, 2.2, 0.8])
            
            with col_etapa:
                st.markdown(f"<br>**Etapa {item['Etapa']}**", unsafe_allow_html=True)
            with col_desc:
                nova_desc = st.text_input(
                    "Descrição", 
                    value=item["Descrição da Atividade"], 
                    key=f"desc_{i}",
                    label_visibility="collapsed"
                )
            with col_possui:
                marcado = st.checkbox(
                    "Definir data", 
                    value=possui_data, 
                    key=f"possui_data_{i}"
                )
            with col_data:
                data_inicial_picker = data_atual_item if data_atual_item else hoje
                nova_data = st.date_input(
                    "Data Limite", 
                    value=data_inicial_picker, 
                    format="DD/MM/YYYY",
                    disabled=not marcado,
                    key=f"data_{i}",
                    label_visibility="collapsed"
                )
            with col_resp:
                novo_resp = st.text_input(
                    "Responsáveis", 
                    value=item["Responsáveis / Observações"], 
                    key=f"resp_{i}",
                    label_visibility="collapsed"
                )
            with col_excluir:
                st.markdown("<br>", unsafe_allow_html=True)
                # Botão individual de remoção rápida
                if st.button("🗑️", key=f"btn_excluir_{i}", help="Excluir esta etapa"):
                    indice_para_excluir = i
            
            data_final_gravacao = nova_data if marcado else None
            
            edicoes.append({
                "Etapa": item["Etapa"],
                "Descrição da Atividade": nova_desc,
                "Data Limite": data_final_gravacao,
                "Responsáveis / Observações": novo_resp
            })
            st.markdown("<hr style='margin: 0.1rem 0px; border-top: 1px dashed #ccc;'>", unsafe_allow_html=True)

        # Processar exclusão imediata caso clicada
        if indice_para_excluir is not None:
            st.session_state.cronograma_db.pop(indice_para_excluir)
            st.toast("Etapa excluída com sucesso!", icon="🗑️")
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # BOTOES DE CONTROLE DO CRONOGRAMA EXISTENTE
        col_btn1, col_btn2 = st.columns([2, 8])
        with col_btn1:
            if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                st.session_state.cronograma_db = edicoes
                st.success("✔️ Alterações salvas com sucesso!")
                st.rerun()
        with col_btn2:
            if st.button("🔄 Restaurar Prazos Originais (Padrão)"):
                st.session_state.cronograma_db = obter_cronograma_padrao()
                st.info("🔄 Cronograma restaurado para as 14 etapas de 2027.")
                st.rerun()

        st.markdown("---")
        
        # SEÇÃO PARA INCLUSÃO DE UMA NOVA ETAPA
        with st.expander("➕ Adicionar Nova Etapa ao Cronograma", expanded=False):
            st.markdown("Preencha as informações abaixo para incluir uma nova atividade no final do seu cronograma.")
            
            col_add_desc, col_add_possui, col_add_data, col_add_resp = st.columns([4, 2, 3, 3])
            
            with col_add_desc:
                novo_item_desc = st.text_input("Descrição da Nova Atividade", key="add_desc_campo")
            with col_add_possui:
                novo_item_possui = st.checkbox("Definir Data Limite", value=False, key="add_possui_campo")
            with col_add_data:
                novo_item_data = st.date_input("Data Limite", value=hoje, format="DD/MM/YYYY", disabled=not novo_item_possui, key="add_data_campo")
            with col_add_resp:
                novo_item_resp = st.text_input("Responsáveis / Observações", key="add_resp_campo")
                
            if st.button("➕ Confirmar Inclusão de Etapa", use_container_width=True):
                if not novo_item_desc:
                    st.warning("⚠️ Forneça ao menos uma breve descrição para a nova atividade antes de adicionar.")
                else:
                    data_add_salvamento = novo_item_data if novo_item_possui else None
                    proxima_etapa_num = len(st.session_state.cronograma_db) + 1
                    
                    nova_etapa_dict = {
                        "Etapa": proxima_etapa_num,
                        "Descrição da Atividade": novo_item_desc,
                        "Data Limite": data_add_salvamento,
                        "Responsáveis / Observações": novo_item_resp
                    }
                    
                    st.session_state.cronograma_db.append(nova_etapa_dict)
                    st.success(f"✔️ Etapa {proxima_etapa_num} incluída com sucesso!")
                    st.rerun()

    # NOVA ABA: INSTRUÇÕES DE PREENCHIMENTO
    with aba_instrucoes:
        st.markdown("### 📖 Instruções de Preenchimento — IEG-M")
        st.markdown("Use o campo abaixo para visualizar e, se necessário, editar as instruções oficiais de preenchimento para o município.")
        
        texto_instrucoes_default = (
            "INSTRUÇÕES DE PREENCHIMENTO – IEG-M\n"
            "Índice de Efetividade da Gestão Municipal\n\n"
            "O presente instrumento tem por finalidade orientar o correto preenchimento dos questionários que compõem o Índice de Efetividade da Gestão Municipal (IEG-M), sistema de avaliação desenvolvido pelo Tribunal de Contas do Estado de São Paulo para aferir a qualidade e a efetividade das políticas públicas municipais.\n\n"
            "O preenchimento dos questionários será realizado por meio do Sistema IEG-M Francisco Morato, ferramenta desenvolvida para centralizar, organizar, acompanhar e monitorar as informações necessárias à composição dos índices avaliados pelo Tribunal de Contas. O sistema permite o registro das respostas, o armazenamento de documentos comprobatórios, a elaboração de planos de ação e o acompanhamento da evolução dos resultados obtidos pelo Município.\n\n"
            "Recomendações para o Preenchimento:\n"
            "1. As respostas devem refletir fielmente a situação existente no exercício avaliado, observando-se os critérios estabelecidos pelo Tribunal de Contas do Estado de São Paulo.\n"
            "2. Toda resposta positiva deverá possuir documentação comprobatória válida e atualizada, passível de apresentação em eventual fiscalização ou auditoria.\n"
            "3. Antes do preenchimento, recomenda-se a consulta às legislações, normas internas, portarias, decretos, contratos, relatórios e demais documentos relacionados ao quesito analisado.\n"
            "4. Os responsáveis pelo preenchimento devem verificar a consistência das informações prestadas, evitando divergências entre os dados informados e a documentação existente.\n"
            "5. Sempre que possível, as respostas deverão ser acompanhadas dos respectivos arquivos comprobatórios no Sistema IEG-M Francisco Morato, facilitando a validação e o controle das informações.\n"
            "6. Nos casos em que o Município não atenda integralmente determinado requisito, recomenda-se o registro das medidas adotadas ou planejadas para sua regularização, permitindo a elaboração de planos de ação e o monitoramento das melhorias necessárias.\n"
            "7. Os questionários devem ser preenchidos de forma integrada entre as Secretarias e órgãos municipais responsáveis por cada área temática, garantindo maior precisão e confiabilidade das informações.\n"
            "8. O preenchimento deverá observar os prazos estabelecidos pela Administração Municipal e pelo Tribunal de Contas, evitando inconsistências ou atrasos no envio das informações.\n"
            "9. Em caso de dúvidas quanto à interpretação de determinado quesito, recomenda-se a consulta ao Manual do IEG-M, às orientações do Tribunal de Contas e à equipe responsável pela coordenação do Sistema IEG-M Francisco Morato.\n"
            "10. A prestação de informações incorretas, incompletas ou sem respaldo documental poderá comprometer a avaliação do Município, impactando diretamente os resultados dos índices e eventuais apontamentos dos órgãos de controle.\n"
            "11. Todos os documentos comprobatórios deverão ser disponibilizados por meio de link de acesso direto, anexado no respectivo quesito do Sistema IEG-M Francisco Morato. Os links informados deverão permanecer ativos e com acesso livre para consulta, dispensando solicitações de permissão ou autorização de acesso, uma vez que o Tribunal de Contas não realizará pedidos de liberação para visualização dos documentos. Ademais, todos os documentos encaminhados deverão estar devidamente formalizados e conter as assinaturas das autoridades, responsáveis ou servidores competentes, conforme a natureza do documento e as exigências legais aplicáveis."
        )
        
        instrucoes_editadas = st.text_area(
            label="Edição das Orientações e Recomendações Técnicas:",
            value=texto_instrucoes_default,
            height=500,
            help="Você pode alterar ou atualizar este texto. As mudanças serão refletidas enquanto a sessão estiver ativa."
        )
        
        if st.button("💾 Salvar Alterações das Instruções"):
            st.success("As instruções de preenchimento foram atualizadas com sucesso para esta sessão!")


# CHAMANDO A FUNÇÃO CORRETA PARA INICIALIZAR:
if __name__ == "__main__":
    mostrar_painel_prazos()