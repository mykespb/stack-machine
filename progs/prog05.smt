# program 5 - call functions indirectly
; version 10

addr one
calli

addr two
calli

stop

label one
11 printnum
return 

label two
22 printnum
return

end
; the end.