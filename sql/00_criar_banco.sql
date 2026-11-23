-- =============================================================================
-- Help Desk (Projeto Integrador - ADS Uceff) | Script 00: banco e usuário
-- SGBD: PostgreSQL 14+ | Executar como superusuário (ex.: postgres)
--   psql -h <host> -p 5432 -U postgres -f sql/00_criar_banco.sql
-- =============================================================================

-- Usuário da aplicação (TROQUE a senha em ambientes reais)
CREATE USER helpdesk_user WITH PASSWORD 'helpdesk_pass';

CREATE DATABASE helpdesk
    OWNER helpdesk_user
    ENCODING 'UTF8'
    TEMPLATE template0;

-- -----------------------------------------------------------------------------
-- PARÂMETROS PARA CONEXÃO REMOTA (servidor PostgreSQL)
--  1) postgresql.conf  -> listen_addresses = '*'        (ou o IP do servidor)
--                         port = 5432
--  2) pg_hba.conf      -> exige SSL e senha para quem vem de fora da máquina:
--        hostssl  helpdesk  helpdesk_user  0.0.0.0/0  scram-sha-256
--     (em produção, troque 0.0.0.0/0 pelo IP/rede que realmente precisa acessar)
--  3) Firewall/rede    -> liberar a porta TCP 5432 apenas para o IP necessário
--  4) Reiniciar o PostgreSQL após alterar os arquivos acima.
--
-- Parâmetros usados pela aplicação (arquivo .env):
--   DB_ENGINE=postgres  DB_NAME=helpdesk  DB_USER=helpdesk_user
--   DB_PASSWORD=...     DB_HOST=<ip-ou-dominio>  DB_PORT=5432  DB_SSLMODE=require
-- Teste de conexão:
--   psql "host=<host> port=5432 dbname=helpdesk user=helpdesk_user sslmode=require"
-- =============================================================================
