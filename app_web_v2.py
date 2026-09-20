# -*- coding: utf-8 -*-
import os
import streamlit as st
from PIL import Image
from classificador_denuncias import ClassificadorDenuncias

# Configuração da página do Streamlit
st.set_page_config(page_title="SARO - MPRJ", layout="wide", page_icon="⚖️")

# --- ESTILO CSS CUSTOMIZADO ---
st.markdown("""
<style>
    .caixa-resultado {
        border: 1px solid #FD8412;
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
        margin-bottom: 20px;
    }
    .label-vermelho { color: #FD8412; font-weight: bold; }
    .titulo-custom { color: #FD8412; font-weight: bold; font-size: 1.5rem; }
    .badge-verde {
        background-color: #e8f5e9;
        color: #2e7d32;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        display: inline-block;
        margin-right: 10px;
        border: 1px solid #c8e6c9;
    }
    .resumo-box { 
        background-color: #f0f2f6; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 5px solid #FD8412; 
    }
    div.stButton > button:first-child { 
        background-color: #FD8412 !important; 
        color: white !important; 
        font-weight: bold; 
    }
</style>
""", unsafe_allow_html=True)

# Estado da sessão para armazenar o resultado temporariamente
if "resultado" not in st.session_state:
    st.session_state.resultado = None

# Inicialização da classe de classificação
try:
    classificador = ClassificadorDenuncias()
except Exception as e:
    st.error(f"Erro ao iniciar sistema: {e}")
    st.stop()

# Logo na barra lateral
st.sidebar.image("https://www.mprj.mp.br/mprj-theme/images/mprj/logo_mprj.png", width=180)

# --- CABEÇALHO DA APLICAÇÃO ---
base_path = os.path.dirname(os.path.abspath(__file__))
caminho_imagem = os.path.join(base_path, "IMAGEM CAO CONSUMIDOR.png")

col_img, col_titulo = st.columns([1, 5])

with col_img:
    if os.path.exists(caminho_imagem):
        img = Image.open(caminho_imagem)
        st.image(img, use_container_width=True)
    else:
        st.warning("Imagem não encontrada no diretório.")

with col_titulo:
    st.title("Sistema Automático de Registro de Ouvidorias (SARO) | CAO Consumidor")
    st.markdown("*Versão 3.0* | Registro e Gestão de Ouvidorias com auxílio de Inteligência Artificial")

st.divider()

# --- FORMULÁRIO DE REGISTRO ---
with st.form("form_reg", clear_on_submit=True):
    st.markdown('<p class="titulo-custom">📝 Novo Registro de Ouvidoria</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    num_com = col1.text_input("Nº de Comunicação")
    num_mprj = col2.text_input("Nº MPRJ")
    
    endereco = st.text_input("Endereço Completo")
    denuncia = st.text_area("Descrição da Ouvidoria", height=150)
    
    f1, f2 = st.columns(2)
    responsavel = f1.radio("Responsável:", ["Elias", "Marya Victoria", "Anna Paula" , "Eduarda" , "Ana Beatriz", "Sônia", "Priscila"], horizontal=True)
    vencedor = f2.radio("Consumidor vencedor?", ["Sim", "Não"], horizontal=True)
    
    if st.form_submit_button("🔍 Registrar Ouvidoria", use_container_width=True):
        if endereco and denuncia:
            with st.spinner("Processando classificação via IA..."):
                # Chamada direta sem verificação de envio externo
                res = classificador.processar_denuncia(
                    endereco, denuncia, num_com, num_mprj, vencedor, responsavel
                )
                st.session_state.resultado = res
                st.success("✅ Ouvidoria processada com sucesso!")
        else:
            st.error("Preencha Endereço e Descrição.")

# --- EXIBIÇÃO DO RESULTADO DA CLASSIFICAÇÃO ---
if st.session_state.resultado:
    res = st.session_state.resultado
    st.divider()
    st.markdown("### ✅ Resultado da Classificação Atual")
    
    # Caixa principal com números de registro, município e promotoria
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
    
    # Badges de Tema, Subtema e Empresa
    col_t1, col_t2, col_t3 = st.columns(3)
    col_t1.markdown(f'<div class="badge-verde">Tema: {res["tema"]}</div>', unsafe_allow_html=True)
    col_t2.markdown(f'<div class="badge-verde">Subtema: {res["subtema"]}</div>', unsafe_allow_html=True)
    col_t3.markdown(f'<div class="badge-verde">Empresa: {res["empresa"]}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**Resumo da IA (Máximo 10 palavras):**")
    st.markdown(f'<div class="resumo-box">{res["resumo"]}</div>', unsafe_allow_html=True)
    
    with st.expander("📄 Ver Descrição da Ouvidoria"):
        st.write(res['denuncia'])
    
    # Botão para limpar o estado e apagar o resultado da tela
    if st.button("Limpar Tela para Novo Registro"):
        st.session_state.resultado = None
        st.rerun()

st.divider()
st.caption("SARO v3.0 - Sistema Automático de Registro de Ouvidorias | Ministério Público do Estado do Rio de Janeiro")
