# -*- coding: utf-8 -*-
import streamlit as st
from classificador_3_0 import ClassificadorSARO3
from datetime import datetime

# Configuração com o ícone
st.set_page_config(page_title="SARO 3.0 - MPRJ", layout="wide", page_icon="CAO-CONSUMIDOR.ico")

# CSS para manter o padrão visual
st.markdown("""
<style>
    .caixa-resultado { border: 1px solid #960018; padding: 20px; border-radius: 10px; background-color: #ffffff; }
    .label-vermelho { color: #960018; font-weight: bold; }
    .badge-verde { background-color: #e8f5e9; color: #2e7d32; padding: 8px 15px; border-radius: 5px; font-weight: bold; border: 1px solid #c8e6c9; display: inline-block; margin-right: 5px; }
    .resumo-box { background-color: #f0f2f6; padding: 15px; border-radius: 8px; border-left: 5px solid #960018; }
</style>
""", unsafe_allow_html=True)

if "resultado" not in st.session_state: st.session_state.resultado = None

st.image("CAO-CONSUMIDOR.ico", width=80)
st.title("⚖️ Sistema SARO 3.0 - MPRJ")
st.divider()

classificador = ClassificadorSARO3()

with st.form("form_saro3"):
    st.markdown("### 📝 Novo Registro de Ouvidoria")
    col1, col2 = st.columns(2)
    num_com = col1.text_input("Nº de Comunicação")
    num_mprj = col2.text_input("Nº MPRJ")
    endereco = st.text_input("Endereço Completo")
    denuncia = st.text_area("Descrição da Ouvidoria", height=150)
    
    f1, f2 = st.columns(2)
    responsavel = f1.radio("Responsável:", ["Elias", "Matheus", "Ana Beatriz", "Sônia", "Priscila"], horizontal=True)
    vencedor = f2.radio("Consumidor vencedor?", ["Sim", "Não"], horizontal=True)
    
    if st.form_submit_button("REGISTRAR NO SHAREPOINT", use_container_width=True):
        if endereco and denuncia:
            with st.spinner("Classificando e enviando para o SharePoint..."):
                # Processa a classificação (OpenAI + Local)
                resultado = classificador.processar_completo(endereco, denuncia, num_com, num_mprj)
                resultado["vencedor"] = vencedor
                resultado["responsavel"] = responsavel
                
                # ENVIO PARA O SHAREPOINT VIA WEBHOOK
                sucesso = classificador.enviar_para_webhook(resultado)
                
                st.session_state.resultado = resultado
                if sucesso:
                    st.success("✅ Registro enviado para a Planilha do SharePoint!")
                else:
                    st.error("❌ Erro ao enviar para o SharePoint. Verifique o link do Power Automate.")

# Exibição do Resultado (Sem carregar do disco)
if st.session_state.resultado:
    res = st.session_state.resultado
    st.divider()
    st.markdown("### ✅ Registro Processado")
    st.markdown(f"""
    <div class="caixa-resultado">
        <p><span class="label-vermelho">Promotoria:</span> {res.get('promotoria', 'N/A')}</p>
        <p><span class="label-vermelho">Município:</span> {res.
