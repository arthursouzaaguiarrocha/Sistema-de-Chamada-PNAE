CREATE DATABASE IF NOT EXISTS sistema_pnae;
USE sistema_pnae;

-- Usuários (bolsistas e coordenadores)
CREATE TABLE IF NOT EXISTS usuarios (
    email    VARCHAR(255) PRIMARY KEY,
    nome     VARCHAR(100) NOT NULL,
    senha    VARCHAR(255) NOT NULL,
    is_admin TINYINT(1)   NOT NULL DEFAULT 0
);

-- Alunos
CREATE TABLE IF NOT EXISTS alunos (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    nome  VARCHAR(100) NOT NULL,
    serie VARCHAR(50)  NOT NULL
);

-- Chamadas enviadas pelos bolsistas ao coordenador
CREATE TABLE IF NOT EXISTS chamadas (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    bolsista_email  VARCHAR(255) NOT NULL,
    bolsista_nome   VARCHAR(100) NOT NULL,
    data_chamada    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_alunos    INT          NOT NULL DEFAULT 0,
    receberam       INT          NOT NULL DEFAULT 0,
    pdf_arquivo     LONGBLOB     NOT NULL
);

-- =============================================
-- SE VOCÊ JÁ TEM AS TABELAS, RODE APENAS:
-- =============================================
-- Adicionar coluna nome em usuarios (se não tiver):
--   ALTER TABLE usuarios ADD COLUMN nome VARCHAR(100) NOT NULL DEFAULT '';
--
-- Adicionar coluna is_admin em usuarios (se não tiver):
--   ALTER TABLE usuarios ADD COLUMN is_admin TINYINT(1) NOT NULL DEFAULT 0;
--
-- Criar tabela de chamadas (se não existir):
--   (execute o CREATE TABLE chamadas acima)
--
-- Remover verificacao de alunos (se ainda existir):
--   ALTER TABLE alunos DROP COLUMN verificacao;
--
-- Tornar seu usuário coordenador:
--   UPDATE usuarios SET is_admin=1 WHERE email='seu@email.com';
-- =============================================

-- Coordenador padrão: admin@pnae.com / 1234
INSERT IGNORE INTO usuarios (nome, email, senha, is_admin)
VALUES ('Coordenador', 'admin@pnae.com', '1234', 1);

-- Bolsista de exemplo: bolsista@pnae.com / 1234
INSERT IGNORE INTO usuarios (nome, email, senha, is_admin)
VALUES ('Bolsista Exemplo', 'bolsista@pnae.com', '1234', 0);

-- Alunos de exemplo
INSERT IGNORE INTO alunos (nome, serie) VALUES
    ('Ana Paula Silva',  '5º Ano A'),
    ('Bruno Costa',      '6º Ano B'),
    ('Carlos Eduardo',   '7º Ano A'),
    ('Daniela Souza',    '5º Ano A'),
    ('Eduardo Lima',     '6º Ano B');
