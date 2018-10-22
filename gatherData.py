# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 16:17:10 2018

@author: JulioCaye
"""

import pandas as pd
import sqlite3

selic_url = "https://www.bcb.gov.br/pec/copom/port/taxaselic.asp"
selic_raw = pd.read_html(selic_url, decimal = ",", thousands=".")[0]
selic_raw = selic_raw.drop([0, 1], axis = 0)
selic_raw.columns = ["n_reuniao", "data_reuniao", "vies_reuniao", "periodo", "meta_selic", "TBAN", "taxa_selic_acum", "taxa_selic_media"]


petr4_url = "https://www.infomoney.com.br/Pages/Download/Download.aspx?dtIni=21/10/2008&dtFinish=21/10/2018&Ativo=PETR4&Semana=null&Per=null&type=2&Stock=PETR4&StockType=1"
petr4_raw = pd.read_html(petr4_url, decimal = ",", thousands = ".", header = 0)[0]

conn = sqlite3.connect("desafio.db")
selic_raw.to_sql("selic", conn, if_exists = "replace")
petr4_raw.to_sql("petr4", conn, if_exists = "replace")