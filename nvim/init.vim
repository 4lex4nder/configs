" Plugins
call plug#begin('~/.config/nvim/plug')

Plug 'gcmt/taboo.vim'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'octol/vim-cpp-enhanced-highlight'
Plug 'neomake/neomake'
Plug 'vim-scripts/ifdef-highlighting'

function! DoRemote(arg)
	UpdateRemotePlugins
endfunction
Plug 'Shougo/deoplete.nvim', { 'do': function('DoRemote') }

call plug#end()

call deoplete#enable()

" Basic
set sessionoptions+=tabpages,globals
syntax on
filetype indent plugin on
set noerrorbells

" Line numbering
set number
noremap <F3> :set invnumber<CR>
inoremap <F3> <C-O>:set invnumber<CR>
highlight LineNr ctermfg=grey ctermbg=NONE

" Status
" set statusline=%t[%{strlen(&fenc)?&fenc:'none'},%{&ff}]%h%m%r%y%=%c,%l/%L\ %P
set laststatus=2

" Bling
set t_Co=256
"set termguicolors
let g:taboo_tabline = 0
let g:airline_powerline_fonts = 1
let g:airline_theme = 'base16_monokai'
let g:airline#extensions#taboo#enabled = 1
let g:airline#extensions#tabline#enabled = 1
"let base16colorspace = 256
set background=dark

:highlight NeomakeWarningMsg ctermfg=3
:highlight NeomakeErrorMsg ctermfg=1
:highlight SignColumn ctermbg=0
let g:neomake_warning_sign={'text': '', 'texthl': 'NeomakeWarningMsg'}
let g:neomake_error_sign={'text': '', 'texthl': 'NeomakeErrorMsg'}

" Searching
set hlsearch
set ignorecase
set smartcase
nnoremap <Esc> :noh<Return><Esc>

" Projects
"let g:projecttabs#projectlist = {'HybridPlanningGenerator': '/home/alex/Documents/Project/other/UPMurphi_parser1.0R4'}
"call projecttabs#enable()
noremap <F5> :Neomake!<CR>

function SetupEnvironment()
	let l:path = expand('%:p')

	" HybridPlanningGenerator
	if l:path =~ '/home/alex/Documents/Project/other/UPMurphi_parser1.0R4'
		" Set working directory
		cd /home/alex/Documents/Project/other/UPMurphi_parser1.0R4/build-HybridPlanningGenerator-Desktop-Release
		noremap <F4> :call neomake#Sh('make clean')<CR>
	endif
endfunction

augroup code_environment
	autocmd!
	autocmd BufReadPost * call SetupEnvironment() | Neomake
	autocmd BufWritePost * Neomake
augroup END
