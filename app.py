from flask import Flask, render_template, url_for, request, redirect, session

app = Flask(__name__)
app.secret_key = 'chave'

import psycopg2
db_config = { #configurações
    'dbname': 'mydatabase',
    'user': 'postgres',
    'password': '123',
    'host': 'localhost',
    'port': 5432
}

# Testando a conexão
try:
    conn = psycopg2.connect(**db_config)
    print("Conexão estabelecida com sucesso!")
    conn.close()
except Exception as e:
    print("Erro ao conectar ao banco de dados:", e)

@app.route('/', methods=['POST', 'GET']) #define a rota
def login():
   
  if request.method == 'POST':
    usuario = request.form['login-usuario']
    senha = request.form['login-senha']

    try:
       with psycopg2.connect(**db_config) as conn:
        with conn.cursor() as cursor:
          select_query = """
          SELECT * FROM alunos WHERE matricula = %s;
          """
          valores = (usuario,)
          cursor.execute(select_query, valores)

          resultados = cursor.fetchone()
          print(resultados)

          if resultados:
            if senha == resultados[2]:
              session['usuario'] = usuario 
              print(session)
              return redirect(url_for('index'))
            else:
               print('Senha incorreta')
               return redirect('/')
          else:
             print('Usuário não encontrado')
             return redirect('/')
          
    except Exception as e:
        return render_template('login.html')

  else:
    return render_template('login.html')


@app.route('/index')
def index():
   return render_template('index.html')


# MOSTRAR NA TABELA DE DOAR

@app.route('/doar', methods=['POST', 'GET'])
def doar():
   usuario = session.get('usuario')
   
   try:
      with psycopg2.connect(**db_config) as conn:
         with conn.cursor() as cursor:
            select_query = """
            SELECT * FROM refeicoes WHERE matricula = %s AND status = 'deferido';
            """
            valores = (usuario,)
            cursor.execute(select_query, valores)

            resultados = cursor.fetchall()
            # exibe as refeições deferidas na tela

# --------------------------------------------------------------

            idRef = request.form.get('idRef')
            if idRef:
                verID = """
                SELECT * FROM refeicoes WHERE refeicao_id = %s;
                """
                pesquisar = (idRef,)
                cursor.execute(verID, pesquisar)

                resultado = cursor.fetchall()
                print(f'Aqui ó {resultado}')
                # recebe o id do botão(id da refeição) e exibe a tupla correspondente
                # basicamente, a refeição/ tupla que vai ser doada

                def deletar(idRef):
                    deletar = """DELETE FROM refeicoes WHERE refeicao_id = %s"""
                    cursor.execute(deletar, (idRef,))
                    rows_affected = cursor.rowcount
                    print(f"Linhas afetadas: {rows_affected}")
                    print('linha deletada')
                    #deleta a linha que contem o idRef (id referente a tupla a qual o usuário quer doar)


# ----------------------------DOAÇÕES EMERGENCIAIS----------------------------

                cursor.execute(""" SELECT * FROM refeicoes WHERE status = 'emergencial' ORDER BY refeicao_id ASC LIMIT 1 """)
                doacao_emergencial = cursor.fetchone()
                print(doacao_emergencial)
                # busca a tupla que contenha o menor id e o status for emergencial

                if doacao_emergencial:
                   refeicao_id_emergencial = doacao_emergencial[0]
                #pega o primeiro valor da tupla (o id)

                   update = """UPDATE refeicoes SET status = 'deferido' WHERE refeicao_id = %s"""
                   cursor.execute(update, (refeicao_id_emergencial,))

                   rows_affected = cursor.rowcount
                   print(f"Linhas afetadas: {rows_affected}")
                   #verifica se há pedidos emergenciais e atualiza a tupla para deferido

                   deletar(idRef)
                   return redirect(url_for("doar"))
                   
                else:
                   print('Não há refeições emergenciais!')
                     

                    # ATENÇÃO: 
                    # Funções deletar estão funcionando bem, atualizar e pesquisa tbm.

                    # PROBLEMAS ATÉ AGORA: 
                    # Possibilidade de reenviar formulário atualizando a página manualmente, faz com que possa doar mais de uma refeição. O que causaria problemas por deferir também mais de uma refeição. Gerando erro por ter mais refeições deferidas do que as refeições reais disponiveis;

                    # Outro problema é com questão ao CHECK, não está possibilitando que refeições emergenciais do tipo almoço, agendadas para o mesmo dia sejam deferidas. Existe a condição de que não pode haver almoço para o mesmo dia. Porém isso deveria ser possível através do status emergencial. FAVOR REVISAR O BANCO!


            return render_template('doar.html', resultados=resultados)
         
         # Resolver questão da tabela ficar em branco quando não há refeições previstas no banco para aquele aluno

   except Exception as e:
      print("Erro ao buscar dados:", e)
      return render_template('doar.html', resultados=[])
   

@app.route("/solicitar")
def solicitar_page():
    
    usuario = session.get("usuario")

    #exibe a tabela refeicoes_solicitadas do usuário
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT refeicao_id, matricula, tipo, motivo, para, status 
            FROM refeicoes
            WHERE matricula = %s
            ORDER BY refeicao_id DESC;
        """, (usuario,))
        
        refeicoes = cursor.fetchall()
        
    except Exception:
        print("erro ao exibir refeições")
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template("solicitar.html", refeicoes=refeicoes)  # Página inicial
    #-----------------------------------------------


# Insere dados na tabela refeicoes_solicitadas através do formulário
@app.route("/adicionar_ref", methods=["POST"])
def adicionar_refeicao():
    global status
    try:
        # Obtém os valores do formulário de solicitar refeicoes
        tipo = request.form.get("tipo_refeicao")
        motivo = request.form.get("escolha_motivo_solicitacao")
        para = request.form.get("dia_solicitacao")

        usuario = session.get("usuario") #id do usuário logado (linkado a session)

            
        # Conectar ao banco de dados
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("Conexão estabelecida com sucesso.")
        
        #verifica de qual formulário o valor está sendo enviado
        origem = request.form.get("origem")
        if origem == 'form1' and usuario == '2':
            status = 'indeferido'

        elif origem == 'form1' and usuario == '3':
            status = 'deferido'
            
        elif origem == 'form2':
            status = 'emergencial'
            tipo = request.form.get("tipo_refeicao_emergencial")
            motivo = request.form.get("escolha_motivo_emergencial")
            para = 'hoje'
            
        # Insere os dados na tabela refeicoes_solicitadas
        insertin_refeicoes = """
        INSERT INTO refeicoes (matricula, tipo, motivo, para, status)
        VALUES (%s, %s, %s, %s, %s);
        """
        valores = (usuario, tipo, motivo, para, status)

        cursor.execute(insertin_refeicoes, valores)
        conn.commit()
        print("Registro inserido com sucesso.")


    except Exception as e:
        conn.rollback()  # Reverte a transação em caso de erro
        print(f"Erro ao inserir registro: {e}")  

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
                
    return redirect(url_for("solicitar_page"))  # Redireciona para evitar reenvio do formulário
#------------------------------------------------------------------


@app.route("/pegar_status")
def obter_status():
    usuario = session.get("usuario")

    if not usuario:
        return "Nenhum aluno encontrado. Faça um pedido primeiro."

    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # obtem o status da ultima refeição do usuário logado
        cursor.execute("""
            SELECT status FROM refeicoes
            WHERE matricula = %s
            ORDER BY refeicao_id DESC 
            LIMIT 1;
        """, (usuario,))

    except Exception:
        print(f"Erro ao exibir tabela de refeições solicitadas")
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("solicitar.html")


@app.route("/doar_ref")
def doar_refeicao():
    usuario = session.get("usuario")
    
    #filtra as refeições deferidas do usuário
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM refeicoes 
            WHERE matricula = %s and status = 'deferido'
            ORDER BY refeicao_id DESC;
        """, (usuario,))
        
        refeicoes = cursor.fetchall()
    #--------------------------------------   
     
    except Exception:
        print("erro ao exibir refeições")
        
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    
    return render_template("doar.html", refeicoes=refeicoes)  # Página inicial



if __name__ == "__main__":
  app.run(debug=True)
