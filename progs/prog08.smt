# program 8
; version 10

println
"---macros---" printstr 
println

println
"---macros-without-parameters---" printstr 
println

macro _one
1 printnum
2 printnum
3 printnum

macro _two
'q' printchar
'w' printchar
'e' printchar

noop

_one

noop

_two

noop

println
"---macros-with-parameters---" printstr 
println

macro _three
$0 $1
add 
printnum

_three 1 2 
_three 11 22 
_three 111 222 

noop

end 

----------------------------------
result:

---macros---

---macros-without-parameters---
1 2 3 qwe
---macros-with-parameters---
3 33 333 

----------------------------------
