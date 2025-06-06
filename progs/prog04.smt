# program 4 - factorials 1..7
; version 10

7 1
calld dofacts
stop

label dofacts

    label loop1

    dup 
    calld fact

    1 add  ; 7 2 
    2 over ; 7 2 7
    2 over ; 7 2 7 2
    sub    ; 7 2 5
    1 add
    jne loop1  ; 7 2

    drop drop

    return 

label fact

    dup printnum
    33 printchar
    space printchar
    61 printchar
    space printchar

    1 dsrs

    label start

    dup rsds mul dsrs

    1 sub
    dup jne start
    drop

    rsds
    printnum
    println

    return

end
; the end.

-----------------------------

result:
1 ! = 1 
2 ! = 2 
3 ! = 6 
4 ! = 24 
5 ! = 120 
6 ! = 720 
7 ! = 5040 

-----------------------------
