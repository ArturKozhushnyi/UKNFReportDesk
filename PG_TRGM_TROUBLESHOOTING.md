# PostgreSQL pg_trgm Extension Troubleshooting

## Issue: `operator class "gin_trgm_ops" does not exist for access method "gin"`

This error occurs when trying to create a GIN trigram index but the `pg_trgm` extension is not installed in the PostgreSQL database.

## Root Cause

The `pg_trgm` extension provides trigram matching capabilities for fuzzy text search. It's part of the PostgreSQL contrib modules and needs to be explicitly installed.

## Solutions

### Solution 1: Use Standard postgres:15 Image (Recommended)

The standard `postgres:15` image includes contrib modules by default. Ensure your `docker-compose.yaml` uses:

```yaml
db:
  image: postgres:15  # This includes contrib modules
  container_name: local_postgres
  # ... rest of configuration
```

Then restart your services:
```bash
docker-compose down
docker-compose up -d
```

### Solution 2: Install Extension Manually

If you're using a different PostgreSQL setup, install the extension manually:

```sql
-- Connect to your database and run:
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Solution 3: System-Level Installation

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install postgresql-contrib-15
```

#### CentOS/RHEL:
```bash
sudo yum install postgresql15-contrib
```

#### macOS (Homebrew):
```bash
brew install postgresql@15
# contrib modules are included by default
```

## Verification

After installation, verify the extension is available:

```sql
-- Check if extension exists
SELECT * FROM pg_extension WHERE extname = 'pg_trgm';

-- Test trigram functions
SELECT similarity('hello', 'helo');
SELECT show_trgm('hello');
```

## Migration Order

The migrations have been updated to handle this gracefully:

1. **008.5_install_pg_trgm_extension.sql** - Installs the extension
2. **009_chat_schema.sql** - Creates tables with conditional trigram indexes

## Fallback Behavior

If the `pg_trgm` extension is not available:

- ✅ **Migration will still succeed**
- ✅ **Regular indexes will be created instead**
- ⚠️ **Fuzzy search capabilities will be limited**
- ✅ **All other functionality works normally**

## Docker Troubleshooting

### Check Extension Installation:
```bash
# Connect to the database container
docker exec -it local_postgres psql -U myuser -d mydatabase

# Check if extension is installed
\dx pg_trgm
```

### Force Reinstall:
```bash
# Stop and remove containers
docker-compose down

# Remove the database volume to start fresh
docker volume rm uknfreportdesk_postgres_data

# Start with contrib image
docker-compose up -d
```

## Alternative: Disable Trigram Indexes

If you cannot install the contrib modules, you can modify the migration to skip trigram indexes entirely by commenting out the trigram index creation in `009_chat_schema.sql`.

## Performance Impact

Without trigram indexes:
- ✅ **Exact tag matching** still works perfectly
- ✅ **Regular LIKE queries** work normally
- ⚠️ **Fuzzy/partial tag search** will be slower
- ✅ **All other functionality** unaffected

## Production Considerations

For production deployments:
1. **Use postgres:15** (includes contrib modules by default)
2. **Test extension availability** before deployment
3. **Monitor search performance** if trigram indexes are missing
4. **Consider full-text search alternatives** if needed

## Related Files

- `migrations/008.5_install_pg_trgm_extension.sql` - Extension installation
- `migrations/009_chat_schema.sql` - Chat schema with conditional indexes
- `docker-compose.yaml` - Updated to use contrib image

## Support

If you continue to have issues:
1. Check PostgreSQL logs: `docker logs local_postgres`
2. Verify extension installation: `\dx` in psql
3. Test with minimal migration: `008.5_install_pg_trgm_extension.sql`
4. Consider using regular indexes as fallback
