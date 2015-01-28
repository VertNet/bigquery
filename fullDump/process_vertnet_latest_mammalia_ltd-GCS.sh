#!/usr/bin/bash
rm tmpfile*
rm vertnet_latest_mammalia*
gsutil cp gs://vertnet-byclass/vertnet_latest_mammalia_ltd* .
mv vertnet_latest_mammalia_ltd.csv.gz000000000000 vertnet_latest_mammalia_ltd0.csv.gz
mv vertnet_latest_mammalia_ltd.csv.gz000000000001 vertnet_latest_mammalia_ltd1.csv.gz
mv vertnet_latest_mammalia_ltd.csv.gz000000000002 vertnet_latest_mammalia_ltd2.csv.gz
mv vertnet_latest_mammalia_ltd.csv.gz000000000003 vertnet_latest_mammalia_ltd3.csv.gz
mv vertnet_latest_mammalia_ltd.csv.gz000000000004 vertnet_latest_mammalia_ltd4.csv.gz
gunzip vertnet_latest_mammalia_ltd*
sed '1d' vertnet_latest_mammalia_ltd1.csv > tmpfile1
sed '1d' vertnet_latest_mammalia_ltd2.csv > tmpfile2
sed '1d' vertnet_latest_mammalia_ltd3.csv > tmpfile3
sed '1d' vertnet_latest_mammalia_ltd4.csv > tmpfile4
cat vertnet_latest_mammalia_ltd0.csv tmpfile1 tmpfile2 tmpfile3 tmpfile4 > vertnet_latest_mammalia_ltd.csv
gzip vertnet_latest_mammalia_ltd.csv
gsutil cp vertnet_latest_mammalia_ltd.csv.gz gs://vertnet-byclass/vertnet_latest_mammalia_ltd.csv.gz
