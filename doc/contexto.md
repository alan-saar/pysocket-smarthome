# 1. Contextualização do Sistema
Neste trabalho, você atuará como um engenheiro de software responsável por assumir, documentar e expandir um sistema legado. O sistema original é uma aplicação Cliente/Servidor desenvolvida em Python (versão 3.6 ou superior) que utiliza a biblioteca de programação socket com protocolo TCP para controlar dispositivos inteligentes em ambientes residenciais (smart home devices).

## Como o sistema funciona:

### Protocolo de Comunicação:
Existe um protocolo previamente acordado entre clientes e servidor que especifica quais são as mensagens trocadas, a ordem de envio e o formato de cada mensagem.

### Servidor:
Atua como a central de controle da casa, gerenciando os ambientes da residência. O servidor mantém uma conexão TCP ativa com cada dispositivo e é multitarefa (multithread).

### Clientes (Dispositivos):
Cada dispositivo age como um cliente de uma arquitetura Cliente/Servidor e se comunica com o servidor central. Os dispositivos suportados no código base são:

#### Lâmpadas:
São ligadas e desligadas remotamente via mensagens enviadas pelo servidor.

#### Sensores de presença:
Informam para o servidor a presença ou não de pessoas nos ambientes. Quando detectam pessoas, as lâmpadas são acesas; quando não há pessoas, são desligadas.

#### Termômetros:
Informam para o servidor a temperatura do ambiente.

### Inicialização e Operação:
O servidor recupera a lista de ambientes e dispositivos suportados a partir de um arquivo. Ao conectar, o dispositivo informa seu tipo. O servidor valida o tipo, solicita ao usuário o ambiente de instalação (ex: sala de tv, quarto 1) e gera um ID para o dispositivo. Esse ID será usado em todas as mensagens trocadas a partir de então.
O objetivo desta atividade não é construir este sistema do zero, pois o código-fonte base (gabarito) já funcional está sendo fornecido. O foco é demonstrar domínio teórico e prático sobre redes e concorrência, produzindo um repositório altamente didático.

## 2. Passo a Passo e Escopo do Trabalho
### Passo 1: Repositório e Código Original
Comece criando um repositório Git para o projeto.
O seu primeiro commit deve conter exclusivamente o código original (gabarito) fornecido em anexo, exatamente como está.

### Passo 2: Documentação Didática (README.md)
O arquivo README.md será o núcleo da sua entrega. Ele deve ser escrito de forma extremamente didática, estruturado com os seguintes tópicos:

#### Fundamentos de Sockets TCP:
Crie uma seção explicando detalhadamente os conceitos de sockets TCP. É obrigatório explicar o funcionamento do buffer TCP e o motivo pelo qual o código precisa tratar o recebimento de mensagens, uma vez que não se pode garantir que cada send() de uma extremidade resultará em exatamente um recv() na extremidade oposta.

#### Arquitetura e Diagramas de Fluxo:
Você encontrará em anexo o arquivo "Fluxogramas.pptx" contendo os diagramas básicos do sistema. Você deve incluir e aprimorar esses diagramas no seu README, tornando-os visualmente mais claros e explicativos. Detalhe o papel da Thread Principal, das threads iniciadas pelo servidor para cada cliente (Temperatura, Presença, Lâmpada), da Thread de Controle Geral e como ocorre a troca de mensagens utilizando filas (queues).

#### O Protocolo de Comunicação:
Explique quais são as mensagens trocadas, a ordem de envio e o formato de cada mensagem. Detalhe o formato fixo das mensagens, explicando a ordem dos campos com tamanhos múltiplos de 1 byte (código da mensagem, data e hora da mensagem, e ID do dispositivo).

#### Roteiro Detalhado de Testes:
Crie um guia minucioso explicando como inicializar o servidor e registrar os dispositivos. Descreva como simular mudanças via teclado no console dos clientes, fornecendo a temperatura ou os valores 1 e 0 para presença. Documente também como observar a impressão obrigatória de logs nos terminais. Inclua capturas de tela (printscreens) detalhadas de todas as etapas, incluindo o que acontece se um tipo de dispositivo não suportado for registrado, resultando em erro e finalização da conexão.

### Passo 3: Extensão do Sistema
* Implemente um novo cliente simples à sua escolha (ex: Ar-Condicionado Inteligente, Cortina Automática, etc.).
* O novo dispositivo deve inicializar uma conexão TCP, enviar o identificador do seu tipo, ser validado pelo servidor e receber seu ID gerado para comunicação contínua.
* Realize essa implementação mantendo boas práticas de versionamento (commits lógicos, pequenos e bem descritos).
* Identifique possíveis bugs e melhorias no sistema
