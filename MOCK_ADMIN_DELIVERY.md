# Mock Subject Admin Users - Delivery Summary

## 📦 Deliverables Overview

Создана полная инфраструктура для административных пользователей существующих субъектов UKNF и Bank Pekao.

---

## ✅ Что Доставлено

### 1. Миграция Базы Данных
**Файл:** `migrations/014_add_mock_subject_admins.sql`

**Создает:**
- ✅ Административная группа для UKNF: `admins_of_UKNF`
- ✅ Административная группа для Bank Pekao: `admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna`
- ✅ Ресурсы: `subject:admin:1` и `subject:admin:2`
- ✅ Пользователи с корректными хешами паролей (sha256_crypt)
- ✅ Связи пользователь-группа (USERS_GROUPS)
- ✅ Права доступа группа-ресурс (RESOURCES_ALLOW_LIST)
- ✅ Связи субъект-ресурс (SUBJECTS.RESOURCE_ID)

**Особенности:**
- 🔄 Полная идемпотентность (можно запускать многократно)
- 🔒 Обернуто в транзакцию (BEGIN/COMMIT)
- 🔍 Динамический lookup ID для корректных связей
- 📝 WHERE NOT EXISTS проверки для предотвращения дубликатов

### 2. Документация
**Файл:** `MOCK_ADMIN_USERS.md`

**Содержит:**
- 📋 Полное описание созданных пользователей
- 🔐 Учетные данные (email/password)
- 📊 Диаграммы цепочек прав доступа
- 🚀 Примеры использования (cURL + Python)
- 🔍 SQL запросы для верификации
- ⚠️ Рекомендации по безопасности
- 🐛 Руководство по устранению неполадок

### 3. Тестовый Скрипт
**Файл:** `test_mock_admin_users.py`

**Проверяет:**
- ✅ Наличие пользователей в базе
- ✅ Наличие групп и корректное членство
- ✅ Наличие ресурсов
- ✅ Правильность прав доступа (RESOURCES_ALLOW_LIST)
- ✅ Связи субъект-ресурс
- ✅ Возможность входа в систему (authentication)
- ✅ Правильность авторизации (authorization)
- ✅ Изоляцию субъектов (UKNF не может получить доступ к Pekao)

---

## 👥 Созданные Пользователи

### UKNF Администратор
```
Email: admin_uknf@example.com
Password: password123
Subject ID: 1
Group: admins_of_UKNF
Resource: subject:admin:1
```

**Права:**
- ✅ Полный административный контроль над субъектом UKNF
- ❌ НЕТ доступа к субъекту Bank Pekao

### Bank Pekao Администратор
```
Email: admin_pekao@example.com
Password: password456
Subject ID: 2
Group: admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna
Resource: subject:admin:2
```

**Права:**
- ✅ Полный административный контроль над субъектом Bank Pekao
- ❌ НЕТ доступа к субъекту UKNF

---

## 🔄 Архитектура Прав Доступа

### Цепочка Прав для UKNF Admin:
```
admin_uknf@example.com (USER)
         ↓
    USER_ID связан с
         ↓
admins_of_UKNF (GROUP)
         ↓
    GROUP_ID имеет разрешение на
         ↓
subject:admin:1 (RESOURCE)
         ↓
    RESOURCE_ID контролирует
         ↓
UKNF Subject (ID: 1)
```

### Цепочка Прав для Bank Pekao Admin:
```
admin_pekao@example.com (USER)
         ↓
    USER_ID связан с
         ↓
admins_of_Bank_Polska_Kasa_Opieki_Spółka_Akcyjna (GROUP)
         ↓
    GROUP_ID имеет разрешение на
         ↓
subject:admin:2 (RESOURCE)
         ↓
    RESOURCE_ID контролирует
         ↓
Bank Pekao Subject (ID: 2)
```

---

## 🚀 Как Использовать

### Шаг 1: Применить Миграцию

**Автоматически (через Docker Compose):**
```bash
cd /Users/kan/Projects/hackyeah/UKNFReportDesk
docker-compose down
docker-compose up -d
```

**Вручную (через psql):**
```bash
psql -U myuser -d mydatabase -f migrations/014_add_mock_subject_admins.sql
```

### Шаг 2: Запустить Тесты

```bash
cd /Users/kan/Projects/hackyeah/UKNFReportDesk
python test_mock_admin_users.py
```

**Ожидаемый результат:**
```
✅ ALL TESTS PASSED!

Mock admin users are working correctly:
  ✅ UKNF admin can login and access UKNF subject
  ✅ Bank Pekao admin can login and access Bank Pekao subject
  ✅ Admins cannot access each other's subjects
  ✅ Permission chains are complete and correct
```

### Шаг 3: Войти как Администратор

**Пример: Вход как UKNF admin**
```bash
curl -X POST http://localhost:8001/authn \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin_uknf@example.com",
    "password": "password123"
  }'
```

**Ответ:**
```json
{
  "session_id": "abc123...",
  "message": "Login successful"
}
```

**Проверка авторизации:**
```bash
curl -X POST http://localhost:8001/authz \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc123...",
    "resource_id": "subject:admin:1"
  }'
```

**Ответ:**
```json
{
  "authorized": true,
  "message": "Access granted (group permission)"
}
```

---

## 🔍 Верификация Установки

### Проверить пользователей в базе:
```sql
SELECT 
    u."ID",
    u."EMAIL",
    u."SUBJECT_ID",
    u."IS_USER_ACTIVE",
    s."NAME_STRUCTURE" as subject_name
FROM "USERS" u
LEFT JOIN "SUBJECTS" s ON u."SUBJECT_ID" = s."ID"
WHERE u."EMAIL" IN ('admin_uknf@example.com', 'admin_pekao@example.com')
ORDER BY u."ID";
```

**Ожидаемый результат:**
```
 ID |          EMAIL           | SUBJECT_ID | IS_USER_ACTIVE |     SUBJECT_NAME     
----+--------------------------+------------+----------------+----------------------
  X | admin_uknf@example.com   |          1 | t              | UKNF
  Y | admin_pekao@example.com  |          2 | t              | Bank Pekao
```

### Проверить полную цепочку прав:
```sql
SELECT 
    u."EMAIL",
    g."GROUP_NAME",
    ral."RESOURCE_ID",
    s."NAME_STRUCTURE"
FROM "USERS" u
JOIN "USERS_GROUPS" ug ON u."ID" = ug."USER_ID"
JOIN "GROUPS" g ON ug."GROUP_ID" = g."ID"
JOIN "RESOURCES_ALLOW_LIST" ral ON g."ID" = ral."GROUP_ID"
JOIN "SUBJECTS" s ON ral."RESOURCE_ID" = s."RESOURCE_ID"
WHERE u."EMAIL" IN ('admin_uknf@example.com', 'admin_pekao@example.com')
ORDER BY u."EMAIL";
```

**Ожидаемый результат:**
```
          EMAIL           |              GROUP_NAME                      | RESOURCE_ID      | NAME_STRUCTURE
--------------------------+----------------------------------------------+------------------+----------------
admin_pekao@example.com   | admins_of_Bank_Polska_Kasa_Opieki_Spółka_... | subject:admin:2  | Bank Pekao
admin_uknf@example.com    | admins_of_UKNF                               | subject:admin:1  | UKNF
```

---

## 🔐 Безопасность

### ⚠️ ВАЖНО: Только для Разработки!

Эти учетные данные предназначены **ТОЛЬКО для разработки и тестирования**:

- ❌ НЕ используйте в production
- ❌ НЕ коммитьте пароли в репозиторий
- ❌ НЕ делитесь этими учетными данными

### Для Production:

1. **Немедленно смените пароли** после развертывания
2. **Используйте сильные пароли:**
   - Минимум 12 символов
   - Смесь прописных, строчных, цифр, символов
   - Не словарные слова
   - Уникальные для каждого аккаунта

3. **Генерация новых хешей:**
   ```python
   from passlib.context import CryptContext
   
   pwd_context = CryptContext(schemes=["sha256_crypt"])
   new_hash = pwd_context.hash("your_strong_password")
   print(new_hash)
   ```

4. **Обновление пароля в БД:**
   ```sql
   UPDATE "USERS"
   SET "PASSWORD_HASH" = '<new_hash>'
   WHERE "EMAIL" = 'admin_uknf@example.com';
   ```

5. **Дополнительная защита:**
   - Внедрите MFA/2FA
   - Используйте временные пароли с принудительным сбросом
   - Включите блокировку после неудачных попыток входа
   - Мониторьте активность администраторов
   - Ротация паролей каждые 90 дней

---

## 📊 Технические Детали

### Хеширование Паролей

**Алгоритм:** `sha256_crypt`  
**Раунды:** 535,000  
**Библиотека:** `passlib` (Python)  
**Совместимость:** ✅ С `auth-service/main.py`

**Формат хеша:**
```
$5$rounds=535000$<salt>$<hash>
```

**Пример:**
```
$5$rounds=535000$gSpPLga29gP012XY$Z853E27e9023fVeZ2dc1a1260xyzABCDEF12345678
```

### Структура Базы Данных

**Затронутые таблицы:**
1. `USERS` - Хранит пользователей
2. `GROUPS` - Хранит группы
3. `USERS_GROUPS` - Связь многие-ко-многим между пользователями и группами
4. `RESOURCES` - Хранит ресурсы (точки контроля доступа)
5. `RESOURCES_ALLOW_LIST` - Хранит разрешения (группа → ресурс)
6. `SUBJECTS` - Хранит субъекты (UKNF, Bank Pekao, etc.)

**Новые связи:**
- `SUBJECTS.RESOURCE_ID` → `RESOURCES.ID` (FK)
- Позволяет каждому субъекту иметь выделенный административный ресурс

---

## 🧪 Тестовое Покрытие

Скрипт `test_mock_admin_users.py` проверяет:

### Database Layer (Слой БД)
- ✅ Существование пользователей
- ✅ Существование групп
- ✅ Членство в группах (USERS_GROUPS)
- ✅ Существование ресурсов
- ✅ Права доступа (RESOURCES_ALLOW_LIST)
- ✅ Связи субъект-ресурс (SUBJECTS.RESOURCE_ID)
- ✅ Целостность цепочки прав

### Service Layer (Слой Сервисов)
- ✅ Аутентификация (логин)
- ✅ Проверка session_id
- ✅ Авторизация для собственного субъекта
- ✅ Отказ в доступе к чужому субъекту
- ✅ Корректные сообщения об ошибках

### End-to-End (Полный цикл)
- ✅ Логин → Получение сессии → Проверка прав → Выдача решения
- ✅ Multi-tenancy изоляция
- ✅ Permission inheritance через группы

---

## 📁 Структура Файлов

```
/Users/kan/Projects/hackyeah/UKNFReportDesk/
├── migrations/
│   └── 014_add_mock_subject_admins.sql     # Миграция БД
├── MOCK_ADMIN_USERS.md                      # Подробная документация
├── MOCK_ADMIN_DELIVERY.md                   # Этот файл - сводка доставки
└── test_mock_admin_users.py                 # Тестовый скрипт (executable)
```

---

## 🔗 Связанная Документация

1. **Мультитенантная безопасность:**  
   `MULTI_TENANT_SECURITY.md` - Общая архитектура multi-tenant security

2. **Регистрация пользователей с субъектами:**  
   `USER_SUBJECT_REGISTRATION.md` - Процесс автоматического создания субъектов

3. **Auth Service README:**  
   `auth-service/README.md` - Документация сервиса аутентификации

4. **Миграции:**  
   - `012_add_subjects_history_trigger.sql` - Аудит trail для SUBJECTS
   - `013_add_subject_resource_link.sql` - Добавление RESOURCE_ID к SUBJECTS
   - `014_add_mock_subject_admins.sql` - Этот скрипт

---

## 📝 Примеры Использования

### Python: Полный цикл

```python
import requests

AUTH_URL = "http://localhost:8001"

# Логин
response = requests.post(f"{AUTH_URL}/authn", json={
    "email": "admin_uknf@example.com",
    "password": "password123"
})

session_id = response.json()["session_id"]
print(f"Logged in with session: {session_id}")

# Проверка доступа к UKNF subject
response = requests.post(f"{AUTH_URL}/authz", json={
    "session_id": session_id,
    "resource_id": "subject:admin:1"
})

if response.json()["authorized"]:
    print("✅ Access granted to UKNF subject")
else:
    print("❌ Access denied")

# Проверка доступа к Bank Pekao subject (должна быть отказана)
response = requests.post(f"{AUTH_URL}/authz", json={
    "session_id": session_id,
    "resource_id": "subject:admin:2"
})

if not response.json()["authorized"]:
    print("✅ Correctly denied access to Bank Pekao subject")
```

### cURL: Быстрый тест

```bash
#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Логин как UKNF admin
echo "Logging in as UKNF admin..."
SESSION=$(curl -s -X POST http://localhost:8001/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin_uknf@example.com", "password": "password123"}' \
  | jq -r '.session_id')

echo "Session ID: $SESSION"

# Проверка доступа
echo -e "\nTesting access to UKNF subject..."
AUTHORIZED=$(curl -s -X POST http://localhost:8001/authz \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION\", \"resource_id\": \"subject:admin:1\"}" \
  | jq -r '.authorized')

if [ "$AUTHORIZED" == "true" ]; then
  echo -e "${GREEN}✅ Access granted${NC}"
else
  echo -e "${RED}❌ Access denied${NC}"
fi
```

---

## 🎯 Итоги

### Что Работает
✅ Администраторы UKNF и Bank Pekao могут входить в систему  
✅ Каждый администратор может управлять только своим субъектом  
✅ Multi-tenant изоляция работает корректно  
✅ Все права доступа настроены правильно  
✅ Миграция идемпотентна и безопасна  
✅ Полное тестовое покрытие  

### Следующие Шаги (Рекомендации)

1. **Для Development/Testing:**
   - ✅ Используйте эти учетные данные как есть
   - ✅ Запускайте тесты для проверки функциональности
   - ✅ Тестируйте API endpoints с этими пользователями

2. **Перед Production:**
   - 🔒 Смените все пароли на сильные
   - 🔒 Включите MFA/2FA
   - 🔒 Настройте мониторинг активности админов
   - 🔒 Проведите security audit
   - 🔒 Внедрите password rotation policy

3. **Для Будущих Субъектов:**
   - 📝 Используйте `/register` endpoint для автоматического создания
   - 📝 Или создайте аналогичные SQL блоки для других субъектов
   - 📝 Следуйте той же структуре: Group → Resource → Permission → User

---

## 📞 Поддержка

При возникновении проблем:

1. **Проверьте сервисы:**
   ```bash
   docker-compose ps
   docker-compose logs auth-service
   ```

2. **Проверьте БД:**
   ```bash
   docker-compose exec postgres psql -U myuser -d mydatabase
   ```

3. **Запустите тесты:**
   ```bash
   python test_mock_admin_users.py
   ```

4. **Проверьте логи:**
   ```bash
   docker-compose logs -f auth-service
   ```

---

**Статус:** ✅ Готово к Использованию (Development/Testing)  
**Версия:** 1.0.0  
**Дата:** 2025-10-05  
**Автор:** Kan (через AI Assistant)

**⚠️ ВАЖНО: Это mock-данные для разработки. Смените пароли перед production!**

