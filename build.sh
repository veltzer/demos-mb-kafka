#!/bin/bash -e
go mod tidy
mkdir -p bin
for x in go_apps/*.elf
do
	echo go build "${x}"
done
