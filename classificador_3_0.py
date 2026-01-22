# -*- coding: utf-8 -*-
import json
import os
import requests
import streamlit as st
from openai import OpenAI

class ClassificadorSARO3:
    def __init__(self):
        # Tenta pegar as chaves, se não existir, define como None para não travar o início
        self.api_key = st.secrets.get("OPENAI_API_KEY")
        self.webhook_url = st.secrets.get("SHAREPOINT_WEBHOOK")
        
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            st.warning("⚠️ OPENAI_API_KEY não configurada nos Secrets.")

    def registrar_sharepoint(self, dados):
        if not self.webhook_url:
            st.error("❌ Erro: URL do Webhook do SharePoint não configurada.")
            return False
        
        try:
            # Envia os dados para o Power Automate
            response = requests.post(self.webhook_url, json=dados, timeout=15)
            if response.status_code in [200, 202]:
                return True
            else:
                st.error(f"❌ Erro no Power Automate: Status {response.status_code}")
                return False
        except Exception as e:
            st.error(f"❌ Falha de conexão com SharePoint: {e}")
            return False

    # ... (restante das funções de carregar bases permanecem iguais)
