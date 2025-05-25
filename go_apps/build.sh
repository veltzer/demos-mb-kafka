#!/bin/bash -e
go mod tidy
for x in *.go
do
	go build -o "bin/${x%.go}.elf" "${x}"
done
