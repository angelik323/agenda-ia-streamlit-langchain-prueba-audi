# 📅 Agenda Audifarma - Asistente con IA

Este proyecto es un asistente de gestión de agendas potenciado por **LangChain** y **OpenAI**, diseñado específicamente para **Audifarma**. Permite gestionar eventos en un archivo Excel (`agenda_audi.xlsx`) utilizando lenguaje natural.

## 🚀 Características Principales

- **Gestión Natural**: Crea, consulta y elimina eventos hablando con la IA.
- **Inteligencia Temporal**: El sistema entiende expresiones como "mañana", "pasado mañana", "el próximo lunes" o "el próximo semestre" y las convierte a fechas exactas.
- **Selección de Modelos**: Permite elegir entre diferentes modelos de la serie GPT-5. Se recomienda **GPT-5 o superiores** para mayor precisión en cálculos temporales.
- **Arquitectura Hexagonal**: Estructura profesional basada en Puertos y Adaptadores para máxima mantenibilidad y desacoplamiento.
- **Interfaz Premium**: Construida con **Streamlit**, optimizada para una experiencia de usuario fluida.

## 🏗️ Arquitectura del Proyecto

El proyecto implementa una **Arquitectura Hexagonal (Ports & Adapters)**. Esto permite que el "corazón" de la aplicación (la lógica de la agenda) sea independiente de la tecnología utilizada para guardar los datos (Excel) o de la IA utilizada (OpenAI/LangChain).

```mermaid
graph TD
    subgraph UI ["Capa de Interfaz (UI)"]
        A[Streamlit App]
    end
    
    subgraph App ["Capa de Aplicación"]
        B[AgendaService]
    end
    
    subgraph Domain ["Capa de Dominio (Core)"]
        C[Event Entity]
        D[Ports/Interfaces]
    end
    
    subgraph Infra ["Capa de Infraestructura (Adapters)"]
        E[ExcelRepositoryAdapter]
        F[LangChainAgentAdapter]
    end

    A --> B
    B --> D
    D <|-- E
    D <|-- F
    E --> G[(agenda_audi.xlsx)]
    F --> H[OpenAI API]
```

### Rol de cada Componente:
1.  **Dominio (`domain/`)**: Contiene las reglas de negocio puras (qué es un evento) y los **Puertos** (contratos/interfaces) que definen qué acciones pueden realizar los componentes externos.
2.  **Aplicación (`application/`)**: Contiene el `AgendaService`, que actúa como orquestador. Recibe peticiones de la UI y coordina los puertos de datos e IA para cumplir la tarea.
3.  **Infraestructura (`infrastructure/`)**: Contiene los **Adaptadores**. Son las implementaciones reales que "hablan" con tecnologías externas como archivos Excel o la API de OpenAI.
4.  **UI (`ui/`)**: La puerta de entrada para el usuario. En este caso, una aplicación Streamlit que delega toda la lógica al Servicio de Aplicación.

## 📂 Estructura de Directorios

```text
agenda_module/
├── domain/                # Core: Entidades y Puertos (Interfaces)
│   ├── entities.py        # Modelo de datos 'Event'
│   └── ports/             # Contratos abstractos (Interfaces)
├── application/           # Lógica de los casos de uso (Servicio)
├── infrastructure/        # Adaptadores (Excel y Agente de IA)
│   └── adapters/          # Implementaciones técnicas
├── ui/                    # Capa de Interfaz (Streamlit)
├── prompts/               # Instrucciones del sistema en Markdown
├── tools.py               # Definición técnica de herramientas
└── config.py              # Configuración (archivos, modelos, logs)
```

## 🧠 ¿Cómo sabe la IA qué acción realizar?

El funcionamiento del asistente se basa en tres pilares:

1.  **Semántica (Descriptions)**: Cada herramienta en `tools.py` tiene una descripción que el LLM lee para saber si debe "Agregar", "Listar" o "Eliminar".
2.  **Estructura (Schemas)**: Se definen esquemas de datos (Pydantic) que le indican a la IA exactamente qué información extraer del texto del usuario.
3.  **Manual de Procedimientos (System Prompt)**: Las instrucciones en `system_prompt.md` guían el comportamiento del asistente para que sea profesional y verifique la información antes de actuar.

## 🛠️ Configuración y Ejecución

### Requisitos
- Python 3.9+ o **Docker** (Recomendado)
- [Poetry](https://python-poetry.org/) (Para ejecución local)

### 🐳 Ejecución con Docker (Recomendado)
La forma más robusta de ejecutar el proyecto es usando Docker Compose, lo que garantiza persistencia y aislamiento:

1.  **Construir y Correr**:
    ```bash
    docker-compose up -d --build
    ```
2.  **Acceso**: La aplicación estará disponible en `http://localhost:8501`.
3.  **Persistencia**: El archivo `agenda_audi.xlsx` se sincroniza como un volumen, manteniendo tus datos seguros.
4.  **Desarrollo**: El código local está montado en el contenedor; cualquier cambio en los archivos Python activará el **Hot Reload** automáticamente.

### 🐍 Ejecución Local (Alternativa)
1.  **Instalación**:
    ```bash
    poetry install
    ```
2.  **Ejecución**:
    ```bash
    poetry run streamlit run agenda_module/app.py
    ```

## 📏 Reglas de Negocio
- **Límite Temporal**: El asistente solo permite agendar eventos hasta **1 año** en el futuro.
- **Recurrencia**: Soporta agendamientos periódicos (ej: "todos los lunes del mes"). La IA calcula las fechas y realiza múltiples acciones automáticamente.
- **Formatos**: Acepta lenguaje natural o formato `AAAA-MM-DD`.

## 🔐 Seguridad y Logs
- **Logs**: Todos los eventos técnicos se registran en `app.log`.
- **Secretos**: Las claves de API se manejan vía `.streamlit/secrets.toml` (ver `secrets.toml.example`).

---
*Este proyecto utiliza el [Apache License 2.0](LICENSE).*
