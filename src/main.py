import time
from machine import Pin, ADC

# --- Parâmetros de configuração ---
LIMIAR_BLOQUEIO = 400   # acima disso = escuro (peça bloqueando)
LIMIAR_LIVRE = 300      # abaixo disso = claro (linha livre)
TEMPO_MICROPARADA = 5000     # ms contínuos bloqueado = alerta de micro-parada
DEBOUNCE_BOTAO = 50          # ms de debounce do botão de reset

# --- Inicialização do hardware ---
ldr_pin = ADC(Pin(34))
ldr_pin.atten(ADC.ATTN_11DB)
btn_pin = Pin(27, Pin.IN, Pin.PULL_UP)

# --- Estado global do sistema ---
estado = {
    "contador_pecas": 0,
    "bloqueado": False,
    "tempo_inicio_bloqueio": 0,
    "alerta_microparada_emitido": False,
    "ultimo_estado_botao": 1,
    "tempo_ultimo_evento_botao": 0,
}


def ler_lux():
    # --- Conversão simplificada do valor bruto do ADC (0-4095) para escala de lux ---
    valor_bruto = ldr_pin.read()
    return (valor_bruto / 4095) * 1000


def verificar_contagem_pecas(lux_atual, tempo_atual):
     # --- Detecção de transição: livre -> bloqueada ---
    if not estado["bloqueado"] and lux_atual > LIMIAR_BLOQUEIO:
        estado["bloqueado"] = True
        estado["tempo_inicio_bloqueio"] = tempo_atual
        estado["alerta_microparada_emitido"] = False

    # --- Detecção de transição de subida: bloqueada -> livre = incrementa contagem ---
    elif estado["bloqueado"] and lux_atual < LIMIAR_LIVRE:
        estado["bloqueado"] = False
        estado["contador_pecas"] += 1
        print("Peca detectada! Total: " + str(estado["contador_pecas"]))


def verificar_microparada(tempo_atual):
    # --- Monitoramento não-bloqueante de tempo contínuo em bloqueio ---
    if estado["bloqueado"] and not estado["alerta_microparada_emitido"]:
        tempo_bloqueado = time.ticks_diff(tempo_atual, estado["tempo_inicio_bloqueio"])
        if tempo_bloqueado > TEMPO_MICROPARADA:
            print("Alerta: Micro-parada detectada!")
            estado["alerta_microparada_emitido"] = True


def verificar_reset(tempo_atual):
    # --- Leitura do botão de reset com debounce ---
    estado_botao_atual = btn_pin.value()

    if estado_botao_atual != estado["ultimo_estado_botao"]:
        estado["tempo_ultimo_evento_botao"] = tempo_atual

    tempo_estavel = time.ticks_diff(tempo_atual, estado["tempo_ultimo_evento_botao"])
    if tempo_estavel > DEBOUNCE_BOTAO:
        if estado_botao_atual == 0 and estado["ultimo_estado_botao"] == 1:
            executar_reset_turno()

    estado["ultimo_estado_botao"] = estado_botao_atual


def executar_reset_turno():
    # --- Zera contadores e cronômetros do turno atual ---
    estado["contador_pecas"] = 0
    estado["bloqueado"] = False
    estado["alerta_microparada_emitido"] = False
    print("Turno resetado com sucesso. Contadores zerados.")


def main():
    print("Contador de Producao Inicializado")

    while True:
        tempo_atual = time.ticks_ms()
        lux_atual = ler_lux()

        verificar_contagem_pecas(lux_atual, tempo_atual)
        verificar_microparada(tempo_atual)
        verificar_reset(tempo_atual)

        time.sleep_ms(10)


main()