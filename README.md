# Trabalho Prático GCC218/262: Problemas Logísticos em Grafos

Este repositório se refere aos entregáveis exigidos pelo trabalho prático da máteria de Sistemas de Informação, Grafos e suas Aplicações.

## 📌 Descrição do Projeto

Este projeto implementa a **Etapa 1** de um trabalho prático focado em modelar problemas logísticos em multigrafos (grafos com arestas bidirecionais e arcos unidirecionais). O código realiza:

- Leitura de dados de entrada.
- Cálculo de métricas estatísticas do grafo.
- Implementação do algoritmo de Floyd-Warshall para matriz de caminhos mais curtos.

**Funcionalidades Principais**:

- Representação do grafo com vértices, arestas e arcos.
- Cálculo de 13 métricas, incluindo densidade, componentes conectados, betweenness centrality, caminho médio e diâmetro.
- Geração de matrizes de distâncias e predecessores.

## 📂 Estrutura do Código

### 1. Classe Graph

Armazena a estrutura do grafo:

    vertices: Conjunto de vértices.

    edges: Arestas bidirecionais.

    arcs: Arcos unidirecionais.

    required_vertices, required_edges, required_arcs: Elementos que exigem serviços.

### 2. Função read_graph(filename)

Lê o arquivo de entrada e popula o objeto Graph.

### 3. Algoritmo floyd_warshall(graph)

Calcula:

    Matriz de distâncias mais curtas (dist).

    Matriz de predecessores (pred).

### 4. Métricas Estatísticas

    Componentes Conectados: Usa BFS (trata arcos como bidirecionais - ver limitações).

    Grau Mínimo/Máximo: Considera arestas e arcos.

    Betweenness Centrality: Frequência de um vértice em caminhos mais curtos.

    Caminho Médio e Diâmetro: Baseados na matriz dist.

## 📇 Partes do Algorítmo

- **Classe Graph**: Armazena os vértices, arestas, arcos e elementos requeridos.
- **Leitura de Dados**: A função read_graph lê um arquivo de entrada e popula o objeto Graph.
- **Algoritmo de Floyd-Warshall**: Calcula a matriz de distâncias mais curtas e predecessores, considerando arestas bidirecionais e arcos unidirecionais.
- **Componentes Conectados**: Usa BFS para encontrar componentes tratando arestas e arcos como não direcionados.
- **Grau dos Vértices**: Calcula grau mínimo e máximo, considerando arestas e arcos.
- **Betweenness Centrality**: Usa a matriz de predecessores para reconstruir caminhos e contar a intermediação.
- **Caminho Médio e Diâmetro**: Calculados a partir da matriz de distâncias.
