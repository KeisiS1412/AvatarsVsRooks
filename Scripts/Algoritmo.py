import math

# Variable global que guarda el puntaje máximo alcanzado
puntaje_acumulado_global = 0

def calcular_puntaje_ajustado(tempo, popularidad, avatars_matados, puntos_avatar, limite_maximo):
    """
    Calcula un puntaje ajustado que solo puede crecer a lo largo de la partida.
    Se basa en tempo, popularidad, enemigos eliminados y puntos obtenidos del jugador.
    """

    global puntaje_acumulado_global

    # Calcular media armónica solo si los valores son positivos
    if tempo > 0 and popularidad > 0:
        media_armonica = 2 / ((1 / tempo) + (1 / popularidad))
    else:
        media_armonica = 0

    # Factor de intensidad: depende de la cantidad de enemigos eliminados y el ritmo del juego
    factor_intensidad = (avatars_matados / (tempo + 1)) * 0.05

    # Factor del avatar: crece con la raíz cuadrada de los puntos acumulados
    factor_avatar = 1 + math.sqrt(puntos_avatar / 500)

    # Cálculo principal
    puntaje_ajustado = (media_armonica + (factor_intensidad * 100)) * factor_avatar

    # Limita el puntaje al valor máximo
    if puntaje_ajustado > limite_maximo:
        puntaje_ajustado = limite_maximo

    #  Nueva lógica: nunca disminuir el puntaje
    if puntaje_ajustado < puntaje_acumulado_global:
        puntaje_ajustado = puntaje_acumulado_global
    else:
        puntaje_acumulado_global = puntaje_ajustado

    return puntaje_ajustado
