# 🚀 Быстрый старт - UKNF Report Desk

## Вход в систему

### Откройте страницу входа
👉 http://localhost:3000/login

---

## 🎯 Демонстрационные учетные записи

На странице входа теперь есть **3 готовые демо-учетные записи** с кнопкой **"Click to auto-fill"**.

### 1️⃣ UKNF Administrator (РЕКОМЕНДУЕТСЯ)
```
Email:    admin_uknf@example.com
Password: password123
Роль:     Administrator
Субъект:  Urząd Komisji Nadzoru Finansowego
```
**Использование**: Полный доступ к административным функциям UKNF.

---

### 2️⃣ Bank Pekao Administrator
```
Email:    admin_pekao@example.com
Password: password456
Роль:     Administrator
Субъект:  Bank Polska Kasa Opieki Spółka Akcyjna
```
**Использование**: Администратор банка с доступом к своему субъекту.

---

### 3️⃣ System Administrator
```
Email:    admin@example.com
Password: admin
Роль:     Administrator
Субъект:  Нет
```
**Использование**: Системный администратор без привязки к субъекту.

---

## 📋 Как войти

### Способ 1: Автозаполнение (быстро)
1. Откройте http://localhost:3000/login
2. **Кликните** на одну из синих карточек с учетными записями
3. Поля автоматически заполнятся
4. Нажмите кнопку **"Login"**

### Способ 2: Ручной ввод
1. Скопируйте email и пароль из списка выше
2. Введите в форму входа
3. Нажмите **"Login"**

---

## ✅ Что вы увидите после входа

После успешного входа как **admin_uknf@example.com**:

**В правом верхнем углу отображается:**
```
UKNF Administrator
Urząd Komisji Nadzoru Finansowego  ← Название субъекта
administrator                       ← Роль
```

**Доступные разделы:**
- 🏠 Dashboard
- 💬 Communication Module (Reports, Cases, Messages, etc.)
- 🔒 Authentication & Authorization
- ⚙️ Administrative Module (User Management, Roles, etc.)

---

## 🧪 Тестирование API

### Получить информацию о текущем пользователе

```bash
# 1. Войти и получить session_id
SESSION_ID=$(curl -s -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin_uknf@example.com", "password": "password123"}' | jq -r '.session_id')

# 2. Получить информацию о пользователе
curl -s "http://localhost:3000/auth/me?session_id=$SESSION_ID" | jq .
```

**Ожидаемый результат:**
```json
{
  "user_id": 2,
  "email": "admin_uknf@example.com",
  "firstName": "UKNF",
  "lastName": "Administrator",
  "phone": null,
  "isActive": true,
  "subjectId": 1,
  "subjectName": "Urząd Komisji Nadzoru Finansowego",
  "uknfId": null
}
```

---

## 📚 Документация

### Основные документы
- 📄 **NEW_FEATURES_SUMMARY.md** - Полное описание новых функций
- 📄 **API_TESTING_GUIDE.md** - Руководство по тестированию API
- 📄 **LOGIN_PAGE_UPDATE.md** - Подробности об обновлении страницы входа
- 📄 **LOGIN_CREDENTIALS.md** - Все учетные данные для входа

### Архитектурная документация
- 📄 **MICROSERVICES_ARCHITECTURE.md** - Архитектура микросервисов
- 📄 **CHAT_SYSTEM.md** - Система чатов
- 📄 **USER_SUBJECT_REGISTRATION.md** - Регистрация пользователей

---

## 🔧 Управление сервисами

### Проверить статус всех сервисов
```bash
docker compose ps
```

### Перезапустить конкретный сервис
```bash
docker compose restart auth-service    # Сервис аутентификации
docker compose restart frontend        # Фронтенд
```

### Просмотреть логи
```bash
docker logs auth-service -f     # Логи auth-service
docker logs frontend -f         # Логи frontend
```

### Остановить все сервисы
```bash
docker compose down
```

### Запустить все сервисы заново
```bash
docker compose up -d
```

---

## 🎨 Новые возможности страницы входа

### Что нового?
✅ **Интерактивные карточки** с демо-учетными записями  
✅ **Автозаполнение формы** одним кликом  
✅ **Визуальная индикация** роли и организации  
✅ **Hover-эффекты** для лучшего UX  
✅ **Информативные описания** каждой учетной записи  

### Преимущества
- 🚀 **Быстрое тестирование** - не нужно запоминать пароли
- 👀 **Прозрачность** - сразу видно доступные учетные записи
- ✨ **Красивый UI** - современный дизайн
- 📱 **Адаптивность** - работает на всех устройствах

---

## 🐛 Устранение неполадок

### Проблема: Не могу войти
**Решение**: Убедитесь, что используете правильные учетные данные из списка выше.

### Проблема: Страница не загружается
**Решение**: 
```bash
docker compose restart frontend
```

### Проблема: "Session expired"
**Решение**: Войдите заново - сессии истекают через 24 часа.

### Проблема: Frontend показывает ошибку 502
**Решение**: 
```bash
docker compose restart auth-service frontend
```

---

## 📞 Дополнительная информация

### Порты сервисов
- Frontend: http://localhost:3000
- Auth Service: http://localhost:8001
- Administration Service: http://localhost:8000
- Communication Service: http://localhost:8002

### База данных
- PostgreSQL: localhost:5432
- Database: uknf_db
- User: postgres
- Password: postgres

### Redis
- Host: localhost:6379
- Использование: Хранилище сессий

---

## 🎉 Готово!

Система полностью настроена и готова к использованию.

**Начните с входа как UKNF Administrator** для лучшего демонстрационного опыта:
- Email: `admin_uknf@example.com`
- Password: `password123`

Приятной работы! 🚀
