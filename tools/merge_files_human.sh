#!/bin/bash
#
# Shell script to merge ethnic and genre into one single human csv file
#

ethnics="Chondathan Damaran Illuskan Mulan Rashemi Shou Turami Calishite"

input_dir="../data/names/source"
output_dir="../data/names"

new_file="${output_dir}/human.csv"

# echo "Ethnic, Category, Name" >$new_file
>$new_file
for ethnic in $ethnics; do
  for cat in male female surname; do
    file="${input_dir}/${cat}-${ethnic}-human.csv"
    # echo "$file"
    if [ -e "$file" ]; then
      # shellcheck disable=SC2162
      # shellcheck disable=SC2002
      cat "$file" | while read name; do
        echo "$ethnic,$cat,$name"
      done >>$new_file
    fi
  done
done

# cp -p ${output_dir}/human.csv ${output_dir}/half-elf.csv
