# Compiler V3

Compiler project for Formal Languages and Theory of Translation (5 sem course). Transforms code 
from specified language to delivered wirtual machine language (desc below).



### Language
- ![](https://placehold.it/15/f03c15/000000?text=+) `program -> DECLARE declarations   BEGIN commands END 
 | BEGIN commands END`
 
- ![](https://placehold.it/15/c5f015/000000?text=+) `declarations -> declarations , pidentifier
 | declarations , pidentifier (num :num )
 | pidentifier
 | pidentifier (num :num )`
 
- ![](https://placehold.it/15/1589F0/000000?text=+) `commands -> commands command
 | command`
 
- ![#](https://placehold.it/15/c5a015/000000?text=+) `command -> identifier ASSIGN expression ;
 | IF condition THEN commands ELSE commands ENDIF
 | IF condition THEN commands ENDIF
 | WHILE condition DO commands ENDWHILE
 | DO commands WHILE condition ENDDO
 | FOR pidentifier FROM value TO value DO commands ENDFOR
 | FOR pidentifier FROM value DOWNTO value DO commands ENDFOR
 | READ identifier ;
 | WRITE value ;`

-  ![#](https://placehold.it/15/efe015/000000?text=+) `expression -> value
 | value + value
 | value - value
 | value * value
 | value / value
 | value % value`
 
- ![#](https://placehold.it/15/000/000000?text=+) `condition -> value = value
 | value != value
 | value < value
 | value > value
 | value <= value
 | value >= value`
 
- ![#](https://placehold.it/15//000000?text=+) `value -> num
 | identifier`
 
- ![#](https://placehold.it/15/c5ffff/000000?text=+) `identifier -> pidentifier
 | pidentifier ( pidentifier )
 | pidentifier (num )`


### Program example

```diff
1 [ Rozkład liczby na czynniki pierwsze ]
2 DECLARE
3 n , m , reszta , potega , dzielnik
4 BEGIN
5 READ n ;
6 dzielnik := 2;
7 m := dzielnik * dzielnik ;
8 WHILE n >= m DO
9 potega := 0;
10 reszta := n % dzielnik ;
11 WHILE reszta = 0 DO
12 n := n / dzielnik ;
13 potega := potega + 1;
14 reszta := n % dzielnik ;
15 ENDWHILE
16 IF potega > 0 THEN [ czy znaleziono dzielnik ]
17 WRITE dzielnik ;
18 WRITE potega ;
19 ELSE
20 dzielnik := dzielnik + 1;
21 m := dzielnik * dzielnik ;
22 ENDIF
23 ENDWHILE
24 IF n != 1 THEN [ ostatni dzielnik ]
25 WRITE n ;
26 WRITE 1;
27 ENDIF
28 END
```


### Writual-machine

Machine consists of 6 registers (r_{a},r_{b},r_{c},r_{d},r_{e},r_{f}), and  memory cells ***p[i]*** labeled as _0,1,2..._ up to _2^62_ and orders counter ***k***. 
Machine performs step by step each order starting from 0. 
Comments are allowed, only in square braces.
Table below contains possible orders, their interpretation and cost . 

| ***COMMAND*** | ***INTERPRETATION*** |***COST***|
| ------ | ------ | ------ |
| ***GET x***  | gets value from input, at stores it at cell p_{r_{x}} |***100***|
| ***PUT x*** |  gets value from memory cell p_{r_{x}} and displays it on screen |***100***|
| ***LOAD x y*** | loads r_{x} value from p_{r_{y}} cell |***20***|
| ***STORE x y*** |  stores r_{x} value at p_{r_{y}} cell |***20***|
| ***ADD x y*** | adds r_{y} value to r_{x}   |***5***|
| ***SUB x y*** | subs r_{y} from r_{x}. Returns max(r_{x}-r_{y},0)  |***5***|
| ***RESET x*** | resets value at r_{x} to 0 |***1***|
| ***INC x*** |  increases value at r_{x} by 1 |***1***|
| ***DEC x*** |  reduces value at r_{x} by 1 |***1***|
| ***SHR x*** |  shifts right value at r_{x}. Returns floor (r_{x}/2)  |***1***|
| ***SHL x*** |  shifts left value at r_{x}.  |***1***|
| ***JUMP j*** | jumps j commands |***1***|
| ***JZERO x j*** |  if value at r_{x} equals 0 jumps j commands, otherwise goes to next command |***1***|
| ***JODD x j*** |   if value at r_{x} is odd jumps j commands, otherwise goes to next command  |***1***|
| ***HALT*** |  Ends program |***0***|


### Installation

Compiler requires  python 3 to run.

```sh
$ sudo apt update
$ sudo apt install python3
$ sudo apt install python3-pip
$ pip3 install sly
```

Usage:

```sh
$ python3 Compiler.py ${input_file} ${output_file}
```


