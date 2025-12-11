"""
Environment Template
Template de variables de entorno
"""

ENV_TEMPLATE = """# Moodle Docker Infrastructure Configuration
# Generado automaticamente

# GENERAL
MOODLE_VERSION={moodle_version}
PROJECT_NAME=moodle_infrastructure

# TESTING ENVIRONMENT
TEST_URL={test_url}
TEST_DB_NAME={test_db_name}
TEST_DB_USER={test_db_user}
TEST_DB_PASS={test_db_pass}
TEST_DB_ROOT_PASS={test_db_root_pass}
TEST_MOODLE_ADMIN_USER={test_admin_user}
TEST_MOODLE_ADMIN_PASS={test_admin_pass}
TEST_MOODLE_ADMIN_EMAIL={test_admin_email}
TEST_HTTP_PORT={test_http_port}
TEST_HTTPS_PORT={test_https_port}

# PRODUCTION ENVIRONMENT
PROD_URL={prod_url}
PROD_DB_NAME={prod_db_name}
PROD_DB_USER={prod_db_user}
PROD_DB_PASS={prod_db_pass}
PROD_DB_ROOT_PASS={prod_db_root_pass}
PROD_MOODLE_ADMIN_USER={prod_admin_user}
PROD_MOODLE_ADMIN_PASS={prod_admin_pass}
PROD_MOODLE_ADMIN_EMAIL={prod_admin_email}
PROD_HTTP_PORT={prod_http_port}
PROD_HTTPS_PORT={prod_https_port}

# NGINX
NGINX_HTTP_PORT={nginx_http_port}
NGINX_HTTPS_PORT={nginx_https_port}

# BACKUP (opcional - para integracion futura)
BACKUP_RETENTION_DAYS=7
BACKUP_SCHEDULE=0 2 * * *

# SMTP (opcional - para notificaciones)
SMTP_SERVER=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
SMTP_FROM=
SMTP_TO=
"""
