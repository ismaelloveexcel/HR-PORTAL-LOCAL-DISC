#!/bin/bash
# Generate a strong PostgreSQL password that meets Azure requirements
#
# Requirements:
# - 3 of 4 character types: uppercase, lowercase, numbers, special chars
# - Cannot contain username (uutfqkhm) or parts of it
# - Minimum 8 characters (recommended: 16+)

# Generate random password
generate_password() {
  # Generate 16 character password with all required types
  local upper=$(LC_ALL=C tr -dc 'A-Z' < /dev/urandom | head -c 4)
  local lower=$(LC_ALL=C tr -dc 'a-z' < /dev/urandom | head -c 4)
  local digits=$(LC_ALL=C tr -dc '0-9' < /dev/urandom | head -c 4)
  local special=$(LC_ALL=C tr -dc '!@#$%^&*' < /dev/urandom | head -c 4)
  
  # Combine and shuffle
  echo "${upper}${lower}${digits}${special}" | fold -w1 | shuf | tr -d '\n'
  echo ""
}

echo "=== PostgreSQL Password Generator ==="
echo ""
echo "Generated password:"
PASSWORD=$(generate_password)
echo "$PASSWORD"
echo ""
echo "Password meets requirements:"
echo "  ✓ Contains uppercase letters"
echo "  ✓ Contains lowercase letters"  
echo "  ✓ Contains numbers"
echo "  ✓ Contains special characters"
echo "  ✓ Does not contain username"
echo ""
echo "Save this password securely!"
echo ""
echo "Use this password when:"
echo "  1. Resetting PostgreSQL password in Azure Portal"
echo "  2. Running: ./scripts/deploy_automated.sh 'PASSWORD'"
