Tools to assist with 900 Voices Project
======================

# file_mangler
file_mangler.py takes output of https://trint.com's audo parser and converts it to database friendly format.  
Usage:  
file_mangler.py 'source file' 'destination file'  

Example input:  
```    
<article><header><h1>20240112_1243.wav</h1></header><section><p time="940" data-tc="00:00:00"><span class="speaker">Speaker 1 </span><span class="timecode">[00:00:00] </span><span class="word" data-m="940" data-d="90">I </span><span class="word" data-m="1030" data-d="240">remember </span><span class="word" data-m="1270" data-d="149">your </span><span class="word" data-m="1420" data-d="690">communion. </span><span class="word" data-m="3760" data-d="419">Gosh, </span><span class="word" 
```
Example output:
```
id,data_m,data_d,data_w
,940,90,I [BLANK]
,1030,240,remember [BLANK]
,1270,149,your [BLANK]
,1420,690,communion[BLANK]
,3760,419,Gosh[BLANK]
```  
