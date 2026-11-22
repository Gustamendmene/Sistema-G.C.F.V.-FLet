"""Conexão com o MySQL (usuário, senha e banco vêm do arquivo .env)."""
import os
from contextlib import contextmanager

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def conectar():
    """Abre uma conexão com o MySQL usando as variáveis do arquivo .env.

    Nenhuma senha fica escrita no código (veja o modelo em .env.example).
    """
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "mercado"),
        connection_timeout=5,  # evita o app travar se o MySQL estiver desligado
    )


@contextmanager
def transacao(dicionario=False):
    """Abre conexão + cursor; confirma no fim, desfaz se der erro e fecha tudo.

        with transacao() as cur:
            cur.execute("SELECT ...")
            return cur.fetchall()

    Com dicionario=True cada linha vem como dict (acesso pelo nome da coluna).
    """
    con = conectar()
    try:
        cur = con.cursor(dictionary=dicionario)
        try:
            yield cur
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            cur.close()
    finally:
        con.close()
