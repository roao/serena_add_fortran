# Fortran project configuration
# This could be used for build systems like CMake or Make

# Compiler settings
FC = gfortran
FFLAGS = -O2 -Wall -Wextra -std=f2008

# Source files
SOURCES = main.f90 utils.f90 math_operations.f90 data_processor.f90 legacy.f

# Object files
OBJECTS = $(SOURCES:.f90=.o)
OBJECTS := $(OBJECTS:.f=.o)

# Executable name
PROGRAM = fortran_test

# Build rules
all: $(PROGRAM)

$(PROGRAM): $(OBJECTS)
	$(FC) $(FFLAGS) -o $(PROGRAM) $(OBJECTS)

%.o: %.f90
	$(FC) $(FFLAGS) -c $<

%.o: %.f
	$(FC) $(FFLAGS) -c $<

clean:
	rm -f *.o *.mod $(PROGRAM)

.PHONY: all clean