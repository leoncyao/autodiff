# python3 diff.py -f sample2.py 
#!/bin/bash
for file in sample_scripts/*;
do
    echo $file
    python3 diff.py -f $file
done