for file in vid/*
do
   python detect.py -v "$file" -o "$file".csv
   mv "$file".csv vid/processed/
   mv "$file" vid/processed/
done