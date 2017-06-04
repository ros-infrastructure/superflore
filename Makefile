all: run-all

run-all: regen-all-parallel.c
	gcc regen-all-parallel.c -o regen-all-parallel


clean:
	rm -f *~ *.o regen-all-parallel
