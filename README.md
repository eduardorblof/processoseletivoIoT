# Processo Seletivo – Intensivo Maker | IoT

### Identificação do Candidato

- **Nome completo:** Eduardo Rabelo Feitosa
- **GitHub:** eduardorblof

---

## Visão Geral da Solução

O projeto implementa um Contador de Produção Não-Intrusivo, voltado para linhas de montagem sem CLP. Para isso, utiliza-se um sensor óptico (LDR) para detectar a passagem de peças em uma esteira, incrementando um contador de produção a cada peça detectada. Além disso, o sistema é capaz de monitorar micro-paradas na linha, permitindo reset manual com um botão.

## Arquitetura do Sistema Embarcado

O firmware é estruturado em um loop principal (main()), que, a cada iteração, (i) lê o valor atual do sensor LDR (ler_lux()); (ii) verifica se houve uma transição de estado que indique passagem de peça (verificar_contagem_pecas()); (iii) verifica se a linha está bloqueada há tempo suficiente para configurar uma micro-parada (verificar_microparada()); e,por fim, (iv) verifica se o botão de reset foi pressionado e solto, com debounce (verificar_reset()). O estado do sistema é centralizado em um único dicionário (estado), evitando múltiplas variáveis globais soltas e deixando explícito tudo que compõe o estado do contador em um só lugar.

* Fluxo de reset (debounce de 2 fases):

O botão é lido a cada iteração. Quando uma mudança de leitura é detectada, um temporizador de debounce (50ms) é iniciado. Somente após esse período de estabilidade a leitura é "confirmada". O reset é disparado na transição de pressionado para solto (borda de subida do sinal, considerando pull-up), e não no momento do aperto — isso evita que o reset dispare prematuramente, antes do cenário completar a ação de soltar o botão.

* Micro-parada:

Utiliza time.ticks_ms() e time.ticks_diff() para medir o tempo contínuo em que a linha permanece bloqueada, sem bloquear o loop principal. Se esse tempo ultrapassar o limiar parametrizado (5000ms), um alerta único é emitido, evitando repetição da mensagem enquanto a condição persiste.

## Componentes Utilizados na Simulação

ESP32 DevKit C v4: microcontrolador principal, responsável por toda a lógica do firmware e pela comunicação serial.

Sensor Óptico (LDR) — ID ldr1: conectado ao pino analógico 34 (AO), realiza a leitura contínua de luminosidade para detectar a passagem de peças pela esteira.

Botão de Reset — ID btn1: conectado ao pino digital 27, configurado em modo PULL_UP, permite ao operador encerrar e zerar o turno atual.

Interface Serial (UART): utilizada para emitir logs de inicialização, detecção de peças, alertas de micro-parada e confirmação de reset, além de servir como canal de validação para os testes automatizados do Wokwi CI.

## Decisões Técnicas Relevantes

Organização em funções por responsabilidade: o firmware foi refatorado para separar cada regra de negócio em uma função isolada (ler_lux, verificar_contagem_pecas, verificar_microparada, verificar_reset, executar_reset_turno), deixando o loop principal curto e fácil de acompanhar.

Debounce de duas fases: a leitura bruta do botão é separada do "estado confirmado", evitando que o processo de debounce consumisse a transição do botão antes do tempo mínimo de estabilidade ser respeitado.


## Resultados Obtidos

Os três cenários de teste automatizados (Wokwi CI) foram validados com sucesso via GitHub Actions:

Cenário 1 – Contagem Normal de Peças: o sistema detecta corretamente a transição de bloqueio e liberação do sensor, incrementando o contador apenas quando a peça termina de passar.

Cenário 2 – Micro-parada: o sistema identifica corretamente quando a linha permanece bloqueada além do tempo limite parametrizado, emitindo o alerta correspondente.

Cenário 3 – Reset Manual de Turno: o sistema reconhece o acionamento completo do botão (pressionar e soltar), com debounce, e zera corretamente os contadores do turno.
