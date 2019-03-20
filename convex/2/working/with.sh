
#!/usr/bin/env bash

# with tool
# usage: with <program>
# opens an interactive shell instance that automatically prefixes all subsequent commands with program name

pmpt="$*>"

prefix=$*
which $1 2>&1 > /dev/null
program_installed=$?
if [ ! $program_installed -eq 0 ]; then
  echo "error: Program" $1 "is not installed"
  exit 1
fi

stop=false
while [ true ]; do
  while IFS="" read -r -e -d $'\n' -p "$pmpt " options; do
    #history -s "$options"
    curr_command="$(echo $options | { read first rest ; echo $first ; })" 

    if [ -z "$curr_command" ]; then
      # null case
      eval "${prefix}"

      history -s "$prefix" # Chris made this
    else
      # remove with
      if [ $curr_command == - ]; then
        prefix=$( echo $prefix | awk '{$NF="";sub(/[ \t]+$/,"")}1' )
        pmpt="$prefix>"
      # nesting withs
      elif [[ $curr_command == +* ]]; then
        parsed=${options#"+"}
        prefix=$( echo "$prefix" "$parsed" )
        pmpt="$prefix>"
      # process shell commands
      elif [[ $curr_command == :* ]]; then
        parsed=${options#":"}
        if [ "$parsed" = "q" ]; then
          # terminate out of while loop instead of exiting so we can do some safe exiting
          stop=true
          break
        fi
        exec "$parsed"

        history -s "$parsed" # Chris made this
      else
        eval "$prefix $options"

        history -s "$prefix $options" # Chris made this
      fi
    fi



    # see if there are any commands left
    if [ -z "$prefix" ]; then
      echo "No program. Returning to shell."
      # null case
      stop=true
      break
    fi
  done

  if [ stop=true ]; then
    break
  fi

done
