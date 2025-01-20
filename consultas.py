from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__) 

# Carregar o DataFrame de exemplo (substitua com o seu arquivo CSV)
dados_df = pd.read_csv('./analise-vendas.csv')

campos_casting = ['Total de Nota Fiscal de Saída', 'Lucro bruto', 'Total de NS em aberto']

for casting in campos_casting:
    dados_df[casting] = dados_df[casting].replace({r'R\$ ': '', r'\.': '', ',': '.'}, regex=True).astype(float)

# Criar página do site
# 1- Route 
# 2- Função
# 3- Template
@app.route('/')
def home():
    return render_template('homepage.html')

@app.route('/consulta', methods=['GET', 'POST'])
def consulta():
    if request.method == 'POST':
        campo = request.form['campo']
        valor = request.form['valor']
        
        if campo in dados_df.columns:
            # Verifique se o valor é numérico para campos específicos
            if campo in ["#", "Nota Fiscal de Saída"]:
                try:
                    valor = int(valor)
                except ValueError:
                    return f"O valor para '{campo}' deve ser numérico."
            
            if campo in '% de lucro bruto':
                try:
                    valor = float(valor)
                except ValueError:
                    return f"O valor para {campo} deve ser decimal"
                
            if campo in ['Total de Nota Fiscal de Saída', 'Lucro bruto', 'Total de NS em aberto']:
                try:
                    valor = float(valor)
                except ValueError:
                    return f"O valor deve ser decimal"

            # Filtrar os dados
            cliente_info = dados_df[dados_df[campo] == valor] # Retorna o valor de todos os campos
            if not cliente_info.empty:
                return render_template('resultado.html', cliente_info=cliente_info)
            else:
                return f"Nenhum registro encontrado para o campo '{campo}' com o valor '{valor}'."
        else:
            return f"Campo '{campo}' não encontrado no arquivo."

    return render_template('consulta.html')

if __name__ == '__main__': # é usada para garantir que um trecho de código seja executado apenas quando o script for executado diretamente, e não quando ele for importado como um módulo em outro script 
    app.run(host='0.0.0.0', port=5000, debug=True)