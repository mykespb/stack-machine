# program 7
; version 10
; conditions and loops

println
"---if-else-then---" printstr 
println

11 printnum

1 if
111 printnum

    0 if
    "yes" printstr
    space printchar
    else 
    "no" printstr
    space printchar
    then
    println

    5 2 sub 
    if 
    "good_age" printstr 
    else
    "grown_up" printstr
    then
    println

; else
; 222 printnum
then

22 printnum

println
"---begin-while-repeat---" printstr 
println

701 printnum

2
begin 

702 printnum

dup printnum

1 sub dup
while

703 printnum

repeat

drop

704 printnum

println
"---do-loop---" printstr 
println

"start-do" printstr println

60
3 do

    1 add dup printnum
    random printnum

loop
drop

println
"finish-do" printstr println

end
; the end.

------------------------------

labset[word] = len(cf)

labref[len(cf)] = word
cf.append(0)
cf.append(0)

do ::    dsrs <do>: rsds dup dsrs jeq <loop> 

loop ::  rsds 1 sub dup dsrs jump <do> <loop>: 

---if-else-then---
11 111 no 
good_age
22 
---begin-while-repeat---
701 702 2 703 702 1 704 
---do-loop---
start-do
61 62362 62 44725 63 61864 
finish-do


------------------------------