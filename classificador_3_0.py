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
        # Pega as chaves dos Secrets do Streamlit
        self.api_key = st.secrets.get("OPENAI_API_KEY")
        self.webhook_url = st.secrets.get("SHAREPOINT_WEBHOOK")
        
        if not self.api_key:
            st.error("❌ OPENAI_API_KEY não configurada nos Secrets.")
            st.stop()
            
        self.client = OpenAI(api_key=self.api_key)
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.carregar_bases()

    def carregar_bases(self):
        with open(os.path.join(self.base_path, "base_temas_subtemas.json"), 'r', encoding='utf-8') as f:
            self.temas_subtemas = json.load(f)
        with open(os.path.join(self.base_path, "base_promotorias.json"), 'r', encoding='utf-8') as f:
            self.base_promotorias = json.load(f)
        
        # Mapa para busca rápida de municípios
        self.municipios_map = {}
        for nucleo, dados in self.base_promotorias.items():
            for m in dados["municipios"]:
                self.municipios_map[self.remover_acentos(m.upper())] = {
                    "promotoria": dados["promotoria"],
                    "oficial": m
                }

    def remover_acentos(self, texto):
        if not texto: return ""
        return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    def identificar_local(self, endereco):
        end_limpo = self.remover_acentos(endereco.upper())
        for m_busca, info in self.municipios_map.items():
            if m_busca in end_limpo:
                return info["oficial"], info["promotoria"]
        return "Não Identificado", "Não Identificada"

    def classificar_ia(self, denuncia):
        catalogo = json.dumps(self.temas_subtemas, ensure_ascii=False)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Você é um classificador do MPRJ. Use este catálogo: {catalogo}"},
                    {"role": "user", "content": f"Retorne apenas JSON com chaves: tema, subtema, empresa, resumo (máx 10 palavras). Texto: {denuncia}"}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"tema": "Outros", "subtema": "Geral", "empresa": "Não identificada", "resumo": f"Erro IA: {str(e)[:20]}"}

    def registrar_sharepoint(self, dados):
        if not self.webhook_url:
            return False
        try:
            # O nome das chaves aqui deve ser igual ao que você colou no Power Automate
            response = requests.post(self.webhook_url, json=dados, timeout=15)
            return response.status_code in [200, 202]
        except:
            return False
