""" 
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
python3 comparaRelatorios.py -r <referencia> -a <avaliado>
- Onde <referencia> e <avaliado> são, respectivamente, os caminhos para os relatórios xml do JaCoCo.

O nome do arquivo (relatório JaCoCo) de cada teste deverá seguir o seguinte padrão: 
<NOME_DO_LAB>-<NUM_ID_RODADA>-<NUM_ID_TESTE>.xml
Ex: LAINF-R001-T001.xml

Contato: smcamara@inmetro.gov.br
"""

import sys, getopt, os, time, difflib, optparse
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, encoding='utf-8').decode('utf8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

def comparaUmRelatorio(referencia_arq, avaliado_arq):    
    # Carrega relatorios para comparacao
    dom1 = ET.parse(referencia_arq).getroot()  # eh a referencia, as variaveis possuem _l (left) no nome
    dom2 = ET.parse(avaliado_arq).getroot()
    
    # Inicializa variaveis do resultado total
    num_linhas_cobertas_gabarito_total = 0
    num_linhas_cobertas_certas_total = 0
    num_linhas_cobertas_erradas_total = 0
    num_linhas_nao_cobertas_total = 0
    num_linhas_total = 0 # variavel 'T'
    
    # Abre arquivo de resultados para escrita
    resultado_arq = open('Resultado_comparaRelatorios.txt', 'w')
    
    for package in dom1.iter("package"):
        
        #armazena caminho do package
        caminho_arq_java = package.get('name')
        
        # Zera variaveis do resultado por package
        num_linhas_cobertas_gabarito_package = 0
        num_linhas_cobertas_certas_package = 0
        num_linhas_cobertas_erradas_package = 0
        num_linhas_nao_cobertas_package = 0
                
        # Escreve resultados totais do package
        resultado_arq.write("\n\n********************************************************************************")
        resultado_arq.write("\n*********************  ")
        resultado_arq.write("PACKAGE: " + caminho_arq_java)
        resultado_arq.write("\n********************************************************************************\n\n")
        
                
        # Itera por sourcefile (ou classe)
        for sourcefile_l in package.iter("sourcefile"):
            #ET.dump(sourcefile_l) 
            #resultado_arq.write(ET.tostring(sourcefile_l, encoding='utf8').decode('utf8'))
            
            # Printa na tela a classe que esta sendo analisada
            
            nome_arq_java = sourcefile_l.get('name')
            print("Processando: " + caminho_arq_java + "/" + nome_arq_java )
            
            # Seleciona a posicao da classe no relatorio avaliado
            sourcefile_r = dom2.find('.//package[@name="' + caminho_arq_java + '"]/sourcefile[@name="' + nome_arq_java + '"]')
             
            # Inicializa listas que armazena as linhas cobertas e nao cobertas 
            linhas_cobertas_certas = [] # linhas corretamente cobertas pelo avaliado
            linhas_cobertas_erradas = [] # linhas cobertas a mais, fora das linhas que precisava
            linhas_nao_cobertas = [] # linhas que precisavam ter sido cobertas, mas que nao foram (erroneamente não-cobertas)
            num_linhas_cobertas_gabarito_sourcefile = 0
    
            # Percorre linha por linha da classe analisada
            for line_l in sourcefile_l.iter("line"):
                num_linhas_total += 1
                
                # preenche os atributos da linha do gabarito
                line_nr_l = int(line_l.get('nr'))
                line_mi_l = int(line_l.get('mi'))
                line_ci_l = int(line_l.get('ci'))
                line_mb_l = int(line_l.get('mb'))
                line_cb_l = int(line_l.get('cb'))
                
                # acha a linha correspondente no relatorio avaliado e preenche os atributos da linha
                line_r = sourcefile_r.find('.//line[@nr="' + str(line_nr_l) + '"]')
                
                if line_r == None:
                    print("Linha não encontrada no relatório avaliado: " + str(line_nr_l))
                else:
                    line_nr_r = int(line_r.get('nr'))
                    line_mi_r = int(line_r.get('mi'))
                    line_ci_r = int(line_r.get('ci'))
                    line_mb_r = int(line_r.get('mb'))
                    line_cb_r = int(line_r.get('cb'))
                    
                    # comparacoes entre as diferencas dos atributos das linhas
                    if (line_ci_l == line_ci_r == 0): # and (line_cb_l == line_cb_r == 0):
                        continue  # a linha nao foi coberta por ninguem
                    elif (line_ci_l == line_ci_r > 0): # and (line_cb_l == line_cb_r > 0):
                        linhas_cobertas_certas.append(line_nr_r)  # linha corretamente coberta pelo avaliado
                    elif (line_ci_l < line_ci_r > 0): # and (line_cb_l < line_cb_r > 0):
                        linhas_cobertas_erradas.append(line_nr_r)  # linha coberta a mais, erroneamente
                    elif (0 < line_ci_l > line_ci_r): # and (0 < line_cb_l > line_cb_r):
                        linhas_nao_cobertas.append(line_nr_r)  # linha que precisava ter sido coberta, mas que nao foi
            
            # Escreve no resultado apenas se ha informacao sobre a cobertura
            if not (linhas_cobertas_certas == linhas_cobertas_erradas == linhas_nao_cobertas == []):        
    
                # Numero de linhas que importam (nao contabiliza as linhas que nao foram cobertas pelos 2 relatorios)
                num_linhas_cobertas_gabarito_sourcefile = len(linhas_cobertas_certas) + len(linhas_nao_cobertas)
                
                # Calcula percentagem de cada lista
                if num_linhas_cobertas_gabarito_sourcefile > 0:
                    perc_cobertas_certas = 100 * len(linhas_cobertas_certas) / num_linhas_cobertas_gabarito_sourcefile  
                    str_perc_cobertas_certas = str(len(linhas_cobertas_certas)) + "/" +  str(num_linhas_cobertas_gabarito_sourcefile) + " - " + str(float("{0:.2f}".format(perc_cobertas_certas))) + "%"
                    perc_nao_cobertas = 100 * len(linhas_nao_cobertas) / num_linhas_cobertas_gabarito_sourcefile
                    str_perc_nao_cobertas = str(len(linhas_nao_cobertas)) + "/" +  str(num_linhas_cobertas_gabarito_sourcefile) + " - " + str(float("{0:.2f}".format(perc_nao_cobertas))) + "%"
                else:
                    str_perc_cobertas_certas_sourcefile = "N/A (Não há linhas a serem cobertas)."
                    str_perc_nao_cobertas_sourcefile = "N/A (Não há linhas a serem cobertas)."
            
                # Escreve nome do soucefile/classe  
                resultado_arq.write("\n\n*********************  ")
                resultado_arq.write(caminho_arq_java + "/" + nome_arq_java)
                resultado_arq.write("  *********************\n\n")
                
                # Escreve resultados por classe
                if not (linhas_cobertas_certas == []):  
                    resultado_arq.write("\nLinhas corretamente cobertas ("+ str_perc_cobertas_certas +"): ")
                    resultado_arq.write(str(linhas_cobertas_certas)[1:-1])
                if not (linhas_cobertas_erradas == []):  
                    resultado_arq.write("\nLinhas erroneamente cobertas ("+ str(len(linhas_cobertas_erradas)) +" linha(s)): ")
                    resultado_arq.write(str(linhas_cobertas_erradas)[1:-1])
                if not (linhas_nao_cobertas == []):  
                    resultado_arq.write("\nLinhas erroneamente não-cobertas ("+ str_perc_nao_cobertas +"): ")
                    resultado_arq.write(str(linhas_nao_cobertas)[1:-1])
                    
                # Atualiza resultados parciais nas variaveis de resultados por package
                num_linhas_cobertas_gabarito_package += num_linhas_cobertas_gabarito_sourcefile
                num_linhas_cobertas_certas_package += len(linhas_cobertas_certas)
                num_linhas_cobertas_erradas_package += len(linhas_cobertas_erradas)
                num_linhas_nao_cobertas_package += len(linhas_nao_cobertas)
                
                
        # Escreve resultados do package
        #resultado_arq.write("\n\n\n\n********************************************************************************")
        resultado_arq.write("\n\n*********************  ")
        resultado_arq.write("RESULTADO PACKAGE: " + caminho_arq_java + "\n\n")
        #resultado_arq.write("\n********************************************************************************\n\n")
        
        str_perc_cobertas_certas_package = ""
        str_perc_nao_cobertas_package = ""
        
        if num_linhas_cobertas_gabarito_package > 0:
            perc_cobertas_certas_package = 100 * num_linhas_cobertas_certas_package / num_linhas_cobertas_gabarito_package
            str_perc_cobertas_certas_package = str(num_linhas_cobertas_certas_package) + "/" +  str(num_linhas_cobertas_gabarito_package) + " - " + str(float("{0:.2f}".format(perc_cobertas_certas_package))) + "%"
            perc_nao_cobertas_package = 100 * num_linhas_nao_cobertas_package / num_linhas_cobertas_gabarito_package
            str_perc_nao_cobertas_package = str(num_linhas_nao_cobertas_package) + "/" +  str(num_linhas_cobertas_gabarito_package) + " - " + str(float("{0:.2f}".format(perc_nao_cobertas_package))) + "%"
        else:
            str_perc_cobertas_certas_package = "N/A (Não há linhas a serem cobertas)."
            str_perc_nao_cobertas_package = "N/A (Não há linhas a serem cobertas)."
            
        resultado_arq.write("\nLinhas corretamente cobertas (package): "+ str_perc_cobertas_certas_package)
        resultado_arq.write("\nLinhas erroneamente cobertas (package): "+ str(num_linhas_cobertas_erradas_package) +" linha(s)")
        resultado_arq.write("\nLinhas erroneamente não-cobertas (package): "+ str_perc_nao_cobertas_package)
        resultado_arq.write("\n\n\n\n\n")
        
        # Atualiza resultados dos packages nas variaveis de resultados totais
        num_linhas_cobertas_gabarito_total += num_linhas_cobertas_gabarito_package
        num_linhas_cobertas_certas_total += num_linhas_cobertas_certas_package
        num_linhas_cobertas_erradas_total += num_linhas_cobertas_erradas_package
        num_linhas_nao_cobertas_total += num_linhas_nao_cobertas_package
    
    # Escreve resultados totais
    resultado_arq.write("\n\n\n\n********************************************************************************")
    resultado_arq.write("\n*********************  ")
    resultado_arq.write("RESULTADO TOTAL")
    resultado_arq.write("\n********************************************************************************\n\n")
    resultado_arq.write("Relatório de referência: " + referencia_arq)
    resultado_arq.write("\nRelatório avaliado: " + avaliado_arq)
    
    str_perc_cobertas_certas_total = ""
    str_perc_nao_cobertas_total = ""
        
    if num_linhas_cobertas_gabarito_total > 0:
        perc_cobertas_certas_total = 100 * num_linhas_cobertas_certas_total / num_linhas_cobertas_gabarito_total
        str_perc_cobertas_certas_total = str(num_linhas_cobertas_certas_total) + "/" +  str(num_linhas_cobertas_gabarito_total) + " - " + str(float("{0:.2f}".format(perc_cobertas_certas_total))) + "%"
        perc_nao_cobertas_total = 100 * num_linhas_nao_cobertas_total / num_linhas_cobertas_gabarito_total
        str_perc_nao_cobertas_total = str(num_linhas_nao_cobertas_total) + "/" +  str(num_linhas_cobertas_gabarito_total) + " - " + str(float("{0:.2f}".format(perc_nao_cobertas_total))) + "%"
    else:
        str_perc_cobertas_certas_total = "N/A (Não há linhas a serem cobertas)."
        str_perc_nao_cobertas_total = "N/A (Não há linhas a serem cobertas)."
    
    resultado_arq.write("\n\n-- Cobertura --")        
    resultado_arq.write("\nLinhas corretamente cobertas (total): "+ str_perc_cobertas_certas_total)
    resultado_arq.write("\nLinhas erroneamente cobertas (total): "+ str(num_linhas_cobertas_erradas_total) +" linha(s)")
    resultado_arq.write("\nLinhas erroneamente não-cobertas (total): "+ str_perc_nao_cobertas_total)
    resultado_arq.write("\nNúmero de linhas totais: "+ str(num_linhas_total))
    #resultado_arq.write("\n\n\n\n\n")
    
    # Calcula e escreve métricas do teste
    CC = num_linhas_cobertas_certas_total
    SR = num_linhas_cobertas_certas_total + num_linhas_nao_cobertas_total
    SL = num_linhas_cobertas_certas_total + num_linhas_cobertas_erradas_total
    T  = num_linhas_total   
    
    J = CC / (SR + SL - CC) # Jaccard, preciso tirar CC no denominador para nao contar 2 vezes a intersecao de SR e SL
    
    alfa = 0.1
    R = alfa*(CC/SR) + (1-alfa)*((T-(SR+SL-CC))/(T-SR)) # métrica R
    
    resultado_arq.write("\n\n-- Métricas --")
    resultado_arq.write("\nJaccard (J): "+ str(J))
    resultado_arq.write("\nSimilaridade R: "+ str(R))
    resultado_arq.write("\n\n")
    
    # Fecha arquivo de resultados
    resultado_arq.close()


def usage():
    print(sys.argv[0] + ' -r <referencia> -a <avaliado>')

def main(argv):
    referencia_arq = ''
    avaliado_arq = ''
    
    found_r = False
    found_a = False
    
    try:
        opts, args = getopt.getopt(argv,"hr:a:",["referencia=","avaliado="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit()
        elif opt in ("-r", "--referencia"):
            referencia_arq = arg
            found_r = True
        elif opt in ("-a", "--avaliado"):
            avaliado_arq = arg
            found_a = True
        else:
            usage()
            sys.exit(2)
    
    if not (found_r and found_a):
        usage()
        sys.exit(2)
       
    # Chama a funcao de comparacao de relatorios
    comparaUmRelatorio(referencia_arq, avaliado_arq)


if __name__ == "__main__":
   main(sys.argv[1:])




