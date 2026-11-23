-- =============================================================================
-- Help Desk (Projeto Integrador - ADS Uceff) | Script 02: DML - dados iniciais
-- Carga de dados de demonstração. Execute DEPOIS do 01_ddl.sql (ou do migrate).
--   psql -h <host> -U helpdesk_user -d helpdesk -f sql/02_dml_dados_iniciais.sql
--
-- Senha de TODOS os usuários de demonstração: Senha@123  (somente para testes)
-- =============================================================================

BEGIN;

INSERT INTO departamento (id, nome, descricao) VALUES
    (1, 'Tecnologia da Informação', 'Suporte a computadores, sistemas e rede'),
    (2, 'Infraestrutura', 'Manutenção predial, elétrica e climatização'),
    (3, 'Administrativo', 'Solicitações de documentos, compras e acessos');

INSERT INTO categoria (id, nome, descricao, departamento_id) VALUES
    (1, 'Hardware', 'Computador, monitor, impressora e periféricos', 1),
    (2, 'Software', 'Instalação e erros em programas', 1),
    (3, 'Rede e Internet', 'Wi-Fi, cabo, VPN e acesso a sistemas', 1),
    (4, 'Manutenção Predial', 'Reparos, iluminação e mobiliário', 2),
    (5, 'Climatização', 'Ar-condicionado e ventilação', 2),
    (6, 'Solicitação Administrativa', 'Documentos, compras e acessos', 3);

INSERT INTO usuario (id, nome, email, senha, perfil, ativo, departamento_id) VALUES
    (1, 'Administrador do Sistema', 'admin@helpdesk.com', 'pbkdf2_sha256$1000000$helpdeskdemo0001$6o9dfR/43OxKjuirWeXG1vZjDsLzkRCL3bRL+48ybJ4=', 'admin',   TRUE, 1),
    (2, 'Carlos Técnico',           'carlos@helpdesk.com', 'pbkdf2_sha256$1000000$helpdeskdemo0001$6o9dfR/43OxKjuirWeXG1vZjDsLzkRCL3bRL+48ybJ4=', 'tecnico', TRUE, 1),
    (3, 'Marina Técnica',           'marina@helpdesk.com', 'pbkdf2_sha256$1000000$helpdeskdemo0001$6o9dfR/43OxKjuirWeXG1vZjDsLzkRCL3bRL+48ybJ4=', 'tecnico', TRUE, 2),
    (4, 'Ana Cliente',              'ana@cliente.com',     'pbkdf2_sha256$1000000$helpdeskdemo0001$6o9dfR/43OxKjuirWeXG1vZjDsLzkRCL3bRL+48ybJ4=', 'cliente', TRUE, 3),
    (5, 'João Cliente',             'joao@cliente.com',    'pbkdf2_sha256$1000000$helpdeskdemo0001$6o9dfR/43OxKjuirWeXG1vZjDsLzkRCL3bRL+48ybJ4=', 'cliente', TRUE, 3);

INSERT INTO chamado (id, titulo, descricao, status, prioridade, solicitante_id, tecnico_id, categoria_id, aberto_em, atualizado_em, fechado_em) VALUES
    (1, 'Computador não liga', 'O computador da recepção não liga desde ontem à tarde.', 'em_andamento', 'alta', 4, 2, 1, now() - interval '3 days', now() - interval '1 day', NULL),
    (2, 'Instalar pacote Office', 'Preciso do pacote Office instalado na máquina nova.', 'aberto', 'media', 5, NULL, 2, now() - interval '2 days', now() - interval '2 days', NULL),
    (3, 'Wi-Fi caindo na sala 2', 'A conexão cai a cada 10 minutos na sala de reuniões 2.', 'aguardando', 'media', 4, 2, 3, now() - interval '5 days', now() - interval '1 day', NULL),
    (4, 'Lâmpada queimada no corredor', 'Duas lâmpadas queimadas no corredor do 2º andar.', 'resolvido', 'baixa', 5, 3, 4, now() - interval '6 days', now() - interval '4 days', NULL),
    (5, 'Ar-condicionado vazando', 'O ar-condicionado da sala 5 está pingando água no chão.', 'fechado', 'alta', 4, 3, 5, now() - interval '10 days', now() - interval '7 days', now() - interval '7 days'),
    (6, 'Sistema fora do ar', 'Ninguém consegue acessar o sistema interno.', 'aberto', 'critica', 5, NULL, 3, now() - interval '2 hours', now() - interval '2 hours', NULL);

INSERT INTO comentario (chamado_id, autor_id, texto, interno, criado_em) VALUES
    (1, 2, 'Vou verificar a fonte de alimentação ainda hoje.', FALSE, now() - interval '2 days'),
    (1, 2, 'Suspeita de fonte queimada. Verificar estoque.', TRUE, now() - interval '2 days'),
    (3, 2, 'Pode informar se o problema ocorre em todos os aparelhos?', FALSE, now() - interval '1 day'),
    (4, 3, 'Lâmpadas trocadas pela equipe de manutenção.', FALSE, now() - interval '4 days'),
    (5, 3, 'Dreno desentupido, sem novos vazamentos.', FALSE, now() - interval '7 days');

INSERT INTO historico_status (chamado_id, alterado_por_id, status_anterior, status_novo, alterado_em) VALUES
    (1, 2, 'aberto', 'em_andamento', now() - interval '2 days'),
    (3, 2, 'aberto', 'em_andamento', now() - interval '4 days'),
    (3, 2, 'em_andamento', 'aguardando', now() - interval '1 day'),
    (4, 3, 'aberto', 'em_andamento', now() - interval '5 days'),
    (4, 3, 'em_andamento', 'resolvido', now() - interval '4 days'),
    (5, 3, 'aberto', 'em_andamento', now() - interval '9 days'),
    (5, 3, 'em_andamento', 'resolvido', now() - interval '8 days'),
    (5, 3, 'resolvido', 'fechado', now() - interval '7 days');

INSERT INTO anexo (chamado_id, enviado_por_id, arquivo) VALUES
    (3, 4, 'anexos/2026/11/foto_roteador.jpg');

-- Ajusta as sequências (identity) após inserir ids explícitos
SELECT setval(pg_get_serial_sequence('departamento', 'id'), (SELECT MAX(id) FROM departamento));
SELECT setval(pg_get_serial_sequence('categoria', 'id'), (SELECT MAX(id) FROM categoria));
SELECT setval(pg_get_serial_sequence('usuario', 'id'), (SELECT MAX(id) FROM usuario));
SELECT setval(pg_get_serial_sequence('chamado', 'id'), (SELECT MAX(id) FROM chamado));

COMMIT;
