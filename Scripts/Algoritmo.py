import math

def calcular_puntaje_ajustado(tempo, popularidad, avatars_matados, puntos_avatar, limite_maximo):
    # Calcular media armónica solo si los valores son positivos
    if tempo > 0 and popularidad > 0:
        media_armonica = 2 / ((1 / tempo) + (1 / popularidad))
    else:
        media_armonica = 0

    # Factor de intensidad: depende de la cantidad de enemigos eliminados y del tempo
    factor_intensidad = (avatars_matados / (tempo + 1)) * 0.05

    # Factor del avatar: crece con la raíz cuadrada de los puntos
    factor_avatar = 1 + math.sqrt(puntos_avatar / 500)

    # Puntaje ajustado combinando los factores
    puntaje_ajustado = (media_armonica + (factor_intensidad * 100)) * factor_avatar

    # Limitar el valor máximo permitido
    if puntaje_ajustado > limite_maximo:
        puntaje_ajustado = limite_maximo

    # Retornar el resultado final
    return puntaje_ajustado


# ============================
# Ejemplo de uso:
# ============================
tempo = 120
popularidad = 80
avatars_matados = 25
puntos_avatar = 1000
limite_maximo = 500

resultado = calcular_puntaje_ajustado(tempo, popularidad, avatars_matados, puntos_avatar, limite_maximo)
print(f"Puntaje ajustado: {resultado:.2f}")
