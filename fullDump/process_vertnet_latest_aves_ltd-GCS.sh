#!/usr/bin/bash
rm tmpfile*
rm vertnet_latest_aves*
gsutil cp gs://vertnet-byclass/vertnet_latest_aves_ltd* .
mv vertnet_latest_aves_ltd.csv.gz000000000000 vertnet_latest_aves_ltd0.csv.gz
mv vertnet_latest_aves_ltd.csv.gz000000000001 vertnet_latest_aves_ltd1.csv.gz
mv vertnet_latest_aves_ltd.csv.gz000000000002 vertnet_latest_aves_ltd2.csv.gz
mv vertnet_latest_aves_ltd.csv.gz000000000003 vertnet_latest_aves_ltd3.csv.gz
mv vertnet_latest_aves_ltd.csv.gz000000000004 vertnet_latest_aves_ltd4.csv.gz
mv vertnet_latest_aves_ltd.csv.gz000000000005 vertnet_latest_aves_ltd5.csv.gz
gunzip vertnet_latest_aves_ltd*
sed '1d' vertnet_latest_aves_ltd1.csv > tmpfile1
sed '1d' vertnet_latest_aves_ltd2.csv > tmpfile2
sed '1d' vertnet_latest_aves_ltd3.csv > tmpfile3
sed '1d' vertnet_latest_aves_ltd4.csv > tmpfile4
sed '1d' vertnet_latest_aves_ltd5.csv > tmpfile5
cat vertnet_latest_aves_ltd0.csv tmpfile1 tmpfile2 tmpfile3 tmpfile4 tmpfile5 > vertnet_latest_aves_ltd.csv
gzip vertnet_latest_aves_ltd.csv
gsutil cp vertnet_latest_aves_ltd.csv.gz gs://vertnet-byclass/vertnet_latest_aves_ltd.csv.gz
