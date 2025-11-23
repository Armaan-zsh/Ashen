" Enable line numbers
set number

" Enable syntax highlighting
syntax on

" Set tabs and indentation
set tabstop=4       " Number of spaces tabs count for
set shiftwidth=4    " Indentation width for < and >
set expandtab       " Use spaces instead of tabs

" Enable smart indentation
set smartindent

" Highlight current line
set cursorline

" Enable mouse support (for terminal vim)
set mouse=a

" Enable incremental search
set incsearch

" Highlight search results
set hlsearch

" Enable line wrapping
set wrap

" Enable clipboard to use system clipboard (requires vim with +clipboard)
set clipboard=unnamedplus

" Show matching brackets
set showmatch

" Enable status line always visible
set laststatus=2

" Set color scheme (optional, requires installed scheme)
colorscheme desert
call plug#begin('~/.vim/plugged')

" Example plugins:
Plug 'tpope/vim-sensible'          " Basic sane defaults
Plug 'junegunn/fzf', { 'do': { -> fzf#install() } } " Fuzzy finder
Plug 'airblade/vim-gitgutter'     " Git diff in gutter

call plug#end()

