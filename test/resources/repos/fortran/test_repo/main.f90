! Main program demonstrating various Fortran features
program main
    use utils_module
    use math_operations
    implicit none
    
    ! Variable declarations
    integer, parameter :: n = 10
    real(kind=8) :: values(n)
    real(kind=8) :: result
    integer :: i
    
    ! Initialize array
    do i = 1, n
        values(i) = real(i, kind=8) * 1.5_8
    end do
    
    ! Call subroutine
    call print_array(values, n)
    
    ! Call function
    result = calculate_mean(values, n)
    
    write(*,*) 'Mean value:', result
    
    ! Call procedure from another module
    call process_data(values, n, result)
    
end program main