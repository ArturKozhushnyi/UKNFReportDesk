# Краткое руководство по тестированию API

## Быстрые тесты новых endpoint'ов

### 1. Тест endpoint /get-user-id-by-session

```bash
# Войти в систему и сохранить session_id
SESSION_ID=$(curl -s -X POST http://localhost:3000/auth/authn \
  -H "Content-Type: application/json" \
  -d '{"email": "admin_uknf@example.com", "password": "password123"}' | jq -r '.session_id')

# Получить user_id по session_id
curl -s "http://localhost:3000/auth/get-user-id-by-session/$SESSION_ID" | jq .
```

**Ожидаемый результат:**
```json
{
  "user_id": 2,
  "session_id": "..."
}
```

---

### 2. Тест endpoint /me

```bash
# Получить полную информацию о пользователе
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

### 3. Полный тест для всех пользователей

```bash
#!/bin/bash

echo "==================================="
echo "Тестирование всех пользователей"
echo "==================================="

# Массив пользователей для тестирования
declare -a users=(
  "admin@example.com:admin:Default Administrator"
  "admin_uknf@example.com:password123:UKNF Administrator"
  "admin_pekao@example.com:password456:Bank Pekao Administrator"
)

# Тестирование каждого пользователя
for user_info in "${users[@]}"; do
  IFS=':' read -r email password name <<< "$user_info"
  
  echo ""
  echo "-----------------------------------"
  echo "Тестирование: $name"
  echo "Email: $email"
  echo "-----------------------------------"
  
  # Логин
  echo "1. Выполнение входа..."
  SESSION_ID=$(curl -s -X POST http://localhost:3000/auth/authn \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$email\", \"password\": \"$password\"}" | jq -r '.session_id')
  
  if [ -z "$SESSION_ID" ] || [ "$SESSION_ID" = "null" ]; then
    echo "❌ Ошибка входа!"
    continue
  fi
  
  echo "✅ Session ID: $SESSION_ID"
  
  # Получение user_id
  echo ""
  echo "2. Получение user_id..."
  USER_DATA=$(curl -s "http://localhost:3000/auth/get-user-id-by-session/$SESSION_ID")
  echo "$USER_DATA" | jq .
  
  # Получение полной информации
  echo ""
  echo "3. Получение полной информации о пользователе..."
  USER_INFO=$(curl -s "http://localhost:3000/auth/me?session_id=$SESSION_ID")
  echo "$USER_INFO" | jq .
  
  echo ""
done

echo ""
echo "==================================="
echo "Тестирование завершено!"
echo "==================================="
```

Сохраните этот скрипт как `test_all_users.sh` и запустите:
```bash
chmod +x test_all_users.sh
./test_all_users.sh
```

---

## Учетные записи для тестирования

| Email | Пароль | Имя | Субъект |
|-------|--------|-----|---------|
| admin@example.com | admin | Default Administrator | Нет |
| admin_uknf@example.com | password123 | UKNF Administrator | Urząd Komisji Nadzoru Finansowego |
| admin_pekao@example.com | password456 | Bank Pekao Administrator | Bank Polska Kasa Opieki Spółka Akcyjna |

---

## Проверка через браузер

1. Откройте http://localhost:3000
2. Войдите с учетными данными: `admin_uknf@example.com` / `password123`
3. В правом верхнем углу должно отображаться:
   - **Имя**: UKNF Administrator
   - **Субъект**: Urząd Komisji Nadzoru Finansowego
   - **Роль**: administrator

---

## Проверка через DevTools

1. Откройте DevTools (F12)
2. Перейдите на вкладку Console
3. Выполните:
   ```javascript
   // Получить session_id из localStorage
   const sessionId = localStorage.getItem('sessionId');
   console.log('Session ID:', sessionId);
   
   // Вызвать API /me
   fetch(`/auth/me?session_id=${sessionId}`)
     .then(res => res.json())
     .then(data => console.log('User info:', data));
   ```

---

## Устранение неполадок

### Проблема: "Session not found or expired"
**Решение**: Войдите заново, session мог истечь.

### Проблема: "404 Not Found"
**Решение**: Убедитесь, что auth-service запущен:
```bash
docker compose ps auth-service
docker logs auth-service --tail 20
```

### Проблема: Frontend не показывает имя пользователя
**Решение**: 
1. Очистите localStorage: `localStorage.clear()`
2. Перезагрузите страницу
3. Войдите заново

### Проблема: "Connection refused" в Nginx
**Решение**: Перезапустите frontend:
```bash
docker compose restart frontend
```

---

## Полезные команды

```bash
# Просмотр логов auth-service
docker logs auth-service -f

# Просмотр логов frontend
docker logs frontend -f

# Перезапуск всех сервисов
docker compose restart

# Проверка статуса всех сервисов
docker compose ps

# Подключение к Redis для проверки сессий
docker exec -it local_redis redis-cli
> KEYS session:*
> GET session:{session_id}

# Подключение к PostgreSQL для проверки данных
docker exec -it local_postgres psql -U postgres -d uknf_db
> SELECT * FROM "USERS";
> SELECT * FROM "SUBJECTS";
```

