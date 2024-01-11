# CryptoPriceAnalysis
Автоматизированный инструмент для обнаружения и уведомления о значительных движениях цен Ethereum, исключающий внешние влияние BTC.

## Особенности
- Анализ временных рядов цен на ETH и BTC.
- Две стратегии анализа:
  - Линейная регрессия.
  - Случайный лес.
- Асинхронное выполнение анализа и обновление данных.
- Логирование результатов анализа.



## Установка
Склонируйте репозиторий проекта:
```bash
git clone https://github.com/exetch/CryptoPriceAnalysis.git
```
Установите зависимости:
```bash
pip install -r requirements.txt
```
Создайте файл .env с вашими данными для подключения к БД Postgres
```makefile
DB_USER=your_DB_USER
DB_PASSWORD=your_DB_PASSWORD
DB_HOST=localhost
DB_NAME=your_DB_NAME
```
## Запуск
Запустите программу:
```bash
python main.py
```