#! /bin/bash

# rename "s/WhatsApp\ Chat\ with\ ([\w \(\)]+.txt)/\1/" *.txt

SAVEIFS=$IFS
IFS=":"

for f in WhatsApp/raw_data/*.txt;
do
    new_f=${f/.txt/-times.txt}
    new_f=${f/WhatsApp\/raw_data\//}
    echo $new_f
    grep -Po -e "\d\d/\d\d/\d\d\d?\d?, \d?\d:\d\d [APap][Mm] +- +[\w ]+: +.*" "$f" > WhatsApp/timestamps/"$new_f";
    sed -i -r  "s/([0-9]{2}\/[0-9]{2}\/[0-9]{2,4}), ([0-9]{1,2}:[0-9]{2} [aApP][Mm]) +- +([a-zA-Z0-9 ]+): +(.*)/\1,\2,\3,\"\4\"/g" WhatsApp/timestamps/"$new_f";
    rename "s/.txt/.csv/" WhatsApp/timestamps/"$new_f"
done

IFS=$SAVEIFS