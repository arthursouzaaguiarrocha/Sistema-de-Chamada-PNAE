# 📌 Sistema de Chamada PNAE

O **Sistema de Chamada PNAE** é uma aplicação web desenvolvida em **Python**, utilizando o framework **Flask**, com o objetivo de facilitar o controle de chamadas e o registro de presença de alunos no contexto do **Programa Nacional de Alimentação Escolar (PNAE)**.

O sistema foi criado para substituir processos manuais, tornando o acompanhamento da distribuição de refeições escolares mais organizado, seguro e eficiente.

---

## 🎯 Objetivo do Projeto

Permitir que **bolsistas e coordenadores** realizem o controle de presença dos alunos no momento da entrega da alimentação escolar, além de gerar relatórios em **PDF** para acompanhamento e arquivamento.

---

## 🛠️ Funcionalidades

### 👤 Autenticação
- Sistema de **login e cadastro de usuários**.
- Diferenciação de permissões:
  - **Bolsista**
  - **Administrador (Coordenação)**

### 📋 Gerenciamento de Alunos
- Cadastro de alunos.
- Edição e exclusão de registros.
- Organização por série.

### 📝 Chamada
- Marcação de presença e ausência.
- Registro diário da chamada.
- Histórico de chamadas realizadas.

### 📄 Relatórios
- Geração automática de **PDFs de chamada**.
- Relatórios com:
  - Nome do aluno
  - Série
  - Presença ou ausência
- Download de arquivos diretamente pelo sistema.

### 📊 Painel Administrativo
- Total de alunos cadastrados.
- Total de usuários.
- Histórico de chamadas.
- Gerenciamento de usuários (criar, editar e excluir).

---

## 💻 Tecnologias Utilizadas

- **Python**
- **Flask**
- **MySQL**
- **HTML5**
- **CSS3**
- **Jinja2**
- **ReportLab** (geração de PDFs)