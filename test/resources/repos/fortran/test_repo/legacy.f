! Legacy Fortran 77 style subroutines for compatibility testing
      subroutine legacy_routine(a, b, n, result)
      implicit none
      integer n
      double precision a(n), b(n), result
      integer i
      
c     Calculate dot product using Fortran 77 syntax
      result = 0.0d0
      do 100 i = 1, n
         result = result + a(i) * b(i)
100   continue
      
      return
      end
      
      function legacy_function(x, y)
      implicit none
      double precision legacy_function, x, y
      
c     Simple arithmetic function
      legacy_function = x * x + y * y
      
      return
      end