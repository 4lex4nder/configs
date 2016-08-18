#Path
export PATH=~/bin:$PATH

export DEFAULT_USER="alex"

# Base16 Shell
[[ -s $BASE16_SHELL ]] && source $BASE16_SHELL

#aliases
alias actr='ccl -l /home/alex/actr6/actr.lisp'
alias coffeebreak='touch ~/Pause/Start-$(date +%x-%H%M) && espeak "Coffee break initialized" && notify-send "Coffee break initialized" && sleep 20m && espeak "Coffee break terminated! Get back to work, peon." && notify-send "Coffee break terminated" && touch ~/Pause/Pause-$(date +%x-%H%M)'
#alias actrgui='sh /home/alex/actr6/environment/GUI/starter.tcl'
#alias actr='actrgui &;sleep 5;actrcl'
alias ls='ls -lah'

# Set up the prompt

autoload -Uz promptinit
promptinit
prompt agnoster

setopt histignorealldups sharehistory

# Use emacs keybindings even if our EDITOR is set to vi
bindkey -e

# Keep 1000 lines of history within the shell and save it to ~/.zsh_history:
HISTSIZE=1000
SAVEHIST=1000
HISTFILE=~/.zsh_history

# Use modern completion system
autoload -Uz compinit
compinit

zstyle ':completion:*' auto-description 'specify: %d'
zstyle ':completion:*' completer _expand _complete _correct _approximate
zstyle ':completion:*' format 'Completing %d'
zstyle ':completion:*' group-name ''
zstyle ':completion:*' menu select=2
eval "$(dircolors -b /home/alex/dircolors.default)"
zstyle ':completion:*:default' list-colors ${(s.:.)LS_COLORS}
zstyle ':completion:*' list-colors ''
zstyle ':completion:*' list-prompt %SAt %p: Hit TAB for more, or the character to insert%s
zstyle ':completion:*' matcher-list '' 'm:{a-z}={A-Z}' 'm:{a-zA-Z}={A-Za-z}' 'r:|[._-]=* r:|=* l:|=*'
zstyle ':completion:*' menu select=long
zstyle ':completion:*' select-prompt %SScrolling active: current selection at %p%s
zstyle ':completion:*' use-compctl false
zstyle ':completion:*' verbose true

zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
zstyle ':completion:*:kill:*' command 'ps -u $USER -o pid,%cpu,tty,cputime,cmd'

# Word jump
bindkey '\033[1;5C' forward-word
bindkey '\033[1;5D' backward-word
