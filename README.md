Scripts para o Ensaio de Proficiência em Software (Lainf/Inmetro)

# comparaRelatorios.py
O script comparaRelatorios.py compara dois arquivos xml no formato de 
relatório JaCoCo. 

Entradas:
- O relatório 'referência'; 
- O relatório 'avaliado'.

Saída:
- A cobertura de código (linha por linha, totalizada e percentual) do 
relatório avaliado em relação ao relatório referência.
- A avaliação do teste obtida segundo as métricas estipuladas.

Modo de usar:
- python3 comparaRelatorios.py -r [referencia] -a [avaliado]
- Onde [referencia] e [avaliado] são, respectivamente, os caminhos para os relatórios xml do JaCoCo.
