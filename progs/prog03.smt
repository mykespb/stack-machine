# program 3 - factorial 7!
; version 10

7

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

end
; the end.