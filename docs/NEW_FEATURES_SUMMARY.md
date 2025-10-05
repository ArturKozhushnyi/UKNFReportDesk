# Новые функции UKNF Report Desk

## Обзор

В приложение UKNF Report Desk были добавлены несколько новых функций для улучшения управления пользователями и отображения информации о пользователях. Эти изменения включают как изменения бэкенда (auth-service), так и изменения фронтенда (React).

---

## 1. Изменения бэкенда (auth-service)

### 1.1. Новый endpoint: GET /get-user-id-by-session/{session_id}

**Назначение**: Получение ID пользователя по ID сессии.

**Путь**: `GET /auth/get-user-id-by-session/{session_id}`

**Параметры**:
- `session_id` (path parameter) - ID сессии, полученный при входе

**Ответ**:
```json
{
  "user_id": 2,
  "session_id": "97f42ead-df0e-4c70-8e74-1a4def9d3dc2"
}
```

**Примеры использования**:
```bash
# Прямой доступ к auth-service
curl http://localhost:8001/get-user-id-by-session/{session_id}

# Через frontend proxy
curl http://localhost:3000/auth/get-user-id-by-session/{session_id}
```

**Возможные ошибки**:
- `404 Not Found` - сессия не найдена или истекла
- `500 Internal Server Error` - ошибка сервера

---

### 1.2. Улучшенный endpoint: GET /me

**Назначение**: Получение полной информации о текущем пользователе, включая имя, фамилию и название субъекта.

**Путь**: `GET /auth/me`

**Параметры**:
- `session_id` (query parameter) - ID сессии

**Ответ**:
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

**Поля ответа**:
- `user_id` - уникальный ID пользователя
- `email` - email пользователя
- `firstName` - имя пользователя (из поля `USER_NAME`)
- `lastName` - фамилия пользователя (из поля `USER_LASTNAME`)
- `phone` - номер телефона (может быть null)
- `isActive` - активен ли пользователь
- `subjectId` - ID субъекта, к которому принадлежит пользователь (может быть null)
- `subjectName` - название субъекта (из поля `NAME_STRUCTURE` таблицы `SUBJECTS`, может быть null)
- `uknfId` - UKNF ID пользователя (может быть null)

**Примеры использования**:
```bash
# Прямой доступ к auth-service
curl "http://localhost:8001/me?session_id={session_id}"

# Через frontend proxy
curl "http://localhost:3000/auth/me?session_id={session_id}"
```

**Возможные ошибки**:
- `401 Unauthorized` - session_id не предоставлен или недействителен
- `404 Not Found` - пользователь не найден
- `500 Internal Server Error` - ошибка сервера

---

## 2. Изменения фронтенда

### 2.1. Обновленный API Client (frontend/src/services/api.ts)

Добавлены два новых метода в класс `AuthAPI`:

#### getMe(sessionId: string)
```typescript
async getMe(sessionId: string) {
  return this.get<{
    user_id: number;
    email: string;
    firstName: string | null;
    lastName: string | null;
    phone: string | null;
    isActive: boolean;
    subjectId: number | null;
    subjectName: string | null;
    uknfId: string | null;
  }>('/me', { session_id: sessionId });
}
```

#### getUserIdBySession(sessionId: string)
```typescript
async getUserIdBySession(sessionId: string) {
  return this.get<{ user_id: number; session_id: string }>(
    `/get-user-id-by-session/${sessionId}`
  );
}
```

---

### 2.2. Обновленный Zustand Store (frontend/src/stores/authStore.ts)

#### Новые поля в AuthState:
```typescript
interface AuthState {
  // ... существующие поля ...
  firstName: string | null;
  lastName: string | null;
  subjectName: string | null;
  // ... действия ...
}
```

#### Улучшенная функция login:
Теперь после успешной аутентификации автоматически вызывается endpoint `/me` для получения полной информации о пользователе:

```typescript
login: async (email: string, password: string) => {
  // 1. Выполнить вход
  const response = await authAPI.login(email, password);
  
  // 2. Получить детали пользователя
  const userDetails = await authAPI.getMe(response.session_id);
  
  // 3. Сохранить в store
  set({
    user,
    sessionId: response.session_id,
    role,
    isAuthenticated: true,
    firstName: userDetails.firstName,
    lastName: userDetails.lastName,
    subjectName: userDetails.subjectName,
  });
}
```

#### Персистентность:
Новые поля (`firstName`, `lastName`, `subjectName`) автоматически сохраняются в localStorage и восстанавливаются при перезагрузке страницы.

---

### 2.3. Обновленный MainLayout (frontend/src/layouts/MainLayout.tsx)

#### Отображение информации о пользователе:
В шапке приложения теперь отображается:
1. **Полное имя пользователя** - имя и фамилия из полей `firstName` и `lastName`
2. **Название субъекта** - если пользователь принадлежит субъекту
3. **Роль пользователя** - администратор, внутренний пользователь и т.д.

**Пример отображения**:
```
┌─────────────────────────────────────┐
│ UKNF Administrator                  │
│ Urząd Komisji Nadzoru Finansowego   │  ← Название субъекта
│ administrator                        │  ← Роль
└─────────────────────────────────────┘
```

**Код компонента**:
```typescript
<div className="text-right">
  <p className="text-sm font-medium text-gray-900">
    {firstName && lastName 
      ? `${firstName} ${lastName}` 
      : user?.USER_NAME && user?.USER_LASTNAME
      ? `${user.USER_NAME} ${user.USER_LASTNAME}`
      : user?.EMAIL || 'User'}
  </p>
  {subjectName && (
    <p className="text-xs text-gray-600 mt-0.5">
      {subjectName}
    </p>
  )}
  <p className="text-xs text-gray-500 capitalize mt-0.5">
    {role?.replace('_', ' ')}
  </p>
</div>
```

---

## 3. Тестирование

### 3.1. Тестовые учетные записи

#### 1. Администратор по умолчанию (без субъекта):
- **Email**: `admin@example.com`
- **Пароль**: `admin`
- **Результат /me**:
  ```json
  {
    "firstName": "Default",
    "lastName": "Administrator",
    "subjectId": null,
    "subjectName": null
  }
  ```

#### 2. Администратор UKNF (с субъектом):
- **Email**: `admin_uknf@example.com`
- **Пароль**: `password123`
- **Результат /me**:
  ```json
  {
    "firstName": "UKNF",
    "lastName": "Administrator",
    "subjectId": 1,
    "subjectName": "Urząd Komisji Nadzoru Finansowego"
  }
  ```

#### 3. Администратор Bank Pekao (с субъектом):
- **Email**: `admin_pekao@example.com`
- **Пароль**: `password456`
- **Результат /me**:
  ```json
  {
    "firstName": "Bank Pekao",
    "lastName": "Administrator",
    "subjectId": 2,
    "subjectName": "Bank Polska Kasa Opieki Spółka Akcyjna"
  }
  ```

---

### 3.2. Сценарии тестирования

#### Тест 1: Получение user_id по session_id
```bash
# Шаг 1: Войти в систему
SESSION_ID=$(curl -s -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin_uknf@example.com", "password": "password123"}' | jq -r '.session_id')

# Шаг 2: Получить user_id
curl "http://localhost:3000/auth/get-user-id-by-session/$SESSION_ID" | jq .
```

**Ожидаемый результат**:
```json
{
  "user_id": 2,
  "session_id": "..."
}
```

#### Тест 2: Получение полной информации о пользователе
```bash
# Получить информацию о текущем пользователе
curl "http://localhost:3000/auth/me?session_id=$SESSION_ID" | jq .
```

**Ожидаемый результат**:
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

#### Тест 3: Проверка отображения в UI
1. Войдите на сайт `http://localhost:3000`
2. Используйте учетные данные: `admin_uknf@example.com` / `password123`
3. После успешного входа в правом верхнем углу должно отображаться:
   - **Имя**: "UKNF Administrator"
   - **Субъект**: "Urząd Komisji Nadzoru Finansowego"
   - **Роль**: "administrator"

---

## 4. Технические детали

### 4.1. Архитектурные изменения

1. **Backend (auth-service/main.py)**:
   - Добавлены два новых endpoint'а
   - Endpoint `/me` выполняет JOIN между таблицами `USERS` и `SUBJECTS`
   - Используется Redis для хранения сессий
   - Используется PostgreSQL для хранения данных пользователей

2. **Frontend (React/TypeScript)**:
   - Обновлен API client с типизированными методами
   - Zustand store расширен новыми полями
   - MainLayout обновлен для отображения дополнительной информации
   - Все изменения полностью типизированы с TypeScript

### 4.2. Схема взаимодействия

```
┌─────────────┐      1. Login      ┌──────────────┐
│   Browser   │ ──────────────────> │ auth-service │
└─────────────┘                     └──────────────┘
       │                                    │
       │         2. Return session_id       │
       │ <──────────────────────────────────┘
       │
       │            3. Call /me
       │ ──────────────────────────────────>
       │                                    │
       │                             ┌──────▼──────┐
       │                             │   Redis     │
       │                             │  (session)  │
       │                             └──────┬──────┘
       │                                    │
       │                             ┌──────▼──────┐
       │                             │ PostgreSQL  │
       │                             │ (users +    │
       │                             │  subjects)  │
       │                             └──────┬──────┘
       │                                    │
       │    4. Return user details          │
       │ <──────────────────────────────────┘
       │
       │    5. Update store & UI
       └──────────────────────────────>
```

---

## 5. Файлы изменений

### Backend:
- ✅ `auth-service/main.py` - добавлены новые endpoints

### Frontend:
- ✅ `frontend/src/services/api.ts` - добавлены новые API методы
- ✅ `frontend/src/stores/authStore.ts` - обновлен store с новыми полями
- ✅ `frontend/src/layouts/MainLayout.tsx` - обновлен UI для отображения информации

---

## 6. Статус реализации

| Функция | Backend | Frontend | Тестирование | Статус |
|---------|---------|----------|--------------|--------|
| GET /get-user-id-by-session | ✅ | ✅ | ✅ | Готово |
| GET /me (enhanced) | ✅ | ✅ | ✅ | Готово |
| Обновленный authStore | N/A | ✅ | ✅ | Готово |
| Отображение в UI | N/A | ✅ | ✅ | Готово |

---

## 7. Дальнейшие улучшения (опционально)

1. **Добавить фото профиля пользователя**
   - Расширить endpoint `/me` для возврата URL фото
   - Обновить UI для отображения аватара

2. **Добавить информацию о правах доступа**
   - Расширить endpoint `/me` для возврата групп и разрешений
   - Использовать для детального контроля доступа на фронтенде

3. **Кэширование данных пользователя**
   - Реализовать TTL кэш для данных пользователя
   - Минимизировать количество запросов к базе данных

4. **Добавить webhook для обновления данных в реальном времени**
   - Использовать WebSocket для push-уведомлений
   - Автоматически обновлять данные пользователя при изменениях

---

## 8. Заключение

Все запрошенные функции успешно реализованы и протестированы:

✅ **Backend**: Новый endpoint `/get-user-id-by-session/{session_id}` работает корректно  
✅ **Backend**: Улучшенный endpoint `/me` возвращает firstName, lastName и subjectName  
✅ **Frontend**: Zustand store обновлен с новыми полями  
✅ **Frontend**: Login автоматически вызывает `/me` и сохраняет данные  
✅ **Frontend**: MainLayout отображает полное имя пользователя и название субъекта  

Система готова к использованию! 🎉

