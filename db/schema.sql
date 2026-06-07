-- ============================================================
-- Gestform - Schema da base de dados
-- ============================================================
-- Cola este SQL inteiro no SQL Editor do Supabase.

-- 1. UTILIZADORES E PERFIS
create type user_role as enum (
  'formador', 'coordenador', 'gestor_projeto', 'financeiro', 'admin'
);

create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text unique not null,
  nome text not null,
  nif text,
  iban text,
  role user_role not null default 'formador',
  ativo boolean not null default true,
  magna_id text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index idx_profiles_role on profiles(role);
create index idx_profiles_magna_id on profiles(magna_id);

-- 2. ACOES DE FORMACAO
create type acao_estado as enum (
  'planeada', 'a_decorrer', 'terminada_sem_fecho', 'fechada'
);

create table acoes (
  id uuid primary key default gen_random_uuid(),
  magna_id text unique not null,
  nome text not null,
  codigo text,
  empresa_cliente text,
  formador_id uuid references profiles(id),
  coordenador_id uuid references profiles(id),
  data_inicio date,
  data_fim date,
  volume_horas numeric(10, 2),
  formandos_inscritos int,
  formandos_certificados int,
  valor_formador numeric(10, 2),
  valor_consultor numeric(10, 2),
  valor_empresa numeric(10, 2),
  estado acao_estado not null default 'planeada',
  fechada_em timestamptz,
  last_sync_magna timestamptz,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index idx_acoes_estado on acoes(estado);
create index idx_acoes_formador on acoes(formador_id);
create index idx_acoes_coordenador on acoes(coordenador_id);
create index idx_acoes_data_fim on acoes(data_fim);

-- 3. FATURAS DOS FORMADORES
create type fatura_estado as enum (
  'submetida', 'leitura_falhada', 'acao_nao_fechada',
  'aprovada', 'paga', 'rejeitada'
);

create table faturas (
  id uuid primary key default gen_random_uuid(),
  formador_id uuid not null references profiles(id),
  acao_id uuid references acoes(id),
  acao_nome_submetido text,
  numero_fatura text,
  data_fatura date,
  valor numeric(10, 2),
  nif_emitente text,
  nif_destinatario text,
  ficheiro_url text,
  comprovativo_url text,
  estado fatura_estado not null default 'submetida',
  dados_extraidos jsonb,
  erro_leitura text,
  prazo_pagamento date,
  pago_em timestamptz,
  ultimo_alerta_em timestamptz,
  num_alertas_enviados int default 0,
  notas text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index idx_faturas_formador on faturas(formador_id);
create index idx_faturas_acao on faturas(acao_id);
create index idx_faturas_estado on faturas(estado);
create index idx_faturas_prazo on faturas(prazo_pagamento);

-- 4. FATURACAO DE CONSULTORES
create type faturacao_estado as enum (
  'disponivel', 'selecionada', 'aguarda_confirmacao',
  'confirmada', 'fatura_emitida', 'paga'
);

create table faturacao_consultores (
  id uuid primary key default gen_random_uuid(),
  acao_id uuid not null references acoes(id),
  consultor_id uuid not null references profiles(id),
  valor numeric(10, 2) not null,
  estado faturacao_estado not null default 'disponivel',
  numero_fatura text,
  ficheiro_fatura_url text,
  comprovativo_url text,
  selecionada_em timestamptz,
  confirmada_gestor_em timestamptz,
  confirmada_financeiro_em timestamptz,
  fatura_emitida_em timestamptz,
  paga_em timestamptz,
  notas text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index idx_fc_consultor on faturacao_consultores(consultor_id);
create index idx_fc_estado on faturacao_consultores(estado);

-- 5. REEMBOLSOS
create type reembolso_estado as enum (
  'disponivel', 'selecionado', 'em_processamento', 'concluido'
);

create table reembolsos (
  id uuid primary key default gen_random_uuid(),
  acao_id uuid not null references acoes(id),
  empresa text not null,
  valor numeric(10, 2) not null,
  estado reembolso_estado not null default 'disponivel',
  selecionado_por uuid references profiles(id),
  selecionado_em timestamptz,
  notas text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- 6. LOG DE EMAILS
create type email_tipo as enum (
  'alerta_acao_nao_fechada', 'reforco_acao_nao_fechada',
  'alerta_financeiro_pagamento', 'alerta_leitura_falhada',
  'pedido_confirmacao_faturacao', 'instrucao_emissao_fatura',
  'alerta_financeiro_consultor', 'confirmacao_pagamento',
  'alerta_reembolso'
);

create table email_log (
  id uuid primary key default gen_random_uuid(),
  tipo email_tipo not null,
  destinatario text not null,
  cc text,
  assunto text,
  corpo text,
  fatura_id uuid references faturas(id),
  faturacao_id uuid references faturacao_consultores(id),
  acao_id uuid references acoes(id),
  enviado_em timestamptz default now(),
  resposta_recebida boolean default false,
  resposta_em timestamptz,
  thread_id text
);

create index idx_email_log_enviado on email_log(enviado_em);
create index idx_email_log_tipo on email_log(tipo);

-- 7. EVENTOS DO AGENTE
create table agent_events (
  id uuid primary key default gen_random_uuid(),
  tipo text not null,
  descricao text,
  dados jsonb,
  sucesso boolean default true,
  erro text,
  criado_em timestamptz default now()
);

create index idx_agent_events_criado on agent_events(criado_em desc);

-- 8. ROW-LEVEL SECURITY
alter table profiles enable row level security;
alter table acoes enable row level security;
alter table faturas enable row level security;
alter table faturacao_consultores enable row level security;
alter table reembolsos enable row level security;
alter table email_log enable row level security;

create policy "Ver proprio perfil"
  on profiles for select
  using (auth.uid() = id or exists (
    select 1 from profiles where id = auth.uid()
    and role in ('admin', 'financeiro', 'gestor_projeto')
  ));

create policy "Atualizar proprio perfil"
  on profiles for update
  using (auth.uid() = id);

create policy "Ver acoes relevantes"
  on acoes for select
  using (
    formador_id = auth.uid()
    or coordenador_id = auth.uid()
    or exists (
      select 1 from profiles where id = auth.uid()
      and role in ('admin', 'financeiro', 'gestor_projeto')
    )
  );

create policy "Ver faturas relevantes"
  on faturas for select
  using (
    formador_id = auth.uid()
    or exists (
      select 1 from profiles where id = auth.uid()
      and role in ('admin', 'financeiro')
    )
  );

create policy "Formador insere proprias faturas"
  on faturas for insert
  with check (formador_id = auth.uid());

create policy "Ver faturacao relevante"
  on faturacao_consultores for select
  using (
    consultor_id = auth.uid()
    or exists (
      select 1 from profiles where id = auth.uid()
      and role in ('admin', 'financeiro', 'gestor_projeto')
    )
  );

-- 9. TRIGGERS para updated_at
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger trg_profiles_updated before update on profiles
  for each row execute function set_updated_at();
create trigger trg_acoes_updated before update on acoes
  for each row execute function set_updated_at();
create trigger trg_faturas_updated before update on faturas
  for each row execute function set_updated_at();
create trigger trg_fc_updated before update on faturacao_consultores
  for each row execute function set_updated_at();
create trigger trg_reembolsos_updated before update on reembolsos
  for each row execute function set_updated_at();
