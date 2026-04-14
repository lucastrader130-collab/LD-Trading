
LD Trading PRO — versão com parser ampliado e layout aprimorado

Como usar:
1. Instale as dependências:
   pip install -r requirements.txt

2. Rode o app:
   streamlit run app.py

3. Cole o texto bruto do seu painel e clique em "Analisar mercado".

O sistema entrega:
- regime de mercado
- viés do WIN e do WDO
- probabilidades de alta, baixa e lateralização
- armadilhas prováveis
- plano operacional
- histórico recente salvo em SQLite

Estrutura:
- app.py
- core/parser.py
- core/engine.py
- core/database.py
- core/ui.py
- data/ld_trading.db (criado automaticamente)
