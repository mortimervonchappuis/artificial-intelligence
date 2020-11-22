# Markov Blankets in Baysian Networks

##### Conditional Independence

$P(X, Y|Z) = P(X|Z) \cdot P(Y|Z)$

##### Chainrule

$P(x_1, \dots, x_n) = \prod_{i=1}^{n} P(x_i|x_{i-1}, \dots, x_1)$

##### Baysian Network

$P(x_1, \dots, x_n) = \prod_{i=1}^{n} P(x_i|parents(X_i))$

##### No Link in Network

$¬(X, Y) \Leftrightarrow P(X|Parents(X), Y) = P(X|Parents(X))$

## Markov Cut

$U \in Parent(X)$

$X \in Parent(Y)$

$Z \in Parent(Y)$

$Z \not\in Parent(X)$

$X \not\in Parent(Z)$

##### Theorem

$P(X, Z|U_1, \dots, U_n) = P(X|U_1, \dots, U_n) \cdot P(Z|U_1, \dots, U_n)$

##### Proof

$$
P(X, Z|U_1, \dots, U_n)
$$

$$
\frac{P(U_1, \dots, U_n|X, Z)\cdot P(X, Z)}{P(U_1, \dots, U_n)}
$$

$$
\frac{P(U_1, \dots, U_n, X, Z)}{P(U_1, \dots, U_n)} 
$$

$$
 \frac{P(U_1, \dots, U_n, Z|X)\cdot P(X)}{P(U_1, \dots, U_n)}
$$

$$
\frac{P(X|U_1, \dots, U_n, Z)\cdot P(U_1, \dots, U_n, Z)}{P(U_1, \dots, U_n)}
$$

$$
P(X|U_1, \dots, U_n, Z)\cdot P(Z|U_1, \dots, U_n)
$$

Da keine Verbindung von $Z$ nach $X$ existiert gilt$P(X|Parents(X), Y) = P(X|Parents(X))$ und damit auch $P(X|U_1, \dots, U_n, Z) = P(X|U_1, \dots, U_n)$

$$
P(X|U_1, \dots, U_n) \cdot P(Z|U_1, \dots, U_n)
$$

## Markov Blanket

#### Theorem

$$
P(X, N|U, Y, Z) = P(X|U, Y, Z)\cdot P(N|U, Y, Z)
$$

##### Proof

$$
P(X, N|U, Y, Z)
$$

$$
\frac{P(N, X, U, Y, Z)}{P(U, Y, Z)}
$$

$$
\frac{P(X|U, Y, Z, N) \cdot P(U, Y, Z, N)}{P(U, Y, Z)}
$$

$$
P(X|U, Y, Z, N) \cdot P(N|U, Y, Z)
$$

Da $U = Parents(X)$ ist entweder $N \sub U$ ergo  $P(X|U, Y, Z, N) = P(X|U, Y, Z)$ oder $N \not \sub U$ weshalb ebenfalls $P(X|U, Y, Z, N) = P(X|U, Y, Z)$ und damit

$$

$$


