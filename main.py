# Importa a função factory que cria a aplicação Flask configurada
from app import create_app

# Este bloco só executa quando o arquivo é rodado diretamente (não quando importado)
if __name__ == '__main__':
    # Cria a instância da aplicação usando a factory function
    app = create_app()

    # Inicia o servidor de desenvolvimento
    # debug=True: ativa modo debug (recarrega automático, mostra erros detalhados)
    # host='0.0.0.0': aceita conexões de qualquer IP (não só localhost)
    # port=5000: porta onde o servidor vai rodar
    app.run(debug=True, host='0.0.0.0', port=5000)
