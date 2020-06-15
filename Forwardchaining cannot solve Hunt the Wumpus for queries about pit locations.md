# Forwardchaining cannot solve Hunt the Wumpus for queries about pit locations

The rules for *Hunt the Wumpus* state that when we stand adjacent to a pit $P$ we percieve a breeze $B$. This would be logicllay expressed the following way:

$$
B_{i, j} \equiv P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1}
$$

To transform this rule into horn clauses we first convert it into a CNF

1. Rule: $B_{i, j} \equiv P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1}$

2. Equivalence elimination: $B_{i, j} \Rightarrow  P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1}) \wedge \newline
   (B_{i, j} \Leftarrow  P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1})$

3. Implication elimination: $(\neg B_{i, j} \vee  P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1}) \wedge \newline
   (B_{i, j} \vee  \neg ( P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1}))$

4. De Morgan: $(\neg B_{i, j} \vee  P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1}) \wedge \newline
   (B_{i, j} \vee   (\neg P_{i-1, j} \wedge \neg P_{i+1, j} \wedge \neg P_{i, j-1} \wedge \neg P_{i, j+1}))$

5. Distribute: $(\neg B_{i, j} \vee  P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1}) \wedge \newline
   ( B_{i, j} \vee  \neg P_{i-1, j})  \wedge (B_{i, j} \vee  \neg P_{i+1, j}) \wedge (B_{i, j} \vee \neg P_{i, j-1}) \wedge (B_{i, j} \vee \neg P_{i, j+1})$

But from this CNF we can see that the first clause is not a horn clause. Since a redundance free CNF is unique there is no way to transform this CNF to make it horn clause compatible. However, if we simply ignore the unfitting clause from our KB we are unable to derive some queries, that are provable in the original CNF.

$$
P_{i-1, j} \Rightarrow B_{i, j}
\newline
P_{i+1, j} \Rightarrow B_{i, j}
\newline
P_{i, j-1} \Rightarrow B_{i, j}
\newline
P_{i, j+1} \Rightarrow B_{i, j}
\newline
$$

In this set of clauses that we obtain after eliminating all non-horn clauses, we can see that a breeze is only the conclusion but never the premise of a rule for pits. Therefore we cannot predict the position of pits from percepts like breezes with the forward chaining algorithm. $\square $

## A different approach

... has been stated in the [lecture forum](https://www.ili.fh-aachen.de/ilias.php?ref_id=511551&cmdClass=ilobjforumgui&post_created_below=37100&pos_pk=38162&thr_pk=9784&cmd=viewThread&cmdNode=vu:mo&baseClass=ilRepositoryGUI).  Instead of using $B_{i, j} \equiv P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1}$ as a rule one could use the following rule $ B_{i-1, j} \wedge B_{i+1, j} \wedge B_{i, j-1} \wedge B_{i, j+1} \Rightarrow P_{i, j} $but this also does not work because

$$
(B_{i, j} \equiv P_{i-1, j} \vee P_{i+1, j} \vee P_{i, j-1} \vee P_{i, j+1} )\not \models  (B_{i-1, j} \wedge B_{i+1, j} \wedge B_{i, j-1} \wedge B_{i, j+1} \Rightarrow P_{i, j})
$$

Consider the following $3 \times 3$ Wumpus world:

$P$   $B$   $P$


$B$ $\neg P$  $B$


$P$   $B$   $P$

The first rule is satisfied since $\forall B \exist i, j: P_{i, j} \wedge Adj(\{i, j\},B) $ and $\forall P: Adj(\{i, j\}) \Rightarrow B_{i, j}$.

*For all breezes at least on adjacent square has a pit and for all pits all adjacent squares have breezes.*

The second rule however is not satisfied since the middle square is surrounded by breezes but does not contain a pit. Therfore $B_{i-1, j} \wedge B_{i+1, j} \wedge B_{i, j-1} \wedge B_{i, j+1} \not \Rightarrow P_{i, j} $


