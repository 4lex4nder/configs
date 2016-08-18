" Script for managing project specific tabs

" Require taboo script to be present
if exists('g:projecttabs')
    finish
endif

let g:projecttabs = 1

let s:FINE = 0
let s:NO_BUFFERS_NO_PROJECT = 1
let s:BUFFERS_NO_PROJECT = 2
let s:BUFFERS_PROJECT = 3

let s:bufferpending = []
let s:bufferpendingkind = s:FINE
let s:projecttabnr = 0
let s:lastwindow = 0
let s:enterWindow = 0
let s:leaveWindow = 0

" Get dictionary of projects
let s:projectlist = get(g:, 'projecttabs#projectlist', {})

function s:IsBufferInTab(buffer, tabnr)	
    if a:tabnr < 1
        return 1
    endif

    for itx in tabpagebuflist(a:tabnr)
        if a:buffer == itx
            return 1
        endif
    endfor

    return 0
endfunction

function s:SaveBufferInfo(window, buffer, file, project)
    let s:bufferpending = [a:window, a:buffer, a:file, a:project]
endfunction

function s:HandleWindowChange()
    if s:bufferpendingkind == s:FINE
        return
    elseif s:bufferpendingkind == s:BUFFERS_NO_PROJECT
        exe "TabooOpen " . s:bufferpending[3]
        exe "e " . s:bufferpending[2]
    elseif s:bufferpendingkind == s:BUFFERS_PROJECT
        exe s:projecttabnr . "gt"
        exe "e " . s.bufferpending[2]
    endif

    let s:bufferpending = s:FINE
endfunction

function s:MoveBuffer(buffer, file, project)
    let l:tabexists = 0

    for it in range(1, tabpagenr("$"))
        if TabooTabName(it) == a:project
            let l:tabexists = it
            let s:projecttabnr = it
            break
        endif
    endfor

    let l:tabmatch = s:IsBufferInTab(a:buffer, l:tabexists)
    if l:tabexists && l:tabmatch < 1
        let s:bufferpendingkind = s:BUFFERS_PROJECT
    elseif l:tabexists && l:tabmatch
        let s:bufferpendingkind = s:FINE
    elseif l:tabexists == 0 && a:buffer > 1
        "exe a:buffer . "bd"
        "exe "syntax on"
        let s:bufferpendingkind = s:BUFFERS_NO_PROJECT
        exe "TabooOpen " . a:project
    else
        "exe "TabooRename " . a:project
        let s:bufferpendingkind = s:FINE
    endif

    "doauto BufRead file
endfunction

function s:HandleProjectBuffer()
    let l:path = expand("%:p")
    let l:buffer = bufnr(l:path)
    echom "entering " . l:path

    "if len(s:bufferpending) > 1 && l:path != s:bufferpending[2] && s:bufferpendingkind != s:FINE
     "   call s:HandleWindowChange()
     "   echom "window changed"
     "   return
    "endif

    for [key, val] in items(s:projectlist)
        if l:path =~ val
            "call s:SaveBufferInfo(winnr(), l:buffer, l:path, key)
            call s:MoveBuffer(l:buffer, l:path, key)
        endif
    endfor
endfunction

function s:HandleWindowLeaving()
    echom "leaving " . winnr()
    let s:lastwindow = winnr()
endfunction

function s:WinEnter()
    echom "winenter " . expand("%:p")
    let s:enterWindow = winnr()
endfunction

function s:WinLeave()
    echom "winleave " . expand("%:p")
    let s:leaveWindow = winnr()
endfunction

function projecttabs#enable()
    augroup projecttabs
        autocmd!
        autocmd BufWinEnter * call s:HandleProjectBuffer()
        "autocmd BufWinLeave * call s:HandleWindowLeaving()
        "autocmd BufRead * call s:WinEnter()
        "autocmd BufLeave * call s:WinLeave()
    augroup END
endfunction
