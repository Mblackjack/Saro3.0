# -*- coding: utf-8 -*-
"""
SARO v3.0 - Sistema Automático de Registro de Ouvidorias
Interface Web com Integração OpenAI + SharePoint
"""

import streamlit as st
from datetime import datetime
from classificador_3_0 import ClassificadorSARO3
from sharepoint_sync import SharePointSync

# Configuração
st.set_page_config(page_title="SARO 3.0 - MPRJ", layout="wide")

# Inicialização
if "resultado" not in st.session_state: st.session_state.resultado = None

st.title("⚖️ SARO 3.0 - CAO Consumidor")
st.markdown("### Integração OpenAI + Planilha Viva SharePoint")
st.divider()

# Sidebar para Status de Conexão
with st.sidebar:
    st.header("🔌 Status de Conexão")
    
    # Check OpenAI
    if st.secrets.get("OPENAI_API_KEY"):
        st.success("✅ OpenAI Conectada")
    else:
        st.error("❌ OpenAI Desconectada")
        
    # Check SharePoint
    if st.secrets.get("SHAREPOINT_USER") and st.secrets.get("SHAREPOINT_PASSWORD"):
        st.success("✅ SharePoint Configurado")
    else:
        st.warning("⚠️ SharePoint em Modo Manual")
        st.info("Configure as credenciais nos Secrets para atualização automática.")

# Formulário
with st.form("form_saro3"):
    col1, col2 = st.columns(2)
    with col1: num_com = st.text_input("Nº de Comunicação")
    with col2: num_mprj = st.text_input("Nº MPRJ")
    
    endereco = st.text_input("Endereço")
    denuncia = st.text_area("Descrição da Denúncia", height=200)
    
    col1, col2 = st.columns(2)
    with col1: responsavel = st.selectbox("Responsável", ["Elias", "Matheus", "Ana Beatriz", "Sônia", "Priscila"])
    with col2: vencedor = st.radio("Consumidor Vencedor?", ["Sim", "Não"], horizontal=True)
    
    submit = st.form_submit_button("🚀 Processar e Enviar para o SharePoint", use_container_width=True, type="primary")

if submit:
    if not endereco or not denuncia:
        st.error("❌ Preencha os campos obrigatórios!")
    else:
        with st.spinner("Classificando com OpenAI e sincronizando com SharePoint..."):
            # 1. Classificar
            st.session_state.data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            classificador = ClassificadorSARO3()
            resultado = classificador.processar_completo(endereco, denuncia, num_com, num_mprj)
            resultado["Responsável"] = responsavel
            resultado["Consumidor Vencedor"] = vencedor
            
            # 2. Sincronizar SharePoint
            sync = SharePointSync()
            sucesso_sp = sync.adicionar_linha(resultado)
            
            if sucesso_sp:
                st.success("✅ Dados registrados instantaneamente na planilha do SharePoint!")
            else:
                st.warning("⚠️ Dados processados, mas não foi possível atualizar o SharePoint automaticamente.")
            
            st.session_state.resultado = resultado

# Exibição do Resultado
if st.session_state.resultado:
    res = st.session_state.resultado
    st.divider()
    st.markdown("### 📋 Último Registro Processado")
    
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Tema", res["Tema"])
    with col2: st.metric("Subtema", res["Subtema"])
    with col3: st.metric("Empresa", res["Empresa"])
    
    st.info(f"**Resumo:** {res['Resumo']}")
    
    with st.expander("Ver Detalhes do Encaminhamento"):
        st.write(f"**Promotoria:** {res['Promotoria']}")
        st.write(f"**Município:** {res['Município']}")
        st.write(f"**Data do Registro:** {res['Data']}")

st.divider()
st.caption("SARO v3.0 | Desenvolvido para o MPRJ - CAO Consumidor")
