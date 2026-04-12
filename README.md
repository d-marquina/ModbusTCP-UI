# Modbus TCP Control Center

Aplicación de escritorio simple construida con Flet que proporciona una interfaz gráfica para interactuar con dispositivos Modbus TCP. Puede actuar como un servidor Modbus TCP local o como un cliente para conectarse a un servidor remoto.

## Funcionalidades

- **Modo Servidor**: Expone un servidor Modbus TCP local, permitiendo que otros clientes se conecten, lean y escriban en sus registros.
- **Modo Cliente**: Se conecta a un servidor Modbus TCP externo para monitorear y modificar sus registros.
- **Interfaz de Usuario Dual**:
    - **Vista de Tabla**: Muestra un rango configurable de registros `holding` y permite la escritura de nuevos valores.
    - **Dashboard**: Ofrece controles interactivos (slider, switch) que se pueden mapear a registros específicos, y un indicador LED para monitorear un registro.
- **Configuración Dinámica**: Permite cambiar la IP y el puerto tanto para el modo servidor como para el cliente directamente desde la interfaz.
- **Refresco Automático**: La interfaz se actualiza periódicamente para reflejar los cambios en los registros.

## Tecnologías Usadas

- `Python`
- `Flet` para la interfaz de usuario.
- `pyModbusTCP` para la comunicación Modbus.
- `asyncio` para la programación asíncrona.

## Estructura del Proyecto

```text
.
|-- backends/
|   |-- __init__.py
|   |-- client_backend.py
|   |-- modbus_backend.py
|   `-- server_backend.py
|-- models/
|   |-- __init__.py
|   `-- registers.py
|-- ui/
|   |-- __init__.py
|   |-- builders.py
|   |-- dashboard_view.py
|   `-- table_view.py
|-- main.py
`-- README.md
```

## Requisitos

Para ejecutar la aplicación, necesitas instalar las siguientes dependencias:

```bash
pip install flet pyModbusTCP
```

## Ejecución

Para iniciar la aplicación, ejecuta el siguiente comando en la raíz del proyecto:

```bash
python main.py
```

## Cómo Usar

1.  **Elige un modo**:
    *   **Servidor**: Para crear un servidor Modbus local. Introduce la IP y el puerto que desees y haz clic en "Iniciar servidor".
    *   **Cliente**: Para conectarte a un servidor existente. Introduce la IP y el puerto del servidor y haz clic en "Conectar".

2.  **Interactúa con los registros**:
    *   **Vista de Tabla**:
        *   Define el "Offset inicial" y la "Cantidad" de registros que quieres ver.
        *   Haz clic en "Cargar" para leer y mostrar los valores.
        *   Para escribir en un registro, introduce el nuevo valor en el campo correspondiente y presiona Enter.
    *   **Dashboard**:
        *   Usa los menús desplegables para mapear el slider, el switch y el LED a los registros que desees.
        *   Mueve el slider o activa el switch para escribir en los registros mapeados.
        *   El LED cambiará de color para indicar el estado del registro que está monitoreando (1 para encendido, 0 para apagado).

## Mapa de Registros Base

La aplicación viene preconfigurada con 5 `holding registers` (del `40001` al `40005`), pero puedes interactuar con cualquier registro a través de la vista de tabla.

| Registro | Offset | Descripción Sugerida |
|---|---:|---|
| `40001` | `0` | Valor general |
| `40002` | `1` | Velocidad |
| `40003` | `2` | Luz de proceso |
| `40004` | `3` | Pulsador simulado |
| `40005` | `4` | Valor general |

## Mejoras y Próximos Pasos

- [ ] Añadir un archivo `requirements.txt`.
- [ ] Implementar pruebas automatizadas.
- [ ] Mejorar el manejo de errores y la retroalimentación al usuario.
- [ ] Añadir soporte para más tipos de registros Modbus (coils, inputs).
- [ ] Guardar y cargar configuraciones de conexión.
