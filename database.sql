create table alunos(
	matricula serial primary key,
	nome varchar(80) not null unique,
	senha varchar(50) not null
);

create type status_refeicao as enum('deferido', 'indeferido', 'emergencial');
create type tipo_refeicao as enum('almoço', 'jantar');
create type para_odia as enum('hoje', 'amanhã');

CREATE TABLE refeicoes (
    refeicao_id SERIAL PRIMARY KEY,
    matricula int NOT NULL,
    tipo tipo_refeicao NOT NULL,
    motivo VARCHAR(30),
    para para_odia NOT NULL,
    status status_refeicao NOT NULL,
    FOREIGN KEY (matricula) REFERENCES alunos(matricula)
);

CREATE VIEW doar_refeicoes AS
SELECT *
FROM refeicoes
WHERE status = 'deferido';


insert into alunos(nome, senha)
values ('fulano', 1234),
('sicrano', 4321);

-- -- select * from refeicoes;
-- select * from doar_refeicao;
