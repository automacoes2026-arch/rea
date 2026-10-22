# Contagens da base de prospecção (R1 + R2)

Implementa os requisitos R1 e R2 de [`docs/crm-teardown-salesforce-cockpit.md`](../../docs/crm-teardown-salesforce-cockpit.md):
deduplicação por CNPJ e as contagens separadas da regra 7.4.

Ambiente: **06_CLEAN_ROOM**. Escrito e testado só com CNPJs sintéticos.

## Regras de uso

- Rode **somente no ambiente autorizado** onde a base já está. Não copie a base para cá nem para o repositório.
- A saída contém apenas contagens agregadas, o SHA-256 do arquivo e a versão do script. Nenhum CNPJ, nome ou contato.
- Antes de levar os números para fora do ambiente autorizado, confirme com o compliance.

## Uso

```bash
python3 contagens_base.py base.csv --config mapeamento.json --saida contagens.json
```

Aceita CSV (`,` `;` ou tab, UTF-8) e XLSX (precisa de `openpyxl`). O XLSX lê só a primeira aba.

## Mapeamento

Copie `mapeamento.exemplo.json` e troque os nomes das colunas pelos da sua exportação:

| Campo | Significado |
|---|---|
| `cnpj` | Coluna do CNPJ (obrigatória; aceita formatado ou só dígitos) |
| `chave` | `raiz` (8 dígitos, matriz + filiais = 1 empresa) ou `completo` (14 dígitos) |
| `colunas` | Coluna de cada contagem por entidade (opcional; omitida → `null`) |
| `verdadeiros` | Valores aceitos como "sim" (padrão: `1 s sim true verdadeiro x yes`) |

Uma coluna mapeada que não existe no arquivo interrompe a execução (código 2), para evitar contagem zero por erro de digitação.

## Saída: as 10 contagens da regra 7.4

| Regra 7.4 | Campo |
|---|---|
| registros totais | `registros_totais` |
| CNPJs ou entidades únicas | `cnpjs_unicos`, `entidades_unicas` |
| registros duplicados | `registros_duplicados` (válidos − entidades únicas) |
| cadastros válidos | `cadastros_validos` (CNPJ com DV correto); inválidos em `registros_cnpj_invalido` |
| empresas no segmento | `no_segmento` |
| empresas enriquecidas | `enriquecida` |
| com canal de contato corporativo | `canal_corporativo` |
| priorizadas | `priorizada` |
| abordadas | `abordada` |
| oportunidades abertas | `oportunidade_aberta` |

Por entidade, a contagem é verdadeira se **qualquer** linha daquela entidade estiver marcada.
"No segmento" depende da sua coluna. O script não aplica faixa de faturamento, porque o piso do segmento está ⚠️ CONFLITANTE (pendência 9.3 #17).

## Testes

```bash
python3 -I -m unittest discover -s tests
```
