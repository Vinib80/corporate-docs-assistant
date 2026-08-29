import sqlite3

conexao = sqlite3.connect('database.db')

# Criando um cursor para executar comandos SQL
cursor = conexao.cursor()

conexao.close()