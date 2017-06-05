all: run-all

run-all: src/regen-all-parallel.c
	gcc src/regen-all-parallel.c -o bin/regen-all-parallel

clean:
	rm -f src/*.pyc bin/*.pyc *~ src/*~ bin/regen-all-parallel
