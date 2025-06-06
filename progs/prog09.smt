# program 9
; version 10
; fibonacci 24 times

println
"---fibonacci---" printstr 
println

1 printnum       ; print 1
1 printnum       ; print 1

1 1              ; starter
22               ; limit (24, with 2 already printed)
do               ; loop for 22 more times

swap 2 over add  ; calculate

dup printnum     ; print next number

loop             ; aha, loop

drop drop        ; clear stack

end              ; good-bye

----------------------------------
result:

---fibonacci---
1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987 1597 2584 4181 6765 10946 17711 28657 46368 

----------------------------------
