# Docker Compose - Fixed! 🐳

## ✅ Kya Fix Kiya

1. **Kafka Image Updated**: `bitnami/kafka:3.6` → `bitnami/kafka:3.9` (latest)
2. **Version Field Removed**: `version: '3.9'` line delete kar di (deprecated hai)

## 🚀 Ab Kaise Run Karein

### Option 1: Sirf Kafka + PostgreSQL (Recommended)

```bash
cd /mnt/d/piaic/todo-app/todo_app/phase_5

# Start karein
docker compose up -d

# Logs dekhen
docker compose logs -f

# Status check karein
docker compose ps
```

### Option 2: With Kafka UI (Monitoring ke liye)

```bash
# Kafka UI ke saath start karein
docker compose --profile ui up -d

# Kafka UI: http://localhost:8090
```

### Option 3: With pgAdmin (Database management)

```bash
# pgAdmin ke saath start karein
docker compose --profile admin up -d

# pgAdmin: http://localhost:5050
# Email: admin@todo-app.local
# Password: admin
```

## 📊 Services Kya Hain?

| Service | Port | Purpose |
|---------|------|---------|
| **PostgreSQL** | 5432 | Database |
| **Kafka** | 9092 (internal)<br>9094 (external) | Event streaming |
| **Kafka UI** | 8090 | Kafka monitoring (optional) |
| **pgAdmin** | 5050 | DB admin (optional) |

## 🔍 Verify Karein

### 1. Check Services
```bash
docker compose ps
```

Sab services `healthy` honi chahiye.

### 2. Check Kafka Topics
```bash
docker compose exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --list
```

Yeh topics dikhne chahiye:
- `task-events`
- `reminders`
- `notifications`
- `task-events-dlq`
- `reminders-dlq`

### 3. Check PostgreSQL
```bash
docker compose exec postgres psql -U todo_user -d todo_db -c "SELECT version();"
```

## 🛑 Stop Karein

```bash
# Stop (data preserve hoga)
docker compose down

# Stop + data delete
docker compose down -v
```

## 🔧 Troubleshooting

### Issue 1: Port already in use
```bash
# Port 5432 check karein (PostgreSQL)
netstat -ano | findstr :5432

# Port 9092 check karein (Kafka)
netstat -ano | findstr :9092
```

### Issue 2: Kafka unhealthy
```bash
# Logs dekhen
docker compose logs kafka

# Restart karein
docker compose restart kafka
```

### Issue 3: Topics nahi bane
```bash
# Manually create karein
docker compose exec kafka kafka-topics.sh --bootstrap-server localhost:9092 --create --topic task-events --partitions 3 --replication-factor 1
```

## 📝 Connection Strings

### PostgreSQL (for backend .env)
```env
DATABASE_URL=postgresql://todo_user:todo_password@localhost:5432/todo_db
```

### Kafka (for backend .env)
```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9094
```

## 🎯 Next Steps

1. ✅ Docker Compose start karein: `docker compose up -d`
2. ✅ Backend start karein (separate terminal)
3. ✅ Frontend start karein (separate terminal)
4. ✅ Test karein!

---

**Tip**: Pehli baar start karne mein 1-2 minutes lag sakte hain (images download hogi). Baad mein fast hoga! 🚀
