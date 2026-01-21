# Doc-Builder (Gostdown Wrapper)

Автоматизированная система сборки отчетов по ГОСТ 7.32 на базе [Gostdown](https://github.com/L1CH7/gostdown).

## Структура
- `src/`: Логика сборки (Python).
- `templates/`: Централизованные шаблоны (`reference.docx`).
- `input/`: Папки с проектами отчетов.
- `gostdown/`: Подмодуль с оригинальными скриптами сборки (PowerShell).
- `Makefile`: Интерфейс запуска (`make all`).
- `config.json`: Глобальная конфигурация.

## Установка
1. Клонирование:
   ```bash
   git clone --recursive https://github.com/L1CH7/doc-builder.git
   ```
2. Настройка `config.json` (см. `Guides.md`).

## Использование
```bash
make output/ProjectName.docx
```
Подробнее в [Guides.md](Guides.md).
