# Especificação

Documento de referência da implementação (ambiente, sensores, atuadores e
agentes). O código correspondente está em `core/`.

## 1. Ambiente (`core/ambiente.py`)

Grade 2D de células com três estados:

| valor | constante | significado |
|---|---|---|
| 0 | `LIVRE` | célula livre e limpa |
| 1 | `SUJO` | célula livre com sujeira |
| 2 | `OBSTACULO` | célula bloqueada |

Parâmetros: `largura`, `altura`, `densidade_sujeira`, `densidade_obstaculo`,
`seed` e `posicao_inicial`.

A geração sorteia obstáculos e sujeira com `random.Random(seed)` e usa *flood
fill* (BFS) para garantir que todas as células livres estejam conectadas. Se a
posição inicial for informada, ela nunca é obstáculo e o mapa é reamostrado
(até 500 tentativas) até atender às condições. Isso torna cada cenário
**reprodutível** pela seed.

### Propriedades

- **Determinístico** — nenhuma fonte de aleatoriedade durante a execução.
- **Parcialmente observável** — não expõe o mapa; apenas os sensores leem.
- **Desconhecido inicialmente** — o agente não recebe geografia nem sujeira.
- **Dinâmico** — o estado muda com as ações.

### Consultas

- `celula(x, y)`, `quadrados_limpos()`, `limpo()`, `copia_grade()`,
  `mapa_inicial_str()`, `dentro(x, y)`.

## 2. Sensores (`core/sensores.py`)

`Percepcao` (imutável):

- `sujo` — sujeira na célula atual;
- `bateu` — colisão na última tentativa de movimento;
- `posicao` — coordenada **relativa** ao ponto de partida;
- `vizinhanca` — tuplas `(dx, dy, sujo, obstaculo)` no alcance do sensor.

O sensor guarda a posição absoluta de partida (`reset`) e converte a posição
para relativa. Limites do ambiente são reportados como barreira. **Nunca** é
entregue a grade completa.

## 3. Atuadores (`core/atuadores.py`)

`aplicar(ambiente, acao) -> bool` (retorna `bateu`):

- movimentos `CIMA/BAIXO/ESQUERDA/DIREITA`: incrementam o contador de
  movimentos (mesmo quando batem) e movem apenas se a célula destino for livre;
- `ASPIRAR`: remove sujeira da célula atual e incrementa `limpas`;
- `NOOP`: nada faz.

## 4. Agente reativo simples (`AgenteReativoSimples`)

```text
SE sujo  -> ASPIRAR
SENÃO    -> movimento aleatório (seed própria)
```

Não possui mapa interno nem histórico; `mapa_interno()` retorna `None`.

## 5. Agente baseado em modelos (`AgenteBaseadoEmModelo`)

Mantém um `EstadoInterno` (`core/estado_interno.py`): matriz com capacidade
máxima fixa (41×41 por padrão), origem `(0, 0)` no ponto de partida.

Valores da matriz:

| valor | significado |
|---|---|
| 0 | nada / desconhecido |
| 1 | passado (já estava limpo) |
| 2 | sujo conhecido |
| 3 | passado e limpo |
| 4 | barreira / obstáculo / limite |

O agente atualiza a matriz a cada percepção (posição reconciliada pela flag
`bateu`) e decide por BFS: sujo conhecido mais próximo → fronteira mais próxima
→ `NOOP`.

## 6. Contrato

```text
Agente.agir(percepcao) -> Acao
Agente.reset(seed)     -> reinicia estado interno
Agente.mapa_interno()  -> EstadoInterno | None
Sensor.perceber(ambiente, bateu) -> Percepcao
atuadores.aplicar(ambiente, acao) -> bool (bateu)
Simulador.rodar(T) -> Resultado(score_a, score_b, movimentos, passos, acoes, ...)
```
