# -*- coding: utf-8 -*-
"""
SARO v3.0 - Motor de Classificação OpenAI
Otimizado para GPT-4o Mini e integração com SharePoint.
"""

import json
import os
import unicodedata
import streamlit as st
from typing import Dict, Optional
from openai import OpenAI

class ClassificadorSARO3:
    def __init__(self):
        self.api_key = st.secrets.get("OPENAI_API_KEY")
        if not self.api_key:
            st.error("❌ OPENAI_API_KEY não configurada nos Secrets.")
            st.stop()
            
        self.client = OpenAI(api_key=self.api_key)
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.carregar_bases()

    def carregar_bases(self):
        try:
            with open(f"{self.base_path}/base_temas_subtemas.json", 'r', encoding='utf-8') as f:
                self.temas_subtemas = json.load(f)
            with open(f"{self.base_path}/base_promotorias.json", 'r', encoding='utf-8') as f:
                self.base_promotorias = json.load(f)
        except Exception as e:
            st.error(f"❌ Erro ao carregar bases JSON: {e}")
            st.stop()
            
        self.municipio_para_promotoria = {}
        for nucleo, dados in self.base_promotorias.items():
            for municipio in dados["municipios"]:
                self.municipio_para_promotoria[municipio.upper()] = {
                    "promotoria": dados["promotoria"],
                    "municipio_oficial": municipio
                }

    def remover_acentos(self, texto: str) -> str:
        if not texto: return ""
        return "".join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

    def extrair_municipio(self, endereco: str) -> Optional[str]:
        if not endereco: return None
        end_upper = self.remover_acentos(endereco.upper())
        for m_chave in self.municipio_para_promotoria.keys():
            if self.remover_acentos(m_chave) in end_upper:
                return self.municipio_para_promotoria[m_chave]["municipio_oficial"]
        return None

    def classificar(self, denuncia: str) -> Dict:
        catalogo = "\n".join([f"- {t}: {', '.join(s)}" for t, s in self.temas_subtemas.items()])
        
        prompt = f"""Analise a denúncia e classifique seguindo o catálogo oficial.
        CATÁLOGO:
        {catalogo}
        
        Retorne APENAS um JSON:
        {{"tema": "...", "subtema": "...", "empresa": "...", "resumo": "uma frase curta"}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um classificador rigoroso do MPRJ. Responda apenas com JSON puro."},
                    {"role": "user", "content": prompt + f"\n\nDenúncia: {denuncia}"}
                ],
                temperature=0,
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.warning(f"⚠️ Erro na IA: {e}")
            return {"tema": "Serviços", "subtema": "Outros", "empresa": "Não identificada", "resumo": "Erro no processamento."}

    def processar_completo(self, endereco: str, denuncia: str, num_comunicacao: str, num_mprj: str) -> Dict:
        municipio = self.extrair_municipio(endereco)
        promotoria = self.municipio_para_promotoria.get(municipio.upper() if municipio else "", {}).get("promotoria", "Promotoria não identificada")
        
        dados_ia = self.classificar(denuncia)
        
        return {
            "Nº Comunicação": num_comunicacao,
            "Nº MPRJ": num_mprj,
            "Data": st.session_state.get("data_atual", ""),
            "Endereço": endereco,
            "Município": municipio or "Não identificado",
            "Promotoria": promotoria,
            "Tema": dados_ia.get("tema"),
            "Subtema": dados_ia.get("subtema"),
            "Empresa": dados_ia.get("empresa"),
            "Resumo": dados_ia.get("resumo"),
            "Denúncia Original": denuncia
        }
