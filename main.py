from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

class Tarefa(BaseModel):
    descricao: str
    concluida: bool
class Status(BaseModel):
    concluida: bool

def conectar():
    return sqlite3.connect('Banco.db')

def criar_tabela():  #Essa função será responsável por criar uma tabela no banco de dados.
    conexão = conectar()    #Essa função normalmente faz a conexão com o banco SQLite
    cursor = conexão.cursor()  #O cursor é quem executa comandos SQL no banco
    # Aqui você está mandando um comando SQL para o banco.
    cursor.execute(""" CREATE TABLE IF NOT EXISTS Tarefas( 
            id integer primary key autoincrement,
            descricao text,
            concluida boolean
        )""")
    #cada tarefa terá um ID único automático. A descrição é um texto e o campo concluída é um booleano para indicar se a tarefa foi concluída ou não.

    conexão.commit()  #Sem isso, a tabela pode não ser criada de verdade.
    conexão.close() #Fecha a conexão com o banco.

#Aqui você está chamando a função.
criar_tabela()

# LISTAR TAREFAS NA API

@app.get("/tarefas")
def listar(): #Aqui você está chamando a função.
    conexão = conectar()  #Essa função normalmente faz a conexão com o banco SQLite
    cursor = conexão.cursor()  #O cursor é quem executa comandos SQL no banco
    cursor.execute("SELECT * FROM Tarefas") #Me dá tudo que tem dentro da tabela Tarefas
    dados = cursor.fetchall() #Pega os resultados da consulta e armazena na variável dados.

    tarefas = []
    for tarefa in dados:  #Aqui você está iterando sobre os resultados da consulta e criando uma lista de dicionários, onde cada dicionário representa uma tarefa.
        tarefas.append({
            "id": tarefa[0],
            "descricao": tarefa[1],
            "concluida": bool(tarefa[2]) # converte 0/1 para true/false
        })

    conexão.close()  #Fecha a conexão com o banco.
    
    if not dados:  #Se não tiver dados, ou seja, se a lista estiver vazia, você levanta uma exceção HTTP 404.
        raise HTTPException(status_code=404, detail="Nenhuma tarefa encontrada.")
    else:   
        return {"tarefas": tarefas} #Retorna os dados em formato de dicionário.

@app.post("/adicionar")
def adicionar(tarefa: Tarefa): #Aqui você está chamando a função.
        
    if not tarefa.descricao:  #Se o ID ou a descrição não forem fornecidos, levanta uma exceção HTTP 400.
        raise HTTPException(status_code=400, detail="ID e descrição são obrigatórios.")
    
    
    conexão = conectar()
    cursor = conexão.cursor()
    cursor.execute("INSERT INTO Tarefas ( descricao, concluida) VALUES ( ?, ?)", (tarefa.descricao, tarefa.concluida))

    conexão.commit()
    conexão.close()
    
    return {"message": "Tarefa adicionada com sucesso."}

@app.put("/atualizar/{id}")
def atualizar(id: int, status: Status): #Aqui você está chamando a função.
    conexão = conectar() #Essa função normalmente faz a conexão com o banco SQLite
    cursor = conexão.cursor() #O cursor é quem executa comandos SQL no banco
    cursor.execute("UPDATE Tarefas SET concluida = ? where id = ?", (status.concluida, id)) #Aqui você está executando um comando SQL para atualizar o campo concluída da tarefa com o ID fornecido. O valor de concluída é passado como um parâmetro para evitar problemas de injeção de SQL.

    conexão.commit()
    if cursor.rowcount == 0:  #Se o número de linhas afetadas for zero, significa que a tarefa com o ID fornecido não foi encontrada, e você levanta uma exceção HTTP 404.
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    
    conexão.close()

    return {"message": "Tarefa atualizada com sucesso."}  

@app.delete("/deletar/{id}")
def deletar_tarefa(id:int):
    conexão = conectar() #Essa função normalmente faz a conexão com o banco SQLite
    cursor = conexão.cursor() #O cursor é quem executa comandos SQL no banco
    cursor.execute("DELETE FROM Tarefas WHERE id= ?", (id,)) #Aqui você está executando um comando SQL para deletar a tarefa com o ID fornecido. O ID é passado como um parâmetro para evitar problemas de injeção de SQL.
    if not cursor.rowcount:  #Se o número de linhas afetadas for zero, significa que a tarefa com o ID fornecido não foi encontrada, e você levanta uma exceção HTTP 404.
        conexão.close()  #Fecha a conexão com o banco.
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    
    conexão.commit()
    conexão.close()

    return {"message": "Tarefa deletada com sucesso."}