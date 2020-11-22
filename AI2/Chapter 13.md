# Chapter 13

### Exercise 1

Prove from first Principle that $P(b|a \wedge b) = 1$

Proof: $P(b|a\wedge b) = \frac{P(b , a \wedge b)}{P(a \wedge b)} = 1$

### Exercise 2

Using the axioms of Probability, prove that any probability distribution on a discrete random variable must sum to 1.

Trivial? I mean... if one of the Axioms is $\sum_{\omega \in \Omega} P(\omega)=1$ what exactly is left to prove?

### Exercise 3

Prove: $P(a|b, c) = P(b|a, c) \Rightarrow P(a|c) = P(b|c)$



$P(a|b, c) = P(a, b, c)/P(b, c) = P(b|a, c)\cdot P(a, c)/P(b, c)$

Da $P(a|b, c) = P(b|a, c)$ muss also $P(a, c)/P(b, c) = 1$ sein.

$P(a,c) = P(b, c)$

$P(a|c)/P(c)= P(b|c)/P(c)$

$P(a|c) = P(b|c)\quad \square$



Prove: $P(a|b, c) = P(a) \Rightarrow P(b|c) = P(b)$

$P(a, b, c)/P(b, c) = P(a)$

$P(a, b, c) = P(a) \cdot P(b, c) = P(a) \cdot P(c|b) \cdot P(b)$

False



Prove: $P(a|b) = P(a) \Rightarrow P(a|b, c) = P(a|c)$

$P(a, b, c)/P(b, c) = P(a|c)$

$P(a, c)P(b, c)/[P(b, c)P(c)] = P(a|c)$

$P(a, c)/P(c) = P(a|c)$



### Exercise 4

$P(a \vee b) = P(a) + P(b) - P(a\wedge b)$



### Exercise 6

1. $0 \le P(\omega) \le 1$ and $\sum_{\omega \in \Omega} P(\omega) = 1$

2. $\forall \phi: P(\phi) = \sum_{\omega \in \phi}P(\omega)$

Supose: $\phi = a \vee b$

$P(\phi) = P(a \wedge b) + P(a \wedge \neg b) + P(\neg a \wedge b)$

$P(a \wedge b) + P(a \wedge \neg b) + P(\neg a \wedge b) + P(\neg a \wedge \neg b) - P(\neg a \wedge \neg b) = 1 - P(\neg a \wedge \neg b)$

$P(a \wedge b) = P(\neg (\neg a \vee \neg b)) = 1 - P(\neg a \vee \neg b)$

$P(a) = P(a \wedge b) + P(a \wedge \neg b)$

$P(b) = P(b \wedge a) + P(b \wedge \neg a)$

$P(a) + P(b) - P(a\wedge b) = P(a \wedge b) + P(a \wedge \neg b) + P(b \wedge a) + P(b \wedge \neg a) - 1 + P(\neg a \vee \neg b))$

$P(a \wedge b) + P(\neg b \wedge \neg a) + P(\neg a \vee \neg b))$

$P(a \wedge b) + P(\neg b \wedge \neg a) + P(\neg (a \wedge b))$

$1 + P(\neg b \wedge \neg a)$

$1 + P(\neg (a \vee b)) $

$1 + 1 - P(a \vee b)$

$P(a \vee b) = P(a) + P(b) - P(a\wedge b)$


