! Utility module with common procedures
module utils_module
    implicit none
    
    private
    public :: print_array, read_config
    
    ! Module variables
    integer, parameter :: max_size = 1000
    
contains
    
    ! Subroutine to print array elements
    subroutine print_array(arr, size)
        implicit none
        integer, intent(in) :: size
        real(kind=8), intent(in) :: arr(size)
        integer :: i
        
        write(*,*) 'Array contents:'
        do i = 1, size
            write(*,'(I3, F10.3)') i, arr(i)
        end do
    end subroutine print_array
    
    ! Function to read configuration
    function read_config(filename) result(config_value)
        implicit none
        character(len=*), intent(in) :: filename
        integer :: config_value
        integer :: unit_num
        
        unit_num = 10
        open(unit=unit_num, file=filename, status='old', action='read')
        read(unit_num, *) config_value
        close(unit_num)
    end function read_config
    
    ! Private subroutine (not exported)
    subroutine internal_helper()
        implicit none
        write(*,*) 'Internal helper routine'
    end subroutine internal_helper
    
end module utils_module