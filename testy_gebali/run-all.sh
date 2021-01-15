rm *.compiled
for f in *.imp; do
  python3 ../Compiler.py $f $f.compiled
  done

rm WYNIKI

for f in *.compiled; do
    echo "ZADANIE $f" >> WYNIKI
     ../maszyna-wirtualna  $f >> WYNIKI
done
