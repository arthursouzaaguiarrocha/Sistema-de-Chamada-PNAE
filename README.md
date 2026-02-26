# Sistema-de-Chamada-PNAE

O Sistema de Chamada PNAE é uma aplicação web desenvolvida em Python com o framework Flask, projetada para facilitar o controle de chamadas e a geração de listas de presença no contexto do Programa Nacional de Alimentação Escolar (PNAE) — um programa governamental brasileiro que busca garantir alimentação adequada e saudável para estudantes da educação básica. �
Serviços e Informações do Brasil
🧠 Objetivo do Projeto
O sistema tem como principal objetivo permitir que bolsistas e coordenadores acompanhem e registrem a presença de alunos no recebimento de lanche/refeição escolar, automatizando processos manuais e gerando relatórios em PDF com a chamada.
🛠️ Funcionalidades Principais
👤 Autenticação de Usuários
Login e cadastro de usuários.
Diferenciação entre bolsistas e coordenadores (admin) com privilégios distintos.
📋 Controle de Alunos
Cadastro, edição e remoção de alunos.
Listagem de estudantes por série.
📄 Chamada e Relatórios
Marcação de presença individual por bolsista.
Geração de PDFs de chamada com dados organizados (aluno, série, presença ou ausência).
Relatórios com total de alunos que receberam ou não o lanche.
📨 Envio e Armazenamento
Envio de chamadas para coordenação com armazenamento de PDF no banco de dados.
Download de chamadas diretamente pela interface administrativa.
📊 Painel Administrativo
Dashboard com estatísticas:
Total de alunos cadastrados.
Total de bolsistas.
Chamadas realizadas por dia e no histórico.
Listagem de usuários.
Gestão de usuários (promover/demover privilégios e exclusão).
📁 Tecnologias Utilizadas
Flask – para o backend web.
MySQL – banco de dados relacional para armazenamento de usuários, alunos e chamadas.
ReportLab – geração dinâmica de PDF das chamadas.
HTML/CSS/Jinja2 – templates e interface visual do sistema.
Python como linguagem principal de desenvolvimento.
📦 Estrutura do Projeto
O repositório contém:
app.py – lógica principal e rotas do sistema.
banco.sql – estrutura de banco de dados.
templates/ – arquivos HTML para as páginas do sistema.
static/ – arquivos CSS/JS utilizados na interface.
📈 Benefícios Práticos
✔️ Permite organizar de forma digital e eficiente as chamadas de distribuição de alimentos no contexto escolar.
✔️ Automatiza relatórios e facilita auditoria e acompanhamento por parte da coordenação.
✔️ Reduz erros e tempo gasto em processos manuais de registro.