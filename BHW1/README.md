
# Trabalho Prático GCC218/262 – Problemas Logísticos em Grafos

Este repositório contém a solução para o trabalho prático da disciplina de Grafos e suas Aplicações, com foco em problemas logísticos em multigrafos.

## 📌 Objetivo Geral

O trabalho é dividido em duas etapas principais:

- **Etapa 1**: Leitura e análise estatística de uma instância de grafo com arcos e arestas.
- **Etapa 2**: Resolução do CARP (Capacitated Arc Routing Problem) com uma heurística baseada em Clarke & Wright.

---

## 📁 Estrutura do Projeto

```
BHW1/
├── BHW1.dat             # Instância de entrada (grafo)
├── main.ipynb           # Notebook com execução da Etapa 1
├── grafo.py             # Leitura e modelagem do grafo
├── estatisticas.py      # Cálculo de estatísticas do grafo
├── etapa2.py            # Implementação da heurística de Clarke & Wright
├── sol_BHW1.dat         # Arquivo de saída com a solução construída
└── README.md            # Este arquivo
```

---

## ✅ Etapa 1 – Estatísticas do Grafo

Nesta etapa, realizamos:

- Leitura do grafo a partir do arquivo `BHW1.dat`
- Cálculo de 13 estatísticas estruturais:

| Métrica                | Descrição |
|------------------------|-----------|
| `vertices`             | Número de vértices no grafo |
| `edges`                | Número de arestas bidirecionais |
| `arcs`                 | Número de arcos unidirecionais |
| `required_vertices`    | Vértices com serviço obrigatório |
| `required_edges`       | Arestas com serviço obrigatório |
| `required_arcs`        | Arcos com serviço obrigatório |
| `density`              | Densidade do grafo considerando arestas + arcos |
| `connected_components` | Número de componentes conexos |
| `min_degree`           | Grau mínimo |
| `max_degree`           | Grau máximo |
| `average_path_length`  | Caminho médio entre pares de vértices |
| `diameter`             | Diâmetro do grafo |
| `betweenness`          | Centralidade de intermediação |

> ⚠️ Limitação: A função de componentes conexos trata arcos como bidirecionais, o que pode superestimar a conectividade.

---

## 🚚 Etapa 2 – Resolução com Clarke & Wright

Nesta etapa, resolvemos uma instância do CARP utilizando a heurística clássica de Clarke & Wright (C&W Savings), adaptada para arcos e arestas com demanda.

### 🔁 Etapas:

1. Leitura da instância e extração de serviços obrigatórios (ReN, ReE, ReA).
2. Cálculo das distâncias mínimas entre todos os pares (Floyd-Warshall).
3. Aplicação da heurística de C&W:
   - Inicialmente, cada serviço é uma rota separada.
   - Cálculo de economias (savings) entre pares de serviços.
   - Combinação de rotas sempre que possível, respeitando a capacidade.

### 📤 Saída gerada (formato `sol_BHW1.dat`):

- Custo total da solução
- Número de rotas
- Tempo de CPU (início e fim)
- Para cada rota:
  - Carga total
  - Custo total
  - Visitas e segmentos no formato: `(D 0,u,v)` para deadhead, `(S id,u,v)` para serviço

Exemplo de linha:
```
0 1 2 1 52 4 (D 0,1,1) (D 0,1,2) (S 1,2,3) (D 0,3,1)
```

---

## 📈 Avaliação da Heurística

- **Instância utilizada**: `BHW1.dat`
- **Capacidade do veículo**: 5 unidades
- **Serviços atendidos**: 12
- **Número de veículos usados**: 6
- **Custo total**: 342
- **Tempo de execução**: ~0.02 segundos

> ⚠️ A solução é viável e respeita a capacidade, mas não há garantias de ótima qualidade. Futuras versões podem incluir:
> - Comparação com heurísticas alternativas (Path Scanning, R&D)
> - Análise do gap entre heurística e lower bounds
> - Execução em múltiplas instâncias públicas (ex: gdb)

---

## 🛠️ Execução

### Requisitos:

- Python 3.8+
- Jupyter Notebook (para `main.ipynb`)

### Como rodar a Etapa 2:
```bash
python etapa2.py
```

Isso gerará o arquivo `sol_BHW1.dat` com a solução formatada.

---

## 👨‍💻 Autoria

Este trabalho foi desenvolvido como parte da disciplina GCC218/GCC262 – Grafos e suas Aplicações, no curso de Sistemas de Informação da Universidade Federal de Lavras (UFLA), pelos alunos: Gabriel Andrade Carvalho e Alexandre Moraes Pereira Carvalhaes Filho.
