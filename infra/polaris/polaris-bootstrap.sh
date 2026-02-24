#!/bin/bash
# Bootstrap script to initialize Polaris catalog and create namespaces/roles

set -e

echo "=== Polaris Bootstrap Script ==="

# Wait for Polaris to be ready
echo "Waiting for Polaris to start..."
until curl -s http://polaris:8181/api/catalog/v1/config > /dev/null 2>&1; do
    echo "Polaris not ready yet... waiting"
    sleep 5
done
echo "Polaris is ready!"

# Create catalog if it doesn't exist
echo "Creating catalog..."
curl -X POST http://polaris:8181/api/management/v1/catalogs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "default",
    "type": "ICEBERG",
    "properties": {
      "warehouse": "default"
    }
  }' || echo "Catalog may already exist"

# Create namespaces
echo "Creating namespaces..."
for ns in gold silver bronze; do
    echo "Creating namespace: $ns"
    curl -X POST http://polaris:8181/api/management/v1/namespaces \
      -H "Content-Type: application/json" \
      -d "{
        \"name\": \"$ns\",
        \"properties\": {
          \"description\": \"$ns layer data\",
          \"owner\": \"data-team\"
        }
      }" || echo "Namespace $ns may already exist"
done

# Create roles
echo "Creating roles..."
roles=("catalog_admin" "data_engineer" "analyst")
for role in "${roles[@]}"; do
    echo "Creating role: $role"
    curl -X POST http://polaris:8181/api/management/v1/roles \
      -H "Content-Type: application/json" \
      -d "{
        \"name\": \"$role\",
        \"description\": \"Role for $role\"
      }" || echo "Role $role may already exist"
done

# Assign privileges (simplified example)
echo "Assigning role privileges..."
curl -X PUT http://polaris:8181/api/management/v1/roles/data_engineer/privileges \
  -H "Content-Type: application/json" \
  -d '{
    "privileges": [
      {
        "type": "namespace:create",
        "resource": "default"
      },
      {
        "type": "table:create",
        "resource": "default"
      },
      {
        "type": "table:write",
        "resource": "default"
      },
      {
        "type": "table:read",
        "resource": "default"
      }
    ]
  }' || echo "Privileges may already exist"

echo ""
echo "=== Polaris Bootstrap Complete ==="
echo "Catalog, namespaces, and roles created successfully."
echo ""
echo "You can verify by running:"
echo "  curl http://polaris:8181/api/catalog/v1/config"
