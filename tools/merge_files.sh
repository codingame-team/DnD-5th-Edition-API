#!/bin/bash
#
# Shell script to merge genres and surnames/nicknames into multiple race csv files
#

races="dragonborn dwarf elf gnome half-elf half-orc halfling human tiefling"

input_dir="../data/names/source"
output_dir="../data/names"

for race in $races; do
  new_file=".${output_dir}/${race}.csv"
  # echo "Category, Name" >"$new_file"
  for cat in male female surname nickname; do
    file="${input_dir}/${cat}-${race}.csv"
    if [ -e "$file" ]; then
      # shellcheck disable=SC2162
      # shellcheck disable=SC2002
      cat "$file" | while read name; do
        echo "$cat,$name"
      done >>"$new_file"
    fi
  done
done
