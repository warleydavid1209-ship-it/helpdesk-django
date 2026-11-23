-- =============================================================================
-- Help Desk (Projeto Integrador - ADS Uceff) | Script 03: DML - operações
-- Exemplos das operações que o sistema executa (INSERT, UPDATE, DELETE, SELECT).
-- =============================================================================

-- 1) Abrir um chamado (cliente Ana, categoria Hardware) + registro no histórico
BEGIN;
INSERT INTO chamado (titulo, descricao, prioridade, solicitante_id, categoria_id)
VALUES ('Mouse sem funcionar', 'O mouse parou de responder após queda.', 'baixa', 4, 1);
INSERT INTO historico_status (chamado_id, alterado_por_id, status_anterior, status_novo)
VALUES (currval(pg_get_serial_sequence('chamado', 'id')), 4, '', 'aberto');
COMMIT;

-- 2) Técnico assume um chamado e muda o status para "em andamento"
BEGIN;
UPDATE chamado
   SET tecnico_id = 2, status = 'em_andamento', atualizado_em = now()
 WHERE id = 2 AND status = 'aberto';
INSERT INTO historico_status (chamado_id, alterado_por_id, status_anterior, status_novo)
VALUES (2, 2, 'aberto', 'em_andamento');
COMMIT;

-- 3) Encerrar um chamado resolvido
UPDATE chamado SET status = 'fechado', fechado_em = now(), atualizado_em = now()
 WHERE id = 4 AND status = 'resolvido';

-- 4) Adicionar comentário (público e interno)
INSERT INTO comentario (chamado_id, autor_id, texto, interno) VALUES
    (2, 2, 'Instalação agendada para amanhã cedo.', FALSE),
    (2, 2, 'Licença disponível no cofre de senhas.', TRUE);

-- 5) Excluir um anexo enviado por engano
DELETE FROM anexo WHERE id = 1;

-- 6) Consultas ------------------------------------------------------------

-- 6.1 Fila de atendimento (chamados abertos, mais críticos primeiro)
SELECT c.id, c.titulo, c.prioridade, cat.nome AS categoria, u.nome AS solicitante, c.aberto_em
  FROM chamado c
  JOIN categoria cat ON cat.id = c.categoria_id
  JOIN usuario   u   ON u.id   = c.solicitante_id
 WHERE c.status = 'aberto'
 ORDER BY CASE c.prioridade WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 WHEN 'media' THEN 3 ELSE 4 END,
          c.aberto_em;

-- 6.2 Chamados de um cliente
SELECT id, titulo, status, prioridade, aberto_em FROM chamado WHERE solicitante_id = 4 ORDER BY aberto_em DESC;

-- 6.3 Comentários visíveis ao cliente (sem notas internas)
SELECT cm.criado_em, u.nome AS autor, cm.texto
  FROM comentario cm JOIN usuario u ON u.id = cm.autor_id
 WHERE cm.chamado_id = 1 AND cm.interno = FALSE ORDER BY cm.criado_em;

-- 6.4 Indicadores: quantidade de chamados por status
SELECT status, COUNT(*) AS total FROM chamado GROUP BY status ORDER BY total DESC;

-- 6.5 Carga de trabalho por técnico (chamados em andamento)
SELECT u.nome AS tecnico, COUNT(c.id) AS em_andamento
  FROM usuario u LEFT JOIN chamado c ON c.tecnico_id = u.id AND c.status = 'em_andamento'
 WHERE u.perfil = 'tecnico' GROUP BY u.nome ORDER BY em_andamento DESC;

-- 6.6 Tempo médio de resolução (chamados fechados)
SELECT ROUND(AVG(EXTRACT(EPOCH FROM (fechado_em - aberto_em)) / 3600)::numeric, 1) AS horas_medias
  FROM chamado WHERE fechado_em IS NOT NULL;
