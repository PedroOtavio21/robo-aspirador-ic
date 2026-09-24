# Metodologia experimental

## 1. Objetivo

Comparar um **agente reativo simples** e um **agente baseado em modelos** no
mundo do aspirador de pó, sob duas medidas de desempenho, nas mesmas
configurações.

## 2. Delineamento

- **Tamanho do ambiente:** fixo em **8 × 8**.
- **Períodos:** **T = 500** por execução para todos os agentes (mesmo número de
  períodos — necessário para comparar a Medida A).
- **Configurações:** 40 cenários, variando sujeira, obstáculos e posição
  inicial do agente.
- **Repetições:** o reativo simples é aleatório e roda **10 repetições** por
  configuração (comparado pela média); o baseado em modelos é determinístico e
  roda 1 vez.
- **Controle:** ambos os agentes enfrentam a mesma configuração (mesma grade,
  obstáculos, sujeira, posição inicial, T, pontuação e parada).

Total: 40 configs × (10 reativo + 1 modelo) = **440 execuções**.

## 3. Medidas de desempenho

### Medida A — recompensa por limpeza

A cada período soma-se a **quantidade de quadrados limpos**:

```text
score_A = Σ_t (quadrados limpos no período t)
```

### Medida B — limpeza com penalização por movimento

```text
score_B = score_A − total de movimentos
```

Ambas são calculadas na **mesma execução**, pois a trajetória do agente não
depende da medida.

**Regra de movimento:** toda tentativa de movimento conta (−1), inclusive
batidas em parede/obstáculo; `ASPIRAR` e `NOOP` não contam.

## 4. Geração das configurações

`experimentos/gerador_config.py`:

- `config_id`, `seed`, `largura = altura = 8`;
- `densidade_sujeira ∈ [0,2; 0,6]`;
- `densidade_obstaculo ∈ [0,0; 0,25]`;
- `posicao_inicial` sorteada dentro da grade.

As configurações são gravadas em
`experimentos/configurations/configuracoes.json`. Objetos `Config` são
`dataclasses` imutáveis e guardam a receita completa, permitindo reproduzir
exatamente cada cenário.

## 5. Execução

```bash
python -m experimentos --configs 40 --repeticoes 10 --T 500 --seed 2024
```

`experimentos/executor.py` percorre as configurações e, para cada uma, roda os
dois agentes. Saídas:

- `experimentos/raw/resultados.csv` — uma linha por execução (inclui a
  sequência completa de ações e o mapa inicial);
- `experimentos/raw/historico.csv` — células limpas por período;
- `resultados/tables/medias_globais.csv` — médias por agente e medida;
- `resultados/tables/por_config.csv` — resultados médios por configuração;
- `resultados/charts/*.png` — gráficos.

## 6. Reprodutibilidade

- Sementes registradas (do gerador e por configuração).
- Configurações salvas em JSON.
- Resultados brutos preservados.
- Gerador e simulador puramente determinísticos dadas as sementes.
- Recomenda-se versionar o código em git e registrar o *hash* e a versão do
  Python (ver README).
