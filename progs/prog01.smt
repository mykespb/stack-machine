# program 1
; version 10
noop
11 22 
2 over
printnum printnum printnum

21 22 23 2 rot
printnum printnum printnum

1
dup
swap drop ; 2 ops
printnum

jump lab001
noop
label lab001
noop

1000 printnum
-300 printnum

10 jeq good
label bad
0 printnum
jump all
label good
1 printnum
label all
-1 printnum

# sub
calld sub
noop
jump after

label sub
111 printnum
return

label after
222 printnum

; memory test
42 1 store
noop
1 fetch
printnum

; show
; noop

61 printchar
println

; dump
; noop

; 999 printnum
; wait
; 888 printnum

# inputs
; inputnum
; 51 printnum
; printnum
; 52 printnum

; inputchar
; 61 printnum
; printchar
; 62 printnum

end
; the end.