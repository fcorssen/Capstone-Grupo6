## Cálculo y Visualización de Curvas de Rendimiento de Bombas

### Importación de Módulos
```python
import numpy as np
import matplotlib.pyplot as plt
# Bomba a 1750 RPM con impulsor de 6.5"
Q_1750_65 = np.array([0, 50, 100, 150, 200, 250])  # Caudal en GPM
H_1750_65 = np.array([44, 42, 38, 32, 24, 14])  # Altura en pies

# Bomba a 3500 RPM con impulsor de 6"
Q_3500_60 = np.array([0, 50, 100, 150, 200, 250])  # Caudal en GPM
H_3500_60 = np.array([68, 65, 60, 53, 44, 34])  # Altura en pies
# graficar
plt.figure(figsize=(12, 8))
plt.plot(Q_1750_65, H_1750_65, 'bo-', label='Bomba Individual a 1750 RPM, 6.5" Impulsor')
plt.plot(Q_3500_60, H_3500_60, 'ro-', label='Bomba Individual a 3500 RPM, 6" Impulsor')
plt.plot(Q_1750_65, H_1750_65 + H_3500_60[:len(H_1750_65)], 'mo-', label='Curva de Rendimiento Compuesto')
plt.title('Curvas de Rendimiento de Bombas Combinadas')
plt.xlabel('Caudal (GPM)')
plt.ylabel('Altura Total (pies)')
plt.legend()
plt.grid(True)
plt.show()
