#!/bin/bash

echo "Enter number of requests:"
read num_requests

for (( i=1; i<=$num_requests; i++ ))
do
   echo "Making request $i"
   curl http://localhost:5001/url1
done