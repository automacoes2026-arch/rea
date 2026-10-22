# Teardown funcional: Salesforce Sales Cloud → Cockpit de Prospecção PJ

> Ambiente: **06_CLEAN_ROOM** · Acesso: PESSOAL · Evidência: 🔍 INFERIDO / 📥 conhecimento público do produto, **não revalidado contra a documentação oficial nesta sessão**.
> Escopo: análise funcional do produto público. Nenhuma instância, código, tráfego ou dado de terceiros foi acessado. Nenhum insumo do empregador foi usado.
> Antes de qualquer decisão de construção, validar cada item marcado "V" na documentação oficial (Salesforce Help / Object Reference).

## 1. Problema real a resolver

O Cockpit deve ajudar a priorizar, abordar e acompanhar empresas PJ. O Salesforce resolve isso para times grandes; a pergunta útil não é "o que ele tem", e sim **quais capacidades produzem decisão de abordagem** e quais são peso de administração.

## 2. Modelo de dados (Sales Cloud, resumo) — V

| Objeto Salesforce | Função | Equivalente no Cockpit |
|---|---|---|
| Lead | Pessoa/empresa ainda não qualificada | `Empresa` com status `prospect` (chave: CNPJ) |
| Account | Empresa qualificada | `Empresa` com status `carteira` |
| Contact | Pessoa na empresa | `Contato` (canal corporativo apenas, ver §6) |
| Opportunity | Negócio com estágio, valor, probabilidade | `Oportunidade` (produto, estágio, valor estimado) |
| Task / Event | Atividades | `Atividade` (ligação, visita, e-mail, retorno) |
| Campaign / CampaignMember | Origem e lote de abordagem | `Lote` / `Segmento` |
| Product / Pricebook / Quote | Catálogo e cotação | **Fora de escopo**: cálculo de crédito é do motor determinístico (4.5) |
| User / Role / Territory | Dono e hierarquia | `Responsável` / território |

Mecanismo-chave: **Lead Conversion** (Lead → Account + Contact + Opportunity, preservando histórico). No Cockpit: promoção `prospect → carteira` sem perder atividades.

## 3. Capacidades que geram valor de prospecção

| Capacidade | Como funciona no Salesforce | Valor p/ Cockpit | Prioridade proposta |
|---|---|---|---|
| Fila priorizada | List Views + Lead Scoring | Lista do dia ordenada por score explicável | **Alta** |
| Score | Regras ou Einstein (modelo) | Score por regras transparentes, campos visíveis, sem caixa-preta | **Alta** |
| Cadência | Sales Engagement / Cadences: passos, intervalos, canal | Sequência fixa de toques com próximo passo e data | **Alta** |
| Path / estágios | Path guiado por estágio com campos-chave | Estágios + campos obrigatórios por estágio | Média |
| Histórico de atividades | Activity Timeline | Linha do tempo por empresa | **Alta** |
| Duplicidade | Duplicate/Matching Rules | Deduplicação por CNPJ raiz (8 dígitos) | **Alta** |
| Atribuição | Assignment Rules | Só relevante com >1 usuário | Baixa |
| Kanban | Kanban de Opportunity | Visão por estágio | Média |
| Relatórios/Dashboards | Reports, dashboards | Funil, conversão por etapa, aging | Média |
| Automação | Flow, Validation Rules | Regras simples declarativas | Baixa (só após uso recorrente) |
| Permissões | OWD, perfis, sharing | Desnecessário para uso individual | Baixa |
| Histórico de campo | Field History Tracking | Auditoria de mudança de estágio/score | Média |
| Previsão | Forecast | Só com dados de valor e probabilidade reais | Baixa |

## 4. Anti-padrões do Salesforce a **não** copiar

1. Administração pesada (perfis, record types, layouts) sem usuário que a justifique.
2. Score opaco: o analista precisa ver por que a empresa subiu na fila.
3. Campos obrigatórios em excesso, que reduzem o registro de atividade.
4. Forecast sem dado real de probabilidade.

## 5. Requisitos propostos para o Cockpit (PROPOSTO — requer aprovação de Felipe)

Cada requisito segue o formato ação · critério de sucesso · condição de início.

| ID | Requisito | Critério de sucesso | Condição de início |
|---|---|---|---|
| R1 | Chave única por CNPJ raiz; importações idempotentes | Reimportar a mesma base não cria duplicatas | Imediata |
| R2 | Separar as 10 contagens da regra 7.4 (registros, entidades únicas, duplicados, válidos, no segmento, enriquecidas, com canal corporativo, priorizadas, abordadas, oportunidades abertas) | Relatório mostra as 10 contagens distintas | Imediata — script em `experiments/cockpit-base-counts/` |
| R3 | Score por regras com fatores exibidos | Cada posição na fila lista os fatores que a justificam | Após R1 |
| R4 | Cadência com próximo passo e data | Toda empresa abordada tem próximo passo ou motivo de encerramento | Após R1 |
| R5 | Timeline de atividades por empresa | Histórico preservado na promoção prospect → carteira | Após R4 |
| R6 | Registro de estágio com data e motivo de perda | Conversão por etapa calculável | Após R5 |
| R7 | Trilha de auditoria de score e estágio | Mudança tem data, valor anterior e origem | Após R6 |

## 6. Restrições aplicáveis

- **4.1 / 4.4:** este documento não deriva de nenhum sistema do empregador. Qualquer evolução do Cockpit para uso comercial externo depende do Gate 1 (autorização escrita) e de procedência registrada dos componentes.
- **4.3 LGPD:** guardar apenas canais corporativos; finalidade, minimização e retenção definidas; sem CPF nem contato pessoal. Dados públicos não são autorização irrestrita.
- **4.5:** valores de crédito vêm do motor determinístico, nunca do Cockpit nem de IA.
- **2.4 Pipeline de produto:** nada aqui autoriza virar software novo; ver §7.

## 7. Decisões necessárias e riscos

| Decisão | Opções | Recomendação |
|---|---|---|
| Interface oficial de prospecção (pendência 9.2 #9) | Evoluir Cockpit v8 · fundir com Safra PJ Intelligence/PainelPJ | Evoluir Cockpit v8; fusão só após análise de funcionalidades e nota de migração |
| Maturidade do Cockpit | Declarar M1/M2 com evidência | Registrar data da última evidência e uso real antes de investir em R3–R7 |

Riscos: (a) o teardown vem de conhecimento do produto, não de verificação nesta sessão; (b) inferir prioridades sem dados reais de uso do Cockpit; (c) escopo crescer além de "um produto/hipótese principal" (5.2).

## 8. Próximo teste

Aplicar R1 e R2 a uma base real do Cockpit (em ambiente permitido), medir duplicatas e as 10 contagens com `experiments/cockpit-base-counts/contagens_base.py`, e só então decidir R3–R7. Revisão sugerida: após o primeiro uso recorrente.

## 9. Lacunas

- Não verifiquei documentação oficial atualizada (itens "V").
- Não há inventário do Cockpit v8 neste repositório; mapeamento é conceitual.
- Pendências bloqueantes 9.1 (política de atividade externa, Gate 1) seguem abertas.
