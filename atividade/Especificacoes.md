Aqui está a análise comparativa detalhada entre o que foi falado/desenhado em sala e o PDF oficial, seguida pela **especificação consolidada e definitiva do trabalho**.

---

### 1. Divergências entre o Áudio/Quadro e o PDF Oficial

| Item | Versão da Aula (Áudio + Foto) | Versão Oficial (PDF) | Como Resolver no Projeto |
| --- | --- | --- | --- |
| **Unidade de Tráfego** | O professor falou e anotou explicitamente **Mbps** (*Megabits por segundo*).

 | O documento oficial padroniza a métrica em **bps** (*bits por segundo*).

 | Calcule em **bps** conforme o PDF (ou exiba em **bps** com formatação dinâmica/legenda clara para não perder pontos no critério de avaliação de 25%).

 |
| **Combinação de Alertas** | O professor explicou como escolha exclusiva ("ou pop-up ou e-mail") para alternar durante o teste.

 | O PDF exige formalmente a possibilidade de selecionar **pop-up, e-mail OU AMBOS** simultaneamente.

 | Use *checkboxes* na interface permitindo marcar `[x] Pop-up` e/ou `[x] E-mail`.

 |
| **Filtro do Histórico** | Exemplificado como atalhos relativos (ex.: "últimos 15 min", "últimas 3 horas", "últimos 3 dias").

 | Exige filtro de período com **data/hora de início e data/hora de fim** (campos de calendário/hora).

 | Implemente os seletores de **Data/Hora Início e Fim** (você pode manter botões de atalho rápido como diferencial visual).

 |

---

### 2. O que constava APENAS no Áudio/Quadro (não está no PDF)

1. **Volume mínimo de coleta real (1 a 2 horas):**
* No áudio, o professor exigiu explicitamente que a base tenha **pelo menos de 1 a 2 horas de dados reais capturados do roteador**, permitindo usar dados sintéticos (gerados por IA/scripts) apenas para estender o histórico para prazos maiores (ex.: 3 dias). O PDF não estipula essa cota mínima.




2. **Wireframe visual da interface:**
* A disposição dos elementos veio exclusivamente do quadro: cabeçalho com intervalo de coleta e botão `Cfg` no canto superior direito; dois gráficos de Tempo Real no topo com a linha tracejada do *threshold*; seletor de intervalo ao centro; e dois gráficos de Histórico no bloco inferior.




3. **Dinâmica prática da apresentação:**
* O professor frisou no áudio que a avaliação será feita passando de bancada em bancada diretamente na máquina da equipe, sem apresentação de seminário/slides na frente da sala.





---

### 3. O que o PDF Oficial ADICIONOU de Requisitos Técnicos

* **Protocolo SNMP e MIBs/OIDs:** Formalizou o uso obrigatório de SNMP (preferência por SNMPv3, ou v2c/v1 com comunidade somente leitura em laboratório) e exigência de documentar quais OIDs foram consultados.


* **Botão "Resetar":** Além de Iniciar e Pausar, a tela de tempo real deve possuir o botão Resetar (limpar a exibição atual sem corromper o banco/arquivo histórico).


* **Prevenção de Tempestade de E-mails (Debouncing):** O sistema não pode disparar um e-mail a cada leitura em que o limiar estiver violado; deve notificar apenas na transição de estado (*Normal $\rightarrow$ Excedido*) e aguardar normalização ou tempo de carência.


* **Tratamento de Contadores e Erros:** Tratar reinicialização do contador SNMP (*counter rollover/reset* para não gerar taxas negativas), timeouts e perda de conexão.


* **Validações na Interface:** Rejeitar intervalos de coleta $\le 0$ e validar a máscara de e-mail.


* **Entregáveis Formais e Pesos:** Repositório Git com README e documentação técnica detalhada dos cálculos e OIDs.



---

---

## Especificação Completa e Consolidada do Trabalho

### 1. Escopo e Objetivo

Desenvolver uma aplicação desktop ou web para monitoramento de telemetria de roteador via **SNMP**, realizando coletas periódicas de tráfego de rede e uso de processamento, exibição visual em tempo real (janela deslizante) e histórico persistente, além de acionamento de alertas por *threshold*.

---

### 2. Métricas Monitoradas e Cálculo

* **Interface:** Monitorar uma única interface de rede do equipamento (a interface ativa/principal).


* **Tráfego de Entrada (IN) e Saída (OUT):**
* Leitura dos contadores de bytes acumulados via SNMP (ex.: MIB-II `ifInOctets`/`ifOutOctets` ou `ifHCInOctets`/`ifHCOutOctets`).


* Fórmula obrigatória:

$$\text{Taxa (bps)} = \frac{(\text{Bytes}_{\text{atual}} - \text{Bytes}_{\text{anterior}}) \times 8}{\Delta t}$$



*(Onde $\Delta t$ é o tempo decorrido real em segundos entre as leituras)*.


* **Tratamento obrigatório:** Tratar *counter rollover* (quando o contador de 32 bits zera e reinicia) e rejeitar valores negativos ou irreais.




* **Utilização de CPU (%):**
* Leitura percentual reportada pelo roteador conforme a MIB do fabricante (ex.: Cisco, Mikrotik ou Linux/NET-SNMP).





---

### 3. Interface com o Usuário (Dashboard)

A disposição deve seguir a estrutura esboçada no quadro:

```
+----------------------------------------------------------------------------------+
|  [ Intervalo de Coleta: (segundos) ]                         [ Configurações ⚙️ ]  |
+----------------------------------------------------------------------------------+
| PAINEL TEMPO REAL (RT)                    [ Iniciar ]  [ Pausar ]  [ Resetar ]   |
|                                                                                  |
|  +-------------------------------------+   +----------------------------------+  |
|  | Gráfico: Tráfego IN / OUT (bps)     |   | Gráfico: Utilização da CPU (%)   |  |
|  | - - - - [ Linha Threshold ] - - - - |   | - - - - [ Linha Threshold ] - -  |  |
|  | (Janela Deslizante / Rolagem)       |   | (Janela Deslizante / Rolagem)    |  |
|  +-------------------------------------+   +----------------------------------+  |
+----------------------------------------------------------------------------------+
| FILTRO DE HISTÓRICO: [ Início: DD/MM/AAAA HH:MM ] até [ Fim: DD/MM/AAAA HH:MM ]  |
+----------------------------------------------------------------------------------+
| PAINEL HISTÓRICO (Hist.)                                                         |
|                                                                                  |
|  +-------------------------------------+   +----------------------------------+  |
|  | Gráfico Histórico: Tráfego (bps)    |   | Gráfico Histórico: CPU (%)       |  |
|  | (Séries temporais estáticas IN/OUT) |   | (Série temporal da utilização)   |  |
|  +-------------------------------------+   +----------------------------------+  |
+----------------------------------------------------------------------------------+

```

#### Regras da Interface:

1. **Área Tempo Real:**
* Gráficos em **janela deslizante** contínua.


* Linhas horizontais tracejadas indicando os *thresholds* configurados.


* Botões: **Iniciar** (inicia a thread de coleta sem duplicar processos se clicado novamente), **Pausar** (congela a tela preservando os pontos) e **Resetar** (limpa a visualização da tela atual sem apagar o histórico gravado no banco/disco).




2. **Área Histórica:**
* Gráficos gerados a partir do banco de dados/arquivo.


* Seletores de data/hora inicial e final.


* Mensagem amigável na tela caso o intervalo selecionado não possua dados.





---

### 4. Sistema de Alertas e Notificações

* **Limiares (*Thresholds*):** Configuráveis separadamente para CPU (%) e Tráfego (bps).


* **Modos de Envio:** Opção de selecionar **Pop-up**, **E-mail** ou **Ambos**.


* **Conteúdo da Notificação:**
* Nome da métrica violada (CPU, Tráfego IN ou Tráfego OUT).


* Valor observado na medição.


* Limite (*threshold*) que estava configurado.


* Data e hora exatas da ocorrência.




* **Prevenção de *Spam* (Histerese):** Disparar o e-mail apenas na transição do estado normal para o estado de sobrecarga. Só reenviar caso a métrica volte ao normal e torne a subir, ou após um tempo de carência configurado.



---

### 5. Parâmetros de Configuração Mínimos (Modal/Aba `Cfg`)

1. **Endereço do Roteador / IP**.


2. **Versão SNMP e Parâmetros:** Versão (v2c ou v3), comunidade de leitura ou credenciais de segurança e identificador da interface monitorada.


3. **Intervalo de Coleta:** Em segundos (validar para rejeitar $\le 0$).


4. **Threshold de Tráfego:** Em bps (definir se para IN, OUT ou ambos).


5. **Threshold de CPU:** Em percentual (%).


6. **Canais de Alerta:** Checkboxes para Pop-up e E-mail.


7. **E-mail de Destino:** Campo com validação de formato (ex.: regex de e-mail) e credenciais SMTP.



---

### 6. Roteiro Prático de Demonstração (Bancada)

Para a avaliação na bancada, garanta que a aplicação esteja pronta para o seguinte fluxo de teste:

1. **Carga Inicial:** Chegar para a avaliação com **pelo menos 1 a 2 horas de dados reais previamente coletados** armazenados no banco/arquivo.


2. **Teste dos Controles:** Iniciar a coleta ao vivo, pausar e resetar o gráfico em tempo real.


3. **Consulta Histórica:** Selecionar um intervalo de data/hora no filtro e carregar as curvas do tráfego e CPU.


4. **Estresse e Pop-up:** Configurar canal em *Pop-up*, estressar o tráfego ou CPU (ou baixar temporariamente o *threshold*) e exibir a janela de notificação na tela.


5. **Estresse e E-mail:** Alternar para *E-mail*, provocar novo pico e mostrar o e-mail chegando na caixa postal.


6. **Resiliência:** Desconectar o cabo de rede/interromper o SNMP temporariamente para mostrar que a aplicação reporta o erro na interface sem travar nem fechar sozinha.



---

### 7. Critérios de Avaliação e Entregáveis

| Critério | Peso | Itens Avaliados |
| --- | --- | --- |
| **Coleta SNMP e Cálculos** | **25%** | Leitura das OIDs corretas, cálculo de bps por $\Delta t$ e leitura de CPU.

 |
| **Gráficos Real Time e Controles** | **20%** | Janela deslizante, botões Iniciar, Pausar e Resetar, fluidez visual.

 |
| **Sistema de Alertas** | **20%** | Pop-up, e-mail, thresholds independentes e controle de disparos repetitivos.

 |
| **Histórico e Persistência** | **15%** | Persistência íntegra (arquivo/banco) e filtro por data/hora inicial e final.

 |
| **Configuração e Tratamento de Erros** | **10%** | Validação de campos e tratamento de falhas SNMP/timeout.

 |
| **Documentação e Código** | **10%** | Repositório Git, README (como rodar), explicação das MIBs/OIDs e capturas de tela.

 |