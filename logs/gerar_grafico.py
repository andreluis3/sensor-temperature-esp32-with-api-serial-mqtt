import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Configurar fontes para padrão científico/ABNT (Times New Roman)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman', 'DejaVu Serif']
plt.rcParams['axes.unicode_minus'] = False

# --- PROTEÇÃO CONTRA FILENOTFOUNDERROR ---
# Descobre automaticamente a pasta onde este script está salvo e busca o CSV no mesmo lugar
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_csv = os.path.join(diretorio_atual, 'ok22sensor_log_2026-05-19_20-43-00.csv')

# Carregar o arquivo de log
df = pd.read_csv(caminho_csv)

# Eixo X definido em Minutos (usando a coluna 'minutes' original do arquivo)
x = df['minutes'].values
y = df['temp_suavizada'].values

# Encontrar o ponto de pico térmico (máximo)
idx_max = np.argmax(y)
x_max = x[idx_max]
y_max = y[idx_max]

# Criar a figura com alta resolução (300 DPI) para Banner/TCC
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)

# Fundo totalmente branco
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# COR IDENTIFICADA NO SEU OUTRO GRÁFICO: Azul Corporativo/Científico (#3579a6)
cor_linha_usuario = '#3579a6'

# Plotar a linha espessa para evidenciar a estabilidade térmica
ax.plot(x, y, color=cor_linha_usuario, linewidth=3, label='Temperatura do PCM')

# Adicionar marcador visual no pico térmico
ax.scatter(x_max, y_max, color='#ff4d4d', s=80, zorder=5, edgecolors='#333333', linewidths=1)

# Anotação textual do pico térmico
ax.annotate(
    f"Pico térmico: {y_max:.3f} °C",
    xy=(x_max, y_max),
    xytext=(x_max + 3, y_max + 0.1),
    arrowprops=dict(arrowstyle="->", color='#ff4d4d', lw=1.2),
    fontsize=10,
    fontweight='bold',
    color='#cc0000',
    bbox=dict(boxstyle="round,pad=0.3", fc="#fff5f5", ec="#ffcccc", lw=0.8)
)

# Configurar eixos conforme padrão ABNT
ax.set_title("Sensor IR — Temperatura do PCM", fontsize=14, fontweight='bold', pad=15, color='#111111')
ax.set_xlabel("Tempo (min)", fontsize=11, labelpad=8, color='#222222')
ax.set_ylabel("Temperatura (°C)", fontsize=11, labelpad=8, color='#222222')

# Ajustar escala do eixo X de forma limpa: de 10 em 10 minutos (até os 80 min do teste)
ax.set_xlim(0, 80)
ax.set_xticks(np.arange(0, 81, 10))

# Ajustar escala do eixo Y para aumentar a percepção visual de estabilidade horizontal em ~31°C
ax.set_ylim(28.0, 35.0) 

# Ajustar ticks dos eixos
ax.tick_params(axis='both', which='major', labelsize=10, colors='#333333')

# Grade discreta em cinza claro para manter o padrão clean
ax.grid(True, linestyle='--', alpha=0.6, color='#e0e0e0', linewidth=0.6)

# Remover bordas desnecessárias (topo e direita)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#555555')
ax.spines['bottom'].set_color('#555555')

# Ajustar layout para evitar cortes de texto
plt.tight_layout()

# Salva o arquivo final na mesma pasta onde o script está rodando
output_filename = os.path.join(diretorio_atual, 'grafico_pcm_minutos_final.png')
plt.savefig(output_filename, facecolor=fig.get_facecolor(), edgecolor='none', dpi=300)
plt.close()

print(f"Gráfico gerado com sucesso em minutos e cores idênticas: {output_filename}")