# -*- coding: utf-8 -*-
import json
import os
import unicodedata
import requests
import streamlit as st
from openai import OpenAI
from datetime import datetime

class ClassificadorSARO3:
    def __init__(self):
        # 1. Configurações via Secrets
        self.api_key = st.secrets.get("OPENAI_API_KEY")
        self.webhook_url = st.secrets.get("SHAREPOINT_WEBHOOK")
        
        if not self.api_key:
            st.error("❌ Erro: OPENAI_API_KEY não configurada no Streamlit.")
            st.stop()
            
        self.client = OpenAI(api_key=self.api_key)
        
        # 2. Caminhos de ficheiros (Correção para FileNotFoundError)
        # Pega o diretório onde este ficheiro .py está localizado
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.carregar_bases()

    def carregar_bases(self):
        """Carrega as bases JSON de forma robusta"""
        try:
            # Caminhos construídos de forma segura
            caminho_temas = os.path.join(self.base_path, "base_temas_subtemas.json")
            caminho_promos = os.path.join(self.base_path, "base_promotorias.json")
            
            with open(caminho_temas, 'r', encoding='utf-8') as f:
                self.temas_subtemas = json.load(f)
            with open(caminho_promos, 'r', encoding='utf-8') as f:
                self.base_promotorias = json.load(f)
                
            # Mapeamento para busca de municípios
            self.municipios_map = {}
            for nucleo, dados in self.base_promotorias.items():
                for m in dados["municipios"]:
                    nome_limpo = self.remover_acentos(m.upper())
                    self.municipios_map[nome_limpo] = {
                        "promotoria": dados["promotoria"],
                        "oficial": m
                    }
        except Exception as e:
            st.error(f"❌ Erro ao carregar ficheiros de base: {e}")
            st.stop()

    def remover_acentos(self, texto):
        if not texto: return ""
        return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    def identificar_local(self, endereco):
        """Busca o município no texto do endereço"""
        end_limpo = self.remover_
