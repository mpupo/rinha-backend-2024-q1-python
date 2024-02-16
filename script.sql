-- Coloque scripts iniciais aqui
CREATE TYPE tipo_transacao AS ENUM ('c', 'd');

CREATE TABLE clientes (
     id    serial PRIMARY KEY,
     limite integer NOT NULL,
     saldo_inicial integer NOT NULL DEFAULT 0
);

CREATE TABLE transacoes (
     id    serial PRIMARY KEY,
     cliente_id   integer REFERENCES clientes(id) NOT NULL,
     tipo  tipo_transacao NOT NULL,
     descricao varchar(40) NOT NULL CHECK (descricao <> ''),
     realizada_em timestamp with time zone DEFAULT current_timestamp
);

DO $$
BEGIN
  INSERT INTO clientes (limite)
  VALUES
    (1000 * 100),
    (800 * 100),
    (10000 * 100),
    (100000 * 100),
    (5000 * 100);
END; $$
