# -*- coding: utf-8 -*-
import streamlit as st
from classificador_3_0 import ClassificadorSARO3
from datetime import datetime

# 1. ÍCONE DO SITE E CONFIGURAÇÃO
st.set_page_config(
    page_title="SARO 3.0 - MPRJ", 
    layout="wide", 
    page_icon="CAO-CONSUMIDOR.ico"
)

# Estilo visual
st.markdown("""
<style>
    .caixa-resultado { border: 1px solid #960018; padding: 20px; border-radius: 10px; background-color: #ffffff; }
    .label-vermelho { color: #960018; font-weight: bold; }
    .badge-verde { background-color: #e8f5e9; color: #2e7d32; padding: 8px 15px; border-radius: 5px; font-weight: bold; border: 1px solid #c8e6c9; display: inline-block; margin-right: 5px; }
    .resumo-box { background-color: #f0f2f6; padding: 15px; border-radius: 8px; border-left: 5px solid #960018; }
</style>
""", unsafe_allow_html=True)

if "resultado" not in st.session_state: st.session_state.resultado = None

# 2. IMAGEM NA PARTE DE CIMA DO TÍTULO
st.image("CAO-CONSUMIDOR.ico", width=80)
st.title("⚖️ Sistema SARO 3.0 - MPRJ")
st.caption("Tecnologia OpenAI + Planilha Viva SharePoint")
st.divider()

classificador = ClassificadorSARO3()

# Formulário de Registro
with st.form("form_saro3", clear_on_submit=True):
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
                mun, prom = classificador.identificar_local(endereco)
                ia = classificador.classificar_ia(denuncia)
                
                dados_final = {
                    "num_com": num_com, "num_mprj": num_mprj, "promotoria": prom,
                    "municipio": mun, "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "denuncia": denuncia, "resumo": ia.get("resumo"), "tema": ia.get("tema"),
                    "subtema": ia.get("subtema"), "empresa": ia.get("empresa"),
                    "vencedor": vencedor, "responsavel": responsavel
                }
                
                sucesso = classificador.registrar_sharepoint(dados_final)
                st.session_state.resultado = dados_final
                
                if sucesso:
                    st.success("✅ Sucesso! Os dados já estão na planilha do SharePoint.")
                else:
                    st.warning("⚠️ Classificado, mas houve um problema ao enviar para o SharePoint. Verifique sua URL do Webhook.")

# 3. EXIBIÇÃO DO RESULTADO (Layout SARO 2.0)
if st.session_state.resultado:
    res = st.session_state.resultado
    st.divider()
    st.markdown("### ✅ Resultado da Classificação Atual")
    st.markdown(f"""
    <div class="caixa-resultado">
        <div style="display: flex; justify-content: space-between;">
            <p><span class="label-vermelho">Nº Comunicação:</span> {res['num_com']}</p>
            <p><span class="label-vermelho">Nº MPRJ:</span> {res['num_mprj']}</p>
        </div>
        <p>📍 <span class="label-vermelho">Município:</span> {res['municipio']}</p>
        <p>🏛️ <span class="label-vermelho">Promotoria Responsável:</span> {res['promotoria']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="badge-verde">Tema: {res["tema"]}</div> <div class="badge-verde">Subtema: {res["subtema"]}</div> <div class="badge-verde">Empresa: {res["empresa"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="resumo-box" style="margin-top:15px;"><b>Resumo:</b> {res["resumo"]}</div>', unsafe_allow_html=True)
