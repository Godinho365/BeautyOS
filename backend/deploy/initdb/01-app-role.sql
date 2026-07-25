-- Cria o role de APLICAÇÃO do BeautyOS: NÃO-superusuário e NOBYPASSRLS.
-- Isso é ESSENCIAL: superusuários e roles com BYPASSRLS ignoram Row-Level
-- Security, anulando o isolamento multi-tenant. Ver ADR-0003 e
-- docs/architecture/multi-tenant.md.
--
-- O app conecta como beautyos_app; as tabelas de negócio usam FORCE RLS, de modo
-- que a política se aplica inclusive ao dono. CREATEDB é concedido apenas para
-- permitir que a suíte de testes crie o banco de teste.

CREATE ROLE beautyos_app WITH LOGIN PASSWORD 'beautyos_app' NOSUPERUSER NOBYPASSRLS CREATEDB;

-- Permite ao app criar/usar objetos no banco principal.
GRANT CONNECT ON DATABASE beautyos TO beautyos_app;
GRANT CREATE, USAGE ON SCHEMA public TO beautyos_app;
-- Permite instalar extensões CONFIÁVEIS (ex.: btree_gist, usada pelo constraint de
-- exclusão do módulo scheduling) sem ser superusuário. btree_gist é trusted no PG13+.
GRANT CREATE ON DATABASE beautyos TO beautyos_app;
