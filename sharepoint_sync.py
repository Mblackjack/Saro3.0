# -*- coding: utf-8 -*-
"""
SARO v3.0 - Sincronização SharePoint
Módulo para atualização instantânea da planilha Tabela_SARO.xlsx.
"""

import os
import streamlit as st
import pandas as pd
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from io import BytesIO

class SharePointSync:
    def __init__(self):
        self.site_url = "https://mprj.sharepoint.com/sites/cao.consumidor.equipe"
        self.file_url = "/sites/cao.consumidor.equipe/Shared Documents/General/Tabela_SARO.xlsx"
        
        # Credenciais via Secrets
        self.username = st.secrets.get("SHAREPOINT_USER")
        self.password = st.secrets.get("SHAREPOINT_PASSWORD")
        
    def conectar(self):
        if not self.username or not self.password:
            return None
        try:
            user_credentials = UserCredential(self.username, self.password)
            ctx = ClientContext(self.site_url).with_credentials(user_credentials)
            return ctx
        except Exception as e:
            st.error(f"❌ Erro de conexão SharePoint: {e}")
            return None

    def adicionar_linha(self, novos_dados: dict):
        """Lê a planilha atual, adiciona a linha e salva de volta no SharePoint"""
        ctx = self.conectar()
        if not ctx:
            st.warning("⚠️ SharePoint não conectado. Salvando apenas localmente.")
            return False

        try:
            # 1. Baixar arquivo atual
            response = ctx.web.get_file_by_server_relative_url(self.file_url).download().execute_query()
            file_content = BytesIO(response.value)
            
            # 2. Ler com Pandas
            df = pd.read_excel(file_content)
            
            # 3. Adicionar novos dados
            new_row = pd.DataFrame([novos_dados])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # 4. Salvar em memória
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            
            # 5. Upload de volta para o SharePoint
            ctx.web.get_folder_by_server_relative_url(os.path.dirname(self.file_url)).upload_file(
                os.path.basename(self.file_url), output.getvalue()
            ).execute_query()
            
            return True
        except Exception as e:
            st.error(f"❌ Erro ao atualizar SharePoint: {e}")
            return False
